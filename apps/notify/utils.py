from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer


def send_notification(recipient, sender, notification_type, title, message, article_slug=None):
    if recipient == sender:
        return

    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        article_slug=article_slug
    )

    channel_layer = get_channel_layer()
    group_name = f'notifications_{recipient.id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification': NotificationSerializer(notification).data
        }
    )

    return notification


def notify_like(article, liker):
    send_notification(
        recipient=article.author,
        sender=liker,
        notification_type='like',
        title='New Like',
        message=f'{liker.get_full_name()} liked your article "{article.title}"',
        article_slug=article.slug
    )


def notify_comment(article, commenter, comment_content):
    send_notification(
        recipient=article.author,
        sender=commenter,
        notification_type='comment',
        title='New Comment',
        message=f'{commenter.get_full_name()} commented on "{article.title}": {comment_content[:50]}',
        article_slug=article.slug
    )


def notify_follow(followed_user, follower):
    send_notification(
        recipient=followed_user,
        sender=follower,
        notification_type='follow',
        title='New Follower',
        message=f'{follower.get_full_name()} started following you',
    )


def notify_review(article, reviewer):
    send_notification(
        recipient=article.author,
        sender=reviewer,
        notification_type='review',
        title='New Review',
        message=f'{reviewer.get_full_name()} reviewed your article "{article.title}"',
        article_slug=article.slug
    )