"""Tests for the rules that are expensive to get wrong.

Not exhaustive coverage -- these guard the decisions the spec cares about:
approval pays once, balances never go negative, chores rotate, weeks stay
clean, and one family cannot see another.
"""

import datetime
import io

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import (
    Chore, ChoreAssignment, Family, LedgerEntry, Profile, monday_of,
)


class FamilyFixture(TestCase):
    """A family with a signed-in parent and two children."""

    def setUp(self):
        self.family = Family.objects.create(name='Test Family')
        self.user = User.objects.create_user('parent', password='pw-for-tests')
        self.parent = Profile.objects.create(
            family=self.family, user=self.user,
            display_name='Parent', role=Profile.Role.PARENT,
        )
        self.ada = Profile.objects.create(
            family=self.family, display_name='Ada', role=Profile.Role.CHILD,
        )
        self.kofi = Profile.objects.create(
            family=self.family, display_name='Kofi', role=Profile.Role.CHILD,
        )
        self.dishes = Chore.objects.create(
            family=self.family, title='Dishes', points=10,
        )
        self.trash = Chore.objects.create(
            family=self.family, title='Trash', points=5,
        )
        self.reward = self.family.rewards.create(name='Screen time', cost=20)
        self.week = monday_of(datetime.date.today())
        self.client.force_login(self.user)


class WeekHelperTests(TestCase):
    def test_every_day_of_a_week_maps_to_its_monday(self):
        monday = datetime.date(2026, 9, 7)
        for offset in range(7):
            day = monday + datetime.timedelta(days=offset)
            self.assertEqual(monday_of(day), monday)

    def test_sunday_belongs_to_the_week_that_started_before_it(self):
        self.assertEqual(
            monday_of(datetime.date(2026, 9, 6)), datetime.date(2026, 8, 31),
        )


