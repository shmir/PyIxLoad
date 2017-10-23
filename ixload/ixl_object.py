"""
Base classes and utilities to manage IxLoad (IXL).

:author: yoram@ignissoft.com
"""

from collections import OrderedDict

from trafficgenerator.tgn_object import TgnObject


class IxlObject(TgnObject):
    """ Base class for all IXN classes. """

    str_2_class = {}

    def __init__(self, **data):
        if data['parent']:
            self.repository = data['parent'].repository
        super(IxlObject, self).__init__(**data)

    def get_obj_class(self, obj_type):
        """
        :param obj_type: IXL object type.
        :return: object class if specific class else IxlObject.
        """

        return IxlObject.str_2_class.get(obj_type.lower(), IxlObject)

    def _create(self, **attributes):
        """ Create new object on IxLoad.

        :return: IXL object reference.
        """

        return self.api.new(self.obj_type(), **attributes)

    def command(self, command, *arguments, **attributes):
        if command != 'setResultDir':
            return self.api.selfCommand(self.obj_ref(), command, *arguments, **attributes)

    def set_attributes(self, **attributes):
        self.api.config(self.obj_ref(), **attributes)

    def get_attribute(self, attribute):
        """
        :param attribute: requested attributes.
        :return: attribute value.
        """

        return self.api.cget(self.obj_ref(), attribute)

    def get_list_attribute(self, attribute):
        """
        :return: attribute value as Python list.
        """
        return self.get_attribute(attribute).split()

    def get_children(self, *types):
        """ Read (getList) children from IXN.

        Use this method to align with current IXN configuration.

        :param types: list of requested children.
        :return: list of all children objects of the requested types.
        """

        children_objs = OrderedDict()
        for child_type in types:
            if child_type.endswith('List'):
                child_type = child_type[:-4]
                children_list = IxlList(self, child_type).get_items()
            else:
                children_list = self.get_list_attribute(child_type)
            children_objs.update(self._build_children_objs(child_type, children_list))
        return list(children_objs.values())

    def get_name(self):
        return self.get_attribute('name')

    def execute(self, command, *arguments):
        return self.api.execute(command, self.obj_ref(), *arguments)


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
