from django.urls import path
from . import views

app_name = 'courses'  # Namespace for the app

urlpatterns = [
    # Course endpoints
    path('courses/', views.get_courses, name='get_courses'),
    path('courses/category/<str:name>/', views.get_courses_by_category, name='get_courses_by_category'),
    path('courses/<int:course_id>/', views.get_course_detail, name='get_course_detail'),

    # WeeklyModule endpoints
    path('courses/<int:course_id>/modules/', views.get_weekly_modules, name='get_weekly_modules'),
    path('courses/<int:course_id>/modules/<int:week_number>/', views.get_weekly_module_details, name='get_weekly_module_details'),

    # Task endpoints
    path('courses/<int:course_id>/modules/<int:week_number>/tasks/', views.get_tasks, name='get_tasks'),
    path('courses/<int:course_id>/modules/<int:week_number>/tasks/create/', views.create_task, name='create_task'),
    path('courses/<int:course_id>/modules/<int:week_number>/tasks/<int:task_id>/', views.update_task, name='update_task'),
    path('courses/<int:course_id>/modules/<int:week_number>/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('courses/<int:course_id>/modules/<int:week_number>/tasks/<int:task_id>/status/', views.mark_task_completed, name='update_task_status'),

    # Resource endpoints
    path('courses/<int:course_id>/modules/<int:week_number>/resources/', views.get_resources, name='get_resources'),
    path('courses/<int:course_id>/modules/<int:week_number>/resources/create/', views.add_resource, name='add_resource'),
    path('courses/<int:course_id>/modules/<int:week_number>/resources/<int:resource_id>/', views.update_resource, name='update_resource'),
    path('courses/<int:course_id>/modules/<int:week_number>/resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),

    # Enrollment endpoints
    path('enrollments/', views.get_enrollments, name='get_enrollments'),
    path('enrollments/create/', views.create_enrollment, name='create_enrollment'),

    # Instructor-specific endpoints
    path('instructor/courses/', views.get_instructor_courses, name='get_instructor_courses'),
]