class ApprovalTests(FamilyFixture):
    def test_approving_credits_the_chore_points_once(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        self.assertTrue(assignment.approve(by=self.parent))
        self.assertEqual(self.ada.balance, 10)

    def test_approving_twice_does_not_pay_twice(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        assignment.approve(by=self.parent)
        self.assertFalse(assignment.approve(by=self.parent))
        self.assertEqual(self.ada.balance, 10)
        self.assertEqual(self.ada.ledger_entries.count(), 1)

    def test_the_view_credits_once_however_often_it_is_posted(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        url = reverse('chores:approve_assignment', args=[assignment.pk])
        for _ in range(3):
            self.client.post(url)
        self.assertEqual(self.ada.balance, 10)

    def test_points_are_not_credited_before_approval(self):
        ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        self.assertEqual(self.ada.balance, 0)


class RedemptionTests(FamilyFixture):
    def earn(self, points):
        LedgerEntry.objects.create(
            child=self.ada, points=points,
            reason=LedgerEntry.Reason.CHORE_APPROVED,
        )

    def test_redeeming_deducts_exactly_the_cost(self):
        self.earn(50)
        self.assertTrue(self.ada.redeem(self.reward))
        self.assertEqual(self.ada.balance, 30)

    def test_a_child_who_cannot_afford_it_is_refused_and_loses_nothing(self):
        self.earn(19)
        self.assertFalse(self.ada.redeem(self.reward))
        self.assertEqual(self.ada.balance, 19)
        self.assertEqual(self.ada.ledger_entries.count(), 1)

    def test_spending_an_exact_balance_is_allowed_and_lands_on_zero(self):
        self.earn(20)
        self.assertTrue(self.ada.redeem(self.reward))
        self.assertEqual(self.ada.balance, 0)
        self.assertFalse(self.ada.redeem(self.reward))

    def test_the_view_refuses_an_unaffordable_redemption(self):
        self.earn(5)
        self.client.post(
            reverse('chores:redeem_reward', args=[self.reward.pk]),
            {'child': self.ada.pk},
        )
        self.assertEqual(self.ada.balance, 5)


class RotationTests(FamilyFixture):
    def holder(self, chore, week):
        return ChoreAssignment.objects.get(chore=chore, week_start=week).child

    def test_a_chore_moves_to_a_different_child_the_following_week(self):
        call_command('generate_week', family=self.family.name, week='2026-09-14', stdout=io.StringIO())
        call_command('generate_week', family=self.family.name, week='2026-09-21', stdout=io.StringIO())
        first = self.holder(self.dishes, datetime.date(2026, 9, 14))
        second = self.holder(self.dishes, datetime.date(2026, 9, 21))
        self.assertNotEqual(first, second)

    def test_running_it_again_creates_nothing(self):
        call_command('generate_week', family=self.family.name, week='2026-09-14', stdout=io.StringIO())
        before = ChoreAssignment.objects.count()
        call_command('generate_week', family=self.family.name, week='2026-09-14', stdout=io.StringIO())
        self.assertEqual(ChoreAssignment.objects.count(), before)

    def test_bounties_are_never_assigned_automatically(self):
        bounty = Chore.objects.create(
            family=self.family, title='Wash the car', points=50,
            kind=Chore.Kind.BOUNTY,
        )
        call_command('generate_week', family=self.family.name, week='2026-09-14', stdout=io.StringIO())
        self.assertFalse(bounty.assignments.exists())

    def test_last_weeks_pending_work_is_left_alone(self):
        stale = ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada,
            week_start=datetime.date(2026, 9, 7),
        )
        call_command('generate_week', family=self.family.name, week='2026-09-14', stdout=io.StringIO())
        stale.refresh_from_db()
        self.assertEqual(stale.status, ChoreAssignment.Status.PENDING)
        self.assertEqual(stale.child, self.ada)


class ConstraintTests(FamilyFixture):
    def test_a_child_cannot_hold_a_login(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profile.objects.create(
                family=self.family,
                user=User.objects.create_user('kid', password='pw-for-tests'),
                display_name='Sneaky', role=Profile.Role.CHILD,
            )

    def test_one_chore_has_one_holder_per_week(self):
        ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ChoreAssignment.objects.create(
                chore=self.dishes, child=self.kofi, week_start=self.week,
            )

    def test_an_approval_cannot_be_credited_twice(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.dishes, child=self.ada, week_start=self.week,
        )
        assignment.approve(by=self.parent)
        with self.assertRaises(IntegrityError), transaction.atomic():
            LedgerEntry.objects.create(
                child=self.ada, points=10,
                reason=LedgerEntry.Reason.CHORE_APPROVED, assignment=assignment,
            )


class AccessTests(FamilyFixture):
    def test_every_page_requires_a_login(self):
        self.client.logout()
        for name in ['home', 'week', 'balances', 'bounties', 'rewards', 'setup']:
            response = self.client.get(reverse('chores:' + name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn('/accounts/login/', response['Location'], name)

    def test_another_familys_child_is_not_visible(self):
        other = Family.objects.create(name='Other Family')
        outsider = Profile.objects.create(
            family=other, display_name='Outsider', role=Profile.Role.CHILD,
        )
        response = self.client.get(
            reverse('chores:child_ledger', args=[outsider.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_a_parent_with_no_family_is_sent_to_setup(self):
        self.client.force_login(
            User.objects.create_user('lonely', password='pw-for-tests')
        )
        response = self.client.get(reverse('chores:home'))
        self.assertRedirects(response, reverse('chores:setup'))


class BountyTests(FamilyFixture):
    def setUp(self):
        super().setUp()
        self.bounty = Chore.objects.create(
            family=self.family, title='Rake leaves', points=30,
            kind=Chore.Kind.BOUNTY,
        )

    def test_a_claim_still_needs_approval_before_it_pays(self):
        self.client.post(
            reverse('chores:claim_bounty', args=[self.bounty.pk]),
            {'child': self.kofi.pk},
        )
        assignment = ChoreAssignment.objects.get(chore=self.bounty)
        self.assertEqual(assignment.status, ChoreAssignment.Status.PENDING)
        self.assertEqual(self.kofi.balance, 0)

        self.client.post(
            reverse('chores:approve_assignment', args=[assignment.pk])
        )
        self.assertEqual(self.kofi.balance, 30)

    def test_an_approved_bounty_leaves_the_open_board(self):
        self.client.post(
            reverse('chores:claim_bounty', args=[self.bounty.pk]),
            {'child': self.kofi.pk},
        )
        assignment = ChoreAssignment.objects.get(chore=self.bounty)
        response = self.client.get(reverse('chores:bounties'))
        open_titles = [row['bounty'] for row in response.context['board']]
        self.assertIn(self.bounty, open_titles)

        assignment.approve(by=self.parent)
        response = self.client.get(reverse('chores:bounties'))
        open_titles = [row['bounty'] for row in response.context['board']]
        finished = [row['bounty'] for row in response.context['finished']]
        self.assertNotIn(self.bounty, open_titles)
        self.assertIn(self.bounty, finished)


class ReminderTests(FamilyFixture):
    def setUp(self):
        super().setUp()
        self.user.email = 'parent@example.com'
        self.user.save()

    def test_friday_sends_the_review_reminder(self):
        call_command('send_reminders', family=self.family.name, date='2026-09-11', stdout=io.StringIO())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Review', mail.outbox[0].subject)

    def test_sunday_sends_the_print_reminder(self):
        call_command('send_reminders', family=self.family.name, date='2026-09-13', stdout=io.StringIO())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Print', mail.outbox[0].subject)

    def test_the_other_five_days_send_nothing(self):
        quiet = ['2026-09-07', '2026-09-08', '2026-09-09', '2026-09-10', '2026-09-12']
        for day in quiet:
            call_command('send_reminders', family=self.family.name, date=day, stdout=io.StringIO())
        self.assertEqual(mail.outbox, [])


class ChartTests(FamilyFixture):
    def test_the_chart_downloads_as_a_pdf(self):
        response = self.client.get(reverse('chores:week_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
