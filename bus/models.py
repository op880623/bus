import re

class BusRoute(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.route_forward = []
        self.route_backward = []


class BusStop(object):


    def __init__(self, id, name=''):
        self.id = id
        self.name = name
        self.route = []

    def route_add(routeId):
        if isinstance(routeId, str):
            self.route.append(routeId)
