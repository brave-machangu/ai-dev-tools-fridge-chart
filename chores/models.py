import datetime

from django.conf import settings
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone


def monday_of(day):
    """The Monday that starts the week containing ``day``.

    The week resets cleanly every Monday, so a week is identified everywhere by
    the date of its Monday.
    """
    return day - datetime.timedelta(days=day.weekday())


class Family(models.Model):
    """A household: the group that parents and children belong to."""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'families'

    def __str__(self):
        return self.name

    @property
    def parents(self):
        return self.members.filter(role=Profile.Role.PARENT)

    @property
    def children(self):
        return self.members.filter(role=Profile.Role.CHILD)


class Profile(models.Model):
    """A member of a family.

    Parents are linked to a Django user and sign in to manage everything.
    Children have no credentials, so their profile carries no user at all --
    they only appear on the printed chart and in the point ledger.
    """

    class Role(models.TextChoices):
        PARENT = 'PARENT', 'Parent'
        CHILD = 'CHILD', 'Child'

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True,
        blank=True,
        help_text='Parents only. Children do not have login credentials.',
    )
    display_name = models.CharField(max_length=50)
    role = models.CharField(max_length=6, choices=Role.choices)

    class Meta:
        ordering = ['family', 'role', 'display_name']
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'display_name'],
                name='unique_display_name_per_family',
            ),
            models.CheckConstraint(
                condition=models.Q(role='PARENT') | models.Q(user__isnull=True),
                name='children_have_no_user_account',
            ),
        ]

    def __str__(self):
        return f'{self.display_name} ({self.get_role_display()})'

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT

    @property
    def is_child(self):
        return self.role == self.Role.CHILD

    @property
    def balance(self):
        """Current point balance: everything earned, less everything spent."""
        total = self.ledger_entries.aggregate(total=Sum('points'))['total']
        return total or 0

    def redeem(self, reward):
        """Spend points on a reward.

        Returns True once the points are deducted, or False if the child cannot
        afford it -- balances never go negative. The check and the deduction
        share a transaction so two redemptions cannot both pass on the same
        points.
        """
        with transaction.atomic():
            child = Profile.objects.select_for_update().get(pk=self.pk)
            if child.balance < reward.cost:
                return False

            LedgerEntry.objects.create(
                child=child,
                points=-reward.cost,
                reason=LedgerEntry.Reason.REWARD_REDEEMED,
                description=reward.name,
                reward=reward,
            )
        return True


class Chore(models.Model):
    """A task a child can be given.

    Routine chores are the recurring ones that rotate between children each
    week. Bounties are one-off, higher-value tasks a child claims voluntarily.
    """

    class Kind(models.TextChoices):
        ROUTINE = 'ROUTINE', 'Routine'
        BOUNTY = 'BOUNTY', 'Bounty'

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='chores',
    )
    title = models.CharField(max_length=100)
    points = models.PositiveIntegerField(
        help_text='Base points credited to the child once a parent approves it.',
    )
    kind = models.CharField(
        max_length=7,
        choices=Kind.choices,
        default=Kind.ROUTINE,
    )

    class Meta:
        ordering = ['family', 'kind', 'title']
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'title'],
                name='unique_chore_title_per_family',
            ),
        ]

    def __str__(self):
        return f'{self.title} ({self.points} pts)'

    @property
    def is_routine(self):
        return self.kind == self.Kind.ROUTINE

    @property
    def is_bounty(self):
        return self.kind == self.Kind.BOUNTY


class Reward(models.Model):
    """Something a child can buy with earned points, priced by the parents."""

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='rewards',
    )
    name = models.CharField(max_length=100)
    cost = models.PositiveIntegerField(
        help_text='Points deducted from the child when they redeem this.',
    )

    class Meta:
        ordering = ['family', 'cost', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'name'],
                name='unique_reward_name_per_family',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.cost} pts)'


class ChoreAssignment(models.Model):
    """One chore handed to one child for one week.

    Approval is deliberate: an assignment starts PENDING and stays that way
    until a parent approves it, which is when points are credited. Nothing
    rolls over -- a pending assignment from last week simply stays pending.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'

    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    child = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='assignments',
        limit_choices_to={'role': Profile.Role.CHILD},
    )
    week_start = models.DateField(help_text='The Monday the week starts on.')
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name='approvals',
        null=True,
        blank=True,
        limit_choices_to={'role': Profile.Role.PARENT},
    )

    class Meta:
        ordering = ['-week_start', 'child', 'chore']
        constraints = [
            models.UniqueConstraint(
                fields=['chore', 'week_start'],
                name='one_holder_per_chore_per_week',
            ),
        ]

    def __str__(self):
        return f'{self.chore.title} -> {self.child.display_name} (week of {self.week_start})'

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    def approve(self, by=None):
        """Approve the chore and credit its points to the child.

        Returns True if this call is what credited the points, False if the
        assignment was already approved. Approving twice must never pay twice,
        so the check and the credit happen together in one transaction -- and
        the one-to-one link from the ledger entry back to the assignment means
        the database refuses a second credit even if two requests race.
        """
        with transaction.atomic():
            locked = (
                ChoreAssignment.objects
                .select_for_update()
                .select_related('chore')
                .get(pk=self.pk)
            )
            if locked.status == self.Status.APPROVED:
                return False

            locked.status = self.Status.APPROVED
            locked.approved_at = timezone.now()
            locked.approved_by = by
            locked.save(update_fields=['status', 'approved_at', 'approved_by'])

            LedgerEntry.objects.create(
                child_id=locked.child_id,
                points=locked.chore.points,
                reason=LedgerEntry.Reason.CHORE_APPROVED,
                description=locked.chore.title,
                assignment=locked,
            )

        self.refresh_from_db()
        return True


class LedgerEntry(models.Model):
    """A signed point movement for one child, kept for auditing.

    Positive points are earned by having a chore approved; negative points are
    spent redeeming a reward.
    """

    class Reason(models.TextChoices):
        CHORE_APPROVED = 'CHORE', 'Chore approved'
        REWARD_REDEEMED = 'REWARD', 'Reward redeemed'

    child = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='ledger_entries',
        limit_choices_to={'role': Profile.Role.CHILD},
    )
    points = models.IntegerField(help_text='Positive to earn, negative to spend.')
    reason = models.CharField(max_length=6, choices=Reason.choices)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # What the entry came from, so a credit or a redemption can be traced back.
    assignment = models.OneToOneField(
        ChoreAssignment,
        on_delete=models.SET_NULL,
        related_name='ledger_entry',
        null=True,
        blank=True,
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.SET_NULL,
        related_name='redemptions',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'ledger entries'
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(points=0),
                name='ledger_entry_moves_points',
            ),
        ]

    def __str__(self):
        return f'{self.child.display_name}: {self.points:+d} pts ({self.get_reason_display()})'
