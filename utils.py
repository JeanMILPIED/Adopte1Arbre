import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from PIL import Image
from csv import writer
from datetime import datetime, timedelta
from collections import defaultdict
import datetime
from streamlit_folium import folium_static
import folium
import requests
import json
import flexpolyline as fp
import qrcode
from qrcode.image.styledpil import StyledPilImage
import math

if not hasattr(Image, 'Resampling'):  # Pillow<9.0
    Image.Resampling = Image


def get_gps_and_insee(the_adress):
    '''
    get GPS and INSEE code from adress
    '''
    accept = 'application/json'
    content_type = 'application/json'

    # get info now
    serviceUrl = "https://api-adresse.data.gouv.fr/search/?q=" + the_adress + '&limit=' + str(1)
    r = requests.get(serviceUrl, headers={'Accept': accept, 'Content-Type': content_type})
    print(r.status_code)
    dataJSON_now = json.loads(r.text)
    return dataJSON_now

def GPS_from_Adress(the_adress):
    json_insee=get_gps_and_insee(the_adress)
    try:
        gps=json_insee['features'][0]['geometry']['coordinates']
        gps_ok=[gps[1],gps[0]]
    except:
        print('no gps')
        gps_ok=[]
    try:
        finalAdress=json_insee['features'][0]['properties']['label']
    except:
        print('no Adress')
        finalAdress='not found'
    return finalAdress, gps_ok

def distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    print(lat1, lon1, lat2, lon2)
    lat1=float(lat1)
    lon1=float(lon1)
    lat2=float(lat2)
    lon2=float(lon2)
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return round(d,2)

def distance_osrm(place_1,place_2):
    '''
    computes distance and time from gps positions of 2 places inputs
    based on a call to osrm API
    '''
    lat1 = place_1[1]
    lon1 = place_1[0]
    lat2 = place_2[1]
    lon2 = place_2[0]
    #use of OpenStreetMap API
    r = requests.get(f"http://router.project-osrm.org/route/v1/driving/{lat1},{lon1};{lat2},{lon2}?overview=false""")
    routes = json.loads(r.content)
    try:
        distance_km=round(float(routes['routes'][0]['distance'])/1000,2)
        time_s=float(routes['routes'][0]['duration'])
    except:
        distance_km='not_found'
        time_s='not_found'
    return distance_km,time_s,routes

def create_map_opti(df, gps_chantier, zoom100=False):
    m = folium.Map()
    for i in range(df.shape[0]):
        folium.Marker([df["lat"].iloc[i], df["lon"].iloc[i]],  popup=("arbre"), icon = folium.Icon(color='green',icon='plus')).add_to(m)
    if gps_chantier!=[]:
        folium.Marker([gps_chantier[0], gps_chantier[1]], popup=('votre position'),
                      icon=folium.Icon(color='black', icon='plus')).add_to(m)
    if zoom100:
        df_100=df[df.distance_au_chantier<100]
        sw = min(df_100[['lat', 'lon']].min().values.tolist(),[gps_chantier[0], gps_chantier[1]])
        ne = max(df_100[['lat', 'lon']].max().values.tolist(),[gps_chantier[0], gps_chantier[1]])
    else:
        sw = min(df[['lat', 'lon']].min().values.tolist(),[gps_chantier[0], gps_chantier[1]])
        ne = max(df[['lat', 'lon']].max().values.tolist(),[gps_chantier[0], gps_chantier[1]])
    m.fit_bounds([sw, ne])
    folium.Marker(location=[ne[0],(sw[1]+ne[1])/2],
              icon=folium.DivIcon(html='<div style="font-size: 10pt; color:black; width: 150px; font-family:verdana;background-color: white; opacity:0.8";display:flex;>{}</div>'.format('Adopte1Arbre'),
                                  class_name="mapText")).add_to(m)
    return m

def airQuality_extract(list_coord):
    '''
    extracts air Quality from open weather call
    '''
    apikey = 'b8d51e7aad387e9dd0906a1eeab034d5'

    # get info now
    serviceUrl = "http://api.openweathermap.org/data/2.5/air_pollution?"
    url = serviceUrl + urllib.parse.urlencode(
        {'lat': list_coord[0], 'lon': list_coord[1], 'APPID': apikey, 'units': 'metric'})
    urlRead = urllib.request.urlopen(url).read()
    dataJSON_now = json.loads(urlRead)
    output_now = extract_airquality_info(dataJSON_now)

    return output_now

def extract_airquality_info(airqual_json):
    '''
    extracts the main meteo info from the API call return
    '''
    output = defaultdict(lambda: 'not available')
    try:
        output['AQI'] = airqual_json["list"][0]["main"]["aqi"]
    except:
        output['AQI'] = 'NA'
    try:
        output['CO'] = airqual_json["list"][0]['components']["co"]
    except:
        output['CO'] = 'NA'
    try:
        output['NO'] = airqual_json["list"][0]['components']["no"]
    except:
        output['NO'] = 'NA'
    try:
        output['NO2'] = airqual_json["list"][0]['components']["no2"]
    except:
        output['NO2'] = 'NA'
    try:
        output['O3'] = airqual_json["list"][0]['components']["o3"]
    except:
        output['O3'] = 'NA'
    try:
        output['SO2'] = airqual_json["list"][0]['components']["so2"]
    except:
        output['SO2'] = 'NA'
    try:
        output['PM2_5'] = airqual_json["list"][0]['components']["pm2_5"]
    except:
        output['PM2_5'] = 'NA'
    try:
        output['PM10'] = airqual_json["list"][0]['components']["pm10"]
    except:
        output['PM10'] = 'NA'
    try:
        output['NH3'] = airqual_json["list"][0]['components']["nh3"]
    except:
        output['NH3'] = 'NA'
    return output

