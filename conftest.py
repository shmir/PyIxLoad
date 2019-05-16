
import pytest

from trafficgenerator.tgn_utils import ApiType


def pytest_addoption(parser):
    parser.addoption('--api', action='store', default='rest', help='api options: rest or tcl')
    parser.addoption('--server', action='store', default='localhost:8080', help='REST server in format ip:port')
    parser.addoption('--Traffic1@Network1', action='store', default='192.168.42.207/1/1', help='chassis1/module1/port1')
    parser.addoption('--Traffic2@Network2', action='store', default='192.168.42.173/1/1', help='chassis2/module2/port2')


@pytest.fixture(autouse=True, scope='class')
def api(request):
    request.cls.api = ApiType[request.param]
    server_ip = request.config.getoption('--server')  # @UndefinedVariable
    request.cls.server_ip = server_ip.split(':')[0]
    request.cls.server_port = server_ip.split(':')[1] if len(server_ip.split(':')) == 2 else 8009
    request.cls.port1 = request.config.getoption('--Traffic1@Network1')
    request.cls.port2 = request.config.getoption('--Traffic2@Network2')


def pytest_generate_tests(metafunc):
    if metafunc.config.getoption('--api') == 'all':
        apis = ['tcl', 'rest']
    else:
        apis = [metafunc.config.getoption('--api')]
    metafunc.parametrize('api', apis, indirect=True)
