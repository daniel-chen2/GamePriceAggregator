import json
from games.models import Game, Link
from django.db.models import Q
import re
import updateDatabase.config as c
from bs4 import BeautifulSoup
import requests
from updateDatabase.classes import Store
import traceback
import pdb
import urllib.parse

# cj greenmangaming
# cj fanatical 5002882
cj_api = 'https://product-search.api.cj.com/v2/product-search?'
headers = {'Authorization': 'Bearer 3f33z1wph9rcp4e5qk2mgzh5y8'}
cj_ad_ids = {
    'fanatical': '5002882',
    'gmg': '3386711',
    'kinguin': '4518745',
    'cdkeys': '5173263',
    'gamersgate':'2821123'
}
website_id = '9271590'

#Commision junction Class 
# Other classes extend this method
class CJ(Store):
    def __init__(self):
        self.advertiser_id = ''
        self.gamesguru_id = ''
        self.name = 'Commision Junction'
    
    def get_price(self,game):
        link = self.get_link(game)
        return {
            'initial_price':link.initial_price,
            'current_price':link.price
        } 

    def get_price_from_link(self,url):
        pass

    # Returns Link object for given game object
    # Checks through the json file created by the EBgames link for the title
    # Returns link object
    # Assumes PC Link
    def get_link(self, game, currency='AUD',strip=[]):
        keywords, links_list = "+".join(game.title.split(' ')), []
        parameters= { 'advertiser-ids': self.advertiser_id, 'keywords':keywords, 'website-id':website_id, 'currency': currency, 'page-number': 1,'records-per-page': 20 }
        soup = BeautifulSoup(c.checkLink(url=cj_api,parameters=parameters, headers=headers).content, 'html.parser')
        games = soup.findAll('product')
        if len(games) == 0: raise Exception('Game Not Found')
        for g in games:
            title =  Store.strip_title(self,g.find('name').text, strip)
            regex = Store.get_regex(self,title)
            if regex.match(game.title.lower()):
                prices = c.getPrice(g.find('sale-price').text, g.find('price').text,in_cents=False,country=currency)
                price_found = prices is not None
                links_list.append({
                    'title': title,
                    'link': Link(game=game,store_id=self.gamesguru_id, platform_id=c.get_platform('pc').id, initial_price=prices['initial_price'],price=prices['current_price'],link=g.find('buy-url').text, price_found=price_found)
                }) 
        return self.__get_most_relevant_link(links_list, game)

    def __get_most_relevant_link(self, links, game):
        # Checks if the game title is equal to the store's title, and then loops through lowest price
        relevant_links = []
        for link in links:
            if link['title'] == game.title.lower():
                relevant_links.append(link['link'])
        if len(relevant_links) == 0: relevant_links = [link['link'] for link in links]

        current_price =float('inf')
        for link in relevant_links:
            if link.price < current_price:
                current_link = link
                current_price = link.price
        return current_link if current_link else None

    # Input storeid and game
    # Checks for each link in platform what exists
    def update_link(self,game):
        links_found = Link.objects.filter(game=game,store_id=self.gamesguru_id)
        try: #First try to update from the links_found link
            if links_found[0].link:
                print('Now getting price from link')
                prices = get_price_from_link(links_found[0].link)
                link_to_save.id = links_found[0].id
        except:
            link_to_save = self.get_link(game)
        link_to_save.save(); 
        return link_to_save

    def update_database(self):
        Store.update_database(self)

class Fanatical(CJ):
    def __init__(self):
        self.advertiser_id = '5002882'
        self.gamesguru_id = c.get_store('fan').id
        self.name = 'Fanatical'
    
    def get_price_from_link(self,url):
        if url.split('.')[1] != 'fanatical':
            raise Exception('URL Invalid: Did you make sure to include https:...')
        url = url.split('/')
        fanatical_id = url[len(url)-1]
        url = 'https://www.fanatical.com/api/products/' + fanatical_id + '/en'
        headers = {'referer': url}
        response = json.loads(c.checkLink(url,headers=headers).content)
        return c.getPrice(response['currentPrice']['AUD'],response['price']['AUD'], in_cents=True)

