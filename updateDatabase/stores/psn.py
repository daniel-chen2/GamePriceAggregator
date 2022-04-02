import json
from games.models import Link, Game
import updateDatabase.config as c
from updateDatabase.classes import Store
import updateDatabase.rawg.rawg_update as rawg_update
from updateDatabase.rawg.rawg_update import get_rawg_stores


class PSN(Store):
    def __init__(self):
        self.store_rawg_id = rawg_update.rawg_stores['psn']
        self.gamesguru_id = c.games_guru_stores['psn']
        self.platform_id = c.games_guru_platforms['ps4']
        self.name = 'PSN'

    """
        Get Price Object
    """
    # Given Link Get Price, Given Normal Playstation Link  
    # Broken need to fix in time
    def get_price(self, url=None, response=None):
        cc = 'AU' if url.split('/')[3] == 'en-au' else 'US'
        psn_id = url.split('/')[5]
        api_res = json.loads(c.checkLink('https://store.playstation.com/store/api/chihiro/00_09_000/container/' + cc +'/en/999/' + str(psn_id)).content) 
        print('https://store.playstation.com/store/api/chihiro/00_09_000/container/' + cc +'/en/999/' + str(psn_id))
        if (13 in api_res['default_sku']['platforms']):
            initial_price = api_res['default_sku']['price']
            current_price = None if not api_res['default_sku']['rewards'] else api_res['default_sku']['rewards'][0]['price']
            prices = c.getPrice(current_price,initial_price, True, cc)
            return prices
        return None

    # Given game get Link Object
    def get_link(self, game):
        # Check link at given rawgid
        us_url, country_code = get_rawg_stores(game=game, store_id=self.store_rawg_id), 'AU'
        response, url = c.checkLink(us_url.replace('en-us','en-au')), us_url.replace('en-us','en-au')
        if response.status_code != 200: 
            response, country_code, url = c.checkLink(us_url), "US", us_url
        if (response):
            psn_id = response.url.split('/')[5]
            api_res = json.loads(c.checkLink('https://store.playstation.com/store/api/chihiro/00_09_000/container/' + country_code +'/en/999/' + str(psn_id)).content) 
            if (13 in api_res['default_sku']['platforms']):
                initial_price = api_res['default_sku']['price']
                current_price = None if not api_res['default_sku']['rewards'] else api_res['default_sku']['rewards'][0]['price']
                prices = c.getPrice(current_price,initial_price,True, country_code)
                price_found = prices is not None
                return Link(game=game,store_id=self.store_rawg_id, platform_id=self.platform_id, initial_price=prices['initial_price'],price=prices['current_price'],link=url,price_found=price_found)

    def update_link(self,game):
        store_id,platform_id=self.store_rawg_id,self.platform_id
        links_in_database = Link.objects.filter(game=game,store_id=store_id,platform_id=platform_id)
        if (links_in_database.count() == 0):
            link_to_save = self.get_link(game)
        else:
            link_to_save = self.get_link(game)
            link_to_save.id = links_in_database[0].id
        link_to_save.save()
        return link_to_save

    def update_database(self):
        Store.update_database(self)