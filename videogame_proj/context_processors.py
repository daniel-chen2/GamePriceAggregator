from games.models import Platform
from django.core.cache import cache
from pages.models import Alert

def platforms(request):
    return {'total_platforms': Platform.objects.all()}

def alerts(request):
    try:
        return {'alert': cache.get('alert', Alert.objects.all().order_by('-id')[0])}
    except:
        return {'alert': "Welcome To Bargain Gamer - We Compare Prices Of Videogames In Australia"}