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
from ui_command_create import Ui_CommandCreate

actions = ('Check', 'Info', 'Create', 'Update', 'Delete',
        'List', 'Transfer', 'Renew', 'Send AuthInfo',
        'Hello', 'Poll', 'Technical test')
objects = ('-', 'Contact', 'NSSET', 'Domain')

class FredCommandCreate(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_CommandCreate()
        self.ui.setupUi(self)
        # Fill QtGui.QComboBox:
        map(self.ui.cbox_action.addItem, actions)
        map(self.ui.cbox_object.addItem, objects)


    def changeAction(self, pos):
        'Change list of the actions'
        print 'changeAction:', pos #!!!

    def changeObject(self, pos):
        'Change list of the actions'
        print 'changeObject:', pos #!!!

    def pushRunButton(self):
        'Run selected action'
        print 'Button Run has been pressed' #!!!


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = FredCommandCreate()
    window.show()
    sys.exit(app.exec_())
