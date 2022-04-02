from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from videogame_proj.sitemaps import Static_Sitemap, Game_Sitemap
from . import views


# Sitemaps
sitemaps = {
    'static': Static_Sitemap(),
    'games': Game_Sitemap
}

urlpatterns = [
    path('secret_admin/', admin.site.urls),
    path('games/', include('games.urls')),
    path('', include('pages.urls')),
    # Sitemaps
    path('sitemap.xml', views.sitemap, name="sitemap"),
    path('generate/sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # robots.txt
    path('robots.txt', views.robotsTxt, name="robots")
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Error Handlers
handler404 = 'videogame_proj.views.handler404'
handler500 = 'videogame_proj.views.handler500'