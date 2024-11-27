from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.get_categories, name='get_categories'),  # Categories endpoint
    path('category/<str:name>/', views.get_category_by_name, name='get_category_by_name'),  # Category by name
]
