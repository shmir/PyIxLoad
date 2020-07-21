"""
"""

import logging
from typing import Optional, Dict

from ixload.api import IxRestUtils, IxLoadUtils


class IxlRestWrapper:

    def __init__(self, logger: logging.Logger):
        """ Init IXL REST package.

        :param looger: application logger.
        """

        self.logger = logger
        IxLoadUtils.logger = logger
        IxRestUtils.logger = logger

        self.connection: Optional[IxRestUtils.Connection] = None
        self.session_url: str = ''

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip: str, port: Optional[int] = None, version: Optional[str] = None,
                auth: Optional[Dict[str, str]] = None) -> None:
        """ Connect to IxLoad gateway server and create session. """
        api_version = 'v1' if version > '8.5' else 'v0'
        default_port = 8443 if api_version == 'v1' else 8080
        port = port if port else default_port
        http_protocol = 'https' if api_version == 'v1' else 'http'
        connection_url = f'{http_protocol}://{ip}:{port}/'
        apikey = auth.get('apikey') if auth else None
        crt = auth.get('crt') if auth else None
        self.connection = IxRestUtils.Connection(connection_url, api_version, version, apikey, crt)
        self.session_url = IxLoadUtils.createSession(self.connection)

    def disconnect(self) -> None:
        """ Delete session and disconnect from IxLoad gateway server. """
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

    def clear_chassis_chain(self, _):
        IxLoadUtils.clearChassisList(self.connection, self.session_url)

    def self_command(self, obj_ref, command, *arguments, **attributes):
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
