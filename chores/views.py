import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import BountyForm
from .pdf import build_week_chart
from .models import Chore, ChoreAssignment, Profile, Reward, monday_of


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


def week_rows(family, week_start):
    """One entry per child: their chores for the week, and their balance."""
    assignments = (
        ChoreAssignment.objects
        .filter(chore__family=family, week_start=week_start)
        .select_related('chore', 'child')
    )

    by_child = {child.pk: [] for child in family.children}
    for assignment in assignments:
        by_child.setdefault(assignment.child_id, []).append(assignment)

    return [
        {
            'child': child,
            'assignments': by_child.get(child.pk, []),
            'balance': child.balance,
        }
        for child in family.children
    ]


@login_required
def week(request):
    """This week's chores, grouped by child, with an Approve button each."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    week_start = requested_week(request)
    rows = week_rows(family, week_start)

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


@login_required
def balances(request):
    """Every child in the family with the points they have right now."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    rows = [
        {
            'child': child,
            'balance': child.balance,
            'entry_count': child.ledger_entries.count(),
        }
        for child in family.children
    ]

    return render(request, 'chores/balances.html', {
        'family': family,
        'rows': rows,
    })


@login_required
def child_ledger(request, pk):
    """One child's full history of points earned and spent."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    child = get_object_or_404(
        Profile,
        pk=pk,
        family=profile.family,
        role=Profile.Role.CHILD,
    )
    entries = (
        child.ledger_entries
        .select_related('assignment__chore', 'reward')
        .order_by('created_at')
    )

    return render(request, 'chores/ledger.html', {
        'child': child,
        'entries': entries,
        'balance': child.balance,
    })


@login_required
def bounties(request):
    """The bounty board: open one-off tasks, and a form to post a new one."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    if request.method == 'POST':
        form = BountyForm(request.POST, family=family)
        if form.is_valid():
            bounty = form.save()
            messages.success(
                request, f'Posted {bounty.title} for {bounty.points} points.'
            )
            return redirect('chores:bounties')
    else:
        form = BountyForm(family=family)

    board = [
        {'bounty': bounty, 'assignment': bounty.assignments.first()}
        for bounty in family.chores.filter(kind=Chore.Kind.BOUNTY)
    ]

    return render(request, 'chores/bounties.html', {
        'family': family,
        'form': form,
        'board': board,
        'children': family.children,
    })


@login_required
@require_POST
def claim_bounty(request, pk):
    """Hand a bounty to the child who claimed it, for the current week.

    It becomes an ordinary assignment from here, so it goes through the same
    parent approval as any routine chore before points are credited.
    """
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    bounty = get_object_or_404(
        Chore,
        pk=pk,
        family=profile.family,
        kind=Chore.Kind.BOUNTY,
    )
    child = get_object_or_404(
        Profile,
        pk=request.POST.get('child'),
        family=profile.family,
        role=Profile.Role.CHILD,
    )

    week_start = monday_of(datetime.date.today())
    assignment, created = ChoreAssignment.objects.get_or_create(
        chore=bounty,
        week_start=week_start,
        defaults={'child': child},
    )
    if created:
        messages.success(
            request,
            f'{child.display_name} claimed {bounty.title}. '
            f'Approve it once the work is done.',
        )
    else:
        messages.info(
            request,
            f'{bounty.title} is already claimed by {assignment.child.display_name}.',
        )

    return redirect('chores:bounties')


@login_required
def rewards(request):
    """The rewards store: what points can buy, and who can afford it."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    return render(request, 'chores/rewards.html', {
        'family': family,
        'rewards': family.rewards.all(),
        'children': family.children,
    })


@login_required
@require_POST
def redeem_reward(request, pk):
    """Spend a child's points on a reward, unless they cannot afford it."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    reward = get_object_or_404(Reward, pk=pk, family=profile.family)
    child = get_object_or_404(
        Profile,
        pk=request.POST.get('child'),
        family=profile.family,
        role=Profile.Role.CHILD,
    )

    if child.redeem(reward):
        messages.success(
            request,
            f'{child.display_name} redeemed {reward.name} for {reward.cost} points. '
            f'Balance is now {child.balance}.',
        )
    else:
        messages.error(
            request,
            f'{child.display_name} has {child.balance} points and '
            f'{reward.name} costs {reward.cost}. Nothing was deducted.',
        )

    return redirect('chores:rewards')


@login_required
def week_pdf(request):
    """The fridge chart: this week as a one-page PDF, ready to print."""
    profile = parent_profile(request.user)
    if profile is None:
        return redirect('chores:home')

    family = profile.family
    week_start = requested_week(request)
    pdf = build_week_chart(
        family,
        week_start,
        week_rows(family, week_start),
        family.chores.filter(kind=Chore.Kind.BOUNTY),
    )

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="chores-{week_start}.pdf"'
    )
    return response
