from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('<slug:slug>/add/', views.comment_create_view, name='create'),
    path('<int:pk>/delete/', views.comment_delete_view, name='delete'),
    path('<int:pk>/like/', views.comment_like_view, name='like'),
]