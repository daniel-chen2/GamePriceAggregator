import numpy as np
import time
import requests
import re
from django.db.models import Q
from games.models import Store, Platform
from django.utils import timezone
from datetime import datetime, timedelta
import re
from lxml.html import fromstring
timezone.localtime(timezone.now())

# change this to choose how long after last update to update
minutes = 30
update_after = timezone.now()-timedelta(minutes=minutes)

games_guru_stores = {
    'steam':5,
    'ebgames': 2,
    'psn': 3,
    'fanatical':4,
    'gmg': 6,
    'kinguin': 7,
    'microsoft': 8,
    'cdkeys':9,
    'gamersgate':10,
    'gamesmen':11,
    'amazon':1
}

games_guru_platforms = {
    'xb1': 1,
    'ps4':2,
    'pc':3
}

def get_store(code):
    return Store.objects.get(code=code) 

def get_platform(code):
    return Platform.objects.get(code=code)

def get_random_ua():
    random_ua = ''
    ua_file = 'ua_file.txt'
    list=[
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.540.0 Safari/534.10'
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5'
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2'
    'Mozilla/5.0 (Windows; U; Windows NT 5.0; es-ES; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3'
    ]
    return np.random.choice(list)

def get_random_referral():
    ua_file = 'ua_file.txt'
    list=[
    'google.com',
    'google.com.nz',
    'google.com.au',
    'rapidapi.com',
    'https://psdeals.net/',
    'https://store.playstation.com/',
    ]
    return np.random.choice(list)

def get_random_headers():
    return {'user-agent': get_random_ua(),'referer': get_random_referral()} 

def random_delay():
    delays = [1,2,3,4]
    delay = np.random.choice(delays)
    time.sleep(delay)

# Misc
def remove_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# Checks if link returns successful code using random headers
# Returns successful if so
def checkLink(url, parameters={},headers=get_random_headers()):
    try:
        response = requests.request("GET", url, params = parameters, headers=headers)
        return response
    except Exception as e:
        print(e)
        print('Link Invalid')
    return None

# AUS to US
def exchange_price(amount, in_currency, out_currency):
    response = requests.request("GET", 'https://api.exchangeratesapi.io/latest').json()['rates']
    response['EUR']=1
    rate = response[in_currency]/response[out_currency]
    return round(amount*rate, 2)
    
def convert_to_aud(price, country):
    if country == 'US' or country == 'USD':
        return exchange_price(price,'AUD','USD')
    if country == 'EUR':
        return exchange_price(price,'AUD','EUR')
    elif country == 'AUD' or country == 'AU' or 'AUS':
        return price
    pass

def getPrice(final_price, initial_price=None, in_cents=False, country="AUD"):
    prices = {}
    formatted_current_price, formatted_initial_price = format_price_to_float(final_price), format_price_to_float(initial_price) 
    prices['current_price'] = formatted_initial_price if formatted_current_price is None else formatted_current_price
    prices['initial_price'] = formatted_current_price if formatted_initial_price is None else formatted_initial_price
    if in_cents: 
        try:
            prices['initial_price'] /= 100; prices['current_price'] /= 100
        except:
            pass
    prices['initial_price'], prices['current_price'] = convert_to_aud(prices['initial_price'], country), convert_to_aud(prices['current_price'], country)
    return prices

def format_price_to_float(price):
    if type(price) == str:
        price = price.replace('$','')
        price = re.sub('[^0-9.]','', price)
    if type(price) != float:
        try:
            price = float(price)
        except Exception as e:
            price = None
    return price