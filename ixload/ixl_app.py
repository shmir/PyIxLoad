"""
Classes and utilities to manage IxLoad application.

@author yoram@ignissoft.com
"""

import time

from trafficgenerator.tgn_utils import is_true, is_false, ApiType, TgnError
from trafficgenerator.tgn_app import TgnApp
from ixload.api import IxLoadUtils

from ixload.api.ixl_tcl import IxlTclWrapper
from ixload.api.ixl_rest import IxlRestWrapper
from ixload.ixl_object import IxlObject
from ixload.api.ixl_tcl import IxlList


def init_ixl(api, logger, install_dir=None):
    """ Create IXN object.

    :param api: tcl/python/rest
    :type api: trafficgenerator.tgn_utils.ApiType
    :param logger: logger object
    :param install_dir: IXL installation directory (Tcl only)
    :return: IXL object
    """

    if api == ApiType.tcl:
        api_wrapper = IxlTclWrapper(logger, install_dir)
    elif api == ApiType.rest:
        api_wrapper = IxlRestWrapper(logger)
    else:
        raise TgnError('{} API not supported - use Tcl or REST'.format(api))
    return IxlApp(logger, api_wrapper)


class IxlApp(TgnApp):
    """ IxLoad driver. Equivalent to IxLoad Application. """

    controller = None

    def __init__(self, logger, api_wrapper):
        """ Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing IxlApi base class.
        """

        super(self.__class__, self).__init__(logger, api_wrapper)

        IxlObject.logger = self.logger
        IxlObject.api = self.api
        IxlObject.str_2_class = TYPE_2_OBJECT

    def connect(self, version=None, ip='localhost', port=8080):
        """ Connect to IxTcl/REST server.

        :param version: IxLoad version, ignored for IxTcl server.
        :param server: IxTcl/REST server.
        :param port: REST port, ignored for IxTcl server.
        """

        self.api.connect(ip, port, version)
        IxlApp.controller = IxlController()

    def disconnect(self):
        """ Disconnect from chassis and server. """
        self.api.disconnect()

    def load_config(self, config_file_name, test_name='Test1'):
        self.repository = IxlRepository(name=config_file_name.replace('\\', '/'), test=test_name)

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
        data['parent'] = None
        super(self.__class__, self).__init__(**data)
        self.set_results_dir(data.get('resultsDir', 'c:/temp/IxLoadResults'))

    def set_results_dir(self, results_dir):
        self.results_dir = results_dir
        self.command('setResultDir', self.results_dir)

    def start_test(self, test, blocking=True):
        self.api.eval('set ::ixTestControllerMonitor {}')
        self.command('run', test.obj_ref())
        while is_false(self.command('isBusy')):
            time.sleep(1)
        rc = self.api.eval('set dummy $::ixTestControllerMonitor')
        if rc and 'status OK' not in rc:
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

    def create_report(self, detailed=True):
        """ Create detailed report under results directory.

        :param detailed: True - detailed report, False - summary report.
        :return: full path to report file.
        """

        self.command('generateReport', detailedReport=1)
        return self.results_dir + ('IxLoad Detailed Report' if detailed else 'IxLoad Summary Report') + '/pdf'


class IxlRepository(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixRepository'
        data['parent'] = None
        super(self.__class__, self).__init__(**data)
        self.repository = self
        self.cc = self.get_child('chassisChain')
        self.cc.clear()
        self.load_test(data.get('test', 'Test1'))

    def _create(self, **attributes):
        return super(self.__class__, self)._create(name=self._data['name'])

    def load_test(self, name='Test1', force_port_ownership=False):
        if type(self.api) == IxlTclWrapper:
            tests = self.get_children('testList')
        else:
            test = IxlObject(parent=self, objType='tests', objRef=self.ref + '/test/activeTest')
            test.get_name()
            tests = [test]

        for test in tests:
            if test.obj_name() == name:
                self.test = test
                self.test.set_attributes(enableForceOwnership=force_port_ownership)
                break
        if type(self.api) == IxlTclWrapper:
            for scenario in self.test.get_children('scenarioList'):
                for column in scenario.get_children('columnList'):
                    column.get_children('elementList')
        else:
            test.get_children('communityList')

    def get_elements(self):
        elements = {}
        if type(self.api) == IxlTclWrapper:
            for scenario in self.test.get_objects_by_type('scenario'):
                for column in scenario.get_objects_by_type('column'):
                    elements.update({o.obj_name(): o for o in column.get_objects_by_type('element')})
        else:
            elements = {o.obj_name(): o for o in column.get_objects_by_type('community')}
        return elements

    def save_config(self, name):
        self.command('write', destination=name, overwrite=True)


class IxlChassisChain(IxlObject):

    def clear(self):
        self.api.clear_chassis_chain(self.ref)

    def append(self, chassis):
        if type(self.api) == IxlTclWrapper:
            chassis_list = self.command('getChassisNames').split()
        else:
            chassis_list = self.get_children('chassisList')
        chassis_id = 0
        for index, name in enumerate(chassis_list):
            if name == chassis:
                chassis_id = index + 1
        if not chassis_id:
            if type(self.api) == IxlTclWrapper:
                self.command('addChassis', chassis)
                self.command('refresh')
                chassis_id = len(self.command('getChassisNames').split())
            else:
                chassis_id = IxLoadUtils.addChassisList(self.api.connection, self.api.session_url, [chassis])[0]
        return chassis_id


class IxlElement(IxlObject):

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.network = self.get_child('network')

    def reserve(self, location):
        port_list = IxlList(self.network, 'port')
        port_list.clear()
        chassis, cardId, portId = location.split('/')
        chassisId = self.repository.cc.append(chassis)
        port_list.append(chassisId=chassisId, cardId=cardId, portId=portId)


class IxlCommunity(IxlObject):

    def reserve(self, location):
        chassis, cardId, portId = location.split('/')
        chassisId = self.repository.cc.append(chassis)
        IxLoadUtils.assignPorts(self.api.connection, self.api.session_url, {self.name: [(chassisId, cardId, portId)]})


class IxlScenario(IxlObject):
    pass


class IxlTest(IxlObject):
    pass


TYPE_2_OBJECT = {'chassischain': IxlChassisChain,
                 'community': IxlCommunity,
                 'element': IxlElement,
                 'scenario': IxlScenario,
                 'test': IxlTest}
