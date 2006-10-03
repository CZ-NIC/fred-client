# -*- coding: utf-8 -*-

from qt import *
from shared_fnc import *
import _update_domain

class ccregWindow(_update_domain.ccregWindow):

    def __init__(self,parent = None,name = None,fl = 0):
        _update_domain.ccregWindow.__init__(self,parent,name,fl)
        self.add_admin.horizontalHeader().resizeSection(0,320)
        self._add_admin_item = None
        self.rem_admin.horizontalHeader().resizeSection(0,320)
        self._rem_admin_item = None

    def add_admin_current_changed(self,r,c):
        self._add_admin_item = table_current_changed(self.add_admin, r, c)
    def add_admin_value_changed(self,r,c):
        table_value_changed(self.add_admin, self._add_admin_item, r, c)

    def rem_admin_current_changed(self,r,c):
        self._rem_admin_item = table_current_changed(self.rem_admin, r, c)
    def rem_admin_value_changed(self,r,c):
        table_value_changed(self.rem_admin, self._rem_admin_item, r, c)
