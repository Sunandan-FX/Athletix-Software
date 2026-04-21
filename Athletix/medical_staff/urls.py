from django.urls import path

from . import views

app_name = 'medical_staff'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('feedback/add/', views.add_feedback, name='add_feedback'),
    path('feedback/add/<int:record_id>/', views.add_feedback_for_record, name='add_feedback_for_record'),
]

