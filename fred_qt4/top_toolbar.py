#!/usr/bin/env python
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
from ui_top_toolbar import Ui_topToolbar

class TopToolbarWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_topToolbar()
        self.ui.setupUi(self)

    def check_domain(self):
        'Set panel to selected command Check domain'
        print self.check_domain.__doc__

    def info_domain(self):
        'Set panel to selected command Info domain'
        print self.info_domain.__doc__

    def create_domain(self):
        'Set panel to selected command Create domain'
        print self.create_domain.__doc__

    def update_domain(self):
        'Set panel to selected command Update domain'
        print self.update_domain.__doc__

    def renew_domain(self):
        'Set panel to selected command Renew domain'
        print self.renew_domain.__doc__

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = TopToolbarWindow()
    window.show()
    sys.exit(app.exec_())
