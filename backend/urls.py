from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('resumes/', views.list_resume),
    path('resume/<int:resume_id>/', views.load_resume),
    path('save_resume/', views.save_resume),
    path('resume/<int:resume_id>/delete/', views.delete_resume),
    path('resume/register/', views.register_view),
]
