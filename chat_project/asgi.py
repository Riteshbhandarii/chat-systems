import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator  # Important for production

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

# Initialize Django ASGI application early to ensure AppRegistry is populated
django_application = get_asgi_application()

# Import websocket routes after Django setup
from messaging.routing import websocket_urlpatterns  # Your WebSocket routes

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AllowedHostsOriginValidator(  # Security layer
        AuthMiddlewareStack(  # Authentication
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})