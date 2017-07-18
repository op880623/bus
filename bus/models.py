import re

class BusRoute(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.routeForward = []
        self.routeBackward = []


class BusStop(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.route = []
        self.latitude = 0
        self.longitude = 0

    def route_add(routeId):
        if isinstance(routeId, str):
            self.route.append(routeId)
