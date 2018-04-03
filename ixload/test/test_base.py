#!/usr/bin/env python
# encoding: utf-8

"""
Base class for all IxLoad package tests.

@author yoram@ignissoft.com
"""

from os import path
import inspect

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.test.test_tgn import TgnTest

from ixload.ixl_app import init_ixl


class IxlTestBase(TgnTest):

    TgnTest.config_file = path.join(path.dirname(__file__), 'IxLoad.ini')

    def setUp(self):
        super(IxlTestBase, self).setUp()
        self.ixl = init_ixl(self.logger)
        self.ixl.connect(self.config.get('IXL', 'version'), self.config.get('IXL', 'server_ip'),
                         self.config.get('IXL', 'server_port'))

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


if __name__ == '__main__':
    import sys
    import unittest
    from StringIO import StringIO
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(unittest.makeSuite(IxlTestBase, 'testHelloWorld'))
    sys.exit(result)
