import requests 
import pandas as pd 
import numpy as np
import json
from pandas.io.json import json_normalize


# returns venues for selected categories
def getVenues(latitude, longitude, radius, categories):
    CLIENT_ID = '4VZ314V4U55K1LZOHHYQ5HFTNFBBKLZZAW3VZXYT4NRONR3G' # your Foursquare ID
    CLIENT_SECRET = 'B4ZPHNYHYEYI2UPAAPWYD5GMVGMHGSZ4K2JFNDKJFHTHQAGI' # your Foursquare Secret
    VERSION = '20180604'
    LIMIT = 50
    search_query = ''
    url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}&categoryId={}'.format(
        CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT, categories)
    return url

# Foursquare root category for food&drink shops
CATEGORY_FOOD_DRINK_SHOP = "4bf58dd8d48988d1f9941735"

# create neighborhoods DF
with open('data/input/NYC_Neighborhood.geojson', 'r') as neighborhoodsFile:
    #str = neighborhoodsFile.read()
    neighborhoodsJSON = json.load(neighborhoodsFile)
    neighborhoodsJSON = neighborhoodsJSON
