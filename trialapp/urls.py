from django.urls import path
from .views import index, upload_and_analyze

urlpatterns = [
    path('', index, name='index'),  # Serve the HTML page
    path('upload/', upload_and_analyze, name='upload_and_analyze'),  # Handle file uploads
]
