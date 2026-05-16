from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'article', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['author__email', 'content']