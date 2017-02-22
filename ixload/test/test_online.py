"""
IxLoad package tests that require actual IxLoad chassis and active ports.

Note that in many places there are (relatively) long delays to make sure the tests work in all setups.

Test setup:
Two IXL ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path

from ixload.test.test_base import IxlTestBase


class IxlTestOnline(IxlTestBase):

    ports = []

    def testReservePorts(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        pass

    def testReleasePorts(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        for port in self.ports:
            port.release()
        pass

    def _reserve_ports(self, config_file):
        self._load_config(config_file)
        repository = self.ixl.repository
        repository.get_object_by_name('Traffic1@Network1').reserve(self.config.get('IXL', 'Traffic1@Network1'))
        repository.get_object_by_name('Traffic2@Network2').reserve(self.config.get('IXL', 'Traffic2@Network2'))
