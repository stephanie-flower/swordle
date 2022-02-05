from django.apps import AppConfig
from django.core.cache import cache

class GameServerConfig(AppConfig):
    name = 'game_server'
    verbose_name = "Swordle Game Server"
    version = "0.0.1"

    def ready(self):
        # Clear the Room cache
        print("Swordle Game Server (%s) ready!" % (self.version))
        cache.delete('current_rooms')
