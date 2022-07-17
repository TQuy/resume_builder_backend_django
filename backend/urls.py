from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.resumes),
    path('<int:resume_id>', views.resume),
]
