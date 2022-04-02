from updateDatabase.stores.logs.scrape_logger import scrape_logger
from updateDatabase.scraper import get_request_from_scraper_api
import json
from games.models import Game, Link, Platform
from django.db.models import Q
import re
import updateDatabase.config as c
from bs4 import BeautifulSoup
from updateDatabase.classes import Store
import os
module_dir = os.path.dirname(__file__)

class EBGames(Store):
    def __init__(self):
        self.gamesguru_id = c.get_store('ebg').id
        self.name = 'EB_Games'
    
    # GET PRICE SECTION
    # Gets price from a specified url
    def get_price(self,url):
        soup = BeautifulSoup(get_request_from_scraper_api(url).content, 'html.parser')
        current_price = initial_price = soup.find('span', {'itemprop':'price'}).text.strip('$').lstrip('.')
        if (initial_soup := soup.find('span', {'class':'product-price-stricken'})) is not None: 
            initial_price = initial_soup.text.strip('$')
        return c.getPrice(final_price=current_price,initial_price=initial_price,in_cents=False)

    # GET LINK SECTION
    # Returns a list of link objects for given game 
    # Checks through the json file created by the EBgames link for the title
    def get_link(self, game_from_database):
        games_list_file = self.__get_games_list_file()
        links_found_for_game = self.__return_link_matches_for_game(game_from_database, games_list_file)
        if len(links_found_for_game) == 0: raise Exception('No Game Found')
        return links_found_for_game

    def __return_link_matches_for_game(self, game_from_database, games_list_file):
        links_found_for_game = []
        for ebgame in games_list_file:
            try:
                if Game.objects.search_games_by_query(query=games_list_file[ebgame]['title'], similarity_level=0.8)[0] == game_from_database:
                    console, url, prices = games_list_file[ebgame]['console'], games_list_file[ebgame]['url'], self.get_price(url=games_list_file[ebgame]['url'])
                    new_link = Link(game=game_from_database,store_id=self.gamesguru_id, platform_id=c.get_platform(console).id, initial_price=prices['initial_price'],price=prices['current_price'],link=url,distribution='Ph' ,price_found= prices is not None)
                    links_found_for_game.append(new_link)
            except:
                pass
        return links_found_for_game

    def __get_games_list_file(self):
        file_path = os.path.join(module_dir, 'ebgames_links.json')
        with open(file_path) as f:
            data = json.load(f)
        return data

    # Input storeid and game
    # Checks for each link in platform what exists
    # Input game and update Links for relevant game
    def update_link(self,game):
        links_from_db = Link.objects.filter(game=game,store_id=self.gamesguru_id)
        links_to_add = links_from_db if len(links_from_db) > 0 else self.get_link(game)
        for current_link_object in links_to_add:
            link_to_save = current_link_object
            if links_from_db.count() != 0: 
                link_to_save = self.__updated_price_link(link_to_save)
            link_to_save.save()
        return links_to_add

    def __updated_price_link(self, link_object):
        try:
            new_prices = self.get_price(link_object.link)
            price_found = new_prices is not None
            link_object.initial_price, link_object.price, link_object.price_found = new_prices['initial_price'], new_prices['current_price'], price_found
        except Exception as e:
            print(e)
        return link_object

    # Loop Through Database and update all links with new price
    def update_database(self, quick=False):
        # self.catalogue_data()
        # Store.update_database(self,quick)
        update_games()

    # dump ebgames File as json
    # Unique helper method that prints out the xml as a json file
    def catalogue_data(self):
        file_path = os.path.join(module_dir, 'ebgames_links.json')
        response = get_request_from_scraper_api('https://www.ebgames.com.au/sitemap-products.xml')
        if response.ok:
            sitemap_index = BeautifulSoup(response.content, 'html.parser')
            data = self.__get_data_from_sitemap(sitemap_index)
            with open(file_path, 'w') as outfile:
                json.dump(data, outfile)
        else:
            print(response.content)
            raise Exception("Catalogue Failed")
    
    def __get_data_from_sitemap(self, sitemap_index):
        data = {}
        urls = [element.text for element in sitemap_index.findAll('loc')]
        for url in urls: 
            split = url.split('/')[5].split('-')
            eb_id = split[0]
            game_name = ' '.join(split[1:]).replace('game of the year edition','').replace('preowned','').replace('complete edition','').strip()
            console = url.split('/')[4]
            if console == 'ps4' or console == 'pc' or console == 'xbox-one':
                console = console if console != 'xbox-one' else 'xb1'
                data[eb_id] = {'title': game_name, 'url':url, 'console': console }
        return data

def update_games():
    console_ids = ["xbox-one", "ps4"]
    for console_id in console_ids:
        try:
            get_games_from_console_id(console_id, True)
        except Exception as e:
            print(e)

def get_games_from_console_id(console_id, do_update_links_in_database = False):
    base_url = "https://www.ebgames.com.au/search?platform=" + console_id + "&category=video-games&condition=new"
    current_page = 1
    while True:
        url_to_scrape = base_url + "&page=" + str(current_page)
        print("Scraping from", url_to_scrape)
        games_from_url, has_next_page = get_games_from_listings_url(url_to_scrape, console_id=console_id)
        if(do_update_links_in_database):
            print(games_from_url)
            update_games_from_dict(games_from_url)
        if not has_next_page:
            break
        else:
            current_page = current_page + 1

def save_link(game_from_ebgames, game_from_database):
    platform = Platform.objects.get(code=game_from_ebgames["platform"])
    link_to_save = Link(game=game_from_database, platform=platform, store_id = c.get_store('ebg').id, initial_price=game_from_ebgames["initial_price"], price=game_from_ebgames["price"], link=game_from_ebgames["link"], distribution="Ph")
    links_from_db = Link.objects.filter(link=game_from_ebgames["link"])
    if(links_from_db.count() > 0):
        link_to_save.id = links_from_db[0].id
    link_to_save.save()
    print("saved link", game_from_ebgames["title"])

def update_games_from_dict(games_dict):
    for game_from_ebgames in games_dict:
        try:
            searched_games_from_database = Game.objects.search_games_by_query(query=game_from_ebgames['title'], similarity_level=0.5)
            if (searched_games_from_database.count() > 0):
                game_from_database = searched_games_from_database[0]
                save_link(game_from_ebgames, game_from_database)
        except Exception as e:
            print(e)

def get_games_from_listings_url(listings_url, console_id):
    """
    Returns product data from "https://www.ebgames.com.au/search?platform=" + console_id + "&category=video-games&condition=new"
    """
    print("scraping from... " + listings_url)
    response = get_request_from_scraper_api(listings_url)
    print(response.url)
    soup = BeautifulSoup(response.data, 'html.parser')
    products = soup.select(".product")
    base_ebgames_url = "https://www.ebgames.com.au"
    links_to_return = []
    for product in products:
        link_obj = {}
        link_obj['title'] = product.find("span", {"itemprop":"name"}).text
        link_obj['initial_price'] = product.find("a")["data-price"]
        link_obj['price'] = product.find("a")["data-price"]
        link_obj['link'] = base_ebgames_url + product.find("a")["href"]
        link_obj['platform'] = console_id if console_id != "xbox-one" else "xb1"
        links_to_return.append(link_obj)
    has_next_page = soup.find("a", {"data-ga-label": "search-filters/pagination/next"}) is not None
    return links_to_return, has_next_page


