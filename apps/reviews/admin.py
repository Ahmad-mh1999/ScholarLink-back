from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'article', 'status', 'rating', 'created_at']
    list_filter = ['status']
    search_fields = ['reviewer__email', 'article__title']