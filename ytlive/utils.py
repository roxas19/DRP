from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_websocket(group_name, message):
    """
    Broadcast a message to a WebSocket group.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "chat.message",  # You can customize the event type
            "message": message,
        }
    )
