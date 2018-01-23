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

        return self.api.cgetList(self.obj_ref(), attribute)

    def get_children(self, *types):
        """ Read (getList) children from IXN.

        Use this method to align with current IXN configuration.

        :param types: list of requested children.
        :return: list of all children objects of the requested types.
        """

        children_objs = OrderedDict()
        for child_type in types:
            children_objs.update(self._build_children_objs(child_type.replace('List', ''),
                                                           self.api.get_children(self, child_type)))
        return list(children_objs.values())

    def get_name(self):
        name = self.get_attribute('name')
        self._data['name'] = name if name else self.ref
        return self._data['name']

    def execute(self, command, *arguments):
        return self.api.execute(command, self.obj_ref(), *arguments)
