from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<slug:slug>/add/', views.review_create_view, name='create'),
    path('<int:pk>/update/', views.review_update_view, name='update'),
]