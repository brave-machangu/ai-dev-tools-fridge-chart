from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Profile


@login_required
def home(request):
    """The parent's landing page: which family they manage, and who is in it.

    Children never sign in, so every authenticated user is expected to be a
    parent. A signed-in user with no profile yet (a fresh superuser, say) still
    gets a page -- it just tells them to create their family in the admin.
    """
    profile = (
        Profile.objects
        .select_related('family')
        .filter(user=request.user)
        .first()
    )
    family = profile.family if profile else None

    return render(request, 'chores/home.html', {
        'profile': profile,
        'family': family,
        'parents': family.parents if family else [],
        'children': family.children if family else [],
    })
