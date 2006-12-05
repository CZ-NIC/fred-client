# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dns.ui'
#
# Created: Tue Dec  5 15:17:03 2006
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,510,157).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel_address = QtGui.QLabel(FredWindow)
        self.textLabel_address.setGeometry(QtCore.QRect(10,40,130,20))
        self.textLabel_address.setWordWrap(False)
        self.textLabel_address.setObjectName("textLabel_address")

        self.name = QtGui.QLineEdit(FredWindow)
        self.name.setGeometry(QtCore.QRect(150,10,340,22))
        self.name.setObjectName("name")

        self.label_dns_name = QtGui.QLabel(FredWindow)
        self.label_dns_name.setGeometry(QtCore.QRect(10,12,130,20))
        self.label_dns_name.setWordWrap(False)
        self.label_dns_name.setObjectName("label_dns_name")

        self.addr = QtGui.QTableWidget(FredWindow)
        self.addr.setGeometry(QtCore.QRect(150,40,340,110))
        self.addr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.addr.setFrameShadow(QtGui.QFrame.Sunken)
        self.addr.setShowGrid(True)
        self.addr.setObjectName("addr")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.addr,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.addr_current_changed)
        QtCore.QObject.connect(self.addr,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.addr_value_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "dns", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel_address.setText(QtGui.QApplication.translate("FredWindow", "address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_dns_name.setText(QtGui.QApplication.translate("FredWindow", "dns name", None, QtGui.QApplication.UnicodeUTF8))
        self.addr.setRowCount(1)
        self.addr.clear()
        self.addr.setColumnCount(1)
        self.addr.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "address", None, QtGui.QApplication.UnicodeUTF8))
        self.addr.setHorizontalHeaderItem(0,headerItem)

