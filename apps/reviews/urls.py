from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register(r'journals', views.JournalViewSet, basename='journal')
router.register(r'review-requests', views.ReviewRequestViewSet, basename='review-request')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Template views
    path('<slug:slug>/add/', views.review_create_view, name='create'),
    path('<int:pk>/update/', views.review_update_view, name='update'),
    
    # API endpoints
    path('api/', include(router.urls)),
]