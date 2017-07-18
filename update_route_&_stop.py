import os
import sys
import re
import shelve

import requests
from bs4 import BeautifulSoup

from bus.models import BusRoute, BusStop

dbRoute = 'route'
dbStop = 'stop'

routeData = shelve.open(dbRoute)
stopData = shelve.open(dbStop)

def extract_stop_info(stop):
    index = str(stop.find(class_='auto-list-stationlist-number').string)
    name = str(stop.find(class_='auto-list-stationlist-place').string)
    id = stop.find(id='item_UniStopId')['value']
    latitude = stop.find(id='item_Latitude')['value']
    longitude = stop.find(id='item_Longitude')['value']
    return {'index': index, 'name': name, 'id': id, 'latitude': latitude, 'longitude': longitude}


# get all routes' id
# now get from file
# get from website in future
with open('routeid.txt', encoding='utf8') as sourceFile:
    idSource = sourceFile.read()

routeIds = re.findall("id: (\S+)", idSource)
# page = requests.get("https://ebus.gov.taipei/Query/BusRoute")
# get routeIds in page.text


# update routes' infomation
for routeId in routeIds:
    page = requests.get("https://ebus.gov.taipei/Route/StopsOfRoute?routeid=" + routeId)
    if page.status_code != 200:
        print('website of route ' + routeId + ' is broken or not found.')
        continue

    route = BeautifulSoup(page.text, "html.parser")

    routeName = str(route.find(class_='stationlist-title').string)
    busRoute = BusRoute(id=routeId, name=routeName)


    goStops = route.find(id='GoDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    for stop_raw_data in goStops:
        stop = extract_stop_info(stop_raw_data)
        busRoute.route_forward.append(stop['id'])

    backStops = route.find(id='BackDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    for stop_raw_data in backStops:
        stop = extract_stop_info(stop_raw_data)
        busRoute.route_backward.append(stop['id'])

    routeData[busRoute.id] = busRoute
    print(busRoute.name + ' is updated.')

# structure of https://ebus.gov.taipei/Route/StopsOfRoute?routeid= routeId
# route <htnl>
# ├ goDirection <ul>
# │ └ goStops <li>
# └ backDirection <ul>
#   └ backStops <li>




routeData.close()
stopData.close()
