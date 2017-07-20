import re
import shelve


dbRoute = 'route'
dbStop = 'stop'

class BusRoute(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.routeForward = []
        self.routeBackward = []

    def stops_after_specific_stop(self, stopId):
        if stopId in self.routeForward:
            return set(self.routeForward[self.routeForward.index(stopId)+1:])
        elif stopId in self.routeBackward:
            return set(self.routeBackward[self.routeBackward.index(stopId)+1:])
        else:
            raise KeyError(stopId + ' is not in route ' + self.id)

    def stops_before_specific_stop(self, stopId):
        if stopId in self.routeForward:
            return set(self.routeForward[:self.routeForward.index(stopId)])
        elif stopId in self.routeBackward:
            return set(self.routeBackward[:self.routeBackward.index(stopId)])
        else:
            raise KeyError(stopId + ' is not in route ' + self.id)


class BusStop(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.route = set()
        self.latitude = 0
        self.longitude = 0

    def connected_stops(self, dbRoute=dbRoute):
        connectedStops = set()
        for route in self.route:
            with shelve.open(dbRoute) as routeData:
                if self.id in routeData[route].routeForward:
                    connectedStops = connectedStops.union(set(routeData[route].routeForward))
                if self.id in routeData[route].routeBackward:
                    connectedStops = connectedStops.union(set(routeData[route].routeBackward))
        return connectedStops.difference({self.id})
