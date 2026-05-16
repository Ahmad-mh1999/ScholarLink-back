from django.db import models
from apps.accounts.models import User
from apps.articles.models import Article


class ReviewRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='review_requests'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_requests'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_reviews'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['article', 'reviewer']
        ordering = ['-created_at']
        verbose_name = 'Review Request'
        verbose_name_plural = 'Review Requests'

    def __str__(self):
        return f"{self.article.title} → {self.reviewer.get_full_name()}"


class Review(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        REVISION = 'revision', 'Needs Revision'

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    review_request = models.OneToOneField(
        ReviewRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    feedback = models.TextField(blank=True)
    rating = models.PositiveIntegerField(default=0)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['article', 'reviewer']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.reviewer.get_full_name()} reviewed {self.article.title}"