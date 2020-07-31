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

## 2.3 NYC Boroughs
I will use open source infromation that is published on site 
https://opendata.cityofnewyork.us/
GeoJSON data of boriughs is availabe under link 
https://data.cityofnewyork.us/api/geospatial/tqmj-j8zm?method=export&format=GeoJSON.
It contains borders for each borough border as "MultiPolygon" in GeoJSON format

## 2.4 NYC Neighborhoods
I will use open source information that is available via link
https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/ArcGIS/rest/services/NYC_Neighborhood_Tabulation_Areas/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson
The file contains data of NYC neighborhoods borders in GeoJSON format.

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