# game_server/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<room_id>\w+)/$', consumers.GameSessionConsumer.as_asgi()),
]
