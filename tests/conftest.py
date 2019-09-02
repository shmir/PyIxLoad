
import pytest

windows_840 = '192.168.65.68'
windows_850 = '192.168.65.94'
windows_900 = '192.168.65.54'
localhost_900 = 'localhost'
linux_850 = '192.168.65.87'
linux_900 = '192.168.65.23'

originate_840 = '192.168.42.174/1/1'
terminate_840 = '192.168.42.210/1/1'
originate_850 = '192.168.65.30/1/1'
terminate_850 = '192.168.65.120/1/1'
originate_900 = '192.168.65.32/1/1'
terminate_900 = '192.168.65.31/1/1'

server_properties = {windows_840: {'originate': originate_840, 'terminate': terminate_840, 'ixversion': '8.40.0.277',
                                   'auth': None},
                     windows_850: {'originate': originate_850, 'terminate': terminate_850, 'ixversion': '8.50.115.333',
                                   'auth': None},
                     windows_900: {'originate': originate_900, 'terminate': terminate_900, 'ixversion': '9.00.0.347',
                                   'auth': None},
                     localhost_900: {'originate': originate_900, 'terminate': terminate_900, 'ixversion': '9.00.0.347',
                                     'crt': None},
                     linux_850: {'originate': originate_850, 'terminate': terminate_850, 'ixversion': '8.50.115.333',
                                 'auth': None},
                     linux_900: {'originate': originate_900, 'terminate': terminate_900, 'ixversion': '9.00.0.347',
                                 'auth': None}}

server_ = [localhost_900]
license_server_ = '192.168.42.61'
api_key_ = 'YWRtaW58elR0MTNZR0NPRTYyREpubGFWOXJzT3R6Ry13PQ=='
crt_file_ = 'C:/Program Files (x86)/Ixia/ixLoadGateway/certificate/ixload_certificate.crt'


def pytest_addoption(parser):
    parser.addoption('--server', action='append', default=server_, help='REST server IP')
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
    metafunc.parametrize('server', metafunc.config.getoption('--server'), indirect=True)


def _get_cli_or_property(request, server, option):
    if request.config.getoption('--' + option):
        return request.config.getoption('--' + option)
    else:
        return server_properties[server].get(option, None)
