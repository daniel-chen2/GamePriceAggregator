from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.render_index_page, name='index'),
    path('about', views.render_about_page, name='about'),
    path('coupons', views.render_coupons_page, name='coupons'),
    path('free-games', views.render_free_games, name='free_games'),
    path('sales', views.render_sales_page, name='sales'),
]