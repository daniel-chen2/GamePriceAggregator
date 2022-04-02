from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:game_id>', views.render_games_gateway, name='games_gateway'),
    path('<str:platform_code>/<int:game_id>/<str:hyphenated_game_title>', views.render_individual_game, name='game'),
    path('search', views.render_search_page, name='search')
]
