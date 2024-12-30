from django.urls import path
from . import views

urlpatterns = [
    # Posts
    path('posts/<int:course_id>/<int:week_number>/', views.get_posts, name='get_posts'),
    path('posts/<int:post_id>/detail/', views.get_post_detail, name='get_post_detail'),
    path('posts/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/flag/', views.flag_post, name='flag_post'),
    path('posts/<int:post_id>/reset_flags/', views.reset_flag_count, name='reset_flag_count'),

    # Comments
    path('comments/', views.create_comment, name='create_comment'),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/flag/', views.flag_comment, name='flag_comment'),

    # Moderation
    path('moderation/<int:course_id>/', views.get_flagged_content, name='get_flagged_content'),
    path('moderation/posts/<int:post_id>/comments/', views.get_comments_for_post, name='get_comments_for_post'),
    path('moderation/reset_flags/<str:content_type>/<int:object_id>/', views.reset_flag_count, name='reset_flag_count'),
    path('moderation/toggle_hidden/<str:content_type>/<int:object_id>/', views.toggle_hidden, name='toggle_hidden'),
]
