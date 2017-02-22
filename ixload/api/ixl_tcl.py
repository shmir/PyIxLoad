"""
@author yoram@ignissoft.com
"""

from os import path
from sys import platform

from trafficgenerator.tgn_tcl import TgnTclWrapper, get_args_pairs

if platform == 'win32':
    pkgIndex_tail = 'TclScripts/bin/IxiaWish.tcl'
else:
    pkgIndex_tail = 'lib/IxTclNetwork/pkgIndex.tcl'


class IxlTclWrapper(TgnTclWrapper):

    def __init__(self, logger, ixl_install_dir, tcl_interp=None):
        super(self.__class__, self).__init__(logger, tcl_interp)
        self.source(path.join(ixl_install_dir, pkgIndex_tail))
        self.eval('package require IxLoadCsv')
        self.eval('package require statCollectorUtils')

    def ixlCommand(self, command, *arguments):
        return self.eval('IxLoad ' + command + ' ' + ' '.join(arguments))

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        str_arguments = ' '.join((str(a) for a in arguments))
        return self.eval(obj_ref + ' ' + command + ' ' + str_arguments + get_args_pairs(attributes))

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip='localhost', port='ignore'):
        return self.ixlCommand('connect ' + ip)

    def disconnect(self):
        self.ixlCommand('disconnect')

    def new(self, obj_type, **attributes):
        return self.ixlCommand('new ' + obj_type, get_args_pairs(attributes))

    def config(self, obj_ref, **attributes):
        self.selfCommand(obj_ref, 'config', get_args_pairs(attributes))

    def cget(self, obj_ref, attribute):
        return self.selfCommand(obj_ref, 'cget', '-' + attribute)
