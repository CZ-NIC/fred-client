# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_nsset.ui'
#
# Created: Mon Jun 25 12:50:06 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,574,663).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel1.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel1.setWordWrap(True)
        self.textLabel1.setObjectName("textLabel1")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,140,160,20))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,250,160,20))
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(10,560,160,20))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.auth_info = QtGui.QLineEdit(FredWindow)
        self.auth_info.setGeometry(QtCore.QRect(180,560,360,22))
        self.auth_info.setObjectName("auth_info")

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")

        self.frame_dns = QtGui.QFrame(FredWindow)
        self.frame_dns.setGeometry(QtCore.QRect(10,280,530,270))
        self.frame_dns.setFrameShape(QtGui.QFrame.Panel)
        self.frame_dns.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_dns.setObjectName("frame_dns")

        self.id = QtGui.QLineEdit(FredWindow)
        self.id.setGeometry(QtCore.QRect(180,110,360,22))
        self.id.setObjectName("id")

        self.tech = QtGui.QTableWidget(FredWindow)
        self.tech.setGeometry(QtCore.QRect(180,140,360,110))
        self.tech.setShowGrid(True)
        self.tech.setObjectName("tech")

        self.textLabel5_2 = QtGui.QLabel(FredWindow)
        self.textLabel5_2.setGeometry(QtCore.QRect(10,620,160,20))
        self.textLabel5_2.setWordWrap(False)
        self.textLabel5_2.setObjectName("textLabel5_2")

        self.cltrid = QtGui.QLineEdit(FredWindow)
        self.cltrid.setGeometry(QtCore.QRect(180,620,360,22))
        self.cltrid.setObjectName("cltrid")

        self.reportlevel = QtGui.QLineEdit(FredWindow)
        self.reportlevel.setGeometry(QtCore.QRect(180,590,360,22))
        self.reportlevel.setObjectName("reportlevel")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,590,160,20))
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.tech,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.tech_current_changed)
        QtCore.QObject.connect(self.tech,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.tech_value_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.id,self.tech)
        FredWindow.setTabOrder(self.tech,self.auth_info)
        FredWindow.setTabOrder(self.auth_info,self.reportlevel)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Create NSSET panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "<h2>create_nsset</h2>\n"
        "The EPP \"create\" command is used to create an instance of an object.\n"
        "An object can be created for an indefinite period of time, or an\n"
        "object can be created for a specific validity period.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "<b>tech. contact</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "<b>dns</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "auth. for transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "<b>NSSET ID</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.tech.clear()
        self.tech.setColumnCount(1)
        self.tech.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.tech.setVerticalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("FredWindow", "contact", None, QtGui.QApplication.UnicodeUTF8))
        self.tech.setHorizontalHeaderItem(0,headerItem1)
        self.textLabel5_2.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "reportlevel", None, QtGui.QApplication.UnicodeUTF8))

