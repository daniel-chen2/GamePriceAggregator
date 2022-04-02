from django.contrib import admin
from .models import Game
from .models import Store
from .models import Link, LinkAdmin
from .models import Platform

admin.site.register(Game)
admin.site.register(Link, LinkAdmin)
admin.site.register(Platform)
admin.site.register(Store)