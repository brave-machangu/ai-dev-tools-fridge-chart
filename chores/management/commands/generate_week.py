import datetime

from django.core.management.base import BaseCommand, CommandError

from chores.models import Chore, ChoreAssignment, Family, monday_of


class Command(BaseCommand):
    help = (
        'Create the coming week\'s routine chore assignments for a family, '
        'rotating the chores between the children.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--family',
            help='Family name or id. Optional when there is only one family.',
        )
        parser.add_argument(
            '--week',
            help='Any date (YYYY-MM-DD) inside the target week. '
                 'Defaults to the coming week.',
        )

    def handle(self, *args, **options):
        family = self._resolve_family(options['family'])
        week = self._resolve_week(options['week'])

        children = list(family.children)
        if not children:
            raise CommandError(f'{family.name} has no children to assign chores to.')

        routines = list(family.chores.filter(kind=Chore.Kind.ROUTINE).order_by('pk'))
        if not routines:
            self.stdout.write(self.style.WARNING(
                f'{family.name} has no routine chores, so there is nothing to rotate.'
            ))
            return

        # The rotation is a function of the week itself, so it is stable no
        # matter when the command runs, and shifts by one child each week.
        offset = week.toordinal() // 7

        self.stdout.write(f'{family.name} -- week of {week} ({len(children)} children)')
        created = existing = 0
        for index, chore in enumerate(routines):
            child = children[(index + offset) % len(children)]
            assignment, was_created = ChoreAssignment.objects.get_or_create(
                chore=chore,
                week_start=week,
                defaults={'child': child},
            )
            if was_created:
                created += 1
                self.stdout.write(f'  + {chore.title} -> {assignment.child.display_name}')
            else:
                existing += 1
                self.stdout.write(
                    f'  = {chore.title} -> {assignment.child.display_name} (already assigned)'
                )

        # Anything still pending from an earlier week stays where it is: the
        # week starts clean, with no carry-over and no penalty.
        stale = ChoreAssignment.objects.filter(
            chore__family=family,
            week_start__lt=week,
            status=ChoreAssignment.Status.PENDING,
        ).count()

        self.stdout.write(self.style.SUCCESS(
            f'created {created}, already present {existing}; '
            f'{stale} pending from earlier weeks left untouched'
        ))

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

    def _resolve_week(self, value):
        if value is None:
            return monday_of(datetime.date.today() + datetime.timedelta(days=7))
        try:
            day = datetime.date.fromisoformat(value)
        except ValueError:
            raise CommandError(f'--week must be YYYY-MM-DD, got {value!r}.')
        return monday_of(day)
