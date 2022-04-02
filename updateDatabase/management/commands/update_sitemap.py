from django.core.management.base import BaseCommand 
from django.core.cache import cache
from games.models import Game, Platform, Cheapest_Link, Store, Link
from pages.models import Sale
from django.test import Client
# from videogame_proj.views import sitemap
from django.contrib.sitemaps.views import sitemap
from videogame_proj.sitemaps import Static_Sitemap, Game_Sitemap

sitemaps = {
    'static': Static_Sitemap(),
    'games': Game_Sitemap
}

class Command(BaseCommand):
    help = 'updates_the_sitemap_in_templates'

    def handle(self, *args, **options):
        client = Client()
        response = client.get('/generate/sitemap.xml')
        response.content_type = "text/plain; charset=utf-8"
        f = open("templates/xml/sitemap.xml", "w", encoding="utf-8")
        xml_file = str(response.content, "utf-8")
        f.write(xml_file)

        print(response.status_code)
        print("Update Sitemap.xml Successful")