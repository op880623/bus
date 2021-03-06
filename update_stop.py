import re
import shelve
from datetime import datetime

import requests

from bus.models import BusRoute, BusStop


logFile = open('update.log', 'a', encoding='utf8')

dbRoute = 'db/route'
dbStop = 'db/stop'

routeData = shelve.open(dbRoute)
stopData = shelve.open(dbStop)

def log(text):
    print(text)
    logFile.write(text + '\n')

# update stops' infomation
log('start update stop time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

# get all stops' id from all routes
stopIds = set()
for key in routeData.keys():
    stopIds = stopIds.union(set(routeData[key].routeForward))
    stopIds = stopIds.union(set(routeData[key].routeBackward))

routeData.close()

# update every stop
for stopId in list(stopIds):
    page = requests.get("https://ebus.gov.taipei/Stop/RoutesOfStop?Stopid=" + stopId)
    if page.status_code != 200 or page.url == "https://ebus.gov.taipei/Query/BusRoute":
        log('website of stop ' + stopId + ' is broken or not found.')
        continue

# check id and name
    try:
        stopName = re.search('<p class="routelist-text">(.+)</p>', page.text).group(1)
    except:
        log('stop ' + stopId + ' name has problem.\n')
        continue
    try:
        busStop = stopData[stopId]
        if busStop.name != stopName:
            log(busStop.name + ' is renamed to ' + stopName + '.')
            busStop.name = stopName
    except KeyError:
        busStop = BusStop(id=stopId, name=stopName)
        log(busStop.name + ' is created.')

# check route pass stop
    route = set(re.findall('"UniRouteId":"(\d+)"', page.text))
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

log('finish update stop time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + '\n')


stopData.close()
logFile.close()
