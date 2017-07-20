import unittest
import shelve

from bus.models import BusRoute, BusStop

dbRoute = 'route_test'
dbStop = 'stop_test'

class TestBusRoute(unittest.TestCase):
    '''
    make sure BusRoute object report the error when unsuitable value is assigned to BusRoute object
    '''

    def setUp(self):
        self.route = BusRoute(id='0', name='r0')
        self.route.routeForward = ['001', '002', '003']
        self.route.routeBackward = ['103', '102', '101']
        # 001       002         003
        # ---->---->---->---->---->---->
        # <----<----<----<----<----<----
        # 101       102         103

    def tearDown(self):
        self.route = None

    def test_stops_after_specific_stop(self):
        self.assertSetEqual(self.route.stops_after_specific_stop('001'), {'002', '003'})
        self.assertSetEqual(self.route.stops_after_specific_stop('002'), {'003'})
        self.assertSetEqual(self.route.stops_after_specific_stop('003'), set())

        self.assertSetEqual(self.route.stops_after_specific_stop('101'), set())
        self.assertSetEqual(self.route.stops_after_specific_stop('102'), {'101'})
        self.assertSetEqual(self.route.stops_after_specific_stop('103'), {'102', '101'})

    def test_stops_before_specific_stop(self):
        self.assertSetEqual(self.route.stops_before_specific_stop('001'), set())
        self.assertSetEqual(self.route.stops_before_specific_stop('002'), {'001'})
        self.assertSetEqual(self.route.stops_before_specific_stop('003'), {'001', '002'})

        self.assertSetEqual(self.route.stops_before_specific_stop('101'), {'103', '102'})
        self.assertSetEqual(self.route.stops_before_specific_stop('102'), {'103'})
        self.assertSetEqual(self.route.stops_before_specific_stop('103'), set())


class TestBusStop(unittest.TestCase):
    '''
    make sure BusStop object report the error when unsuitable value is assigned to BusStop object
    '''

    def setUp(self):
        self.route0 = BusRoute(id='0', name='r0')
        self.route0.routeForward = ['001', '002', '003']
        self.route0.routeBackward = ['103', '102', '101']
        self.route1 = BusRoute(id='1', name='r1')
        self.route1.routeForward = ['003', '004', '005']
        self.route1.routeBackward = ['105', '104', '103']
        with shelve.open(dbRoute) as routeData:
            routeData['0'] = self.route0
            routeData['1'] = self.route1
        self.stop103 = BusStop(id='103', name='s103')
        self.stop103.route = {'0', '1'}
        self.stop104 = BusStop(id='104', name='s104')
        self.stop104.route = {'1'}
        # 001       002         003         004         005
        # ---->---->---->---->---->---->---->---->---->---->
        # |           '0'           |
        #                      |            '1'            |
        # <----<----<----<----<----<----<----<----<----<----
        # 101       102         103         104         105

    def tearDown(self):
        self.route0 = None
        self.route1 = None

    def test_connected_stops(self):
        self.assertSetEqual(self.stop103.connected_stops(dbRoute), {'101', '102', '104', '105'})
        self.assertSetEqual(self.stop104.connected_stops(dbRoute), {'103', '105'})

    def test_stops_can_go(self):
        self.assertSetEqual(self.stop103.stops_can_go(dbRoute), {'101', '102'})
        self.assertSetEqual(self.stop104.stops_can_go(dbRoute), {'103'})

    def test_stops_can_come(self):
        self.assertSetEqual(self.stop103.stops_can_come(dbRoute), {'104', '105'})
        self.assertSetEqual(self.stop104.stops_can_come(dbRoute), {'105'})


if __name__ == '__main__':
    unittest.main()


# python -m unittest in bus folder
