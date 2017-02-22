"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect

from trafficgenerator.test.test_tgn import TgnTest

from ixload.api.ixl_tcl import IxlTclWrapper
from ixload.api.ixl_rest import IxlRestWrapper
from ixload.ixl_app import IxlApp


class IxlTestBase(TgnTest):

    TgnTest.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setUp(self):
        super(IxlTestBase, self).setUp()
        if self.config.get('IXL', 'api').lower() == 'tcl':
            api_wrapper = IxlTclWrapper(self.logger, self.config.get('IXL', 'install_dir'))
        else:
            api_wrapper = IxlRestWrapper(self.logger, self.config.get('IXL', 'install_dir'))
        self.ixl = IxlApp(self.logger, api_wrapper=api_wrapper)
        self.ixl.connect(self.config.get('IXL', 'server_ip'), self.config.get('IXL', 'server_port'))

    def tearDown(self):
        super(IxlTestBase, self).tearDown()
        self.ixl.disconnect()

    def testHelloWorld(self):
        pass

    #
    # Auxiliary functions, no testing inside.
    #

    def _load_config(self, config_file):
        self.ixl.load_config(config_file, 'Test1')

    def _save_config(self):
        test_name = inspect.stack()[1][3]
        self.ixl.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.rxf'))
