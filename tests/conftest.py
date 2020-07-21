"""
Conftest for ixload package testing.
"""

import sys
import logging
from pathlib import Path

import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest
from _pytest.python import Metafunc

from trafficgenerator.tgn_utils import get_test_config
from ixload.ixl_app import init_ixl, IxlApp


ixl_config = Path(__file__).parent.joinpath('test_config.py').as_posix()
if Path(ixl_config).exists():
    ixl_server = get_test_config(ixl_config).server
else:
    ixl_server = None
    ixl_config = None


def pytest_addoption(parser: Parser) -> None:
    """ Add options to allow the user to determine which servers to test. """
    parser.addoption('--ixl-server', action='append', default=ixl_server, help='REST server IP')
    parser.addoption('--ixl-config', action='store', default=ixl_config, help='path to configuration file')


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """ Generate tests for each serever from pytest options. """
    metafunc.parametrize('server', metafunc.config.getoption('--ixl-server'), indirect=True)


@pytest.fixture(scope='session')
def logger() -> logging.Logger:
    """ Yields configured logger. """
    logger = logging.getLogger('ixload')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    yield logger


@pytest.fixture(scope='session')
def server(request: SubRequest) -> str:
    """ Yields server name in confing file - generate tests will generate servers based on the server option. """
    yield request.param


@pytest.fixture(scope='session')
def server_properties(request: SubRequest, server: str) -> dict:
    """ Yields server properties dict for the requested server. """
    yield get_test_config(request.config.getoption('--ixl-config')).server_properties[server]


@pytest.fixture(scope='session')
def ixload(request: SubRequest, logger: logging.Logger, server_properties: dict) -> IxlApp:
    """ Yields connected IxLoad object. """
    ixload = init_ixl(logger)
    ip = server_properties['server']
    version = server_properties['ixversion']
    auth = server_properties['auth']
    ixload.connect(ip, version=version, auth=auth)
    license_server = get_test_config(request.config.getoption('--ixl-config')).license_server
    ixload.controller.set_licensing(license_server)
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
