"""
@author yoram@ignissoft.com
"""

import os
from sys import platform
from collections import OrderedDict

from trafficgenerator.tgn_tcl import TgnTclWrapper, get_args_pairs, py_list_to_tcl_list

if platform == 'win32':
    pkgIndex_tail = 'TclScripts/bin/IxiaWish.tcl'
else:
    pkgIndex_tail = 'lib/pkgIndex.tcl'


class IxlTclWrapper(TgnTclWrapper):

    def __init__(self, logger, ixl_install_dir, tcl_interp=None):
        super(self.__class__, self).__init__(logger, tcl_interp)
        if platform != 'win32':
            self._linux_tcl_env(ixl_install_dir)
        self.source(os.path.join(ixl_install_dir, pkgIndex_tail))
        self.eval('package require IxLoadCsv')

    def ixlCommand(self, command, *arguments):
        return self.eval('IxLoad ' + command + ' ' + ' '.join(arguments))

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        str_arguments = ' '.join((str(a) for a in arguments))
        return self.eval(obj_ref + ' ' + command + ' ' + str_arguments + get_args_pairs(attributes))

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip='localhost', port='ignore', version='ignore'):
        self.ixlCommand('connect ' + ip)
        # In Linux MUST call statCollectorUtils AFTER connect.
        self.eval('package require statCollectorUtils')

    def disconnect(self):
        self.ixlCommand('disconnect')

    def new(self, obj_type, **attributes):
        return self.ixlCommand('new ' + obj_type, get_args_pairs(attributes))

    def config(self, obj_ref, **attributes):
        self.selfCommand(obj_ref, 'config', get_args_pairs(attributes))

    def cget(self, obj_ref, attribute):
        return self.selfCommand(obj_ref, 'cget', '-' + attribute)

    def cgetList(self, obj_ref, attribute):
        return self.cget(obj_ref, attribute).split()

    def get_children(self, parent, child_type):
        """ Read (getList) children from IXN.

        :param parent: parent object .
        :param child_type: requested child type.
        :return: list of all children objects of the requested types.
        """

        if child_type.endswith('List'):
            return IxlList(parent, child_type[:-4]).get_items()
        else:
            return self.cgetList(parent.ref, child_type)

    def clear_chassis_chain(self, obj_ref):
        for chassis in self.selfCommand(obj_ref, 'getChassisNames').split():
            self.selfCommand(obj_ref, 'deleteChassisByName', chassis)

    #
    # Private auxiliary methods.
    #

    def _linux_tcl_env(self, ixl_install_dir):
        self.logger('perform initialization equivalent to /opt/ixia/ixload/version/bin/ixloadtcl')
        uninstall_path = os.path.join(ixl_install_dir, 'Uninstall_IxLoadTclApi' + ixl_install_dir.split('/')[-1])
        properties_file = os.path.join(uninstall_path, 'installvariables.properties')
        with open(properties_file, 'r') as f:
            properties = dict(line.split('=') for line in f if len(line.split('=')) == 2)
        ixia_version = properties['PRODUCT_VERSION_IXOS'].strip()
        ixos_api_dir = os.path.join(ixl_install_dir, '../../ixos-api', ixia_version)
        self.eval('set dir ' + os.path.join(ixl_install_dir, 'lib'))
        self.eval('set ::env(IXIA_VERSION) ' + ixia_version)
        self.eval('set ::env(IXL_libs) ' + ixl_install_dir)
        self.eval('set ::env(IXOS_libs) ' + ixos_api_dir)
        tcl_lib_path = []
        for ixia_dir in [ixl_install_dir, ixos_api_dir]:
            for root, subdirs, _ in os.walk(ixia_dir):
                for subdir in subdirs:
                    full_path = os.path.join(root, subdir)
                    if os.path.exists(os.path.join(full_path, 'pkgIndex.tcl')):
                        tcl_lib_path.append(full_path)
        self.eval('set ::env(TCLLIBPATH) ' + py_list_to_tcl_list(tcl_lib_path))


class IxlList(object):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def get_index_count(self):
        return int(self.parent.command(self.name + 'List.indexCount'))

    def get_items(self):
        items = []
        for item_id in range(self.get_index_count()):
            items.append(self.get_item(item_id))
        return items

    def get_item(self, item_id):
        return self.parent.command(self.name + 'List.getItem', item_id)

    def clear(self):
        self.parent.command(self.name + 'List.clear')

    def append(self, **attributes):
        self.parent.command(self.name + 'List.appendItem', **attributes)
