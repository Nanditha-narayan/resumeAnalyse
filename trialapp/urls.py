from django.urls import path
from trialapp.views import index

urlpatterns = [
    path('', index, name='index'),  # Root URL will show index1.html
]