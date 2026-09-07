from django.contrib import admin

from .models import Family, Profile


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
