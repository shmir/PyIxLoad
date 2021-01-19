"""
Base classes and utilities to manage IxLoad (IXL).
"""
from __future__ import annotations
from collections import OrderedDict
from typing import List, Type, Optional, Dict

from trafficgenerator.tgn_object import TgnObject


class IxlObject(TgnObject):
    """ Base class for all IXN classes. """

    str_2_class = {}

    def __init__(self, parent: Optional[IxlObject], **data: str):
        if parent and hasattr(parent, 'repository'):
            self.repository = parent.repository
        super().__init__(parent, **data)

    def get_obj_class(self, obj_type: str) -> Type[IxlObject]:
        """ Returns object class if specific class else IxlObject.

        :param obj_type: IXL object type.
        """
        return IxlObject.str_2_class.get(obj_type.lower(), IxlObject)

    def _create(self, **attributes: str) -> str:
        """ Creates new object on IxLoad.

        :return: IXL object reference.
        """
        return self.api.new(self.type, **attributes)

    def command(self, command, *arguments, **attributes):
        return self.api.self_command(self.ref, command, *arguments, **attributes)

    def set_attributes(self, **attributes: str) -> None:
        """ Set attributes. """
        self.api.config(self.ref, **attributes)

    def get_attributes(self) -> Dict[str, str]:
        """ Get all attributes values for the object. """
        return self.api.cget(self.ref)

    def get_attribute(self, attribute) -> str:
        """ Get attribute value.

        :param attribute: requested attribute.
        """
        return self.api.cget(self.ref, attribute)

    def get_children(self, *types: str) -> List[IxlObject]:
        """ Read (getList) children from IXN.

        Use this method to align with current IXN configuration.

        :param types: list of requested children.
        """
        children_objects = OrderedDict()
        for child_type in types:
            children_objects.update(self._build_children_objs(child_type.replace('List', ''),
                                                              self.api.get_children(self, child_type)))
        return list(children_objects.values())

    def get_name(self):
        name = self.get_attribute('name')
        self._data['name'] = name if name else self.ref
        return self._data['name']

    def execute(self, command, *arguments):
        return self.api.execute(command, self.obj_ref(), *arguments)

    def get_objects_from_attribute(self, attribute: str) -> List[TgnObject]:
        pass
