# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from ui_sources import Ui_FredWindow

class FredWindow(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredWindow()
    window.show()
    sys.exit(app.exec_())
