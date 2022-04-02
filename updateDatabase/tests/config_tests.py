import updateDatabase.config as c 
from django.test import TestCase

class testConfig(TestCase):
    def test_get_price(self):
        print(c.getPrice(final_price=1.00,initial_price=1.00))
        self.assertTrue(c.getPrice(final_price=1.00,initial_price=1.00) == {'initial_price':1.00,'current_price':1.00})
        self.assertTrue(c.getPrice(final_price=1.00,initial_price=None) == {'initial_price':1.00,'current_price':1.00})
        self.assertTrue(c.getPrice(final_price=None,initial_price=1.00) == {'initial_price':1.00,'current_price':1.00})
        self.assertTrue(c.getPrice(final_price=1.00,initial_price=1.50) == {'initial_price':1.50,'current_price':1.00})
        self.assertTrue(c.getPrice(final_price='ascsac',initial_price=1.50) == {'initial_price':1.50,'current_price':1.50})
        self.assertTrue(c.getPrice(final_price=1.5,initial_price='asdasdsad') == {'initial_price':1.50,'current_price':1.50})