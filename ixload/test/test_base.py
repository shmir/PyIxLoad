"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect

import trafficgenerator.test.test_tgn
from trafficgenerator.tgn_utils import is_local_host
from ixload.ixl_app import init_ixl


class TestIxlBase(trafficgenerator.test.test_tgn.TestTgnBase):

    trafficgenerator.test.test_tgn.TestTgnBase.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setup(self):
        super(TestIxlBase, self).setup()
        self.ixl = init_ixl(self.logger)
        self.ixl.connect(self.version, self.server_ip, auth=self.auth)
        if self.ls:
            self.ixl.controller.set_licensing(self.ls)

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
        if self._supports_download():
            self.ixl.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.rxf'))

    def _supports_download(self):
        return is_local_host(self.server_ip) or self.version >= '8.50.115.333'
