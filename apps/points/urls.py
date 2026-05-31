from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'points'

router = DefaultRouter()
router.register(r'guidelines', views.JournalGuidelineViewSet, basename='journal-guideline')
router.register(r'user-points', views.UserPointsViewSet, basename='user-points')

urlpatterns = [
    path('api/', include(router.urls)),
]
