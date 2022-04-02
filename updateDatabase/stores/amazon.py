import json
from games.models import Game, Link, Platform
from django.db.models import Q
import re
import updateDatabase.config as c
from bs4 import BeautifulSoup
from updateDatabase.classes import Store
import os
from django.utils import timezone

module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'amazon_links.json')
amazon_data_file_path = os.path.join(module_dir, 'amazon_links.json')

console_urls = {
    'ps4':'https://www.amazon.com.au/s?k=PlayStation+4+Games&i=videogames&bbn=5250959051&rh=n%3A4852675051%2Cn%3A5250873051%2Cn%3A5250959051%2Cp_n_availability%3A4910512051%2Cp_6%3AANEGB3WVEVKZB&dc&fst=as%3Aoff&qid=1594530393&rnid=4910514051&ref=sr_pg_3',
    'xb1':'https://www.amazon.com.au/s?keywords=Xbox+One+Games&i=videogames&rh=n%3A5250998051%2Cp_n_availability%3A4910512051%2Cp_6%3AANEGB3WVEVKZB&dc&_encoding=UTF8&c=ts&qid=1594530531&ts_id=5250998051&ref=sr_ex_p_72_0',
}

"""
Amazon Scraper Object
"""
class Amazon(Store):
    def __init__(self):
        self.gamesguru_id = c.get_store('ama').id
        self.name = "Amazon"

    def __get_amazon_data_file_as_dictionary(self):
        with open(file_path) as f:
            amazon_data = json.loads(f.read())
        return amazon_data

    """
    Get Price Method
    Returns An Array Containing Both initial_price and final price
    """
    def get_price(self,url):
        try:
            return self.__get_price_from_file(url)
        except Exception as e:
            print(e)
            # return self.__get_price_from_direct_link(url)
        raise Exception("No Price Found at " + url)

    def __get_price_from_file(self, url):
        amazon_data = self.__get_amazon_data_file_as_dictionary()
        for amazon_game in amazon_data:
                amazon_url, url = amazon_game['url'], url.split('?')[0]
                if url in amazon_url:
                    print("Retrieved price from file")
                    return c.getPrice(amazon_game['current_price'], amazon_game['initial_price'])

    def __get_price_from_direct_link(self, url):
        response, data = c.checkLink(url), []
        soup = BeautifulSoup(response.content, 'lxml')
        return c.getPrice(
            soup.find('span',{'id':'priceblock_dealprice'}).text if soup.find('span',{'id':'priceblock_dealprice'}) else soup.find('span',{'id':'priceblock_ourprice'}).text,
            soup.find('span',{'class':'priceBlockStrikePriceString'}).text if soup.find('span',{'class':'priceBlockStrikePriceString'}) else None, 
        )
    
    """
    Get Link Method
    Returns A list of links that has the matched game
    """
    def get_link(self, game):
        links_data = [] 
        amazon_data = self.__get_amazon_data_file_as_dictionary()
        for amazon_game in amazon_data:
            if matched_game:=self.match_link_from_amazon_data(amazon_game, game):
                links_data.append(matched_game)
        return links_data

    def match_link_from_amazon_data(self, amazon_game, game):
        if not amazon_game: 
            return None
        if (found_games_by_query := Game.objects.search_games_by_query(query=amazon_game['title'], similarity_level=0.3)).count() > 0: 
            if(found_games_by_query[0] == game):
                price_found=(prices:=c.getPrice(amazon_game['current_price'],amazon_game['initial_price'],in_cents=False)) is not None
                print(prices)
                return Link(game=game,store_id=self.gamesguru_id, platform_id=c.games_guru_platforms[amazon_game['console']],distribution='Ph', 
                    initial_price=prices['initial_price'],price=prices['current_price'],link=amazon_game['url'], price_found=price_found)

    """
    Update Link Method
    Input Game and return links relevant to the game for the given store
    """
    def update_link(self,game):
        links_from_db = Link.objects.filter(game=game,store_id=self.gamesguru_id)
        links_to_add = links_from_db if len(links_from_db) > 0 else self.get_link(game)
        for current_link_object in links_to_add:
            self.__save_link_object(current_link_object, links_from_db.count() > 0)
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
    Get Link Method
    Returns An Array Containing Both initial_price and final price
    """
    def update_database(self, do_catalogue_data=True):
        if do_catalogue_data:
            self.catalogue_data()
        self.update_from_file()
        self.update_outliers_from_links()

    def update_outliers_from_links(self):
        for link in Link.objects.filter(store_id = self.gamesguru_id):
            if(link.updated_at.today() < timezone.datetime.today()):
                try:
                    price = self.get_price(link.link)
                    initial_price, current_price = price["initial_price"], price["current_price"] 
                    link.initial_price, link.price = initial_price, current_price
                    link.save()
                    print("Link Saved For ", link)
                except Exception as e:
                    print(e)

    def update_from_file(self):
        amazon_data = self.__get_amazon_data_file_as_dictionary()
        for amazon_game in amazon_data:
            if (found_games_by_query := Game.objects.search_games_by_query(query=amazon_game['title'], similarity_level=0.3)).count() > 0:
                platform_to_save = Platform.objects.get(code=amazon_game["console"])
                link_to_save = Link(game=found_games_by_query[0], platform=platform_to_save, store_id=self.gamesguru_id, initial_price= amazon_game["initial_price"], price=amazon_game["current_price"], price_found=True, link=amazon_game["url"], distribution="Ph")
                self.__save_link(link_to_save)
            else:
                print("Not Found: ", amazon_game["title"])

    def __save_link(self, link_to_save):
        links_in_db = Link.objects.filter(link = link_to_save.link)
        if(links_in_db.count() > 0):
            link_to_save.id = links_in_db[0].id
        link_to_save.save()
        print("Save Successful",link_to_save)
            
    """
    Catalogues All Data From Specified URLs into amazon_links.json file
    """
    # Loops through each console page of Amazon and returns an object containing each game data
    def catalogue_data(self):
        clear_json_file(amazon_data_file_path)
        for console in console_urls.keys():
            self.write_link_data_to_file(console)

    def write_link_data_to_file(self, console):
        url = console_urls[console]
        while True: # While is not last page
            html_soup = BeautifulSoup(c.checkLink(url).content, 'lxml')
            self.__append_amazon_page_data_to_file(self.__get_amazon_page_product_data(html_soup,console))
            is_last_page = html_soup.find('li',{'class':'a-disabled a-last'})
            if is_last_page: 
                break
            else: 
                url = 'https://www.amazon.com.au' + html_soup.find('li',{'class':'a-last'}).find('a')['href']
                c.random_delay()

    def __get_amazon_page_product_data(self,soup,console):
        data = []
        links = soup.findAll('div',{'data-component-type':'s-search-result'})   
        for link in links:
            data.append(self.__get_amazon_link_data(link,console))
        return data  

    def __get_amazon_link_data(self, link,console):
        try:
            a_tag = link.find('a',{'class':'a-link-normal a-text-normal'})
            prices = c.getPrice(final_price=link.find('span',{'class':'a-price'}).find('span',{'class':'a-offscreen'}).text,initial_price=None,in_cents=False)
            data = {
                'title' : a_tag.find('span').text.replace('[Game of the Year Edition]','').replace('Premium Edition','').replace('- PlayStation 4','').replace('- Xbox One','').strip(''),
                'url' : 'https://www.amazon.com.au' + a_tag['href'],
                'current_price': prices['current_price'],
                'initial_price': prices['initial_price'],
                'console': console
            }
            return data
        except Exception as e:
            print('Failed at retrieving data', e)  

    def __append_amazon_page_data_to_file(self, amazon_page_product_data):
        with open(amazon_data_file_path, 'r+') as outfile:
            original_data = list(json.loads(outfile.read()))
            new_data = original_data + amazon_page_product_data
            outfile.seek(0)
            print(new_data, "Successully appended to file")
            json.dump(new_data, outfile)
            outfile.truncate()

def clear_json_file(file_path):
    with open(file_path, 'w') as outfile:
        json.dump([], outfile)
