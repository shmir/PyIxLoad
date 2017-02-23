"""
Classes and utilities to manage IxLoad application.

@author yoram@ignissoft.com
"""

import time
import csv

from trafficgenerator.tgn_utils import is_true, is_false
from trafficgenerator.trafficgenerator import TrafficGenerator

from ixload.ixl_object import IxlObject, IxlList


class IxlApp(TrafficGenerator):
    """ IxLoad driver. Equivalent to IxLoad Application. """

    def __init__(self, logger, api_wrapper=None):
        """ Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing IxlApi base class.
        """

        super(self.__class__, self).__init__()
        self.logger = logger
        self.api = api_wrapper

        IxlObject.logger = self.logger
        IxlObject.api = self.api
        IxlObject.str_2_class = TYPE_2_OBJECT

    def connect(self, ip='localhost', port=8080):
        """ Connect to IxTcl/REST server.

        :param server: TxTcl/REST server.
        :param port: REST port, ignored for IxTcl server.
        """

        self.api.connect(ip, port)
        self.controller = IxlController()

    def disconnect(self):
        """ Disconnect from chassis and server. """
        self.api.disconnect()

    def load_config(self, config_file_name, test_name='Test1'):
        self.repository = IxlRepository(name=config_file_name.replace('\\', '/'), test=test_name)
        IxlObject.repository = self.repository

    def save_config(self, config_file_name):
        self.repository.save_config(config_file_name.replace('\\', '/'))

    #
    # IxLoad GUI commands.
    #

    def start_test(self, blocking=True):
        self.controller.start_test(self.repository.test, blocking)

    def stop_test(self):
        self.controller.stop_test()


class IxlController(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixTestController'
        super(self.__class__, self).__init__(**data)
        self.command('setResultDir', 'c:/temp/IxLoad')

    def start_test(self, test, blocking=True):
        self.api.eval('set ::ixTestControllerMonitor {}')
        self.command('run', test.obj_ref())
        while is_false(self.command('isBusy')):
            time.sleep(1)
        rc = self.api.eval('set dummy $::ixTestControllerMonitor')
        if rc:
            raise Exception(rc)
        if blocking:
            self.wait_for_test_finish()
            self.release_test()

    def stop_test(self):
        self.command('stopRun')
        self.release_test()

    def wait_for_test_finish(self):
        while is_true(self.command('isBusy')):
            time.sleep(1)
        rc = self.api.eval('set dummy $::ixTestControllerMonitor')
        if 'status ok' not in rc.lower() and 'test stopped by the user' not in rc.lower():
            raise Exception(rc)

    def release_test(self):
        self.command('releaseConfigWaitFinish')


class IxlRepository(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixRepository'
        super(self.__class__, self).__init__(**data)
        self.cc = self.get_child('chassisChain')
        self.cc.clear()
        self.load_test(data.get('test', 'Test1'))

    def _create(self, **attributes):
        return super(self.__class__, self)._create(name=self._data['name'])

    def load_test(self, name='Test1'):
        for test in self.get_children('testList'):
            if test.obj_name() == name:
                self.test = test
                break
        for scenario in self.test.get_children('scenarioList'):
            for column in scenario.get_children('columnList'):
                column.get_children('elementList')

    def save_config(self, name):
        self.command('write', destination=name, overwrite=True)


class IxlChassisChain(IxlObject):

    def clear(self):
        for chassis in self.command('getChassisNames').split():
            self.command('deleteChassisByName', chassis)

    def append(self, chassis):
        chassis_id = 0
        for index, name in enumerate(self.command('getChassisNames').split()):
            if name == chassis:
                chassis_id = index + 1
        if not chassis_id:
            self.command('addChassis', chassis)
            self.command('refresh')
            chassis_id = len(self.command('getChassisNames').split())
        return chassis_id


class IxlElement(IxlObject):

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.network = self.get_child('network')

    def reserve(self, location):
        port_list = IxlList(self.network, 'port')
        port_list.clear()
        chassis, cardId, portId = location.split('/')
        repository = IxlObject.repository
        chassisId = repository.cc.append(chassis)
        port_list.append(chassisId=chassisId, cardId=cardId, portId=portId)


class IxlStatView(object):

    def __init__(self, view):
        self.view = view

    def read_stats(self):
        with open('c:/temp/IxLoad/' + self.view + '.csv', 'rb') as csvfile:
            self.csv_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            stats = ''
            for row in self.csv_reader:
                stats += '\n'
                stats += ', '.join(row)
        return stats


TYPE_2_OBJECT = {'chassischain': IxlChassisChain,
                 'element': IxlElement}
