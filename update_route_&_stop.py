import os
import sys
import re
import shelve
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from bus.models import BusRoute, BusStop


print('\nupdate time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

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

# check id and name
    try:
        busRoute = routeData[routeId]
        if busRoute.name != routeName:
            print(busRoute.name + ' is renamed to ' + routeName + '.')
            busRoute.name = routeName
    except KeyError:
        busRoute = BusRoute(id=routeId, name=routeName)
        print(busRoute.name + ' is created.')

# check stops on route
    route_forward = []
    goStops = route.find(id='GoDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    for stop_raw_data in goStops:
        stop = extract_stop_info(stop_raw_data)
        route_forward.append(stop['id'])
    if busRoute.route_forward != route_forward:
        print(busRoute.name + " forward route is updated.")
        busRoute.route_forward = route_forward

    route_backward = []
    backStops = route.find(id='BackDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    for stop_raw_data in backStops:
        stop = extract_stop_info(stop_raw_data)
        route_backward.append(stop['id'])
    if busRoute.route_backward != route_backward:
        print(busRoute.name + " 's backward route is updated.")
        busRoute.route_backward = route_backward

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
