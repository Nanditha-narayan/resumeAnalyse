from django.urls import path
from .views import index, upload_and_analyze, page2, get_matched_jobs

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload_and_analyze, name='upload_and_analyze'),
    path("page2/", page2, name="page2"),
    path("get_results/", get_matched_jobs, name="get_matched_jobs"),
    path('get_matched_jobs/', get_matched_jobs, name='get_matched_jobs'),  
]   
