from django.urls import path

from . import views

app_name = 'chores'

urlpatterns = [
    path('', views.home, name='home'),
    path('week/', views.week, name='week'),
    path(
        'assignments/<int:pk>/approve/',
        views.approve_assignment,
        name='approve_assignment',
    ),
    path('balances/', views.balances, name='balances'),
    path('children/<int:pk>/ledger/', views.child_ledger, name='child_ledger'),
]
