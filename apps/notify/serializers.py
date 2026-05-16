from rest_framework import serializers
from .models import Notification
from apps.accounts.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notification_type', 'title', 'message', 'is_read', 'article_slug', 'created_at']