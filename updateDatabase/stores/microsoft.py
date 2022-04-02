from updateDatabase.rawg import rawg_update as rawg
from games.models import Link, Game
import updateDatabase.config as c
from bs4 import BeautifulSoup as bs
from updateDatabase.classes import Store
import updateDatabase.rawg.rawg_update as rawg_update
from updateDatabase.rawg.rawg_update import get_rawg_stores, rawg_stores
import re

micr_rawg_id, micr_gamesguru_id = rawg_stores['microsoft'], c.games_guru_stores['microsoft']
xbox_platform_id = c.games_guru_platforms['xb1']

class Microsoft(Store):
    def __init__(self):
        self.rawg_id = rawg_update.rawg_stores['microsoft']
        self.gamesguru_id = c.get_store('mic').id
        self.platform_id = c.get_platform('xb1').id
        self.name = 'Microsoft_Store'

    # Get Xbox Link Object From RAWG Database
    # Input Game Object
    # Check if link exists
    # Output Link Object
    # Use rawg store helper function
    def get_link(self, game):   
        us_url = get_rawg_stores(game=game, store_id=micr_rawg_id)
        if (response := c.checkLink(url:=us_url.replace('en-us','en-au',1).replace('/store',''))).status_code == 500 or 200:
            if (bs(response.content, 'html.parser').find('span',{'class':'glyph-xbox-one-console'})):
                prices=self.get_price(response=response)
                return Link(game=game,store_id=self.gamesguru_id, platform_id=self.platform_id, initial_price=prices['initial_price'],price=prices['current_price'],link=url,)
        return None    

    # Get XBOX Link Price
    # Use scraper to add to link object
    # Returns Link Object with Price    
    def get_price(self, url=None, response=None):
        result = c.checkLink(url) if response is None else response
        soup = bs(result.content, 'html.parser')
        discount_price = soup.find(['div','span'], {'class':'price-disclaimer'})
        find_div = ['div','s'] if discount_price else ['div','span']
        initial_price = soup.find('div', {'id':'ProductPrice_productPrice_PriceContainer'}).findChild().text.strip('AU$').strip('+')
        current_price = discount_price.text.strip('AU$').strip('+') if discount_price else initial_price
        return (c.getPrice(current_price, initial_price, in_cents=False))

    def update_link(self,game):
        l = Link.objects.filter(game=game,store_id=self.gamesguru_id,platform_id=self.platform_id)
        if l.count() == 0 or not l[0].link: l = self.get_link(game)
        else: 
            l = l[0]; pricefound = (prices:=self.get_price(url=l.link)) is not None 
            l.initial_price, l.price, l.price_found = prices['initial_price'], prices['current_price'],pricefound
        l.save()
        return l

    # # Update XBOX Link
    # Flag update_price
    # Flag update_all -- Flag denotes that the function will loop through all links not just XBOX Links
    # This is where the try exceptions are really necessary
    def update_database(self):
        Store.update_database(self)