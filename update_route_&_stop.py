import os
import sys
import re
import shelve

import requests
from bs4 import BeautifulSoup

from bus.models import BusRoute, BusStop



def extract_stop_info(stop):
    index = stop.find(class_='auto-list-stationlist-number').string
    name = stop.find(class_='auto-list-stationlist-place').string
    id = stop.find(id='item_UniStopId')['value']
    latitude = stop.find(id='item_Latitude')['value']
    longitude = stop.find(id='item_Longitude')['value']
    return {'index': index, 'name': name, 'id': id, 'latitude': latitude, 'longitude': longitude}


# get all routes' id
# now get from file
# get from website in future
with open('routeid.txt', encoding='utf8') as sourceFile:
    idSource = sourceFile.read()

routeIds = re.findall("id: (\d+)", idSource)
# page = requests.get("https://ebus.gov.taipei/Query/BusRoute")
# get routeIds in page.text


# update routes' infomation
for routeId in routeIds[:3]:
    page = requests.get("https://ebus.gov.taipei/Route/StopsOfRoute?routeid=" + routeId)
    if page.status_code != 200:
        print('website of route ' + routeId + 'is broken or not found.')
        continue

    route = BeautifulSoup(page.text, "html.parser")

    routeName = route.find(class_='stationlist-title').string
    print(routeName)


    goDirection = route.find(id='GoDirectionRoute')
    goStops = goDirection.find_all('span', class_='auto-list auto-list-stationlist')
    print('去程')
    for stop_raw_data in goStops:
        stop = extract_stop_info(stop_raw_data)
        print(stop['index'], stop['name'], stop['id'], stop['latitude'], stop['longitude'])
    print('\n')


    backDirection = route.find(id='BackDirectionRoute')
    backStops = backDirection.find_all('span', class_='auto-list auto-list-stationlist')
    print('回程')
    for stop_raw_data in backStops:
        stop = extract_stop_info(stop_raw_data)
        print(stop['index'], stop['name'], stop['id'], stop['latitude'], stop['longitude'])
    print('\n')

# structure of https://ebus.gov.taipei/Route/StopsOfRoute?routeid= routeId
# route <htnl>
# ├ goDirection <ul>
# │ └ goStops <li>
# └ backDirection <ul>
#   └ backStops <li>
