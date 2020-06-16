"""
Base class for all IxLoad package tests.

todo: move to conftest?
"""

from os import path
import time
import inspect

from trafficgenerator.tgn_utils import is_local_host
from ixload.ixl_app import init_ixl
from ixload.ixl_statistics_view import IxlStatView


class TestIxlBase:

    logger = None
    server_ip = None
    originate = None
    terminate = None
    version = None
    auth = None
    ls = None

    def setup(self):
        self.ixl = init_ixl(self.logger)
        self.ixl.connect(self.server_ip, None, self.version, auth=self.auth)
        if self.ls:
            self.ixl.controller.set_licensing(self.ls)

    def teardown(self):
        self.ixl.disconnect()

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


class TestIxlOffline(TestIxlBase):
    """ IxLoad package tests that can run in offline mode, I.e. does not require actual IxLoad chassis. """

    def test_load_config(self):
        """ Test configuration load. """
        self.logger.info(TestIxlOffline.test_load_config.__doc__)

        self._load_config(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        print(self.ixl.repository.get_elements())

        self._save_config()

    def test_get_set(self):
        """ Test get/set operations. """
        self.logger.info(TestIxlOffline.test_get_set.__doc__)

        self._load_config(path.join(path.dirname(__file__), 'configs/test_config.rxf'))
        print('+++')
        print(self.ixl.api.get_children(self.ixl.api.session_url))
        ixload_url = self.ixl.api.get_children(self.ixl.api.session_url, 'ixload')[0]
        print(self.ixl.api.get_children(ixload_url))
        test_url = self.ixl.api.get_children(ixload_url, 'test')[0]
        print(self.ixl.api.get_children(test_url))
        activeTest_url = self.ixl.api.get_children(test_url, 'activeTest')[0]
        print(self.ixl.api.get_children(activeTest_url))
        timelineList_url = self.ixl.api.get_children(activeTest_url, 'timelineList')[0]
        print(self.ixl.api.get_children(timelineList_url))
        docs_url = self.ixl.api.get_children(timelineList_url, 'docs')[0]
        print(self.ixl.api.get_children(docs_url))
        print(self.ixl.api.cget(timelineList_url))
        print(self.ixl.api.cget(timelineList_url, 'iterations'))
        self.ixl.api.config(timelineList_url, iterations=2)
        print(self.ixl.api.cget(timelineList_url, 'iterations'))
        print('+++')


class TestIxlOnline(TestIxlBase):
    """ IxLoad package tests that require actual IxLoad chassis and active ports.

    Note that in many places there are (relatively) long delays to make sure the tests work in all setups.

    Test setup:
    Two IXL ports connected back to back.
    """

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
        if not self.ixl.is_remote:
            self.ixl.controller.set_results_dir('c:/temp/TestIxlOnline')
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
        if not self.ixl.is_remote:
            self.ixl.controller.set_results_dir('c:/temp/TestIxlOnline')
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