class GMG(CJ):
    def __init__(self):
        self.advertiser_id = cj_ad_ids['gmg']
        self.gamesguru_id = c.get_store('gmg').id
        self.name = 'gmg'

    def get_price_from_link(self,url):
        if url.split('.')[1] != 'greenmangaming':
            raise Exception('URL Invalid: Did you make sure to include https:...')
        response, data = c.checkLink(url), []
        soup = BeautifulSoup(response.content, 'html.parser')
        return c.getPrice(
            soup.find('price',{'class':'current-price'}).text,
            soup.find('price',{'class':'prev-price'}).text if soup.find('price',{'class':'prev-price'}) else None, 
        )

class CD_Keys(CJ):
    # Not yet implemented
    def __init__(self):
        self.advertiser_id = cj_ad_ids['cdkeys']
        self.gamesguru_id = c.games_guru_stores['cdkeys']
    
    def get_link(self, game):
        return CJ.get_link(self=self, game=game,currency='')

class GamersGate(CJ):
    def __init__(self):
        self.advertiser_id = cj_ad_ids['gamersgate']
        self.gamesguru_id = c.get_store('gat').id
        self.name = 'GamersGate'

    def get_link(self, game):
        return CJ.get_link(self=self, game=game,currency='USD')

    def get_price_from_link(self,url):
        if url.split('.')[1] != 'gamersgate':
            raise Exception('URL Invalid: Did you make sure to include https:...')
        split_url = url.split('/')
        keywords = "+".join(split_url[len(split_url)-1].split('-'))
        parameters= { 'advertiser-ids': self.advertiser_id, 'keywords':keywords, 'website-id':website_id, 'currency': 'USD', 'page-number': 1,'records-per-page': 10}
        soup = BeautifulSoup(c.checkLink(url=cj_api,parameters=parameters, headers=headers).content, 'html.parser')
        for product in soup.find('products'):
            if urllib.parse.unquote(url) in urllib.parse.unquote(product.find('buy-url').text):
                return c.getPrice(
                    product.find('sale-price').text if product.find('sale-price') else None,
                    product.find('price').text, 
                    country='USD'
                )
        raise Exception('No Link Found at ' + repr(url))
        return None

class Kinguin(CJ):
    def __init__(self):
        self.advertiser_id = '4518745'
        self.gamesguru_id = c.get_store('kin').id
        self.name = 'Kinguin'

    def get_link(self,game):
        strip = ['CD Key', 'Gift', 'Altergift', 'Game of the Year', 'Complete Edition', 'Edition', 'GOTY', 'GOG', 'Steam','Origin','Uplay','AU','Rockstar Digital Download', 'Digital Download', '/', 'Windows 10']
        return CJ.get_link(self,game,currency='EUR',strip=strip)
    
    def get_price_from_link(self,url):
        if url.split('.')[1] != 'kinguin':
            raise Exception('URL Invalid: Did you make sure to include https:...')
        split_url = url.split('/')
        keywords = "+".join(split_url[len(split_url)-1].split('-'))
        parameters= { 'advertiser-ids': self.advertiser_id, 'manufacturer-sku': split_url[4],'keywords':keywords, 'website-id':website_id, 'currency': 'EUR', 'page-number': 1,'records-per-page': 1}
        soup = BeautifulSoup(c.checkLink(url=cj_api,parameters=parameters, headers=headers).content, 'html.parser')
        for product in soup.find('products'):
            return c.getPrice(
                product.find('sale-price').text if product.find('sale-price') else None,
                product.find('price').text, 
                country='EUR'
            )
        raise Exception('No Link Found at ' + repr(url))
        return None

