"""
Classes and utilities to manage IxLoad chassis.

@author yoram@ignissoft.com
"""

from ixload.api import IxLoadUtils


from ixload.ixl_object import IxlObject


class IxlChassisChain(IxlObject):

    def clear(self):
        self.api.clear_chassis_chain(self.ref)

    def append(self, ip):
        chassis_list = self.get_objects_or_children_by_type('chassisList')
        for chassis in chassis_list:
            if chassis.name == ip:
                return chassis
        chassis_id = IxLoadUtils.addChassisList(self.api.connection, self.api.session_url, [ip])[0]
        return IxlObject(parent=self, objRef=self.ref + '/chassisList/' + chassis_id, objType='chassisList',
                         name=ip)
