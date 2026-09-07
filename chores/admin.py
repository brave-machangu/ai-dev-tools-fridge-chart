from django.contrib import admin

from .models import Chore, Family, Profile, Reward


class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 1
    fields = ['display_name', 'role', 'user']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'role', 'family', 'user']
    list_filter = ['role', 'family']
    search_fields = ['display_name']


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'kind', 'points', 'family']
    list_filter = ['kind', 'family']
    search_fields = ['title']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'family']
    list_filter = ['family']
    search_fields = ['name']
