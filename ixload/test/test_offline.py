"""
IxLoad package tests that can run in offline mode.

@author yoram@ignissoft.com
"""

from os import path

from ixload.test.test_base import IxlTestBase


class IxlTestOffline(IxlTestBase):

    def testLoadConfig(self):
        """ Test configuration load. """
        self.logger.info(IxlTestOffline.testLoadConfig.__doc__)

        self._load_config(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self._save_config()
