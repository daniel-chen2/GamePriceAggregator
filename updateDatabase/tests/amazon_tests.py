import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.amazon import Amazon

class TestAmazon(TestCase):
    @classmethod
    def setUpTestData(self):
        Game.objects.create(title='Fifa 20', publish_date='2020-01-01', rawg_id=1169)
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=1169)
        Store.objects.create(title='Amazon', code='ama')
        Platform.objects.create(id='1',title='Xbox', icon='fab fa-windows',code='xb1')
        Platform.objects.create(id='2',title='Playstation', icon='fab fa-windows',code='ps4')
        self.Stores_to_test = [Amazon()]

    def test_store_data(self):
        pass

    def test_get_link(self):
        game = Game.objects.get(id=1)
        for store in self.Stores_to_test:
            link = store.get_link(game)
            self.assertTrue(len(link) > 0)

    def test_get_price(self):
        price = Amazon().get_price('https://www.amazon.com.au/Mafia-III-for-PlayStation-4/dp/B013H0IRO0')
        self.assertTrue(price == {'initial_price': 54.71 ,'current_price': 54.71 }, "Price Found Was " + str(price))

    def test_update_link(self):
        # Tests Get Link Method for Fanatical Store
        game = Game.objects.get(id=1)
        updated_links = Amazon().update_link(game)
        for updated_link in updated_links:
            link = Link.objects.get(id=updated_link.id)
            self.assertTrue(link == updated_link)
            self.assertTrue(updated_link.price >= updated_link.initial_price)

    def test_update_database(self):
        Amazon().update_database(do_catalogue_data=False)
        self.assertTrue(Link.objects.filter(game_id=1).count() > 0)
        self.assertTrue(Link.objects.filter(game_id=2).count() > 0)
        
        




