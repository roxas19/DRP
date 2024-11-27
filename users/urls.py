# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('instructors/', views.get_instructors, name='get_instructors'),  # Fetch all instructors
    path('instructor/<int:id>/', views.get_instructor_by_id, name='get_instructor_by_id'),  # Fetch instructor by ID
    path('students/', views.get_students, name='get_students'),  # Fetch all students
    path('student/<int:id>/', views.get_student_by_id, name='get_student_by_id'),  # Fetch student by ID
    path('register/', views.register_user, name='register_user'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
