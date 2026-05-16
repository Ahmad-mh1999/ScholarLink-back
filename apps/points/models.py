from django.db import models
from apps.accounts.models import User


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.total} pts"


class PointTransaction(models.Model):

    class Reason(models.TextChoices):
        PUBLISH_ARTICLE = 'publish_article', 'نشر مقال (+10)'
        RECEIVE_LIKE = 'receive_like', 'استقبال إعجاب (+2)'
        SUBMIT_REVIEW = 'submit_review', 'تقديم مراجعة (+5)'
        RECEIVE_COMMENT = 'receive_comment', 'استقبال تعليق (+1)'
        RECEIVE_BOOKMARK = 'receive_bookmark', 'حفظ في المفضلة (+3)'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    reason = models.CharField(max_length=50, choices=Reason.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {'+' if self.points > 0 else ''}{self.points} — {self.reason}"