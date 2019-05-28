
import pytest


server = '127.0.0.1'
version = '8.40.0.277'
server = '192.168.65.87'
version = '8.50.115.333'
gw_crt = 'e:/workspace/python/PyIxLoad/ixload_certificate.crt'
gw_crt = None


def pytest_addoption(parser):
    parser.addoption('--server', action='store', default=server, help='REST server IP')
    parser.addoption('--originate', action='store', default='192.168.42.207/1/1', help='chassis1/module1/port1')
    parser.addoption('--terminate', action='store', default='192.168.42.158/1/1', help='chassis2/module2/port2')
    parser.addoption('--ixload-version', action='store', default=version, help='chassis full vesion')
    parser.addoption('--gw-crt', action='store', default=gw_crt, help='full path to gw crt file')


@pytest.fixture(autouse=True, scope='class')
def api(request):
    server_ip = request.config.getoption('--server')  # @UndefinedVariable
    request.cls.server_ip = server_ip
    request.cls.originate = request.config.getoption('--originate')
    request.cls.terminate = request.config.getoption('--terminate')
    request.cls.version = request.config.getoption('--ixload-version')
    request.cls.crt_file = request.config.getoption('--gw-crt')
