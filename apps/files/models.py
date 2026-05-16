from django.db import models
from apps.accounts.models import User
from apps.articles.models import Article


class File(models.Model):

    class FileType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'
        PDF = 'pdf', 'PDF'
        OTHER = 'other', 'Other'

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='files/')
    file_type = models.CharField(max_length=10, choices=FileType.choices, default=FileType.OTHER)
    size = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.article}"