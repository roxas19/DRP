from django.contrib import admin
from .models import Course, WeeklyModule, Enrollment, Task, TaskCompletion, Resource


class WeeklyModuleInline(admin.TabularInline):
    model = WeeklyModule
    extra = 0
    fields = ('title', 'order', 'status', 'start_date')
    readonly_fields = ('status',)


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ('title', 'description', 'file', 'link', 'created_at')
    readonly_fields = ('created_at',)


class TaskCompletionInline(admin.TabularInline):
    model = TaskCompletion
    extra = 1
    fields = ('task', 'user', 'completed', 'completed_at')
    readonly_fields = ('completed_at',)
    autocomplete_fields = ('user', 'task')

    def get_queryset(self, request):
        """
        Filter TaskCompletion to only show tasks related to the current WeeklyModule.
        """
        queryset = super().get_queryset(request)
        if hasattr(self, 'parent_model') and self.parent_model == WeeklyModule:
            return queryset.filter(task__module=self.instance)
        return queryset


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'description', 'file', 'link', 'created_at')
    list_filter = ('module',)
    search_fields = ('title', 'description', 'module__title')
    ordering = ('-created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'created_at')
    list_display_links = ('module',)  # Make 'module' clickable
    list_editable = ('title',)  # Allow editing task title
    list_filter = ('module', 'created_at')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'created_at')
    inlines = [TaskCompletionInline]


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'completed', 'completed_at')
    list_filter = ('completed', 'task__module', 'user')
    search_fields = ('task__title', 'user__email')
    ordering = ('task', 'user')


@admin.register(WeeklyModule)
class WeeklyModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'status', 'start_date')
    list_filter = ('course', 'status')
    search_fields = ('title', 'description')
    ordering = ('course', 'order')
    inlines = [ResourceInline]  # Inline for resources


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_instructors', 'category', 'created_at')  # Use a custom method for instructors
    list_filter = [] # Remove 'instructor' filter and use filters relevant to your model
    search_fields = ('title', 'description')

    def get_instructors(self, obj):
        """
        Display the instructors as a comma-separated list in the admin.
        """
        return ", ".join([instructor.user.name for instructor in obj.instructors.all()])
    
    get_instructors.short_description = "Instructors"  # Admin column name


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_percentage', 'enrolled_on')
    list_filter = ('course', 'student', 'progress')
    search_fields = ('student__user__name', 'course__title')
    ordering = ['enrolled_on']  # Fixed: Use a list instead of a string

    def progress_percentage(self, obj):
        return f"{obj.progress}%"
    progress_percentage.short_description = "Progress (%)"
