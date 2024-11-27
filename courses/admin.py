from django.contrib import admin
from .models import Course, WeeklyModule, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'created_at')
    list_filter = ('level', 'category', 'instructor')
    search_fields = ('title', 'description')
    ordering = ('created_at',)


@admin.register(WeeklyModule)
class WeeklyModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress', 'enrolled_on')
    list_filter = ('course', 'student')
    search_fields = ('student__username', 'course__title')
    ordering = ('enrolled_on',)
