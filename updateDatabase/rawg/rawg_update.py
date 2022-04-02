import requests
import json
from games.models import Game, Link, Platform
import html
import datetime
import updateDatabase.config as c 
from updateDatabase.stores.logs.scrape_logger import scrape_logger
import os
from updateDatabase.stores.gamesmen import Gamesmen
module_dir = os.path.dirname(__file__)
rawg_api_url = 'https://api.rawg.io/api/'
rawg_headers = {'User-Agent': "GamesGuru"}

# Rawg Functions
rawg_stores = {
    'psn':3,
    'steam':1,
    'microsoft': 2
}

# Input Game Object
# Query for games stores
# Either return specific store or whole JSON object
def get_rawg_stores(game, store_id=None):
    res = c.checkLink(rawg_api_url + 'games/' + str(game.rawg_id) + "/stores")
    if store_id is None: return res.json()['results']
    try:
        return [x['url'] for x in res.json()['results'] if x['store_id'] == store_id][0]
    except Exception as e:
        print (e)
        return None; print('Failed to get Stores for: ', game)
    

class RAWG():
    def __init__(self):
        self.rawg_api_url = 'https://api.rawg.io/api/'
        self.rawg_headers = {'User-Agent': "GamesGuru"}
        self.name='RAWG'

    def get_game(self, rawg_id):
        game_from_rawg = c.checkLink(url = (self.rawg_api_url + 'games/' + str(rawg_id)),headers=self.rawg_headers).json()
        platform_names = [platform['platform']['name'] for platform in game_from_rawg['platforms']]
        platforms_to_add_to_game = Platform.objects.filter(title__in=platform_names)
        game = Game(title=game_from_rawg['name'],description=html.unescape(c.remove_html(game_from_rawg['description'])),publish_date=game_from_rawg['released'],photo_url=game_from_rawg['background_image'],rawg_id=game_from_rawg['id'])
        game.platforms_to_add = platforms_to_add_to_game
        return game if game else None

    def update_game(self, rawg_id, force=False):
        """
        Given RawgID update/add the game to the database
        """
        if force or not (Game.objects.filter(rawg_id=rawg_id).count() > 0):
            try:
                (game := self.get_game(rawg_id)).save()
                self.update_platform_of_game(game)
                print('Successful update for ' + repr(game))
                scrape_logger(self.name).warning('Successful update for ' + repr(game))
            except Exception as e:
                scrape_logger(self.name).warning('Exception for ' + repr(e))
        else: 
            scrape_logger(self.name).warning('Game Found in database' + str(rawg_id))
    
    def update_platform_of_game(self,game_to_update):
        game_from_rawg = self.get_game(game_to_update.rawg_id)
        for platform in game_from_rawg.platforms_to_add:
            game_to_update.platforms.add(platform)
        game_to_update.save()

    def update_all_games_platforms(self):
        for game in Game.objects.all():
            self.update_platform_of_game(game)

    # Return list of RawgIDs from one query to the RAWG Database
    def query_for_game_ids(self,query="", num_results=40, add_params={},page=1):
        parameters = {'search':query,'page_size': num_results,'page':page,**add_params}
        response = c.checkLink(self.rawg_api_url + 'games', headers=self.rawg_headers, parameters=parameters).json()
        return  [game['id'] for game in response['results']]

    # Return list of found games
    # Query rawg
    def update_database(self, num_results):
        page = 1
        while num_results > 0:
            add_params = {'search': '', 'dates': '2019-01-01,2020-12-10.', 'ordering':'-added'}
            number_of_ids = num_results if num_results < 40 else 40
            for rawg_id in self.query_for_game_ids(num_results=number_of_ids,add_params=add_params,page=page):
                    self.update_game(rawg_id=rawg_id)       
            num_results -= number_of_ids; page += 1
    
    def update_from_file(self):
        # Gamesmen().catalogue_data()
        gameslist_file_path = Gamesmen().games_list_file_path
        with open(gameslist_file_path) as f:
            games = json.loads(f.read())
        for game in games:
            print("Querying: ", game["title"])
            found_game_ids = self.query_for_game_ids(query=game["title"], add_params={"platforms":"1,18,7", "exclude_additions":"True","dates":"2013-01-01,"+ str(datetime.datetime.now().year+1) +"-12-12"})
            for found_game_id in found_game_ids[:3]:
                self.update_game(found_game_id)
        
        


