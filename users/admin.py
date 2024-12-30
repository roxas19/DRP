from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, InstructorProfile, StudentProfile, Role


# Define the UserAdmin class to customize how the User model is displayed
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('roles',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'profile_photo')}),
        (_('Roles'), {'fields': ('roles',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )


# Customize the InstructorProfileAdmin display
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'teaching_experience', 'rating', 'certified')
    search_fields = ('user__name', 'specialization')
    list_filter = ('specialization', 'certified', 'teaching_experience', 'rating')
    ordering = ('-teaching_experience',)


# Customize the StudentProfileAdmin display
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'completed_courses_count', 'preferred_language')
    search_fields = ('user__name', 'user__email')
    list_filter = ('preferred_language', 'completed_courses_count')
    ordering = ('-completed_courses_count',)


# Role admin for managing roles
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


# Register the custom User model with the custom UserAdmin class
admin.site.register(User, UserAdmin)
admin.site.register(InstructorProfile, InstructorProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Role, RoleAdmin)
