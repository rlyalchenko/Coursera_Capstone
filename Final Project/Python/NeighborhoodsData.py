import pandas as pd 
import numpy as np
import json
from pandas.io.json import json_normalize
from shapely.geometry import shape, Point
import requests 

# returns venues for selected categories
def getVenuesCount(latitude, longitude, radius, categories, polygon):
    CLIENT_ID = '4VZ314V4U55K1LZOHHYQ5HFTNFBBKLZZAW3VZXYT4NRONR3G' # your Foursquare ID
    CLIENT_SECRET = 'B4ZPHNYHYEYI2UPAAPWYD5GMVGMHGSZ4K2JFNDKJFHTHQAGI' # your Foursquare Secret
    VERSION = '20180604'
    LIMIT = 50
    search_query = ''
    url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}&categoryId={}'.format(
        CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT, categories)
    results = requests.get(url).json()
    venues = results['response']['venues']
    count = 0
    for v in venues:
        point = Point(v["location"]["lng"], v["location"]["lat"])
        if(polygon.contains(point)):
            count = count + 1
    return count

# Foursquare root category for food&drink shops
CATEGORY_FOOD_DRINK_SHOP = "4bf58dd8d48988d1f9941735"

# creating neighborhoods DF
# load geojson file with NYC neighborhoods
with open('data/input/NYC_Neighborhood.geojson', 'r') as neighborhoodsFile:
    neighborhoodsJSON = json.load(neighborhoodsFile)


neighborhoods = neighborhoodsJSON["features"]

# DF with neighborhoods
neighColumns = ['Neighborhood', 'Borough', 'Latitude', 'Longitude', 'NumberOfStores', 'NumberOfCrimes', 'Area']
neighborhoodsDF = pd.DataFrame(columns = neighColumns)
neighborhoodsDF.set_index("Neighborhood", inplace = True)
neighborhoodsDict = {}

for (i, feature) in zip(range(1, len(neighborhoods) + 1), neighborhoods):
    name = feature["properties"]["NTAName"]
    borogh = feature["properties"]["BoroName"]
    area = feature["properties"]["Shape__Area"] / 10000000
    print("Processing neighborhood {} out of {}: {} ({})".format(i, len(neighborhoods), name, borogh))
    
    # fill neighborhood dictionary
    polygon = shape(feature["geometry"])
    neighborhoodsDict[name] = polygon
    
    # get venues number
    venuesCount = getVenuesCount(polygon.boundary.centroid.y, polygon.boundary.centroid.x, 2000, CATEGORY_FOOD_DRINK_SHOP, polygon)

    # add main neighborhood data
    neighborhoodsDF.loc[name] = [borogh, 
                                polygon.boundary.centroid.y, 
                                polygon.boundary.centroid.x, 
                                venuesCount,
                                0,
                                area]


#neighborhoodsDF.to_csv("data/output/neighboors.csv")

# add crime data
crimeDF = pd.read_csv("data/input/NYPD_Complaint_Data_Current__Year_To_Date_.csv", )
crimeDF = crimeDF[["Latitude", "Longitude"]]
crimeDF.astype("float64")
i = 0
for row in crimeDF.itertuples():
    point = Point(row.Longitude, row.Latitude)
    i = i + 1
    if(i % 5000 == 0):
        print("Crimes pecessed: ", i)
    for neig in neighborhoodsDict.keys():
        if(neighborhoodsDict[neig].contains(point)):
            neighborhoodsDF.at[neig, "NumberOfCrimes"] = neighborhoodsDF.loc[neig]["NumberOfCrimes"] + 1
            #print("crime in " + neig)
            break

neighborhoodsDF.to_csv("data/output/neighboors.csv")
