"""
Classes and utilities to manage IxLoad chassis.

@author yoram@ignissoft.com
"""

from ixload.api import IxLoadUtils


from ixload.ixl_object import IxlObject


class IxlChassisChain(IxlObject):

    def clear(self):
        self.api.clear_chassis_chain(self.ref)

    def append(self, chassis):
        chassis_list = self.get_children('chassisList')
        chassis_id = 0
        for index, name in enumerate(chassis_list):
            if name == chassis:
                chassis_id = index + 1
        if not chassis_id:
            chassis_id = IxLoadUtils.addChassisList(self.api.connection, self.api.session_url, [chassis])[0]
        return chassis_id
