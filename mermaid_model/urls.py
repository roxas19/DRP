from django.urls import path
from .views import upload_pdf_page

urlpatterns = [
    path('upload-pdf-page/', upload_pdf_page, name='upload_pdf_page'),
]
