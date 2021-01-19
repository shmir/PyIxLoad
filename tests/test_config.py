"""
Config file for pyixload testing.
"""
windows_910 = 'localhost'
linux_910 = '192.168.65.25'

originate_910 = '192.168.65.21/1/1'
terminate_910 = '192.168.65.44/1/1'

api_key = 'YWRtaW58elR0MTNZR0NPRTYyREpubGFWOXJzT3R6Ry13PQ=='
crt_file = 'C:/Program Files (x86)/Ixia/ixLoadGateway/certificate/ixload_certificate.crt'

server_properties = {'windows_910': {'server': windows_910, 'originate': originate_910, 'terminate': terminate_910,
                                     'version': '9.10.115.94', 'auth': None},
                     'linux_910': {'server': linux_910, 'originate': originate_910, 'terminate': terminate_910,
                                   'version': '9.10.115.94', 'auth': None}}

license_server = '192.168.42.61'
license_mode = 'Perpetual'

# Default for options.
api = ['rest']
server = ['windows_910']
