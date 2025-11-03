from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload_image'),
    path('results/<int:pk>/', views.assessment_results, name='assessment_results'),
    path('history/', views.assessment_history, name='assessment_history'),
    path('delete/<int:pk>/', views.delete_assessment, name='delete_assessment'),
]
