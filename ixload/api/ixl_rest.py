"""
@author yoram@ignissoft.com
"""

import IxRestUtils
import IxLoadUtils


class IxlRestWrapper(object):

    def __init__(self, logger):
        """ Init IXL REST package.

        :param looger: application logger.
        """

        self.logger = logger
        IxLoadUtils.logger = logger
        IxRestUtils.logger = logger

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip, port, version):
        self.connection = IxRestUtils.getConnection(str(ip), str(port))
        self.session_url = IxLoadUtils.createSession(self.connection, str(version))

    def disconnect(self):
        IxLoadUtils.deleteSession(self.connection, self.session_url)

    def new(self, obj_type, **attributes):
        if obj_type == 'ixTestController':
            return self.session_url
        elif obj_type == 'ixRepository':
            if 'name' in attributes:
                IxLoadUtils.loadRepository(self.connection, self.session_url, attributes['name'])
            return self.session_url + '/ixload'

    def cget(self, obj_ref, attribute):
        response = self.connection.httpGet(obj_ref)
        return response.jsonOptions.get(attribute, None)

    def cgetList(self, obj_ref, attribute):
        response = self.connection.httpGet()
        a = self.cget(obj_ref, attribute)
        return a

    def config(self, obj_ref, **attributes):
        IxLoadUtils.performGenericPatch(self.connection, obj_ref, attributes)

    def get_children(self, parent, child_type):
        """ Read (getList) children from IXN.

        :param parent: parent object .
        :param child_type: requested child type.
        :return: list of all children objects of the requested types.
        """

        if child_type.endswith('List'):
            child_ref = parent.ref + '/' + child_type
            return [child_ref + '/' + str(o.objectID) for o in self.connection.httpGet(child_ref)]
        else:
            return [parent.ref + '/' + child_type]

    def clear_chassis_chain(self, obj_ref):
        IxLoadUtils.clearChassisList(self.connection, self.session_url)

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        if command == 'write':
            IxLoadUtils.saveRxf(self.connection, self.session_url, attributes['destination'])
        elif command == 'releaseConfigWaitFinish':
            pass
        elif command == 'setResultDir':
            self.config(obj_ref + '/ixload/test', outputDir=True, runResultDirFull=str(arguments[0]))


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
