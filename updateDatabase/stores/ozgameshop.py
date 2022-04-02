import json
from games.models import Game, Link, Platform
from django.db.models import Q
import re
import updateDatabase.config as config
from bs4 import BeautifulSoup
from updateDatabase.classes import Store
import os
from updateDatabase.scraper import get_request_from_scraper_api
import traceback
import urllib.parse
from updateDatabase.stores.logs.scrape_logger import scrape_logger 
import time


class OzGameShop(Store):
    catalogue = []
    def __init__(self):
        self.gamesguru_id = config.get_store('ozg').id
        self.name = 'OzGameShop'
        self.logger = scrape_logger(self.name)

    """
        Update Database Object Loops through all game objects in database
    """
    def update_database(self, do_catalogue_data=True):  
        console_ids = ["xbox-one", "ps4"]
        
        start = time.time()
        for console_id in console_ids:
            try:
                self.update_games_from_console_id(console_id)
            except Exception as e:
                print(e)

    """
        Listings Scrape Methods
    """
    def update_games_from_console_id(self, console_id):
        base_url = "https://www.ozgameshop.com/" + console_id + "-games/sort-best-match/exclude-oos"
        current_page = 1
        while True:
            url_to_scrape = base_url + "/page-" + str(current_page)
            print("Scraping from", url_to_scrape)
            games_from_url, has_next_page = self.get_games_from_listings_url(url_to_scrape, console_id=console_id)
            self.update_games_from_dict(games_from_url)
            if not has_next_page:
                break
            else:
                current_page = current_page + 1
    
    def update_games_from_dict(self, games_dict):
        for game_from_ozgameshop in games_dict:
            try:
                searched_games_from_database = Game.objects.search_games_by_query(query=game_from_ozgameshop['title'], similarity_level=0.5)
                if (searched_games_from_database.count() > 0):
                    game_from_database = searched_games_from_database[0]
                    self.save_link(game_from_ozgameshop, game_from_database)
                else: 
                    self.logger.info('No link found for ' + game_from_ozgameshop["title"])
            except Exception as e:
                print(self.name + ' exception for ' + game_from_ozgameshop["title"])
                self.logger.info(self.name + ' exception for ' + game_from_ozgameshop["title"])

    def save_link(self, game_from_ozgameshop, game_from_database):
        platform = Platform.objects.get(code=game_from_ozgameshop["platform"])
        link_to_save = Link(game=game_from_database, platform=platform, store_id = self.gamesguru_id, initial_price=game_from_ozgameshop["initial_price"], price=game_from_ozgameshop["price"], link=game_from_ozgameshop["link"], distribution="Ph")
        links_from_db = Link.objects.filter(link=game_from_ozgameshop["link"])
        if(links_from_db.count() > 0):
            link_to_save.id = links_from_db[0].id
        link_to_save.save()
        print('Successful update for ' + repr(link_to_save))
        self.logger.info('Successful update for ' + repr(link_to_save))

    def get_games_from_listings_url(self, listings_url, console_id):
        """
        Returns product data from "https://www.ozgameshop.com/ps4"
        """
        print("scraping from... " + listings_url)
        response = get_request_from_scraper_api(listings_url)
        soup = BeautifulSoup(response.data, 'html.parser')
        products = soup.select(".product_box")
        links_to_return = []
        for product in products:
            link_obj = {}
            prices = config.getPrice(product.select(".price")[0].text, product.select(".price")[0].text)
            a_tag = product.findAll('a')[1]
            link_obj['title'] = a_tag.text.strip("PS4 Game").strip("Edition")
            link_obj['initial_price'] = prices['initial_price']
            link_obj['price'] = prices['current_price']
            link_obj['link'] = self.__convert_to_affiliate_link(a_tag["href"])
            link_obj['platform'] = console_id if console_id != "xbox-one" else "xb1"
            links_to_return.append(link_obj)
        print(links_to_return)
        has_next_page = len(soup.select("#load_more_text")) > 0
        return links_to_return, has_next_page

    def __convert_to_affiliate_link(self,url_to_convert):
        base_affiliate_link = "https://t.cfjump.com/69669/t/11793?Url="
        return base_affiliate_link + urllib.parse.quote(url_to_convert) 

    

