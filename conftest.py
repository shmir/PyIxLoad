
import pytest

windows_840 = '192.168.65.68'
localhost_850 = 'localhost'
windows_850 = '192.168.65.94'
linux_850 = '192.168.65.87'

originate_840 = '192.168.42.207/1/1'
terminate_840 = '192.168.42.162/1/1'
originate_850 = '192.168.65.53/1/1'
terminate_850 = '192.168.65.120/1/1'

server_properties = {windows_840: {'originate': originate_840, 'terminate': terminate_840,
                                   'ixversion': '8.40.0.277',  'auth': None},
                     localhost_850: {'originate': originate_850, 'terminate': terminate_850, 'ixversion': '8.50.0.465',
                                     'crt': 'C:/Program Files (x86)/Ixia/ixLoadGateway/certificate/ixload_certificate.crt'},
                     windows_850: {'originate': originate_850, 'terminate': terminate_850,
                                   'ixversion': '8.50.0.465', 'auth': None},
                     linux_850: {'originate': originate_850, 'terminate': terminate_850,
                                 'ixversion': '8.50.115.333',  'auth': None}}

linux_servers = [linux_850]
windows_servers = [windows_840, localhost_850, windows_850]

gw_crt_ = 'e:/workspace/python/PyIxLoad/ixload_certificate.crt'
gw_crt_ = None

server_ = 'all'
license_server_ = '192.168.42.61'
api_key_ = 'YWRtaW58elR0MTNZR0NPRTYyREpubGFWOXJzT3R6Ry13PQ=='


def pytest_addoption(parser):
    parser.addoption('--server', action='store', default=server_, help='REST server IP')
    parser.addoption('--originate', action='store', default=None, help='chassis1/module1/port1')
    parser.addoption('--terminate', action='store', default=None, help='chassis2/module2/port2')
    parser.addoption('--ixversion', action='store', default=None, help='server full vesion')
    parser.addoption('--apikey', action='store', default=api_key_, help='ApiKey as retrieved from IxLoad GUI')
    parser.addoption('--crt', action='store', default=None, help='full path to gw crt file')
    parser.addoption('--ls', action='store', default=license_server_, help='IP address of license server')


@pytest.fixture
def server(request):
    yield request.param


@pytest.fixture(autouse=True)
def config(request, server):
    request.cls.server_ip = server
    request.cls.originate = _get_cli_or_property(request, server, 'originate')
    request.cls.terminate = _get_cli_or_property(request, server, 'terminate')
    request.cls.version = _get_cli_or_property(request, server, 'ixversion')
    request.cls.auth = {'apikey': _get_cli_or_property(request, server, 'apikey'),
                        'crt': _get_cli_or_property(request, server, 'crt')}
    request.cls.ls = _get_cli_or_property(request, server, 'ls')


def pytest_generate_tests(metafunc):
    if metafunc.config.getoption('--server') == 'all':
        servers = linux_servers + windows_servers
    else:
        servers = [metafunc.config.getoption('--server')]
    metafunc.parametrize('server', servers, indirect=True)


def _get_cli_or_property(request, server, option):
    if request.config.getoption('--' + option):
        return request.config.getoption('--' + option)
    else:
        return server_properties[server].get(option, None)
