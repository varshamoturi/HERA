from data_gen import *
from google_req import *
import re
import requests
import pandas as pd

df=pd.read_csv('../data.csv')
user1='juancraig'
user2='kathleenrobbinsmd'
events,city=events_gen(user1,user2,df)
# Set your Google Maps API key here
api_key = "your-API-key"
listings=[]
#events=None


def extract_info(places_data):
    results = []
    pattern = r'href="([^"]+)"'
    for place in places_data:
        if 'photos' in place and 'html_attributions' in place['photos'][0]:
            name = place['name']
            formatted_address = place['formatted_address']
            icon_link = place['icon']

            attributions_link = re.findall(pattern, place['photos'][0]['html_attributions'][0])
            results.append({'name': name, 'formatted_address': formatted_address, 'icon_link': icon_link, 'attributions_link': attributions_link[0]})
    return results[:3]

def get_listings(api_key, events, city):
    if events is None:
        places_data=get_google_maps_listings(api_key,query="popular",location=city)
        listings.append({"popular activities":extract_info(places_data)})
    else:
        subheadings = re.findall(r'\d+\.\s*(.*?):', events)
        for i,query in enumerate(subheadings):
            places_data=get_google_maps_listings(api_key, query,city)
            listings.append({query:extract_info(places_data)})
    return listings



print(get_listings(api_key,events,city))