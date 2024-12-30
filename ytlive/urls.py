from django.urls import path
from .views import youtube_auth
from . import views

urlpatterns = [
    path('oauth/', youtube_auth, name='youtube_auth'),
    path('oauth2callback/', youtube_auth, name='oauth2callback'),  # Add this line
    path('create/', views.create_livestream, name='create_livestream'),
    path('course/<int:course_id>/', views.get_livestreams_for_course, name='get_livestreams_for_course'),
    path('stream/<int:livestream_id>/details/', views.get_livestream_details, name='get_livestream_details'),
    path('stream/<int:livestream_id>/start/', views.start_livestream, name='start_livestream'),  # New: Start Livestream
    path('stream/<int:livestream_id>/end/', views.end_livestream, name='end_livestream'),  # New: End Livestream
]
