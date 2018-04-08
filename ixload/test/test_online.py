"""
IxLoad package tests that require actual IxLoad chassis and active ports.

Note that in many places there are (relatively) long delays to make sure the tests work in all setups.

Test setup:
Two IXL ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path
import time

from ixload.test.test_base import IxlTestBase
from ixload.ixl_statistics_view import IxlStatView


class IxlTestOnline(IxlTestBase):

    ports = []

    def testReservePorts(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config_840.rxf'))

    def testRunTest(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.start_test(blocking=True)

    def testRunStopTest(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.start_test(blocking=False)
        time.sleep(8)
        self.ixl.stop_test()

    def testRunStats(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.controller.set_results_dir('C:/temp/IxLoad')
        self.ixl.start_test(blocking=True)
        client_stats = IxlStatView('Test_Client')
        client_stats.read_stats()
        print(client_stats.get_all_stats())
        assert(client_stats.get_stat(16, 'TCP SYN Sent/s') > 0)

    def testRerunTest(self):
        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.controller.set_results_dir('C:/temp/IxLoad')
        self.ixl.start_test(blocking=False)
        self.ixl.stop_test()
        self.ixl.start_test(blocking=True)
        client_stats = IxlStatView('Test_Client')
        client_stats.read_stats()
        print(client_stats.get_all_stats())
        assert(client_stats.get_stat(16, 'TCP SYN Sent/s') > 0)

    def testExistingStats(self):
        client_stats = IxlStatView('Test_Client')
        client_stats.read_stats()
        for time_stamp, values in client_stats.get_all_stats().items():
            print('{} : {}'.format(time_stamp, values))
        print(client_stats.get_time_stamp_stats(10))
        print(client_stats.get_stats('TCP Retries'))
        print(client_stats.get_counters('TCP Retries'))

    def testReport(self):
        print self.ixl.controller.create_report()

    def _reserve_ports(self, config_file):
        self._load_config(config_file)
        repository = self.ixl.repository
        repository.test.set_attributes(enableForceOwnership=True)
        repository.get_object_by_name('Traffic1@Network1').reserve(self.config.get('IXL', 'Traffic1@Network1'))
        repository.get_object_by_name('Traffic2@Network2').reserve(self.config.get('IXL', 'Traffic2@Network2'))
