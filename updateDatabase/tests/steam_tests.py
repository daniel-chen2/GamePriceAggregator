import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.steam import Steam

class TestSteam(TestCase):
    @classmethod
    def setUpTestData(self):
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=23585)
        Game.objects.create(title='STAR WARS Jedi: Fallen Order', publish_date='2020-01-01', rawg_id=257201)
        Store.objects.create(title='Steam', code='ste')
        Platform.objects.create(id='1',title='Xbox-One', icon='fab fa-windows',code='xb1')
        Platform.objects.create(id='2',title='PlayStation 4', icon='fab fa-windows',code='ps4')
        Platform.objects.create(id='3',title='PC', icon='fab fa-windows',code='pc')
        store = Steam()
        pass

    def test_get_link(self):
        game = Game.objects.get(id=1)
        link = Steam().get_link(game)
        self.assertTrue(link.price == 89.95)
        pass

    def test_get_price(self):
        price = Steam().get_price('https://store.steampowered.com/app/391220/Rise_of_the_Tomb_Raider/')['current_price']
        self.assertTrue(price == 44.95, "Price Found Was " + str(price))
        price = Steam().get_price('https://store.steampowered.com/app/49520/Borderlands_2/')
        self.assertTrue(price == {'initial_price':25.95,'current_price':6.48}, "Price Found Was " + str(price))
        pass      

    def test_update_link(self):
        game = Game.objects.get(id=1)
        updated_link = Steam().update_link(game)
        link = Link.objects.get(id=updated_link.id)
        self.assertTrue(link == updated_link)
        self.assertTrue(updated_link.price <= updated_link.initial_price)
        pass
    
    def test_update_database(self):
        Steam().update_database()
        self.assertTrue(Link.objects.filter(game_id=1).count() > 0)
        self.assertTrue(Link.objects.filter(game_id=2).count() > 0)
        pass




