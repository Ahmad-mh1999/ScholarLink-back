from django.db import models
from apps.accounts.models import User


class JournalGuideline(models.Model):
    """
    Model for storing journal formatting guidelines and requirements.
    """
    title = models.CharField(max_length=255)
    font_size = models.CharField(max_length=50, help_text="e.g., '12pt Times New Roman'")
    margins = models.CharField(max_length=100, help_text="e.g., '1 inch on all sides'")
    line_spacing = models.CharField(max_length=50, help_text="e.g., 'Double-spaced'")
    image_dimensions = models.CharField(max_length=100, help_text="e.g., 'Min 300 DPI, max 5 inches wide'")
    citation_style = models.CharField(max_length=50, help_text="e.g., 'APA 7th Edition'")
    max_word_count = models.PositiveIntegerField(null=True, blank=True)
    min_word_count = models.PositiveIntegerField(null=True, blank=True)
    additional_requirements = models.TextField(blank=True, help_text="Any additional formatting requirements")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Journal Guideline'
        verbose_name_plural = 'Journal Guidelines'

    def __str__(self):
        return self.title


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total = models.PositiveIntegerField(default=0)
    eligible_for_cost_coverage = models.BooleanField(default=False, help_text="Flag for users eligible for publication cost support")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.total} pts"

    def check_cost_coverage_eligibility(self):
        """
        Check if user is eligible for publication cost support based on total points.
        Threshold: 1000 points
        """
        self.eligible_for_cost_coverage = self.total >= 1000
        self.save(update_fields=['eligible_for_cost_coverage'])
        return self.eligible_for_cost_coverage


class PointTransaction(models.Model):

    class Reason(models.TextChoices):
        PUBLISH_ARTICLE = 'publish_article', 'نشر مقال (+10)'
        RECEIVE_LIKE = 'receive_like', 'استقبال إعجاب (+2)'
        RECEIVE_COMMENT = 'receive_comment', 'استقبال تعليق (+1)'
        RECEIVE_BOOKMARK = 'receive_bookmark', 'حفظ في المفضلة (+3)'
        EXPEDITE_REVIEW = 'expedite_review', 'استعجال تحكيم (-50)'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    reason = models.CharField(max_length=50, choices=Reason.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {'+' if self.points > 0 else ''}{self.points} — {self.reason}"