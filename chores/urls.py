from django.urls import path

from . import views

app_name = 'chores'

urlpatterns = [
    path('', views.home, name='home'),
    path('setup/', views.setup, name='setup'),
    path('week/', views.week, name='week'),
    path('week/chart.pdf', views.week_pdf, name='week_pdf'),
    path(
        'assignments/<int:pk>/approve/',
        views.approve_assignment,
        name='approve_assignment',
    ),
    path('bounties/', views.bounties, name='bounties'),
    path('bounties/<int:pk>/claim/', views.claim_bounty, name='claim_bounty'),
    path('rewards/', views.rewards, name='rewards'),
    path('rewards/<int:pk>/redeem/', views.redeem_reward, name='redeem_reward'),
    path('balances/', views.balances, name='balances'),
    path('children/<int:pk>/ledger/', views.child_ledger, name='child_ledger'),
]
