"""
ASGI config for sse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sse.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# This must be imported after get_asgi_application
# see https://channels.readthedocs.io/en/stable/topics/troubleshooting.html#improperlyconfigured-exception
from sse.events.consumers import ServerSentEventsConsumer

application = ProtocolTypeRouter(
    {  # Routes request based on protocol (i.e. http, websocket etc.)
        "http": AuthMiddlewareStack(  # Middleware to authenticate a user and add their username to the request
            URLRouter(
                [
                    path("sse/notifications", ServerSentEventsConsumer.as_asgi()),
                    re_path("", django_asgi_app),
                ]
            )  # Routes request based on url
        )
    }
)
