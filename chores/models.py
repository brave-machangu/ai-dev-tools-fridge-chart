from django.conf import settings
from django.db import models


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
