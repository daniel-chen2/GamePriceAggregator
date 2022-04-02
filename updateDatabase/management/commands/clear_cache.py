from django.core.management.base import BaseCommand 
from django.core.cache import cache
from games.models import Game, Platform, Cheapest_Link, Store, Link
from pages.models import Sale

class Command(BaseCommand):
    help = 'Clears the cache'

    def handle(self, *args, **options):
        cache.clear()
    print("Clear Cache Successful")