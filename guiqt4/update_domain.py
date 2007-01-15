#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import sys
from PyQt4 import QtCore, QtGui
from ui_update_domain import Ui_FredWindow
from shared_fnc import *

class FredWindow(QtGui.QWidget):
    'Create domain frame.'
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.add_admin.horizontalHeader().resizeSection(0,320)
        self._add_admin_item = QtCore.QString()
        self.ui.rem_admin.horizontalHeader().resizeSection(0,320)
        self._rem_admin_item = QtCore.QString()

    def add_admin_value_changed(self,r,c):
        self._add_admin_item = table_value_changed(self.ui.add_admin, self._add_admin_item, r, c)
    def add_admin_current_changed(self,r,c,x,y):
        self._add_admin_item = table_current_changed(self.ui.add_admin, r, c)
    def rem_admin_value_changed(self,r,c):
        self._rem_admin_item = table_value_changed(self.ui.rem_admin, self._rem_admin_item, r, c)
    def rem_admin_current_changed(self,r,c,x,y):
        self._rem_admin_item = table_current_changed(self.ui.rem_admin, r, c)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
