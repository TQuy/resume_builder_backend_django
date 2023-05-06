from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.resumes),
    path('<str:resume_name>', views.resume)
]
