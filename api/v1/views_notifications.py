from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.notify.models import Notification
from apps.notify.serializers import NotificationSerializer
from common.pagination import SmallPagination
from django.contrib.auth import get_user_model
from apps.notify.utils import send_notification

User = get_user_model()


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SmallPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = Notification.objects.filter(pk=pk, recipient=request.user).first()
        if not notification:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read.'})


class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})


class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})
    

class SendNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.role == 'admin':
            return Response({'error': 'Only admins can send notifications.'}, status=status.HTTP_403_FORBIDDEN)
        
        title = request.data.get('title')
        message = request.data.get('message')
        send_to_all = request.data.get('send_to_all', False)
        user_id = request.data.get('user_id')
        
        if not title or not message:
            return Response({'error': 'Title and message are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if send_to_all:
            recipients = User.objects.all()
        elif user_id:
            recipients = User.objects.filter(id=user_id)
        else:
            return Response({'error': 'Either send_to_all or user_id must be provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        for recipient in recipients:
            send_notification(
                recipient=recipient,
                sender=request.user,
                notification_type='system',
                title=title,
                message=message
            )
        
        return Response({'message': f'Notification sent to {recipients.count()} recipient(s).'})
