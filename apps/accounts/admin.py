from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Expertise


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'academic_status', 'institution', 'is_active']
    list_filter = ['role', 'academic_status', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'institution']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {
            'fields': ('institutional_email', 'institution', 'field_of_study', 'academic_status', 'orcid_id', 'title', 'location', 'bio', 'avatar', 'website')
        }),
        ('Role & Permissions', {
            'fields': ('role',)
        }),
    )


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'description']
    search_fields = ['user__email', 'title']