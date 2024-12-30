from django.urls import path
from . import views

urlpatterns = [
    # Instructor-related endpoints
    path('instructors/', views.get_instructors, name='get_instructors'),
    path('instructor/<int:id>/', views.get_instructor_by_id, name='get_instructor_by_id'),

    # Student-related endpoints
    path('students/', views.get_students, name='get_students'),
    path('student/<int:id>/', views.get_student_by_id, name='get_student_by_id'),

    # User management endpoints
    path('register/', views.register_user, name='register_user'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Use custom view
    path('logout/', views.logout_view, name='logout_view'),
    path('user/', views.get_user_info, name='get_user_info'),

    # New endpoint: Enroll as Tutor
    path('enroll-as-tutor/', views.enroll_as_tutor, name='enroll_as_tutor'),
]
