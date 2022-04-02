from django.core.management.base import BaseCommand 
from django.core.cache import cache
from games.models import Game, Platform, Cheapest_Link, Store, Link
from pages.models import Sale

class Command(BaseCommand):
    help = 'Refreshes my cache'

    def handle(self, *args, **options):
        cache.set('all_games_in_database', Game.objects.all().prefetch_related('platforms'), timeout=2592000)
        cache.set('all_platforms_in_database', Platform.objects.all(), timeout=2592000)
        cache.set('all_cheapest_links_in_database', Cheapest_Link.objects.all().prefetch_related('game').prefetch_related('platform'), timeout=2592000)
        cache.set('all_sales_in_database', Sale.objects.all(), timeout=2592000)
        cache.set('all_links_in_database', Link.objects.all().select_related('game').select_related('store').prefetch_related('platform'), timeout=2592000)
    print("Update Successful")