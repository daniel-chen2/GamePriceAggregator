# import updateDatabase.stores.cj as cj
from updateDatabase.stores.microsoft import Microsoft
from updateDatabase.stores.ebgames import EBGames
from games.models import Game,Link,Cheapest_Link
from updateDatabase.classes import Store
from updateDatabase.stores.cj import Fanatical, GMG, CD_Keys, GamersGate,Kinguin
from updateDatabase.stores.psn import PSN
from updateDatabase.stores.steam import Steam
from updateDatabase.stores.gamesmen import Gamesmen
from updateDatabase.stores.amazon import Amazon
from updateDatabase.stores.ozgameshop import OzGameShop
import time
import datetime
import threading 

stores_queue = [EBGames(), OzGameShop(), Amazon(), PSN(), Microsoft()]
cj_stores_queue = [Fanatical(), GMG(), GamersGate(), Kinguin()]

def start_thread(store):
    thread = threading.Thread(target=store.update_database)
    thread.start()
    return thread

def update_links_in_database():
    threads = []; start = time.time()
    for store in stores_queue:
        threads.append(start_thread(store))
    # while len(cj_stores_queue) > 0:
    #     cj_store_thread = start_thread(cj_stores_queue.pop())
    #     cj_store_thread.join() # Wait for thread to end before popping another
    # cj_store_thread.join()
    for thread in threads:
        thread.join()
    end = time.time()
    print("Time Started: ", start)
    print("Time Ended: ", end)
    print("Time Taken: ", end - start)

# Maintainence functions
def update_cheapest_links_for_each_game():
    Cheapest_Link.objects.all().delete()
    for game in Game.objects.all():
        all_links = game.links.all()
        for platform in game.platforms.all():
            try:
                links_to_check = all_links.filter(platform=platform)
                cheapest_link_found = get_cheapest_link_from_list(links_to_check)
                print(cheapest_link_found)
                Cheapest_Link(platform=platform,game=game,link=cheapest_link_found, initial_price = cheapest_link_found.initial_price, price = cheapest_link_found.price).save()
            except:
                print('Failed to update cheapest link for: ', game, platform)

def get_cheapest_link_from_list(links):
    if len(links) == 0:
        return None
    current_link = links[0]
    for link in links:
        if link.price < current_link.price:
            current_link = link
    return current_link

def delete_multiple_entries():
    for game in Game.objects.all():
        for platform in game.platforms.all():
            while (duplicate_entries := Cheapest_Link.objects.filter(game=game,platform=platform)).count() > 1:
                duplicate_entries[0].delete()


        
