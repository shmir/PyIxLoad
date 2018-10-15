"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect
import pytest

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.test.test_tgn import TestTgnBase

from ixload.ixl_app import init_ixl


class TestIxlBase(TestTgnBase):

    TestTgnBase.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setup(self):
        super(TestIxlBase, self).setup()
        self._get_config()

        self.ixl = init_ixl(self.logger)
        self.ixl.connect(self.config.get('IXL', 'version'), self.server_ip, self.server_port)

    def teardown(self):
        super(TestIxlBase, self).teardown()
        self.ixl.disconnect()

    def test_hello_world(self):
        pass

    #
    # Auxiliary functions, no testing inside.
    #

    def _get_config(self):

        self.api = ApiType[pytest.config.getoption('--api')]  # @UndefinedVariable
        server_ip = pytest.config.getoption('--server')  # @UndefinedVariable
        self.server_ip = server_ip.split(':')[0]
        self.server_port = server_ip.split(':')[1] if len(server_ip.split(':')) == 2 else 8080
        self.originate = pytest.config.getoption('--originate')  # @UndefinedVariable
        self.terminate = pytest.config.getoption('--terminate')  # @UndefinedVariable

    def _load_config(self, config_file):
        self.ixl.load_config(config_file, 'Test1')

    def _save_config(self):
        test_name = inspect.stack()[1][3]
        self.ixl.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.rxf'))
