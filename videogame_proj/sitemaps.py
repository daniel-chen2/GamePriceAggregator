from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from games.models import Game, Cheapest_Link

class Static_Sitemap(Sitemap):
    priority = 1.0
    changefreq = 'yearly'
    protocol = "https"

    def items(self):
        return ['index', 'about']

    def location(self, item):
        return reverse(item)

class Game_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Cheapest_Link.objects.all()

    def location(self, obj):
        return obj.get_game_url()

    def lastmod(self, obj): 
        return obj.date_updated