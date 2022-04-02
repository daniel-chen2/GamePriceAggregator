from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import django.utils
from jsonfield import JSONField
from django.utils.functional import cached_property
from django.core.cache import cache
from django.utils.functional import cached_property
from django.contrib.postgres.search import TrigramSimilarity, TrigramDistance
from django.contrib import admin

"""
Summary: These Models Hold Classes Directly Related To The Game
Game, Platform, Store, Link, Cheapest Link
"""
"""
Holds The Platforms Of The Games e.g. Playstation, Xbox etc.
"""
class Platform(models.Model):
    title = models.CharField(max_length=200)
    img_url = models.CharField(max_length=200, blank=True, default='https://sm.pcmag.com/t/pcmag_au/review/x/xbox-for-p/xbox-for-pc_trav.640.jpg')
    icon = models.CharField(max_length=200, default='<i class="fab fa-playstation"></i>')
    code = models.CharField(max_length=5, default='ps4')

    def __str__(self):
        return self.title

"""
Game Object
"""
class GameManager(models.Manager):
    def get_queryset(self):
        return GameQuerySet(self.model)
    
    def search_games_by_query(self, query, query_platform_id=None, similarity_level = 0.3):
        games = self.order_by("-publish_date")
        if query != '' or query == None or query == "All":
            games = self.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=similarity_level).order_by('-similarity')
        if query_platform_id:
            try:
                games = self.filter(platforms__id=query_platform_id)
            except Exception as e:
                print(e)
        return games

class GameQuerySet(models.QuerySet):
    def filter_links_by_platform(self, platform_id):
        for game in self:
            game.cheapest_game_links_by_platform = Cheapest_Link.objects.filter(game=game, platform_id = platform_id).select_related()
        return self

        
class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField()
    publisher = models.CharField(blank=True,max_length=200)
    platforms = models.ManyToManyField(Platform, default=None)
    photo_url = models.TextField(default=None,null=True)
    rawg_id = models.IntegerField(default=None, blank=True, null=True)
    tags = JSONField(blank=True, null=True)
    objects = GameManager()
    date_modified = models.DateTimeField(blank=True, auto_now=True)

    # @cached_property
    def cheapest_game_links(self, platform_id=None):
        all_cheapest_links = self.cheapest_links.prefetch_related('game').select_related('platform')
        current_cheapest_links = all_cheapest_links
        if platform_id != None:
            try: 
                current_cheapest_links = self.cheapest_links.prefetch_related('game').select_related('platform').filter(platform__id = platform_id)
            except Exception as e:
                print(e) 
        else:
            return all_cheapest_links
        return current_cheapest_links

    def get_game_urls(self):
        """
        Returns a list of bargain gamer urls for each platform
        """
        urls = []
        for platform in self.platforms.all():
            urls.append("/games/" + platform.code + "/" + str(self.game.id) + "/" + self.title)
        return urls

    def get_hyphenated_title(self):
        return "-".join(self.title.split(" "))

    def get_gateway_url(self):
        return "/games/" + platform.code + "/" + str(self.game.id)

    def __str__(self):
        return self.title
        
"""
Holds The Store Within The Database
"""
class Store(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=3)
    trustpilot_url = models.TextField(default=None,blank=True, null=True)
    photo_url = models.TextField(default=None,blank=True, null=True)

    def __str__(self):
        return self.title

"""
Holds A Given Link For A Game
"""
class LinkAdmin(admin.ModelAdmin):
    search_fields = ('game__title', 'store__title', 'platform__title')

class Link(models.Model):
    #on delete
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='links')
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)
    platform = models.ForeignKey(Platform, on_delete=models.DO_NOTHING)
    initial_price = models.DecimalField(default=0,decimal_places=2, max_digits=8)
    price = models.DecimalField(default=0,decimal_places=2, max_digits=8)
    price_found = models.BooleanField(default=True)
    link = models.TextField(default='')
    created_at = models.DateTimeField(blank=True, default=django.utils.timezone.now)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    # Enum
    Distribution = (
        ('Dg', 'Digital'),
        ('Ph', 'Physical'),
    )

    distribution = models.CharField(
        max_length=2,
        choices=Distribution,
        default='Dg',
    )

    def discount_percent(self):
        if self.initial_price > self.price:
            return round(100 - (self.price/self.initial_price)*100)
        else:
            return 0

    def __str__(self):
        return self.game.title + "-" + self.platform.title + "-" +  self.store.title

"""
Holds The Cheapest Link For A Game
"""
class Cheapest_Link(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='cheapest_links')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    initial_price = models.DecimalField(default=0,decimal_places=2, max_digits=8)
    price = models.DecimalField(default=0,decimal_places=2, max_digits=8)
    date_updated = models.DateTimeField(blank=True, default=django.utils.timezone.now)
    
    def get_game_url(self):
        """
        Returns game url on bargain-gamer site
        """
        url = "/games/" + self.platform.code + "/" + str(self.game.id) + "/" + self.game.get_hyphenated_title()
        return url

    def __str__(self):
        return "CHEAPEST LINK: " + self.game.title + " " + self.platform.title

