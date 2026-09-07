from django.contrib import admin

from .models import Chore, ChoreAssignment, Family, LedgerEntry, Profile, Reward


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


@admin.register(ChoreAssignment)
class ChoreAssignmentAdmin(admin.ModelAdmin):
    list_display = ['chore', 'child', 'week_start', 'status', 'approved_at']
    list_filter = ['status', 'week_start', 'child']
    date_hierarchy = 'week_start'


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['child', 'points', 'reason', 'description', 'created_at']
    list_filter = ['reason', 'child']
    readonly_fields = ['created_at']
