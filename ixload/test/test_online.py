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

        for port in self.ports:
            assert(port.is_online())

        for port in self.ports:
            port.release()

        self.ixn.root.get_object_by_name('Port 1').reserve()
        self.ixn.root.get_object_by_name('Port 2').reserve()

        pass

    def testReleasePorts(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.ixncfg'))
        for port in self.ports:
            port.release()
        pass

    def _reserve_ports(self, config_file):
        self._load_config(config_file)
        self.ports = self.ixn.root.get_children('vport')
        self.ixn.root.get_object_by_name('Port 1').reserve(self.config.get('IXN', 'port1'))
        self.ixn.root.get_object_by_name('Port 2').reserve(self.config.get('IXN', 'port2'))
