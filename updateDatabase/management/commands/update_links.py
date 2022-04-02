from django.core.management.base import BaseCommand 
import updateDatabase.update as update
from updateDatabase.rawg.rawg_update import RAWG

# Import the stores
from updateDatabase.stores.amazon import Amazon
from updateDatabase.stores.ebgames import EBGames
from updateDatabase.stores.cj import Fanatical, GMG, CD_Keys, GamersGate,Kinguin
from updateDatabase.stores.psn import PSN
from updateDatabase.stores.microsoft import Microsoft
from updateDatabase.stores.gamesmen import Gamesmen

class Command(BaseCommand):
    help = 'Updates Links/Prices in Database'

    def add_arguments(self, parser):
        parser.add_argument('--amazon', action='store_true', help='Scrapes from amazon')
        parser.add_argument('--ebgames', action='store_true', help='Scrapes from ebgames')
        parser.add_argument('--fanatical', action='store_true', help='Scrapes from fanatical')
        parser.add_argument('--gmg', action='store_true', help='Scrapes from gmg')
        parser.add_argument('--gamersgate', action='store_true', help='Scrapes from gamersgate')
        parser.add_argument('--psn', action='store_true', help='Scrapes from psn')
        parser.add_argument('--kinguin', action='store_true', help='Scrapes from Kinguin')
        parser.add_argument('--microsoft', action='store_true', help='Scrapes from Microsoft')
        parser.add_argument('--gamesmen', action='store_true', help='Scrapes from gamesmen')
        parser.add_argument('--all', action='store_true', help='Scrapes from all stores')

    def handle(self, *args, **options):
        if options['amazon']:
            Amazon().update_database(do_catalogue_data=True)
        if options['ebgames']:
            EBGames().update_database()
        if options['fanatical']:
            Fanatical().update_database()
        if options['gmg']:
            GMG().update_database()
        if options['gamersgate']:
            GamersGate().update_database()
        if options['psn']:
            PSN().update_database()
        if options['kinguin']:
            Kinguin().update_database()
        if options['microsoft']:
            Microsoft().update_database()
        if options['gamesmen']:
            Gamesmen().update_database()
        if options['all']:
            update.update_links_in_database()
        update.update_cheapest_links_for_each_game()