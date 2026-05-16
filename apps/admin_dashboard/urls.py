from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('send-notification/', views.admin_send_notification_view, name='send_notification'),
]

