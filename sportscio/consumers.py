import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Store active chat consumers for broadcasting
chat_consumers = {}
announcement_consumers = []

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Store this consumer for broadcasting
        if self.room_name not in chat_consumers:
            chat_consumers[self.room_name] = []
        chat_consumers[self.room_name].append(self)
        
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_name in chat_consumers:
            if self in chat_consumers[self.room_name]:
                chat_consumers[self.room_name].remove(self)
            if not chat_consumers[self.room_name]:
                del chat_consumers[self.room_name]

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')

        if message_content and self.user.is_authenticated:
            # Save message to database
            db_message = await self.save_message(message_content, self.room_name, self.user)

            # Broadcast to all consumers in this room
            if self.room_name in chat_consumers:
                for consumer in chat_consumers[self.room_name]:
                    await consumer.send(text_data=json.dumps({
                        'type': 'chat_message',
                        'message': message_content,
                        'username': self.user.username,
                        'timestamp': db_message.timestamp.isoformat(),
                        'user_id': self.user.id,
                    }))

    @database_sync_to_async
    def save_message(self, content, room, user):
        from .models import Message
        return Message.objects.create(sender=user, content=content, room=room)


class AnnouncementConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        announcement_consumers.append(self)
        await self.accept()

    async def disconnect(self, close_code):
        if self in announcement_consumers:
            announcement_consumers.remove(self)

    async def announcement_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'announcement',
            'id': event['id'],
            'title': event['title'],
            'content': event['content'],
            'author': event['author'],
            'created_at': event['created_at'],
        }))
