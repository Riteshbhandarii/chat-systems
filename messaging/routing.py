from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),

    re_path(r'ws/group_chat/(?P<group_id>\d+)/$', consumers.GroupChatConsumer.as_asgi()),

    re_path(r'ws/status/$', consumers.StatusConsumer.as_asgi()),
]

