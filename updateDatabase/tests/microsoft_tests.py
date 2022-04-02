import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.microsoft import Microsoft

class TestMicrosoft(TestCase):
    @classmethod
    def setUpTestData(self):
        
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=23585)
        Game.objects.create(title='STAR WARS Jedi: Fallen Order', publish_date='2020-01-01', rawg_id=257201)
        Store.objects.create(title="Microsoft", code='mic')
        Platform.objects.create(id='1',title='Xbox-One', icon='fab fa-windows',code='xb1')
        Platform.objects.create(id='2',title='PlayStation 4', icon='fab fa-windows',code='ps4')
        Platform.objects.create(id='3',title='PC', icon='fab fa-windows',code='pc')
        store = Microsoft()
        pass

    def test_get_link(self):
        game = Game.objects.get(id=1)
        link = Microsoft().get_link(game)
        self.assertTrue(link.price == 99.95, "Price Found was " + str(link.price))
        pass

    def test_get_price(self):
        # price = PSN().get_price('https://store.playstation.com/en-au/product/EP0006-CUSA12529_00-RESPAWNSWBIRDDOG/')['current_price']
        # self.assertTrue(price == 89.95, "Price Found Was " + str(price))
        # price = PSN().get_price('https://store.playstation.com/en-us/product/UP0002-CUSA08829_00-CODMWTHEGAME0001')['current_price']
        # self.assertTrue(price == 74.96, "Price Found Was " + str(price))
        pass      

    def test_update_link(self):
        game = Game.objects.get(id=1)
        updated_link = Microsoft().update_link(game)
        link = Link.objects.get(id=updated_link.id)
        self.assertTrue(link == updated_link)
        self.assertTrue(updated_link.price <= updated_link.initial_price)
        pass
    
    def test_update_database(self):
        Microsoft().update_database()
        self.assertTrue(Link.objects.filter(game_id=1).count() > 0)
        pass




