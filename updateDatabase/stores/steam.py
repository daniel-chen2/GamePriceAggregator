import json
from games.models import Link, Game
import updateDatabase.config as c
from updateDatabase.classes import Store
import updateDatabase.rawg.rawg_update as rawg_update
from updateDatabase.rawg.rawg_update import get_rawg_stores

class Steam(Store):
    def __init__(self):
        self.store_rawg_id = rawg_update.rawg_stores['steam']
        self.gamesguru_id = c.get_store('ste').id
        self.platform_id = c.get_platform('pc').id
        self.name = 'Steam'

    def get_link(self, game):
        url = get_rawg_stores(game=game, store_id=self.store_rawg_id)
        print(url)
        prices=self.get_price(url)
        if price_found := prices is not None:
            return Link(game=game,store_id=self.gamesguru_id, platform_id=self.platform_id, initial_price=prices['initial_price'],price=prices['current_price'],link=url,price_found=price_found)
        return None    
        pass

    def get_price(self, url=None, response=None):
        response = c.checkLink('http://store.steampowered.com/api/appdetails?appids='+url.split('/')[4]+'&cc=AU')
        response = json.loads(response.content)
        results = response[list(response.keys())[0]]['data'] 
        # If is free
        if results['is_free'] == True: return c.getPrice(0,0)
        try:
            return c.getPrice(results['price_overview']['final'],results['price_overview']['initial'],in_cents=True)
        except ValueError as e:
            print(e)
        return None

    def update_link(self,game):
        store_id,platform_id=self.store_rawg_id,self.platform_id
        l = Link.objects.filter(game=game,store_id=self.gamesguru_id,platform_id=self.platform_id)
        if l.count() == 0 or not l[0].link: l = self.get_link(game)
        else: 
            l = l[0]; pricefound = (prices:=self.get_price(url=l.link)) is not None 
            l.initial_price, l.price, l.price_found = prices['initial_price'], prices['current_price'],pricefound
        l.save()
        return l

    def update_database(self):
        Store.update_database(self)