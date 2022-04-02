import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.ebgames import EBGames

class TestEB(TestCase):
    @classmethod
    def setUpTestData(self):
        Game.objects.create(title='Mafia III', publish_date='2020-01-01', rawg_id=1169)
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=1169)
        Store.objects.create(title="EB_Games", code='ebg')
        Platform.objects.create(id='1',title='Xbox-One', icon='fab fa-windows',code='xb1')
        Platform.objects.create(id='2',title='PlayStation 4', icon='fab fa-windows',code='ps4')
        Platform.objects.create(id='3',title='PC', icon='fab fa-windows',code='pc')
        store = EBGames()

    def test_get_link(self):
        game = Game.objects.get(id=1)
        links = EBGames().get_link(game)
        self.assertTrue(len(links) > 0)
        pass

    def test_get_price(self):
        price = EBGames().get_price('https://www.ebgames.com.au/product/ps4/210347-mafia-iii')['current_price']
        self.assertTrue(price == 19.95, "Price Found Was " + str(price))
        pass      

    def test_update_when_link_in_db(self):
        game = Game.objects.get(id=1)
        Link.objects.create(store_id=EBGames().gamesguru_id,platform_id=1,game=game,price=10.00,initial_price=20.00,link='https://www.ebgames.com.au/product/ps4/244381-call-of-duty-modern-warfare')
        updated_links = EBGames().update_link(game)
        for updated_link in updated_links:
            link = Link.objects.get(id=updated_link.id)
            self.assertTrue(float(link.initial_price) == 99.95, 'Price found is ' + str(link.initial_price))
            self.assertTrue(link == updated_link)
            self.assertTrue(updated_link.price <= updated_link.initial_price)
        pass

    def test_update_link(self):
        game = Game.objects.get(id=1)
        updated_links = EBGames().update_link(game)
        for updated_link in updated_links:
            link = Link.objects.get(id=updated_link.id)
            self.assertTrue(link == updated_link)
            self.assertTrue(updated_link.price <= updated_link.initial_price)
        pass

    def test_update_database(self):
        EBGames().update_database()
        
        




