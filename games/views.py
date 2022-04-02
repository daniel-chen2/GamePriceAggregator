from django.shortcuts import render, get_object_or_404
from .models import Game, Link, Platform, Cheapest_Link
from django.db.models import Q, Count, Sum, Min
import html
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity, TrigramDistance

"""
Render Individual Game Page Section
- Gets Platform Object
- Gets Link Object
- Gets Cheapest Link Object
"""
# @cache_page(60 * 15)
def render_individual_game(request, game_id, platform_code, hyphenated_game_title):
    game = get_object_or_404(Game, pk=game_id, title=hyphenated_game_title.replace("-"," "))
    platform = cache.get('all_platforms_in_database', Platform.objects.all()).get(code=platform_code) 
    links = Link.objects.filter(game=game, platform=platform).select_related('store','platform')

    context = {
        'game': game,
        'digi_links': [l for l in links if l.distribution =='Dg'],
        'cheapest_link': links.filter().order_by('price')[0] if links else None,
        'physical_links': [l for l in links if l.distribution =='Ph'],
        'platform': platform
    }
    return render(request, "games/game.html", context)

"""
Render Games Gateway
"""
def render_games_gateway(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    games_by_platform = game.cheapest_links.all().select_related("platform")
    print(games_by_platform)
    context = {
        'games_by_platform':games_by_platform,
        'game': game
    }
    return render(request, "games/games_gateway.html", context)

"""
Render Search for Games Page
"""
# @cache_page(60 * 15)
def render_search_page(request):
    searched_games = Game.objects.search_games_by_query(request.GET.get('search',''), request.GET.get('platform'))
    searched_games = searched_games.filter_links_by_platform(platform_id=request.GET.get('platform'))
    print(searched_games[0].cheapest_game_links_by_platform)
    context = {
        'games' : Paginator(searched_games, 12).page(request.GET.get('page', 1)),
        'results_found': searched_games.count(),
        'current_query': request.GET.get('search','').strip(),
        'platform_id': request.GET.get('platform')
    }
    return render(request, 'games/search.html', context)

# Searches Game By Query
# Outputs gamesqueryset Object
def __search_games_by_query(query, query_platform_id=None):
    games = Game.objects.all().order_by("-publish_date")
    if query != '' or query == None or query == "All":
        games = Game.objects.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.3).order_by('-similarity')
    if query_platform_id:
        try:
            games = games.filter(platforms__id=query_platform_id)
        except Exception as e:
            print(e)
    return games
