# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from ui_update_contact import Ui_FredWindow
from shared_fnc import *

class FredWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.ui.update_contact_street.horizontalHeader().resizeSection(0,294)
        self._street_item = QtCore.QString()

    def street_current_changed(self,r,c,x,y):
        self._street_item = table_current_changed(self.ui.update_contact_street, r, c)

    def street_value_changed(self,r,c):
        self._street_item = table_value_changed(self.ui.update_contact_street, self._street_item, r, c, 3)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
