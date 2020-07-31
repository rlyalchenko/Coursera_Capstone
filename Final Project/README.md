# 1. Introduction
## 1.1 Background
New York City (NYC) is the most populous city in the United States. With an estimated 
2019 population of 8,336,817 distributed over about 302.6 square miles (784 km2), 
New York City is also the most densely populated major city in the United States.

New York City is composed of five boroughs: Brooklyn, Queens, Manhattan, the Bronx, 
and Staten Island.

## 1.2 Business Problem
Business owners should prefer areas where population density is higher, but 
offer level of similar service is low.

I will try to determine areas where new grocery store. Good location criteria are:
1. High density of population in borough. 
1. Absense of grocery stores in area.
1. Low criminal.

The main stakeholders of my research are investors, who want to start new business or
extend their current one.

# 2 Data

## 2.1 Requirements

Problem research requires following type of information:
1. NYC boroughs:
    - Basic information
        - Name
        - Population
        - Square
    - Shape in GeoJSON format
1. List of venues
1. Official crime information for NYC

## 2.2 Foursquare API
I will utilize this data source to export information about venues in borders of each 
NYC borough.

API has limitations for API call and number of results. I will split requests into 
small portions and will join it locally.

API provides a lot of information about venues and includes:
- Location
- Latitude
- Longitude
- Categories

## 2.3 NYC Neighborhhods
I will use open source infromation that is published on site 
https://opendata.cityofnewyork.us/
GeoJSON data of neighborhhods is availabe under link 
https://data.cityofnewyork.us/api/geospatial/tqmj-j8zm?method=export&format=GeoJSON.
It contains borders for each neighborhhods border as "MultiPolygon" in GeoJSON format

## 2.4 NYC Boroghs
I will use open source information that is available via link
https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/ArcGIS/rest/services/NYC_Neighborhood_Tabulation_Areas/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson
The file contains data of NYC Boroghs borders in GeoJSON format.

## 2.5 Crime dataset
This dataset includes all valid felony, misdemeanor, and violation crimes reported 
to the New York City Police Department (NYPD) for all complete quarters 
so far this year (2019):
https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Current-Year-To-Date-/5uac-w243

Dataset includes:
- BORO_NM: The name of the borough in which the incident occurred
- LAW_CAT_CD: Level of offense: felony, misdemeanor, violation
- Latitude: Midblock Latitude coordinate for Global Coordinate System
- Longitude: Midblock Longitude coordinate for Global Coordinate System

# 3 Data Cleaning and preparation
## 3.1 Preparing clean neighborhood data
### Exteral libraries
The following Python libraries will be used in the project:
- numpy
- pandas
- requests
- folium
- shapely.geometry
- json
### Working with Foursquare API 
New function is required to make work with Foursquare API easier. 
It returns number of venues of specific type, that are located inside polygon with 
complex border.
````python
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
```` 
### Creating the main dataset
Main dataset is mainly built out of GeoJSON data (NYC Neighborhhods).
I convert it into pandas Dataframe and add information about amount of venues in
each neighborhood.
Them I add crime data for each row in dataframe.
````python
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
````
### Resulted dataset
![Main dataset](https://github.com/rlyalchenko/Coursera_Capstone/blob/master/Final%20Project/Report/Images/dataset_main.png?raw=true)

# 4 Methodology
We are going to identify neighboorhoods in NYC that lack groccery facilities.
We are interesred in identifying areas, where density of grocery stores is low 
and number of crimes is also low.

During the first step we prepared clean data of neighborhoods and their parameters.

During the second step we will use K-Means clustering method to split neighborhoods
into several groups and then we will identify the most interesting areas for new 
stores.

# 5 Analysis
We work with normilized values for neighborhoods. In this case we need not actual 
numnber of existing stores in each area, but we need density.
Adding additional information in dataset: crime density and stores density
`````
neighborhoodsDF["StoreDensity"] = neighborhoodsDF["NumberOfStores"] / neighborhoodsDF["Area"]
neighborhoodsDF["CrimeDensity"] = neighborhoodsDF["NumberOfCrimes"] / neighborhoodsDF["Area"]
`````
![Main dataset](https://github.com/rlyalchenko/Coursera_Capstone/blob/master/Final%20Project/Report/Images/dataset_main_norm.png?raw=true)

The core of our analysis is K-Means clustering method. We will use it to split all
neighboors into several groups with similar features.
``````
clusteringDF = neighborhoodsDF[["StoreDensity", "CrimeDensity"]]
clusteringDF.head()
kclusters = 5
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(clusteringDF)
neighborhoodsDF.insert(0, "ClusterLabel", kmeans.labels_)
``````
![Main dataset](https://github.com/rlyalchenko/Coursera_Capstone/blob/master/Final%20Project/Report/Images/dataset_main_clustered.png?raw=true)
We can now see, that  most interesting areas for us are located in clusters with labels 1 and 3.
We add Rank column, that will show how interesting areas are for out investors.
``````
neighborhoodsDF["Rank"] = 0
neighborhoodsDF.loc[neighborhoodsDF.ClusterLabel == 3, "Rank"] = 5
neighborhoodsDF.loc[neighborhoodsDF.ClusterLabel == 1, "Rank"] = 4
neighborhoodsDF.loc[neighborhoodsDF.ClusterLabel == 0, "Rank"] = 3
neighborhoodsDF.loc[neighborhoodsDF.ClusterLabel == 2, "Rank"] = 2
neighborhoodsDF.loc[neighborhoodsDF.ClusterLabel == 4, "Rank"] = 1
neighborhoodsDF.head()
``````
![Main dataset](https://github.com/rlyalchenko/Coursera_Capstone/blob/master/Final%20Project/Report/Images/dataset_main_ranked.png?raw=true)
# 6 Visualisation
For visualisation purposes we will be using folium library. 

We are interested in showing on map, where potentially interesting areas are located.
```
geo = r'NYC_Neighborhood.geojson'
nyc_map = folium.Map(location=[40.705693, -73.929600], zoom_start=10)

nyc_map.choropleth(
    geo_data=geo,
    data=neighborhoodsDF,
    columns=['Neighborhood', 'Rank'],
    key_on='feature.properties.NTAName',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Grocery capabilities'
)
```
![Main dataset](https://github.com/rlyalchenko/Coursera_Capstone/blob/master/Final%20Project/Report/Images/Clustered.png?raw=true)
# 7 Results and Discussion
During my research I used open source data from official resources. I used formal data science methonds to clean and process data. All results of my work are available on GitHub. 

The analysis shows, that density of groccery stores in NYC vary a lot. There are a lot of areas, that lack such kind of facility.
In the research I did not focus on a certain part of city, but wanted to make high level analysis, that can be used as first step in deepere reaserches.

I used visualization abilities to show potentially interesting areas on map. This will help investors to find new opportunities in areas, that they are familiar with. There are a lot of important information outside formal figures, that should be considered when making a desicion.
# 8 Conclusion
The target of my project was to identify the optimal places for grocery stores in NYC. My reaserch was based on existing facilities density and crime in neighborhoods.

The results may be interesting for investors who are going to create a new business in NYC.