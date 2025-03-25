"""
ASGI config for chat_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# accesses enviroment variables
# chat_project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from messaging.routing import websocket_urlpatterns  # Import your routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Adding the WebSocket URL routing to the middleware
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Correct routing for WebSocket
        )
    ),
})
