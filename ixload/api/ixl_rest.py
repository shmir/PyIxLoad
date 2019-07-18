"""
@author yoram@ignissoft.com
"""


from ixload.api import IxRestUtils, IxLoadUtils


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

    def connect(self, ip, port=None, version='', auth=None):
        # note that is version is not supplied we will use v0.
        api_version = 'v1' if version > '8.5' else 'v0'
        port = port if port else (8443 if api_version == 'v1' else 8080)
        connection_url = '{}://{}:{}/'.format('https' if api_version == 'v1' else 'http', ip, port)
        self.connection = IxRestUtils.Connection(connection_url, api_version, version, auth['apikey'], auth['crt'])
        self.session_url = IxLoadUtils.createSession(self.connection)

    def disconnect(self):
        IxLoadUtils.deleteSession(self.connection, self.session_url)

    def new(self, obj_type, **attributes):
        if obj_type == 'ixTestController':
            return self.session_url
        elif obj_type == 'ixRepository':
            if 'name' in attributes:
                IxLoadUtils.loadRepository(self.connection, self.session_url, attributes['name'])
            return self.session_url + '/ixload'

    def cget(self, obj_ref, attribute=None):
        response = self.connection.httpGet(obj_ref)
        if attribute:
            return response.jsonOptions.get(attribute, None)
        else:
            response.jsonOptions.pop('links')
            return response.jsonOptions

    def config(self, obj_ref, **attributes):
        IxLoadUtils.performGenericPatch(self.connection, obj_ref, attributes)

    def get_children(self, parent, child_type=None):
        """ Read (getList) children from IXN.

        :param parent: parent object or reference.
        :param child_type: requested child type.
        :return: list of all children objects of the requested types.
        """

        parent_ref = parent if type(parent) is str else parent.ref
        if child_type:
            if child_type.endswith('List'):
                child_ref = parent_ref + '/' + child_type
                return [child_ref + '/' + str(o.objectID) for o in self.connection.httpGet(child_ref)]
            else:
                return [parent_ref + '/' + child_type]
        else:
            links = self.cget(parent, 'links')
            if links:
                return [parent_ref + '/' + link.jsonOptions['rel'] for link in links]

    def clear_chassis_chain(self, obj_ref):
        IxLoadUtils.clearChassisList(self.connection, self.session_url)

    def selfCommand(self, obj_ref, command, *arguments, **attributes):
        if command == 'write':
            IxLoadUtils.saveRepository(self.connection, self.session_url, attributes['destination'])
        elif command == 'releaseConfigWaitFinish':
            pass


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
