from django.urls import path
from . import views

urlpatterns = [
    # Course endpoints
    path('courses/', views.get_courses, name='get_courses'),
    path('courses/category/<str:name>/', views.get_courses_by_category, name='get_courses_by_category'),
    path('courses/<int:course_id>/', views.get_course_detail, name='get_course_detail'),

    # WeeklyModule endpoints
    path('courses/<int:course_id>/modules/', views.get_weekly_modules, name='get_weekly_modules'),

    # Enrollment endpoints
    path('enrollments/', views.get_enrollments, name='get_enrollments'),
    path('enrollments/create/', views.create_enrollment, name='create_enrollment'),
]
