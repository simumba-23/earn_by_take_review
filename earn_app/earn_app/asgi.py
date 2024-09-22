import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import myearn.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'earn_app.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myearn.routing.websocket_urlpatterns
        )
    ),
})
