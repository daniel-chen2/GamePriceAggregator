from django.core.management.base import BaseCommand 
from django.core.cache import cache
from games.models import Game, Platform, Cheapest_Link, Store, Link
from pages.models import Sale
import updateDatabase.update as update
from updateDatabase.rawg.rawg_update import RAWG


class Command(BaseCommand):
    help = 'Updates Games From List'

    def add_arguments(self, parser):
        parser.add_argument('--from_list', action='store_true', help='Update games from gamesmen database')
        parser.add_argument('--rawg_id', type=int, help='Choose RAWG ID to update from')
        parser.add_argument('--from_title', type=str, help='Choose RAWG ID to update from')

    def handle(self, *args, **options):
        if options["from_list"]:
            RAWG().update_from_file()
        if options["rawg_id"]:
            print("Updating RAWG ID: ... ", options["rawg_id"])
            RAWG().update_game(options["rawg_id"])
        if options["from_title"]:
            print("Updating From Title: ... ", options["from_title"])
            found_game_id = RAWG().query_for_game_ids(query=options["from_title"])[0]
            RAWG().update_game(found_game_id)
        print("Update Completed")