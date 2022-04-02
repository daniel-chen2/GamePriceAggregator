import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.gamesmen import Gamesmen

class TestGamesmen(TestCase):
    @classmethod
    def setUpTestData(self):
        Game.objects.create(title='Final Fantasy VII Remake', publish_date='2020-01-01', rawg_id=1169)
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=1169)
        Store.objects.create(title="Gamesmen", code='gme')
        Platform.objects.create(id='1',title='Xbox-One', icon='fab fa-windows',code='xb1')
        Platform.objects.create(id='2',title='PlayStation 4', icon='fab fa-windows',code='ps4')
        Platform.objects.create(id='3',title='PC', icon='fab fa-windows',code='pc')
        Gamesmen()

    def test_get_link(self):
        game = Game.objects.get(id=1)
        links = Gamesmen().get_link(game)
        self.assertTrue(len(links) > 0)

    def test_get_price(self):
        price = Gamesmen().get_price('https://www.gamesmen.com.au/afl-evolution-2-1')
        self.assertTrue(price == {'initial_price':99.95,'current_price':88.00}, "Price Found Was " + str(price))

    def test_update_link(self):
        game = Game.objects.get(id=1)
        updated_links = Gamesmen().update_link(game)
        for updated_link in updated_links:
            link = Link.objects.get(id=updated_link.id)
            self.assertTrue(link == updated_link)
            self.assertTrue(updated_link.price <= updated_link.initial_price)
    
    def test_update_database(self):
        Gamesmen().update_database(do_catalogue_data=False)
        self.assertTrue(Link.objects.filter(game_id=1).count() > 0)
        self.assertTrue(Link.objects.filter(game_id=2).count() > 0)
        




