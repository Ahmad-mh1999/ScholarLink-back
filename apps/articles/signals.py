from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from apps.points.utils import award_points


@receiver(post_save, sender=Article)
def award_points_on_publish(sender, instance, created, **kwargs):
    """
    Award points to the author when an article is published.
    """
    if instance.status == Article.Status.PUBLISHED:
        # Check if points were already awarded for this article
        from apps.points.models import PointTransaction
        already_awarded = PointTransaction.objects.filter(
            user=instance.author,
            reason=PointTransaction.Reason.PUBLISH_ARTICLE
        ).exists()
        
        if not already_awarded:
            award_points(instance.author, PointTransaction.Reason.PUBLISH_ARTICLE)
