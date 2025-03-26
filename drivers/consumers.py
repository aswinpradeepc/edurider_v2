import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.gis.geos import Point
from datetime import datetime
from .models import Driver

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f'driver_{self.driver_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        try:
            data = json.loads(text_data)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))

            # Update driver location in database
            await self.update_driver_location(latitude, longitude)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'latitude': latitude,
                    'longitude': longitude,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            await self.send(text_data=json.dumps({
                'error': f'Invalid data format: {str(e)}'
            }))

    async def location_update(self, event):
        """
        Called when a message is received from the group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def update_driver_location(self, latitude, longitude):
        """
        Update driver location in the database.
        """
        try:
            driver = Driver.objects.get(driver_id=self.driver_id)
            driver.current_location = Point(longitude, latitude)  # Note: Point takes (x, y) which is (longitude, latitude)
            driver.location_updated_at = datetime.now()
            driver.save()
            return True
        except Driver.DoesNotExist:
            return False
