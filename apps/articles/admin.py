from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'access_level', 'is_featured', 'created_at']
    list_filter = ['status', 'access_level', 'is_featured', 'category']
    search_fields = ['title', 'author__email', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']