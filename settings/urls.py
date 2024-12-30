from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # App-specific routes
    path('api/', include('users.urls')),
    path('api/', include('organisations.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('mermaid_model.urls')), 
    path('api/discussions/', include('discussions.urls')),
    path('api/ytlive/', include('ytlive.urls')), 
    
    # Admin panel
    path('admin/', admin.site.urls),

    # JWT Token Refresh and Verify
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)