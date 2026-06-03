
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from apps.points.models import UserPoints


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.get_or_create(user=instance)
