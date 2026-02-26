from django.urls import path
from .views import audit_logs_list, audit_stats

urlpatterns = [
    path('logs/', audit_logs_list, name='audit_logs_list'),
    path('stats/', audit_stats, name='audit_stats'),
]