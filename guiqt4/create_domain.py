# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from ui_create_domain import Ui_FredWindow
from shared_fnc import *

class FredWindow(QtGui.QWidget):
    'Create domain frame.'
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.admin.horizontalHeader().resizeSection(0,320)
        self._admin_item = QtCore.QString()

    def admin_value_changed(self,r,c):
        self._admin_item = table_value_changed(self.ui.admin, self._admin_item, r, c)

    def admin_current_changed(self,r,c,x,y):
        self._admin_item = table_current_changed(self.ui.admin, r, c)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
