"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect
import time

from trafficgenerator.test.test_tgn import TestTgnBase

from ixload.ixl_app import init_ixl


class TestIxlBase(TestTgnBase):

    TestTgnBase.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setup(self):
        super(TestIxlBase, self).setup()
        self.ixl = init_ixl(self.api, self.logger, self.config.get('IXL', 'install_dir'))
        self.ixl.connect(self.config.get('IXL', 'version'), self.server_ip, self.server_port)

    def teardown(self):
        super(TestIxlBase, self).teardown()
        self.ixl.disconnect()
        time.sleep(8)

    def testHelloWorld(self):
        pass

    #
    # Auxiliary functions, no testing inside.
    #

    def _load_config(self, config_file):
        self.ixl.load_config(config_file, 'Test1', )

    def _save_config(self):
        test_name = inspect.stack()[1][3]
        self.ixl.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.rxf'))
