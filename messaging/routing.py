from django import re_path
from . import consumers

# defining URL pattern
websocket_url = [
    # connects with chat consumer class, to handle websocket connection
    re_path(r'ws/chat/(?P<chat_room>\w+)/$', consumers.ChatConsumer.as_asgi()), # Room-based chat
]