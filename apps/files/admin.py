from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'article', 'uploaded_by', 'file_type', 'created_at']
    list_filter = ['file_type']
    search_fields = ['name', 'article__title']