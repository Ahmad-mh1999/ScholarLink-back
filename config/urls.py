from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="ScholarLink API",
        default_version='v1',
        description="API for ScholarLink - Connecting Scholars Worldwide",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/v1/', include('api.v1.urls')),

    # Swagger
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    # Web
    path('accounts/', include('apps.accounts.urls')),
    path('comments/', include('apps.comments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('categories/', include('apps.categories.urls')),
    path('admin-dashboard/', include('apps.admin_dashboard.urls')),
    path('points/', include('apps.points.urls')),



    # Articles آخر شيء لأنه يحتوي على slug عام
    path('', include('apps.articles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)