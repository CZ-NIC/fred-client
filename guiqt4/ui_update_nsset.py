# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_nsset.ui'
#
# Created: Mon Jun 25 12:50:17 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,574,1068).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,470,160,20))
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")

        self.frame_add_dns = QtGui.QFrame(FredWindow)
        self.frame_add_dns.setGeometry(QtCore.QRect(10,190,530,270))
        self.frame_add_dns.setFrameShape(QtGui.QFrame.Panel)
        self.frame_add_dns.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_add_dns.setObjectName("frame_add_dns")

        self.line1_2 = QtGui.QFrame(FredWindow)
        self.line1_2.setGeometry(QtCore.QRect(10,140,530,20))
        self.line1_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2.setObjectName("line1_2")

        self.textLabel9 = QtGui.QLabel(FredWindow)
        self.textLabel9.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel9.setWordWrap(True)
        self.textLabel9.setObjectName("textLabel9")

        self.textLabel10 = QtGui.QLabel(FredWindow)
        self.textLabel10.setGeometry(QtCore.QRect(10,160,530,21))
        self.textLabel10.setWordWrap(False)
        self.textLabel10.setObjectName("textLabel10")

        self.id = QtGui.QLineEdit(FredWindow)
        self.id.setGeometry(QtCore.QRect(180,110,360,22))
        self.id.setObjectName("id")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,610,530,30))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.textLabel7 = QtGui.QLabel(FredWindow)
        self.textLabel7.setGeometry(QtCore.QRect(10,910,530,21))
        self.textLabel7.setWordWrap(False)
        self.textLabel7.setObjectName("textLabel7")

        self.line1_2_2 = QtGui.QFrame(FredWindow)
        self.line1_2_2.setGeometry(QtCore.QRect(10,890,530,20))
        self.line1_2_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2_2.setObjectName("line1_2_2")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,770,160,100))
        self.textLabel4.setAlignment(QtCore.Qt.AlignTop)
        self.textLabel4.setWordWrap(True)
        self.textLabel4.setObjectName("textLabel4")

        self.line1 = QtGui.QFrame(FredWindow)
        self.line1.setGeometry(QtCore.QRect(10,590,530,20))
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setObjectName("line1")

        self.add_tech = QtGui.QTableWidget(FredWindow)
        self.add_tech.setGeometry(QtCore.QRect(180,470,360,110))
        self.add_tech.setFrameShape(QtGui.QFrame.StyledPanel)
        self.add_tech.setFrameShadow(QtGui.QFrame.Sunken)
        self.add_tech.setShowGrid(True)
        self.add_tech.setObjectName("add_tech")

        self.rem_tech = QtGui.QTableWidget(FredWindow)
        self.rem_tech.setGeometry(QtCore.QRect(180,770,360,110))
        self.rem_tech.setFrameShape(QtGui.QFrame.StyledPanel)
        self.rem_tech.setFrameShadow(QtGui.QFrame.Sunken)
        self.rem_tech.setShowGrid(True)
        self.rem_tech.setObjectName("rem_tech")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,650,160,100))
        self.textLabel5.setAlignment(QtCore.Qt.AlignTop)
        self.textLabel5.setWordWrap(True)
        self.textLabel5.setObjectName("textLabel5")

        self.rem_name = QtGui.QTableWidget(FredWindow)
        self.rem_name.setGeometry(QtCore.QRect(180,650,360,110))
        self.rem_name.setFrameShape(QtGui.QFrame.StyledPanel)
        self.rem_name.setFrameShadow(QtGui.QFrame.Sunken)
        self.rem_name.setShowGrid(True)
        self.rem_name.setObjectName("rem_name")

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")

        self.line1_2_2_2 = QtGui.QFrame(FredWindow)
        self.line1_2_2_2.setGeometry(QtCore.QRect(10,1000,530,20))
        self.line1_2_2_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QtGui.QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1_2_2_2.setObjectName("line1_2_2_2")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(10,1020,160,20))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.cltrid = QtGui.QLineEdit(FredWindow)
        self.cltrid.setGeometry(QtCore.QRect(180,1020,360,22))
        self.cltrid.setObjectName("cltrid")

        self.textLabel8 = QtGui.QLabel(FredWindow)
        self.textLabel8.setGeometry(QtCore.QRect(10,940,160,20))
        self.textLabel8.setWordWrap(False)
        self.textLabel8.setObjectName("textLabel8")

        self.textLabel8_2 = QtGui.QLabel(FredWindow)
        self.textLabel8_2.setGeometry(QtCore.QRect(10,970,160,20))
        self.textLabel8_2.setWordWrap(False)
        self.textLabel8_2.setObjectName("textLabel8_2")

        self.reportlevel = QtGui.QLineEdit(FredWindow)
        self.reportlevel.setGeometry(QtCore.QRect(180,970,360,22))
        self.reportlevel.setObjectName("reportlevel")

        self.auth_info = QtGui.QLineEdit(FredWindow)
        self.auth_info.setGeometry(QtCore.QRect(180,940,360,22))
        self.auth_info.setObjectName("auth_info")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.add_tech,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.add_tech_current_changed)
        QtCore.QObject.connect(self.add_tech,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.add_tech_value_changed)
        QtCore.QObject.connect(self.rem_name,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.rem_name_current_changed)
        QtCore.QObject.connect(self.rem_name,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.rem_name_value_changed)
        QtCore.QObject.connect(self.rem_tech,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.rem_tech_current_changed)
        QtCore.QObject.connect(self.rem_tech,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.rem_tech_value_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.id,self.add_tech)
        FredWindow.setTabOrder(self.add_tech,self.rem_name)
        FredWindow.setTabOrder(self.rem_name,self.rem_tech)
        FredWindow.setTabOrder(self.rem_tech,self.auth_info)
        FredWindow.setTabOrder(self.auth_info,self.reportlevel)
        FredWindow.setTabOrder(self.reportlevel,self.cltrid)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Update NSSET panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "technical contact", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel9.setText(QtGui.QApplication.translate("FredWindow", "<h2>update_nsset</h2>\n"
        "The EPP \"update\" command is used to update an instance of an existing object.\n"
        "   Names what are not included into disclose list are set to opposite value of the disclose flag value.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel10.setText(QtGui.QApplication.translate("FredWindow", "<h3>Add</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "<h3>Remove</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel7.setText(QtGui.QApplication.translate("FredWindow", "<h3>Change</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "technical contact", None, QtGui.QApplication.UnicodeUTF8))
        self.add_tech.setRowCount(1)
        self.add_tech.clear()
        self.add_tech.setColumnCount(1)
        self.add_tech.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "technical contact", None, QtGui.QApplication.UnicodeUTF8))
        self.add_tech.setHorizontalHeaderItem(0,headerItem)
        self.rem_tech.setRowCount(1)
        self.rem_tech.clear()
        self.rem_tech.setColumnCount(1)
        self.rem_tech.setRowCount(1)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("FredWindow", "technical contact", None, QtGui.QApplication.UnicodeUTF8))
        self.rem_tech.setHorizontalHeaderItem(0,headerItem1)
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "dns name<br>(max 9 names)", None, QtGui.QApplication.UnicodeUTF8))
        self.rem_name.setRowCount(1)
        self.rem_name.clear()
        self.rem_name.setColumnCount(1)
        self.rem_name.setRowCount(1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("FredWindow", "dns name", None, QtGui.QApplication.UnicodeUTF8))
        self.rem_name.setHorizontalHeaderItem(0,headerItem2)
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "<b>NSSET ID</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8.setText(QtGui.QApplication.translate("FredWindow", "auth. for transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8_2.setText(QtGui.QApplication.translate("FredWindow", "reportlevel", None, QtGui.QApplication.UnicodeUTF8))

