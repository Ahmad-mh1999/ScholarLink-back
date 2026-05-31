import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from .serializers import NotificationSerializer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            print(f'WebSocket connection rejected: No valid user/token')
            await self.close(code=4001, reason='Authentication required')
            return
        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f'WebSocket connection established for user {self.user.id}')
        await self.send_unread_count()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f'WebSocket disconnected for user {self.user.id} with code {close_code}')

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'mark_read':
            notification_id = data.get('notification_id')
            await self.mark_notification_read(notification_id)

    async def notification_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': event['notification']
            }))
        except Exception as e:
            print(f'Error sending notification: {e}')

    async def send_unread_count(self):
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': count
        }))

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        Notification.objects.filter(id=notification_id, recipient=self.user).update(is_read=True)
