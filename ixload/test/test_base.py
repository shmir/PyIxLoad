"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect

from trafficgenerator.test.test_tgn import TestTgnBase
from ixload.ixl_app import init_ixl


class TestIxlBase(TestTgnBase):

    TestTgnBase.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setup(self):
        super(TestIxlBase, self).setup()
        self.ixl = init_ixl(self.logger)
        self.ixl.connect(self.version, self.server_ip, self.crt_file)

    def teardown(self):
        self.ixl.disconnect()
        super(TestIxlBase, self).teardown()

    def test_hello_world(self):
        pass

    #
    # Auxiliary functions, no testing inside.
    #

    def _load_config(self, config_file):
        self.ixl.load_config(config_file, 'Test1')

    def _save_config(self):
        test_name = inspect.stack()[1][3]
        self.ixl.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.rxf'))
