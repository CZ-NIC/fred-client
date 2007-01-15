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
from ui_dns import Ui_FredWindow
from shared_fnc import *

class FredWindowDNS(QtGui.QWidget):

    def __init__(self, rpos, is_bold = 0, parent=None):
        'rpos = (pos/max)'
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.addr.horizontalHeader().resizeSection(0,320)
        self._addr_item = QtCore.QString()
        label = '%s [%d/%d]'%(self.ui.label_dns_name.text(), rpos[0], rpos[1])
        if is_bold: label = '<b>%s</b>'%label
        self.ui.label_dns_name.setText(label)
        self.setFixedSize(490,157)

    def addr_current_changed(self,r,c,x,y):
        self._addr_item = table_current_changed(self.ui.addr, r, c)

    def addr_value_changed(self,r,c):
        self._addr_item = table_value_changed(self.ui.addr, self._addr_item, r, c)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindowDNS((1,1),1)
    window.show()
    sys.exit(app.exec_())
