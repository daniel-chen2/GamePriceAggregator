from django.shortcuts import render
from games.models import Game, Platform, Cheapest_Link
from .models import Sale, Coupon,Free_Game, Carousel_Advertisement
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

"""
Render Index Page Section
"""
# @cache_page(60 * 15)
def render_index_page(request):
    context = {
        "recent_games": __get_recent_games(8),
        "sales": cache.get('all_sales_in_database', Sale.objects.all())[:3],
        "carousel_items": Carousel_Advertisement.objects.all(),
    }
    return render(request, "pages/index.html", context)

# Helper Method for Rendering Games
# Returns the Latest games in the database
def __get_recent_games(number_of_recent_games):
    recent_games = Game.objects.all().filter(publish_date__lt = timezone.now()).order_by("-publish_date")[:number_of_recent_games]
    return recent_games

"""
Render About Page Section
"""
@cache_page(60 * 15)
def render_about_page(request):
    return render(request, "pages/about.html")

"""
Render Coupon Page Section
"""
@cache_page(60 * 15)
def render_coupons_page(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons
    }
    return render(request, "pages/coupons.html", context)

"""
Render Free Games Section
"""
@cache_page(60 * 15)
def render_free_games(request):
    free_games = Free_Game.objects.all()
    context = {
        'free_games': free_games
    }
    return render(request, "pages/free_games.html", context)

"""
Render Sales Page Section
"""
@cache_page(60 * 15)
def render_sales_page(request):
    sales = Sale.objects.all()
    context = {
        'sales': sales
    }
    return render(request, "pages/sales.html", context)

