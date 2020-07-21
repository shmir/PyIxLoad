"""
IxLoad package testing.
"""

import inspect
import logging
import time
from pathlib import Path
from typing import Optional

from ixload.ixl_app import IxlApp
from ixload.ixl_statistics_view import IxlStatView


logger = logging.getLogger('ixload')


def test_hello_world(ixload: IxlApp) -> None:
    """ Fufu test just to verify all fixtures are correct and server is up and running. """
    pass


def test_load_config(ixload: IxlApp) -> None:
    """ Test configuration load. """
    logger.info(test_load_config.__doc__)

    load_config(ixload, 'test_config.rxf')
    print(ixload.repository.get_elements())

    save_config(ixload)


def test_get_set(ixload):
    """ Test get/set operations. """
    logger.info(test_get_set.__doc__)

    load_config(ixload, 'test_config.rxf')

    print('+++')
    print(ixload.api.get_children(ixload.api.session_url))
    ixload_url = ixload.api.get_children(ixload.api.session_url, 'ixload')[0]
    print(ixload.api.get_children(ixload_url))
    test_url = ixload.api.get_children(ixload_url, 'test')[0]
    print(ixload.api.get_children(test_url))
    active_test_url = ixload.api.get_children(test_url, 'activeTest')[0]
    print(ixload.api.get_children(active_test_url))
    timeline_list_url = ixload.api.get_children(active_test_url, 'timelineList')[0]
    print(ixload.api.get_children(timeline_list_url))
    docs_url = ixload.api.get_children(timeline_list_url, 'docs')[0]
    print(ixload.api.get_children(docs_url))
    print(ixload.api.cget(timeline_list_url))
    print(ixload.api.cget(timeline_list_url, 'iterations'))
    ixload.api.config(timeline_list_url, iterations=2)
    print(ixload.api.cget(timeline_list_url, 'iterations'))
    print('+++')


def test_reserve_ports(ixload: IxlApp, originate: str, terminate: str) -> None:
    """ Test port reservation. """
    logger.info(test_reserve_ports.__doc__)

    load_config(ixload, 'test_config.rxf')
    reserve_ports(ixload, originate, terminate)


def test_run_test(ixload: IxlApp, originate: str, terminate: str) -> None:
    """ Test run in blocking mode. """
    logger.info(test_run_test.__doc__)

    load_config(ixload, 'test_config.rxf')
    reserve_ports(ixload, originate, terminate)
    ixload.start_test(blocking=True)


def test_run_stop_test(ixload: IxlApp, originate: str, terminate: str):
    """ Test run in non-blocking mode and stop. """
    logger.info(test_run_stop_test.__doc__)

    load_config(ixload, 'test_config.rxf')
    reserve_ports(ixload, originate, terminate)
    ixload.start_test(blocking=False)
    time.sleep(8)
    ixload.stop_test()


def test_run_stats(ixload: IxlApp, originate: str, terminate: str):
    """ Test run and statistics. """
    logger.info(test_run_stats.__doc__)

    load_config(ixload, 'test_config.rxf')
    reserve_ports(ixload, originate, terminate)
    if not ixload.is_remote:
        ixload.controller.set_results_dir('c:/temp/TestIxlOnline')
    ixload.start_test(blocking=True)
    if supports_download(ixload):
        client_stats = IxlStatView('Test_Client')
        client_stats.read_stats()
        print(client_stats.get_all_stats())
        assert(client_stats.get_counter(16, 'TCP SYN Sent/s') > 0)


def test_rerun_test(ixload: IxlApp, originate: str, terminate: str):
    """ Test re-run test. """
    logger.info(test_rerun_test.__doc__)

    load_config(ixload, 'test_config.rxf')
    reserve_ports(ixload, originate, terminate)
    if not ixload.is_remote:
        ixload.controller.set_results_dir('c:/temp/TestIxlOnline')
    ixload.start_test(blocking=False)
    ixload.stop_test()
    ixload.start_test(blocking=True)
    if supports_download(ixload):
        client_stats = IxlStatView('Test_Client')
        client_stats.read_stats()
        print(client_stats.get_all_stats())
        assert(client_stats.get_counter(16, 'TCP SYN Sent/s') > 0)


#
# Utilities, no testing inside.
#


def load_config(ixload: IxlApp, config_name: str) -> None:
    """ Load configuration file to IxLoad.

    :param ixload: IxLoad server.
    :param config_name: config name under tests/configs sub-directory.
    """
    config_file = Path(__file__).parent.joinpath(f'configs/{config_name}').as_posix()
    ixload.load_config(config_file, 'Test1')


def save_config(ixload: IxlApp, config_file: Optional[str] = None) -> None:
    """ Download configuration file from IxLoad.

    :param ixload: IxLoad server.
    :param config_file: Path to rxf file name. If empty configuration will be saved as
        tests/configs/temp/{test_name}.rxf.
    """
    if not config_file:
        test_name = inspect.stack()[1][3]
        config_file = Path(__file__).parent.joinpath(f'configs/temp/{test_name}.rxf').as_posix()
    if supports_download(ixload):
        ixload.save_config(config_file)


def reserve_ports(ixload: IxlApp, originate: str, terminate: str) -> None:
    """ Reserve ports.

    :param ixload: IxLoad server.
    :param originate: Originate port location in format chassis/card/port.
    :param terminate: Terminate port location in format chassis/card/port.
    """
    repository = ixload.repository
    repository.test.set_attributes(enableForceOwnership=True)
    repository.get_object_by_name('Traffic1@Network1').reserve(originate)
    repository.get_object_by_name('Traffic2@Network2').reserve(terminate)


def supports_download(ixload: IxlApp) -> bool:
    """ Returns True of server supports download, else False.

    :param ixload: IxLoad server.
    """
    return not ixload.is_remote or ixload.api.connection.ixload_version >= '8.50.115.333'
