# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User,Instructor, Student

# Define the UserAdmin class to customize how the User model is displayed
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'name', 'is_staff', 'is_active', 'is_superuser')
    # Fields to filter by in the admin list view
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_student', 'is_instructor')
    # Fields to search for in the admin list view
    search_fields = ('email', 'name')
    ordering = ('email',)

    # Fieldsets for editing a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_instructor')}),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )

    # Fields for creating a new user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_student', 'is_instructor'),
        }),
    )

class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'teaching_experience', 'rating', 'certified')
    search_fields = ('user__name', 'specialization')
    list_filter = ('specialization', 'certified', 'teaching_experience')

# Customize the StudentAdmin display
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_level', 'completed_courses_count', 'preferred_language')
    search_fields = ('user__name', 'user__email')
    list_filter = ('preferred_language', 'activity_level')

# Register the custom User model with the custom UserAdmin class
admin.site.register(User, UserAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Student, StudentAdmin)

