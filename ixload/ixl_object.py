"""
Base classes and utilities to manage IxLoad (IXL).

:author: yoram@ignissoft.com
"""

import re
from collections import OrderedDict

from trafficgenerator.tgn_utils import is_true, TgnError
from trafficgenerator.tgn_object import TgnObject


def extract_ixn_obj_type_from_obj_ref(obj_ref):
    return re.search('.*/(.*)', obj_ref).group(1).split(':')[0]


class IxlObject(TgnObject):
    """ Base class for all IXN classes. """

    # Class level variables
    logger = None
    root = None
    api = None

    str_2_class = {}

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
        return self.api.selfCommand(self.obj_ref(), command, *arguments, **attributes)

    def set_attributes(self, **attributes):
        self.api.config(self.obj_ref(), **attributes)

    def get_attributes(self, *attributes):
        if not attributes:
            return self.get_all_attributes(self.obj_ref())
        attributes_values = {}
        for attribute in attributes:
            attributes_values[attribute] = self.get_attribute(attribute)
        return attributes_values

    def get_attribute(self, attribute):
        """
        :param attribute: requested attributes.
        :return: attribute value.
        :raise TgnError: if invalid attribute.
        """
        value = self.api.getAttribute(self.obj_ref(), attribute)
        # IXN returns '::ixNet::OK' for invalid attributes. We want error.
        if value == '::ixNet::OK':
            raise TgnError(self.obj_ref() + ' does not have attribute ' + attribute)
        return value

    def get_list_attribute(self, attribute):
        """
        :return: attribute value as Python list.
        """
        return self.api.getListAttribute(self.obj_ref(), attribute)

    def get_children(self, *types):
        """ Read (getList) children from IXN.

        Use this method to align with current IXN configuration.

        :param types: list of requested children.
        :return: list of all children objects of the requested types.
        """

        children_objs = OrderedDict()
        if not types:
            types = self.get_all_child_types(self.obj_ref())
        for child_type in types:
            children_list = self.api.getList(self.obj_ref(), child_type)
            children_objs.update(self._build_children_objs(child_type, children_list))
        return list(children_objs.values())

    def get_name(self):
        # self.get_attribute() will throw error in case name does not exists so we bypass it.
        name = self.api.getAttribute(self.obj_ref(), 'name')
        return name if name != '::ixNet::OK' else self.obj_ref()

    def get_enabled(self):
        enabled = self.api.getAttribute(self.obj_ref(), 'enabled')
        return is_true(enabled) if enabled != '::ixNet::OK' else True

    def set_enabled(self, enabled):
        self.set_attributes(enabled=enabled)

    def execute(self, command, *arguments):
        return self.api.execute(command, self.obj_ref(), *arguments)

    def help(self, objRef):
        output = self.api.help(self.obj_ref())
        children = None
        if 'Child Lists:' in output:
            children = output.split('Child Lists:')[1].split('Attributes:')[0].split('Execs:')[0]
        attributes = None
        if 'Attributes:' in output:
            attributes = output.split('Attributes:')[1].split('Execs:')[0]
        execs = None
        if 'Execs:':
            execs = output.split('Execs:')[1]
        return children.strip().split('\n'), attributes.strip().split('\n'), execs.strip().split('\n')

    def get_all_attributes(self, objRef):
        _, attributes, _ = self.help(objRef)
        attr_vals = {}
        for attribute in [attribute.strip().split()[0][1:] for attribute in attributes]:
            attr_vals[attribute] = self.get_attribute(attribute)
        return attr_vals

    def get_all_child_types(self, objRef):
        children, _, _ = self.help(objRef)
        return [attribute.strip().split()[0] for attribute in children]
