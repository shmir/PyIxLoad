"""
IxLoad package tests that require actual IxLoad chassis and active ports.

Note that in many places there are (relatively) long delays to make sure the tests work in all setups.

Test setup:
Two IXL ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path
import time

import ixload.test.test_base
from ixload.ixl_statistics_view import IxlStatView


class TestIxlOnline(ixload.test.test_base.TestIxlBase):

    ports = []

    def test_reserve_ports(self):
        """ Test port reservation. """
        self.logger.info(TestIxlOnline.test_reserve_ports.__doc__)

        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))

    def test_run_test(self):
        """ Test run in blocking mode. """
        self.logger.info(TestIxlOnline.test_run_test.__doc__)

        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.start_test(blocking=True)

    def test_run_stop_test(self):
        """ Test run in non-blocking mode and stop. """
        self.logger.info(TestIxlOnline.test_run_stop_test.__doc__)

        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.start_test(blocking=False)
        time.sleep(8)
        self.ixl.stop_test()

    def test_run_stats(self):
        """ Test run and statistics. """
        self.logger.info(TestIxlOnline.test_run_stop_test.__doc__)

        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.controller.set_results_dir('/tmp/TestIxlOnline')
        self.ixl.start_test(blocking=True)
        if self._supports_download():
            client_stats = IxlStatView('Test_Client')
            client_stats.read_stats()
            print(client_stats.get_all_stats())
            assert(client_stats.get_counter(16, 'TCP SYN Sent/s') > 0)

    def test_rerun_test(self):
        """ Test re-run test. """
        self.logger.info(TestIxlOnline.test_run_stop_test.__doc__)

        self._reserve_ports(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        self.ixl.controller.set_results_dir('/tmp/TestIxlOnline')
        self.ixl.start_test(blocking=False)
        self.ixl.stop_test()
        self.ixl.start_test(blocking=True)
        if self._supports_download():
            client_stats = IxlStatView('Test_Client')
            client_stats.read_stats()
            print(client_stats.get_all_stats())
            assert(client_stats.get_counter(16, 'TCP SYN Sent/s') > 0)

    def _reserve_ports(self, config_file):
        self._load_config(config_file)
        repository = self.ixl.repository
        repository.test.set_attributes(enableForceOwnership=True)
        repository.get_object_by_name('Traffic1@Network1').reserve(self.originate)
        repository.get_object_by_name('Traffic2@Network2').reserve(self.terminate)
