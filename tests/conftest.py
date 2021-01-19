"""
Conftest for ixload package testing.
"""
import logging
from pathlib import Path

import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest
# noinspection PyUnresolvedReferences
from trafficgenerator.tgn_conftest import (tgn_pytest_addoption, pytest_generate_tests, logger, server,
                                           server_properties)
from trafficgenerator.tgn_utils import get_test_config

from ixload.ixl_app import init_ixl, IxlApp


def pytest_addoption(parser: Parser) -> None:
    """ Add options to allow the user to determine which APIs and servers to test. """
    tgn_pytest_addoption(parser, Path(__file__).parent.joinpath('test_config.py').as_posix())


@pytest.fixture(scope='session')
def ixload(request: SubRequest, logger: logging.Logger, server_properties: dict) -> IxlApp:
    """ Yields connected IxLoad object. """
    ixload = init_ixl(logger)
    ip = server_properties['server']
    version = server_properties['version']
    auth = server_properties['auth']
    ixload.connect(ip, version=version, auth=auth)
    license_server = get_test_config(request.config.getoption('--tgn-config')).license_server
    license_model = get_test_config(request.config.getoption('--tgn-config')).license_mode
    ixload.controller.set_licensing(license_server, license_model)
    yield ixload
    ixload.disconnect()


@pytest.fixture(scope='session')
def originate(server_properties: dict) -> str:
    """ Yields originate port location. """
    yield server_properties['originate']


@pytest.fixture(scope='session')
def terminate(server_properties: dict) -> str:
    """ Yields terminate port location. """
    yield server_properties['terminate']
