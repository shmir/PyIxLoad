
import pytest


server = '172.30.26.213'
server = '127.0.0.1'
version = '8.50.0.465'
version = '8.40.0.277'


def pytest_addoption(parser):
    parser.addoption('--server', action='store', default=server + ':8080', help='REST server in format ip:port')
    parser.addoption('--originate', action='store', default='192.168.42.207/1/1', help='chassis1/module1/port1')
    parser.addoption('--terminate', action='store', default='192.168.42.158/1/1', help='chassis2/module2/port2')
    parser.addoption('--app-version', action='store', default=version, help='chassis full vesion')


@pytest.fixture(autouse=True, scope='class')
def api(request):
    server_ip = request.config.getoption('--server')  # @UndefinedVariable
    request.cls.server_ip = server_ip.split(':')[0]
    request.cls.server_port = server_ip.split(':')[1] if len(server_ip.split(':')) == 2 else 8009
    request.cls.originate = request.config.getoption('--originate')
    request.cls.terminate = request.config.getoption('--terminate')
    request.cls.version = request.config.getoption('--app-version')
