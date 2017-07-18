import re
import shelve
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from bus.models import BusRoute, BusStop


logFile = open('update.log', 'a', encoding='utf8')

dbRoute = 'route'

routeData = shelve.open(dbRoute)

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

    routeName = re.search('<span class="stationlist-title">(.+)</span>', page.text).group(1)

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


routeData.close()
logFile.close()