def airQuality_extract_airparif(code_INSEE_place):
    '''
    extracts air quality from INSEE code
    '''
    apikey = 'c8d6caea-f328-7312-2bec-d4c9302a0a2e'
    accept = 'application/json'
    content_type = 'application/json'
    params = {'insee': code_INSEE_place}

    # get info now
    serviceUrl = "https://api.airparif.asso.fr/indices/prevision/commune"
    r = requests.get(serviceUrl, params=params,
                     headers={'Accept': accept, 'Content-Type': content_type, 'X-Api-Key': apikey})
    print(r.status_code)
    dataJSON_now = json.loads(r.text)
    dataJSON_now_clean_0=dataJSON_now[code_INSEE_place][0]
    try:
        dataJSON_now_clean_1 = dataJSON_now[code_INSEE_place][1]
    except:
        dataJSON_now_clean_1={}
    return dataJSON_now_clean_0, dataJSON_now_clean_1

def extract_weather_info(weath_json):
    '''
    extracts the main meteo info from the API call return
    '''
    output = defaultdict(lambda: 'not available')
    try:
        output['weather'] = weath_json["weather"][0]["description"]
    except:
        output['weather'] = 'NA'
    try:
        output['temperature_degC'] = weath_json["main"]["temp"]
    except:
        output['temperature_degC'] = 'NA'
    try:
        output['humidity_%'] = weath_json["main"]["humidity"]
    except:
        output['humidity_%'] = 'NA'
    try:
        output['wind'] = weath_json["wind"]["speed"]
    except:
        output['wind'] = 'NA'
    try:
        output['visibility_m'] = weath_json["visibility"]
    except:
        output['visibility_m'] = 'NA'
    try:
        output['rain_1h_mm'] = weath_json["rain"]["1h"]
    except:
        output['rain_1h_mm'] = 'NA'
    try:
        output['timestamp'] = weath_json["dt"] + weath_json["timezone"]
    except:
        output['timestamp'] = 'NA'
    return output

def weather_extract(list_coord):
    '''
    extracts meteo info from openweather API call
    '''
    apikey = 'b8d51e7aad387e9dd0906a1eeab034d5'
    serviceUrl = "http://api.openweathermap.org/data/2.5/weather?"
    url = serviceUrl + urllib.parse.urlencode(
        {'lat': list_coord[0], 'lon': list_coord[1], 'APPID': apikey, 'units': 'metric'})
    urlRead = urllib.request.urlopen(url).read()
    dataJSON = json.loads(urlRead)
    output = extract_weather_info(dataJSON)
    return output

def meteoPrediction_openWeather(list_coord, when=24):
    '''
    extracts air Quality from open weather call
    '''
    apikey = 'b8d51e7aad387e9dd0906a1eeab034d5'

    # get info now
    serviceUrl = "http://api.openweathermap.org/data/2.5/forecast?"
    url = serviceUrl + urllib.parse.urlencode(
        {'lat': list_coord[0], 'lon': list_coord[1], 'appid': apikey, 'units': 'metric'})
    urlRead = urllib.request.urlopen(url).read()
    dataJSON_all = json.loads(urlRead)
    dataJSON_pred = dataJSON_all['list'][int(when / 3)]
    output = extract_weather_info(dataJSON_pred)
    return output, dataJSON_all

def Air_quality_from_Adress(the_adress, the_when=24):
    json_insee=get_gps_and_insee(the_adress)
    try:
        gps=json_insee['features'][0]['geometry']['coordinates']
        gps_ok=[gps[1],gps[0]]
    except:
        print('no gps')
        return
    try:
        city=json_insee['features'][0]['properties']['citycode']
    except:
        print('no citycode')
        return
    try:
        finalAdress=json_insee['features'][0]['properties']['label']
    except:
        print('no Adress')
        return
    try:
        json_airQuality_airparif_0, json_airQuality_airparif_1=airQuality_extract_airparif(city)
    except:
        json_airQuality_airparif_0, json_airQuality_airparif_1={},{}
        st.write("pas d'accès aux data airparif")
    try:
        json_airQuality_openWeather=airQuality_extract(gps_ok)
    except:
        json_airQuality_openWeather={}
        st.write("pas d'accès aux data airQuality openWeather")
    try:
        json_weather_openWeather=weather_extract(gps_ok)
        json_weather_pred_openWeather, json_pred_all=meteoPrediction_openWeather(gps_ok, when=the_when)
    except:
        json_weather_openWeather={}
        json_weather_pred_openWeather, json_pred_all={},{}
        st.write("pas d'accès aux data openWeather")
    return finalAdress, json_weather_openWeather, json_airQuality_airparif_0, json_airQuality_airparif_1,json_airQuality_openWeather, json_weather_pred_openWeather, json_pred_all
