import os
import sys
import re
import shelve
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from bus.models import BusRoute, BusStop


logFile = open('update.log', 'a', encoding='utf8')

dbRoute = 'route'
dbStop = 'stop'

routeData = shelve.open(dbRoute)
stopData = shelve.open(dbStop)

def log(text):
    print(text)
    logFile.write(text + '\n')

def extract_stop_info(stop):
    index = str(stop.find(class_='auto-list-stationlist-number').string)
    name = str(stop.find(class_='auto-list-stationlist-place').string)
    id = stop.find(id='item_UniStopId')['value']
    latitude = stop.find(id='item_Latitude')['value']
    longitude = stop.find(id='item_Longitude')['value']
    return {'index': index, 'name': name, 'id': id, 'latitude': latitude, 'longitude': longitude}

def update_stops_on_route(stops):
    routeStops = []
    for stopRawData in stops:
        # stop = extract_stop_info(stopRawData)
        # routeStops.append(stop['id'])
        routeStops.append(stopRawData.find(id='item_UniStopId')['value'])
    return routeStops


# update routes' infomation
log('\nstart update route time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

# get all routes' id
# now get from file
# get from website in future
with open('routeid.txt', encoding='utf8') as sourceFile:
    idSource = sourceFile.read()

routeIds = re.findall("id: (\S+)", idSource)
# page = requests.get("https://ebus.gov.taipei/Query/BusRoute")
# get routeIds in page.text

# update every route
for routeId in routeIds:
    page = requests.get("https://ebus.gov.taipei/Route/StopsOfRoute?routeid=" + routeId)
    if page.status_code != 200:
        log('website of route ' + routeId + ' is broken or not found.')
        continue

    route = BeautifulSoup(page.text, "html.parser")

    routeName = str(route.find(class_='stationlist-title').string)

# check id and name
    try:
        busRoute = routeData[routeId]
        if busRoute.name != routeName:
            log(busRoute.name + ' is renamed to ' + routeName + '.')
            busRoute.name = routeName
    except KeyError:
        busRoute = BusRoute(id=routeId, name=routeName)
        log(busRoute.name + ' is created.')

# check stops on route
    stops = route.find(id='GoDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    routeStops = update_stops_on_route(stops)
    if busRoute.routeForward != routeStops:
        log(busRoute.name + ' forward route is updated.')
        busRoute.routeForward = routeStops

    stops = route.find(id='BackDirectionRoute').find_all('span', class_='auto-list auto-list-stationlist')
    routeStops = update_stops_on_route(stops)
    if busRoute.routeBackward != routeStops:
        log(busRoute.name + ' backward route is updated.')
        busRoute.routeBackward = routeStops

    routeData[busRoute.id] = busRoute
    print(busRoute.name + ' is updated.')

# structure of https://ebus.gov.taipei/Route/StopsOfRoute?routeid= routeId
# route <htnl>
# ├ goDirection <ul>
# │ └ goStops <li>
# └ backDirection <ul>
#   └ backStops <li>

log('\nfinish update route time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))



# update stops' infomation
log('\nstart update stop time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

# get all stops' id from all routes
stopIds = set()
for key in routeData.keys():
    stopIds = stopIds.union(set(routeData[key].routeForward))
    stopIds = stopIds.union(set(routeData[key].routeBackward))

# update every stop
for stopId in list(stopIds):
    page = requests.get("https://ebus.gov.taipei/Stop/RoutesOfStop?Stopid=" + stopId)
    if page.status_code != 200:
        log('website of stop ' + stopId + ' is broken or not found.')
        continue

# check id and name
    stopName = re.search('<p class="routelist-text">(.+)</p>', page.text).group(1)
    try:
        busStop = stopData[stopId]
        if busStop.name != stopName:
            log(busStop.name + ' is renamed to ' + stopName + '.')
            busStop.name = stopName
    except KeyError:
        busStop = BusStop(id=stopId, name=stopName)
        log(busStop.name + ' is created.')

# check route pass stop
    route = re.findall('"UniRouteId":"(\d+)"', page.text)
    if busStop.route != route:
        busStop.route = route
        log(busStop.name + ' route is updated.')

# check stop's location
    latitude = float(re.search('"Latitude":(\d+.\d+)', page.text).group(1))
    if busStop.latitude != latitude:
        busStop.latitude = latitude
        log(busStop.name + ' latitude is updated.')

    longitude = float(re.search('"Longitude":(\d+.\d+)', page.text).group(1))
    if busStop.longitude != longitude:
        busStop.longitude = longitude
        log(busStop.name + ' longitude is updated.')

    stopData[busStop.id] = busStop
    print(busStop.name + ' is updated.')

log('\nfinish update stop time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))



routeData.close()
stopData.close()
logFile.close()
