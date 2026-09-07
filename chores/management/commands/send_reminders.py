import datetime

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from chores.models import ChoreAssignment, Family, monday_of

FRIDAY = 4
SUNDAY = 6


class Command(BaseCommand):
    help = (
        'Send the two weekly reminders: review the chores on Friday, print '
        'next week\'s chart on Sunday. Silent on every other day.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--family',
            help='Family name or id. Optional when there is only one family.',
        )
        parser.add_argument(
            '--date',
            help='Pretend today is this date (YYYY-MM-DD). Defaults to today.',
        )

    def handle(self, *args, **options):
        today = self._resolve_date(options['date'])
        weekday = today.weekday()

        if weekday == FRIDAY:
            subject, body = self._review_reminder(options['family'], today)
        elif weekday == SUNDAY:
            subject, body = self._print_reminder(options['family'], today)
        else:
            # Low-noise by design: nothing goes out on the other five days, and
            # nothing is printed either, so a cron run stays quiet.
            if options['verbosity'] >= 2:
                self.stdout.write(f'{today} is a {today:%A}; no reminder is due.')
            return

        family = self._resolve_family(options['family'])
        recipients = [
            parent.user.email
            for parent in family.parents
            if parent.user and parent.user.email
        ]
        if not recipients:
            self.stdout.write(self.style.WARNING(
                f'No parent in {family.name} has an email address, '
                f'so nothing was sent.'
            ))
            return

        send_mail(subject, body, None, recipients)
        self.stdout.write(self.style.SUCCESS(
            f'{today:%A}: sent "{subject}" to {", ".join(recipients)}'
        ))

    def _review_reminder(self, family_option, today):
        family = self._resolve_family(family_option)
        week = monday_of(today)
        pending = (
            ChoreAssignment.objects
            .filter(
                chore__family=family,
                week_start=week,
                status=ChoreAssignment.Status.PENDING,
            )
            .select_related('chore', 'child')
        )

        lines = [
            f'Time to review this week\'s chores for {family.name}.',
            '',
        ]
        if pending:
            lines.append(f'{len(pending)} still waiting for your approval:')
            lines += [
                f'  - {a.chore.title} ({a.child.display_name}, {a.chore.points} pts)'
                for a in pending
            ]
        else:
            lines.append('Everything this week is already approved. Nothing to do.')
        lines += ['', 'Approve them at /week/ so the points land before the week resets.']

        return f'Review this week\'s chores ({family.name})', '\n'.join(lines)

    def _print_reminder(self, family_option, today):
        family = self._resolve_family(family_option)
        next_week = monday_of(today + datetime.timedelta(days=1))

        body = '\n'.join([
            f'Tomorrow starts a new week for {family.name}.',
            '',
            f'Generate the rotation for the week of {next_week}:',
            '  uv run python manage.py generate_week',
            '',
            'Then print the chart from /week/chart.pdf and put it on the fridge.',
        ])
        return f'Print next week\'s chart ({family.name})', body

    def _resolve_family(self, value):
        if value is None:
            families = list(Family.objects.all()[:2])
            if not families:
                raise CommandError('No families exist yet.')
            if len(families) > 1:
                raise CommandError('More than one family exists -- pass --family.')
            return families[0]

        if value.isdigit():
            family = Family.objects.filter(pk=int(value)).first()
            if family:
                return family
        family = Family.objects.filter(name=value).first()
        if not family:
            raise CommandError(f'No family matching {value!r}.')
        return family

    def _resolve_date(self, value):
        if value is None:
            return datetime.date.today()
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            raise CommandError(f'--date must be YYYY-MM-DD, got {value!r}.')
