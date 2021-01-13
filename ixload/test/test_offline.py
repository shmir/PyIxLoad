"""
IxLoad package tests that can run in offline mode.

@author yoram@ignissoft.com
"""

from os import path

from ixload.test.test_base import TestIxlBase


class TestIxlOffline(TestIxlBase):

    def test_load_config(self):
        """ Test configuration load. """
        self.logger.info(TestIxlOffline.test_load_config.__doc__)

        self._load_config(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        print(self.ixl.repository.get_elements())

        self._save_config()
