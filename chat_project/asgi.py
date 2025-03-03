"""
ASGI config for chat_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# accesses enviroment variables
import os
# imports ASGI handler for HTTP requests
from django.core.asgi import get_asgi_application
# Imports the routing classes to handle websocket
from channels.core.asgi import ProtocolTypeRouter, URLRouter
# for handelling authetincation in WebSocket
from channels.auth import AuthMiddlewareStack
# imports the websocket URL routing
from chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

# defines WebSocket
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # routes websocket connections using mw and url patters
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns 
        )
    ),
})
