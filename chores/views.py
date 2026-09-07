import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import ChoreAssignment, Profile, monday_of


def parent_profile(user):
    """The profile of the signed-in parent, or None if they have none yet."""
    return (
        Profile.objects
        .select_related('family')
        .filter(user=user)
        .first()
    )


def requested_week(request):
    """The week being looked at: ?week=YYYY-MM-DD, or the current one."""
    raw = request.GET.get('week') or request.POST.get('week')
    if raw:
        try:
            return monday_of(datetime.date.fromisoformat(raw))
        except ValueError:
            pass
    return monday_of(datetime.date.today())


@login_required
def home(request):
    """The parent's landing page: which family they manage, and who is in it.

    Children never sign in, so every authenticated user is expected to be a
    parent. A signed-in user with no profile yet (a fresh superuser, say) still
    gets a page -- it just tells them to create their family in the admin.
    """
    profile = parent_profile(request.user)
    family = profile.family if profile else None

    return render(request, 'chores/home.html', {
        'profile': profile,
        'family': family,
        'parents': family.parents if family else [],
        'children': family.children if family else [],
    })


@login_required
def week(request):
    """This week's chores, grouped by child, with an Approve button each."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    week_start = requested_week(request)
    assignments = (
        ChoreAssignment.objects
        .filter(chore__family=family, week_start=week_start)
        .select_related('chore', 'child')
    )

    by_child = {child.pk: [] for child in family.children}
    for assignment in assignments:
        by_child.setdefault(assignment.child_id, []).append(assignment)

    rows = [
        {
            'child': child,
            'assignments': by_child.get(child.pk, []),
            'balance': child.balance,
        }
        for child in family.children
    ]

    return render(request, 'chores/week.html', {
        'family': family,
        'week_start': week_start,
        'previous_week': week_start - datetime.timedelta(days=7),
        'next_week': week_start + datetime.timedelta(days=7),
        'rows': rows,
    })


@login_required
@require_POST
def approve_assignment(request, pk):
    """Approve one chore, crediting its points once and only once."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    assignment = get_object_or_404(
        ChoreAssignment,
        pk=pk,
        chore__family=profile.family,
    )
    credited = assignment.approve(by=profile)

    if credited:
        messages.success(
            request,
            f'Approved {assignment.chore.title}: '
            f'{assignment.chore.points} points to {assignment.child.display_name}.',
        )
    else:
        messages.info(
            request,
            f'{assignment.chore.title} was already approved, so no points were added again.',
        )

    url = reverse('chores:week')
    return redirect(f'{url}?week={assignment.week_start.isoformat()}')
