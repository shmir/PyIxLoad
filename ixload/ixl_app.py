"""
Classes and utilities to manage IxLoad application.

@author yoram@ignissoft.com
"""

from os import path

from trafficgenerator.trafficgenerator import TrafficGenerator

from ixload.ixl_object import IxlObject

TYPE_2_OBJECT = {}


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
        pass

    def load_config(self, config_file_name, test_name='Test1'):
        self.repository = IxlRepository(rxf=config_file_name.replace('\\', '/'), test=test_name)

    def save_config(self, config_file_name):
        self.repository.save_config(config_file_name.replace('\\', '/'))

    #
    # IxLoad GUI commands.
    #


class IxlController(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixTestController'
        super(self.__class__, self).__init__(**data)


class IxlRepository(IxlObject):

    def __init__(self, **data):
        data['objType'] = 'ixRepository'
        super(self.__class__, self).__init__(**data)
        if 'test' in data:
            self.load_test(data['test'])

    def _create(self, **attributes):
        return super(self.__class__, self)._create(rxf=self._data['rxf'])

    def load_test(self, name='Test1'):
        self.command('testList.getItem ' + name)

    def save_config(self, name):
        self.command('write', destination=name, overwrite=True)
