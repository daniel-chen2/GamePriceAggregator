import unittest
from django.test import TestCase
from games.models import Game,Link, Store, Platform
from updateDatabase.stores.cj import Fanatical, GMG, CD_Keys, GamersGate,Kinguin, CJ

class TestCJ(TestCase):
    @classmethod
    def setUpTestData(self):
        
        Game.objects.create(title='Mafia III', publish_date='2020-01-01', rawg_id=1169)
        Game.objects.create(title='Far Cry 5', publish_date='2020-01-01', rawg_id=1169)
        Game.objects.create(title="Assassin's Creed Odyssey", publish_date='2020-01-01', rawg_id=1169)
        Store.objects.create(title='Fanatical', code='fan')
        Store.objects.create(title='GMG', code='gmg')
        Store.objects.create(title='gamersgate', code='gat')
        Store.objects.create(title='Kinguin', code='kin')
        Platform.objects.create(id='3',title='PC', icon='fab fa-windows',code='pc')
        self.Stores_to_test = [Fanatical(), GMG(), GamersGate(), Kinguin()]

    def test_get_link(self):
        game = Game.objects.get(id=1)
        for store in self.Stores_to_test:
            self.assertTrue(store.get_link(game) is not None)

    def test_get_price_from_link(self):
        price = Fanatical().get_price_from_link('https://www.fanatical.com/en/game/planet-coaster')
        self.assertTrue(price == {'initial_price':64.95, 'current_price':15.58}, 'Price found : ' + str(price))

        price = GMG().get_price_from_link('https://www.greenmangaming.com/games/playerunknowns-battlegrounds/')
        self.assertTrue(price == {'initial_price':42.95, 'current_price':21.48}, 'Price found : ' + str(price))

        price = GamersGate().get_price_from_link('https://www.gamersgate.com/DD-DEVIL-MAY-CRY-5-REL/devil-may-cry-5')
        price = Kinguin().get_price_from_link('https://www.kinguin.net/category/71374/doom-eternal-eu-bethesda-cd-key')

    def test_get_price(self):
        # Tests Get Link Method for Fanatical Store
        game = Game.objects.get(id=1)
        ac = Game.objects.get(id=3)
        found_price = Fanatical().get_price(game)
        ac_price = Fanatical().get_price(ac)
        self.assertTrue(found_price == {'initial_price': 54.49, 'current_price': 54.49}, "Price Found Was " + repr(found_price))    
        self.assertTrue(ac_price == {'initial_price': 89.95, 'current_price': 26.98}, "Price Found Was " + repr(ac_price))

        # Test GMG
        game = Game.objects.get(id=1)
        found_price = GMG().get_price(game)
        self.assertTrue(found_price['initial_price'] == 69.95, "Price Found Was " + repr(found_price))       

    def test_update_link(self):
        # Tests Get Link Method for Fanatical Store
        game = Game.objects.get(id=1)
        for store in self.Stores_to_test:
            get_link = store.get_link(game)
            updated_link = store.update_link(game)
            get_link.id = updated_link.id
            self.assertTrue(get_link == updated_link)
            self.assertTrue(updated_link.price <= updated_link.initial_price)

        # Fanatical 
        Link.objects.create(store_id=Fanatical().gamesguru_id,platform_id=3,game=game,price=10.00,initial_price=20.00,link='https://www.fanatical.com/en/bundle/sanctuary-bundle')
        game = Game.objects.get(id=1)
        get_link = Fanatical().get_link(game)
        updated_link = Fanatical().update_link(game)
        get_link.id = updated_link.id
        self.assertTrue(get_link == updated_link)
        self.assertTrue(updated_link.price <= updated_link.initial_price)
        
        




