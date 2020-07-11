from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import apps.ws.routing

# noinspection SpellCheckingInspection
application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(apps.ws.routing.websocket_urlpatterns))
    ),
})
