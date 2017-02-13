"""
:author: yoram@ignissoft.com
"""

from sys import platform
import posixpath
import imp


if platform == 'win32':
    py_tail = 'PythonScripts/lib/IxLoad.py'
else:
    py_tail = 'lib/PythonApi/IxNetwork.py'


class IxlPythonWrapper(object):

    def __init__(self, logger, ixl_install_dir):
        """ Init IXL Python package.

        :param looger: application logger, FFU.
        :param ixl_install_dir: full path to IXL installation directory up to (including) version number.
        :todo: Add logger to log IXL Python package commands only to create a clean Python script for debug.
        """

        super(self.__class__, self).__init__()
        ixn_python_module = posixpath.sep.join([ixl_install_dir, py_tail])
        self.ixl = imp.load_source('IxLoad', ixn_python_module).IxLoad()

    def connect(self, ip):
        return self.ixl.connect(ip)

    def new(self, obj_type, **attributes):
        return self.ixl.new(obj_type, **attributes)

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        return obj_ref.setResultDir('c:/temp/justTesting')
