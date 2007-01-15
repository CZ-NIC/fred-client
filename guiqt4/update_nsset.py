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
from ui_update_nsset import Ui_FredWindow
from dns import FredWindowDNS
from shared_fnc import *

class FredWindow(QtGui.QWidget):
    'Create domain frame.'
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        for name in ('add_tech','rem_name','rem_tech'):
            widget = getattr(self.ui, name)
            widget.horizontalHeader().resizeSection(0,320)
            self.__dict__[name] = QtCore.QString()
        self.dns_sets = add_dns_sets(self.ui.frame_add_dns, FredWindowDNS)

    def add_tech_value_changed(self,r,c):
        self.add_tech = table_value_changed(self.ui.add_admin, self.add_tech, r, c)
    def add_tech_current_changed(self,r,c,x,y):
        self.add_tech = table_current_changed(self.ui.add_admin, r, c)

    def rem_tech_value_changed(self,r,c):
        self.rem_tech = table_value_changed(self.ui.rem_tech, self.rem_tech, r, c)
    def rem_tech_current_changed(self,r,c,x,y):
        self.rem_tech = table_current_changed(self.ui.rem_tech, r, c)

    def rem_name_value_changed(self,r,c):
        self.rem_name = table_value_changed(self.ui.rem_name, self.rem_name, r, c, 9)
    def rem_name_current_changed(self,r,c,x,y):
        self.rem_name = table_current_changed(self.ui.rem_name, r, c)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
