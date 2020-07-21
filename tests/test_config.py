
windows_840 = '192.168.65.68'
windows_850 = '192.168.65.94'
windows_900 = '192.168.15.25'
linux_850 = '192.168.65.87'
linux_900 = '192.168.65.69'

originate_840 = '192.168.42.174/1/1'
terminate_840 = '192.168.42.210/1/1'
originate_850 = '192.168.65.30/1/1'
terminate_850 = '192.168.65.120/1/1'
originate_900 = '192.168.65.50/1/1'
terminate_900 = '192.168.65.41/1/1'

api_key = 'YWRtaW58elR0MTNZR0NPRTYyREpubGFWOXJzT3R6Ry13PQ=='
crt_file = 'C:/Program Files (x86)/Ixia/ixLoadGateway/certificate/ixload_certificate.crt'

server_properties = {'windows_840': {'server': windows_840, 'originate': originate_840, 'terminate': terminate_840,
                                     'ixversion': '8.40.0.277', 'auth': None},
                     'windows_850': {'server': windows_850, 'originate': originate_850, 'terminate': terminate_850,
                                     'ixversion': '8.50.115.333', 'auth': None},
                     'windows_900': {'server': windows_900, 'originate': originate_900, 'terminate': terminate_900,
                                     'ixversion': '9.00.0.347', 'auth': None},
                     'linux_850': {'server': linux_850, 'originate': originate_850, 'terminate': terminate_850,
                                   'ixversion': '8.50.115.333', 'auth': None},
                     'linux_900': {'server': linux_900, 'originate': originate_900, 'terminate': terminate_900,
                                   'ixversion': '9.00.0.347', 'auth': None}}

license_server = '192.168.42.61'

# Default for options.
server = ['linux_900']
