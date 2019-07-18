"""
Classes and utilities to manage IxLoad application.

@author yoram@ignissoft.com
"""

import logging

from trafficgenerator.tgn_app import TgnApp

from ixload.api import IxLoadUtils
from ixload.api.ixl_rest import IxlRestWrapper, IxlList
from ixload.ixl_object import IxlObject
from ixload.ixl_hw import IxlChassisChain


def init_ixl(logger=None):
    """ Create IXN object.

    :param logger: python logger object. If no logger the package will create default logger.
    :return: IXL object
    """

    if not logger:
        logger = logging.getLogger('ixload')
        logger.addHandler(logging.StreamHandler())
    api_wrapper = IxlRestWrapper(logger)
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

    def connect(self, ip='localhost', port=None, version=None, auth=None):
        """ Connect to IxTcl/REST server.

        :param ip: IxLoad gateway server.
        :param port: FFU - IxLoad gateway server port. If None - use default port (8080 or 443).
        :param version: IxLoad chassis version. If None - use version from IxLoad gateway.
        :param auth: either user/password or full path to crt file for v1 HTTPS connections.
        """

        self.api.connect(ip=ip, port=port, version=(version if version else ''), auth=auth)
        IxlApp.controller = IxlController()

    def disconnect(self):
        """ Disconnect from chassis and server. """
        self.api.disconnect()

    def new_config(self):
        self.repository = IxlRepository()

    def load_config(self, config_file_name, test_name='Test1'):
        self.repository = IxlRepository(name=config_file_name.replace('\\', '/'), test=test_name)

    def save_config(self, config_file_name):
        self.repository.save_config(config_file_name.replace('\\', '/'))

    #
    # IxLoad GUI commands.
    #

    def start_test(self, blocking=True):
        self.controller.start_test(blocking)

    def stop_test(self):
        self.controller.stop_test()

    @property
    def is_remote(self):
        return self.api.connection.is_remote


class IxlController(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixTestController'
        data['parent'] = None
        super(self.__class__, self).__init__(**data)
        self.test = IxlObject(parent=self, objRef=self.ref + '/ixload/test', objType='test')

    def set_results_dir(self, results_dir):
        self.test.set_attributes(outputDir=True, runResultDirFull=results_dir)

    def set_licensing(self, licenseServer):
        preferences = IxlObject(parent=self, objRef=self.ref + '/ixload/preferences', objType='preferences')
        preferences.set_attributes(licenseServer=licenseServer)

    def start_test(self, blocking=True):
        IxLoadUtils.runTest(self.api.connection, self.api.session_url)
        if blocking:
            self.wait_for_test_finish()
            self.release_test()

    def stop_test(self):
        IxLoadUtils.stopTest(self.api.connection, self.api.session_url)

    def wait_for_test_finish(self):
        IxLoadUtils.waitForTestToReachUnconfiguredState(self.api.connection, self.api.session_url)

    def release_test(self):
        self.command('releaseConfigWaitFinish')


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
        return super(self.__class__, self)._create(name=self._data.get('name', None))

    def load_test(self, name='Test1', force_port_ownership=False):
        test = IxlObject(parent=self, objType='tests', objRef=self.ref + '/test/activeTest')
        test.get_name()
        tests = [test]

        for test in tests:
            if test.name == name:
                self.test = test
                self.test.set_attributes(enableForceOwnership=force_port_ownership)
                break
        self.test.get_children('communityList')

    def get_elements(self):
        elements = {o.obj_name(): o for o in self.test.get_objects_by_type('community')}
        return elements

    def save_config(self, name):
        self.command('write', destination=name, overwrite=True)


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
        ip, cardId, portId = location.split('/')
        chassis = self.repository.cc.append(ip)
        chassisId = chassis.get_attribute('id')
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
