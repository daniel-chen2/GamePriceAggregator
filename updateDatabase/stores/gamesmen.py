import json
from games.models import Game, Link
from django.db.models import Q
import re
import updateDatabase.config as c
from bs4 import BeautifulSoup
from updateDatabase.classes import Store
import os
module_dir = os.path.dirname(__file__)

class Gamesmen(Store):
    catalogue = []
    def __init__(self):
        self.gamesguru_id = c.get_store('gme').id
        self.name = 'Gamesmen'
        self.games_list_file_path = os.path.join(module_dir, 'gamesmen_links.json')
    
    """
        Get Price Method
        From Given URL get the current price
    """
    def get_price(self, link_url):
        gamesmen_json_data = self.__get_gamesmen_json_data()
        for game in gamesmen_json_data:
            if game['url'] == link_url:
                return c.getPrice(game['current_price'], game['initial_price'])

    def __get_gamesmen_json_data(self):
        gamesmen_json_file_path = os.path.join(module_dir, 'gamesmen_links.json')
        with open(gamesmen_json_file_path) as f:
            data = json.load(f)
        return data

    """
        Get Link Method
        return several links given an input game
    """
    def get_link(self, game_from_database):
        gamesmen_json_data = self.__get_gamesmen_json_data()
        links_data = []
        for gamesmen_game in gamesmen_json_data:
            gamesmen_game_title = Store.strip_title(self, gamesmen_game['title'].lower(), ['game of the year','gold edition','(playstation hits)','premium edition','edition',])
            try:
                if Game.objects.search_games_by_query(query=gamesmen_game_title, similarity_level=0.5)[0] == game_from_database:
                    links_data.append(self.__get_matched_link_object(gamesmen_game, game_from_database))
            except:
                pass
        return links_data

    def __get_matched_link_object(self, gamesmen_game, game_from_database):
        prices = c.getPrice(gamesmen_game['current_price'],gamesmen_game['initial_price'],in_cents=False)
        platform = 'xb1' if gamesmen_game['console'] == 'xbox-one' else gamesmen_game['console']
        new_link = Link(game=game_from_database, store_id=self.gamesguru_id, platform=c.get_platform(platform),distribution='Ph', initial_price=prices['initial_price'],price=prices['current_price'],link= gamesmen_game['url'], price_found= prices is not None)
        return new_link

    """
        Update Link Method
        update gamesmen links for a given game
    """
    def update_link(self,game):
        links_from_db = Link.objects.filter(game=game,store_id=self.gamesguru_id)
        links_to_add = links_from_db if len(links_from_db) > 0 else self.get_link(game)
        for current_link_object in links_to_add:
            has_database_entries = links_from_db.count() != 0
            self.__save_link_object(current_link_object, has_database_entries)
        return links_to_add

    def __save_link_object(self, link_to_save, has_database_entries):
        if has_database_entries: 
            link_to_save = self.__get_updated_price_link(link_to_save)
        link_to_save.save()

    def __get_updated_price_link(self, link_object):
        try:
            new_prices = self.get_price(link_object.link)
            price_found = new_prices is not None
            link_object.initial_price, link_object.price, link_object.price_found = new_prices['initial_price'], new_prices['current_price'], price_found
        except Exception as e:
            print(e)
        return link_object

    """
        Update Database Object Loops through all game objects in database
    """
    def update_database(self, do_catalogue_data=True):
        if do_catalogue_data:
            self.catalogue_data()
        Store.update_database(self)

    """
        The catalogue data method produces a json object containing all object data
    """
    def catalogue_data(self):
        file_path = os.path.join(module_dir, 'gamesmen_links.json')
        data = []
        for x in ['ps4','xbox-one']:
            data += self.get_scraped_games_data_for_console(x)
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)
        return data

    def get_scraped_games_data_for_console(self, console):
        scraped_url = 'https://www.gamesmen.com.au/video-games/'+console+'/games/condition/new'
        soup = BeautifulSoup(c.checkLink(scraped_url).content, 'html.parser')
        number_of_pages, returned_data = len(soup.find('div',{'class':'pages'}).findAll('li'))-1, []
        for page_number in range(1, number_of_pages + 1):
            self.__append_games_in_page_to_list(scraped_url, page_number, returned_data, console)
            print("Page Number: ", page_number)
        return returned_data

    def __append_games_in_page_to_list(self, base_url, page, appended_list, console):
        soup = BeautifulSoup(c.checkLink(base_url+'/page/'+ str(page)).content, 'html.parser')
        links_found_in_page = soup.find('div',{'class':'category-products'}).findAll('li',{'class':'item'})
        for html_game_element in links_found_in_page:
            self.__append_game_entry_to_list(html_game_element, appended_list, console)

    def __append_game_entry_to_list(self, html_game_element, data, console):
        a = html_game_element.find('p',{'class':'product-name'}).find('a')
        new_data_entry = {
            'title': a.text.replace('(Playstation Hits)','').replace('[Pre-Owned]','').strip(),
            'url': a['href'],
            'initial_price': self.__get_initial_price(html_game_element),
            'current_price': self.__get_initial_price(html_game_element) if not html_game_element.find('p',{'class':'special-price'}) else html_game_element.find('p',{'class':'special-price'}).find('span',{'class':'price'}).text.strip(),
            'console': console
        }
        print(new_data_entry)
        data.append(new_data_entry)

    def __get_initial_price(self,link):
        initial_price = None
        if link.find('span',{'class':'regular-price'}):
            initial_price = link.find('span',{'class':'regular-price'}).find('span',{'class':'price'}).text.strip()
        elif link.find('p',{'class':'old-price'}):
            initial_price = link.find('p',{'class':'old-price'}).find('span',{'class':'price'}).text.strip()
        return initial_price