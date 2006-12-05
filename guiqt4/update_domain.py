# -*- coding: utf-8 -*-
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
