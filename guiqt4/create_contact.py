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
from ui_create_contact import Ui_FredWindow
from shared_fnc import *

class FredWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.create_contact_street.horizontalHeader().resizeSection(0,320)
        self._street_item = QtCore.QString()

    def street_current_changed(self,r,c,x,y):
        self._street_item = table_current_changed(self.ui.create_contact_street, r, c)

    def street_value_changed(self,r,c):
        self._street_item = table_value_changed(self.ui.create_contact_street, self._street_item, r, c, 3)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
