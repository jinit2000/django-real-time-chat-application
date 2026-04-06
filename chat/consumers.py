import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Add user to participants
        await self.add_participant()

        # Notify group user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.username,
                'user_id': self.user.id,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'username': self.user.username,
                    'user_id': self.user.id,
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            body = data.get('body', '').strip()
            if not body:
                return

            message = await self.save_message(body)
            if message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': message.id,
                        'body': message.body,
                        'username': self.user.username,
                        'user_id': self.user.id,
                        'timestamp': message.created_at.strftime('%H:%M'),
                        'full_timestamp': message.created_at.isoformat(),
                    }
                )

        elif msg_type == 'delete':
            message_id = data.get('message_id')
            success = await self.delete_message(message_id)
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': message_id,
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'body': event['body'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'full_timestamp': event['full_timestamp'],
            'is_self': event['user_id'] == self.user.id,
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
        }))

    @database_sync_to_async
    def save_message(self, body):
        try:
            room = Room.objects.get(id=self.room_id)
            message = Message.objects.create(
                room=room,
                user=self.user,
                body=body
            )
            room.participants.add(self.user)
            return message
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id, user=self.user)
            message.is_deleted = True
            message.body = '[deleted]'
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def add_participant(self):
        try:
            room = Room.objects.get(id=self.room_id)
            room.participants.add(self.user)
        except Room.DoesNotExist:
            pass
