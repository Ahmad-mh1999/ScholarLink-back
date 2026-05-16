from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.article_create_view, name='create'),
    path('<slug:slug>/', views.article_detail_view, name='detail'),
    path('<slug:slug>/update/', views.article_update_view, name='update'),
    path('<slug:slug>/delete/', views.article_delete_view, name='delete'),
    path('<slug:slug>/like/', views.article_like_view, name='like'),
    path('explore/', views.explore_view, name='explore'),
]

