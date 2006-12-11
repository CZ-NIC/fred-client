# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from dns import FredWindowDNS
from ui_create_nsset import Ui_FredWindow
from shared_fnc import *

class FredWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.tech.horizontalHeader().resizeSection(0,320)
        self._tech_item = QtCore.QString()
        self.dns_sets = add_dns_sets(self.ui.frame_dns, FredWindowDNS, 2)

    def tech_current_changed(self,r,c,x,y):
        self._tech_item = table_current_changed(self.ui.tech, r, c)

    def tech_value_changed(self,r,c):
        self._tech_item = table_value_changed(self.ui.tech, self._tech_item, r, c)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
