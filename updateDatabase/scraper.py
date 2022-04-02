import requests
from updateDatabase import config
import json
import urllib.parse 

def get_request_from_scraper_api(url_to_scrape, country_code = "au"):
  prompt_api_url = "https://api.promptapi.com/scraper?url=" + urllib.parse.quote(url_to_scrape) + "&country=" + country_code
  headers= {
    "apikey": "kOaLDd3LRiNPzkqDyFWp0yQStMxPzQ0V"
  }
  number_of_attempts = 3
  for attempt in range(number_of_attempts):
    response = config.checkLink(prompt_api_url, headers=headers)
    if(response.ok):
      response.data = json.loads(response.text)["data"]
      return response
  return response


