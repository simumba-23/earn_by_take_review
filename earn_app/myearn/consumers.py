import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser  # Ensure you import your CustomUser model

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = None
        self.user = await self.get_user()

        if self.user is None or self.user == AnonymousUser():
            await self.close()
            return

        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_user(self):
        try:
            token = self.scope['query_string'].decode().split('=')[1]
            access_token = AccessToken(token)
            return CustomUser.objects.get(id=access_token['user_id'])
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return AnonymousUser()
