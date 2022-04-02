import abc
from games.models import Game, Link
from updateDatabase.stores.logs.scrape_logger import scrape_logger
import re
import time
import datetime

"""
Store Object For Scraper Methods To Implement
A Python Implementation of a Store Interface
"""
class Store(abc.ABC):
    # Get Price For A Given Object
    def get_price(self):
        pass

    # Return Link Object For A Given Object 
    def get_link(self):
        pass
    
    def update_link(self):
        pass

    @abc.abstractmethod
    def update_database(self, quick=False):
        logger = scrape_logger(self.name)
        start = time.time()
        for game in Game.objects.all():
            if quick and Link.objects.filter(game=game, store_id=self.gamesguru_id).count() == 0:
                continue
            try:
                updated_link = self.update_link(game)
                if updated_link: 
                    print('Successful update for ' + repr(updated_link))
                    logger.info('Successful update for ' + repr(updated_link))
                elif not updated_link: logger.info('No link found for ' + repr(game))
            except BaseException as e:
                print(self.name + ' exception for ' + repr(game) + repr(e) + str(game.id))
                logger.info(self.name + ' exception for ' + repr(game) + repr(e) + str(game.id))
        end = time.time()
        logger.info('Start Time ' + repr(datetime.timedelta(seconds=start)))
        logger.info('End Time ' + repr(datetime.timedelta(seconds=end)))
        logger.info('Time taken: ' + repr(datetime.timedelta(seconds=end-start)))


    def get_regex(self,title):
        title = title.lower()
        split_title = title.split(' ')
        regex = re.compile(''.join([r'(?=.*' + r'\b' + re.escape(s) + r').\S*' for s in split_title]) + '$')
        return regex

    # Returns True If There Is a game in database with the same title
    def matches_title(self, title_to_match_with, comparison_title):
        regex = Store.get_regex(self, title_to_match_with.lower())
        return regex.match(comparison_title.strip().lower())

    def strip_title(self,title,strip_list):
        title = title.lower().replace('Game of the Year Edition','').replace('PC','').replace('GOTY','').strip('')
        for rep in strip_list:
            title = re.sub(r'\b' +rep.lower()+ r'\b','',title).strip()
        return title