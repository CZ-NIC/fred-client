# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from ui_dns import Ui_FredWindow
from shared_fnc import *

class FredWindowDNS(QtGui.QWidget):

    def __init__(self, rpos, parent=None):
        'rpos = (pos/max)'
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.addr.horizontalHeader().resizeSection(0,320)
        self._addr_item = QtCore.QString()
        self.ui.label_dns_name.setText(self.ui.label_dns_name.text()+' [%d/%d]'%rpos)
        self.setFixedSize(490,157)

    def addr_current_changed(self,r,c,x,y):
        self._addr_item = table_current_changed(self.ui.addr, r, c)

    def addr_value_changed(self,r,c):
        self._addr_item = table_value_changed(self.ui.addr, self._addr_item, r, c)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindowDNS((1,1))
    window.show()
    sys.exit(app.exec_())
