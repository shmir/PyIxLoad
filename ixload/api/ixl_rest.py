"""
@author yoram@ignissoft.com
"""

from os import path
from sys import platform

from trafficgenerator.tgn_tcl import get_args_pairs

if platform == 'win32':
    utils_sub_dir = 'RestScripts/Utils'
else:
    utils_sub_dir = 'lib/IxTclNetwork/pkgIndex.tcl'


class IxlRestWrapper(object):

    def __init__(self, logger):
        """ Init IXL REST package.

        :param looger: application logger.
        """

        self.logger = logger

    def ixlCommand(self, command, *arguments):
        return self.eval('IxLoad ' + command + ' ' + ' '.join(arguments))

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        if 'testList.getItem' in command:
            pass

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip, port):
        self.api_url = 'http://{}:{}/api/v0/'.format(ip, port)
        self.connection = self.IxRestUtils.getConnection(ip, port)

    def disconnect(self):
        self.IxLoadUtils.deleteSession(self.connection, self.session_url)

    def new(self, obj_type, **attributes):
        if obj_type == 'ixTestController':
            self.session_url = self.IxLoadUtils.createSession(self.connection, str(self.api_version))
            return self.session_url
        elif obj_type == 'ixRepository':
            resource_url = self.api_url + 'resources'
            upload_path = 'c:/temp/ixLoadGatewayUploads' + path.split(attributes['name'])[1]
            self.IxLoadUtils.uploadFile(self.connection, resource_url, attributes['name'], upload_path)
            self.IxLoadUtils.loadRepository(self.connection, self.session_url, upload_path)

    def config(self, obj_ref, **attributes):
        self.selfCommand(obj_ref, 'config', get_args_pairs(attributes))
