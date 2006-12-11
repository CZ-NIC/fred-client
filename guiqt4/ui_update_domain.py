# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_domain.ui'
#
# Created: Mon Dec 11 13:52:26 2006
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,574,725).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel2.setWordWrap(True)
        self.textLabel2.setObjectName("textLabel2")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,160,530,21))
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,190,160,20))
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")

        self.line1 = QtGui.QFrame(FredWindow)
        self.line1.setGeometry(QtCore.QRect(10,140,530,20))
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setObjectName("line1")

        self.name = QtGui.QLineEdit(FredWindow)
        self.name.setGeometry(QtCore.QRect(180,110,360,22))
        self.name.setObjectName("name")

        self.textLabel7 = QtGui.QLabel(FredWindow)
        self.textLabel7.setGeometry(QtCore.QRect(10,360,160,20))
        self.textLabel7.setWordWrap(False)
        self.textLabel7.setObjectName("textLabel7")

        self.line2 = QtGui.QFrame(FredWindow)
        self.line2.setGeometry(QtCore.QRect(10,310,530,20))
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setObjectName("line2")

        self.textLabel8 = QtGui.QLabel(FredWindow)
        self.textLabel8.setGeometry(QtCore.QRect(10,500,530,21))
        self.textLabel8.setWordWrap(False)
        self.textLabel8.setObjectName("textLabel8")

        self.textLabel9 = QtGui.QLabel(FredWindow)
        self.textLabel9.setGeometry(QtCore.QRect(10,640,160,20))
        self.textLabel9.setWordWrap(False)
        self.textLabel9.setObjectName("textLabel9")

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(330,640,210,20))
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")

        self.textLabel11 = QtGui.QLabel(FredWindow)
        self.textLabel11.setGeometry(QtCore.QRect(10,530,160,20))
        self.textLabel11.setWordWrap(False)
        self.textLabel11.setObjectName("textLabel11")

        self.line3 = QtGui.QFrame(FredWindow)
        self.line3.setGeometry(QtCore.QRect(10,480,530,20))
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setObjectName("line3")

        self.check_val_ex_date = QtGui.QCheckBox(FredWindow)
        self.check_val_ex_date.setGeometry(QtCore.QRect(180,640,30,20))
        self.check_val_ex_date.setObjectName("check_val_ex_date")

        self.cltrid = QtGui.QLineEdit(FredWindow)
        self.cltrid.setGeometry(QtCore.QRect(180,670,360,22))
        self.cltrid.setObjectName("cltrid")

        self.textLabel10 = QtGui.QLabel(FredWindow)
        self.textLabel10.setGeometry(QtCore.QRect(10,670,160,20))
        self.textLabel10.setWordWrap(False)
        self.textLabel10.setObjectName("textLabel10")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(10,330,530,30))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.line4 = QtGui.QFrame(FredWindow)
        self.line4.setGeometry(QtCore.QRect(10,620,530,20))
        self.line4.setFrameShape(QtGui.QFrame.HLine)
        self.line4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line4.setFrameShape(QtGui.QFrame.HLine)
        self.line4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line4.setObjectName("line4")

        self.textLabel12 = QtGui.QLabel(FredWindow)
        self.textLabel12.setGeometry(QtCore.QRect(10,560,160,20))
        self.textLabel12.setWordWrap(False)
        self.textLabel12.setObjectName("textLabel12")

        self.val_ex_date = QtGui.QDateEdit(FredWindow)
        self.val_ex_date.setEnabled(False)
        self.val_ex_date.setGeometry(QtCore.QRect(220,640,97,22))
        self.val_ex_date.setObjectName("val_ex_date")

        self.add_admin = QtGui.QTableWidget(FredWindow)
        self.add_admin.setGeometry(QtCore.QRect(180,190,360,110))
        self.add_admin.setFrameShape(QtGui.QFrame.StyledPanel)
        self.add_admin.setFrameShadow(QtGui.QFrame.Sunken)
        self.add_admin.setShowGrid(True)
        self.add_admin.setObjectName("add_admin")

        self.rem_admin = QtGui.QTableWidget(FredWindow)
        self.rem_admin.setGeometry(QtCore.QRect(180,360,360,110))
        self.rem_admin.setFrameShape(QtGui.QFrame.StyledPanel)
        self.rem_admin.setFrameShadow(QtGui.QFrame.Sunken)
        self.rem_admin.setShowGrid(True)
        self.rem_admin.setObjectName("rem_admin")

        self.chg_registrant = QtGui.QLineEdit(FredWindow)
        self.chg_registrant.setGeometry(QtCore.QRect(180,560,360,22))
        self.chg_registrant.setObjectName("chg_registrant")

        self.chg_nsset = QtGui.QLineEdit(FredWindow)
        self.chg_nsset.setGeometry(QtCore.QRect(180,530,360,22))
        self.chg_nsset.setObjectName("chg_nsset")

        self.chg_auth_info = QtGui.QLineEdit(FredWindow)
        self.chg_auth_info.setGeometry(QtCore.QRect(180,590,360,22))
        self.chg_auth_info.setObjectName("chg_auth_info")

        self.textLabel13 = QtGui.QLabel(FredWindow)
        self.textLabel13.setGeometry(QtCore.QRect(10,590,160,20))
        self.textLabel13.setWordWrap(False)
        self.textLabel13.setObjectName("textLabel13")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.add_admin,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.add_admin_value_changed)
        QtCore.QObject.connect(self.add_admin,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.add_admin_current_changed)
        QtCore.QObject.connect(self.rem_admin,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.rem_admin_current_changed)
        QtCore.QObject.connect(self.rem_admin,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.rem_admin_value_changed)
        QtCore.QObject.connect(self.check_val_ex_date,QtCore.SIGNAL("toggled(bool)"),self.val_ex_date.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.name,self.add_admin)
        FredWindow.setTabOrder(self.add_admin,self.rem_admin)
        FredWindow.setTabOrder(self.rem_admin,self.chg_nsset)
        FredWindow.setTabOrder(self.chg_nsset,self.chg_registrant)
        FredWindow.setTabOrder(self.chg_registrant,self.chg_auth_info)
        FredWindow.setTabOrder(self.chg_auth_info,self.check_val_ex_date)
        FredWindow.setTabOrder(self.check_val_ex_date,self.val_ex_date)
        FredWindow.setTabOrder(self.val_ex_date,self.cltrid)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Update domain panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "<h2>update_domain</h2>\n"
        "The EPP \"update\" command is used to update an instance of an existing object.\n"
        "   Names what are not included into disclose list are set to opposite value of the disclose flag value.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "<b>domain name</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "<h3>Add</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "admin handle", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel7.setText(QtGui.QApplication.translate("FredWindow", "admin handle", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8.setText(QtGui.QApplication.translate("FredWindow", "<h3>Change</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel9.setText(QtGui.QApplication.translate("FredWindow", "valExDate", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "(required for <b>enum</b> domains)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel11.setText(QtGui.QApplication.translate("FredWindow", "nsset", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel10.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "<h3>Remove</h3>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel12.setText(QtGui.QApplication.translate("FredWindow", "registrant", None, QtGui.QApplication.UnicodeUTF8))
        self.add_admin.setRowCount(1)
        self.add_admin.clear()
        self.add_admin.setColumnCount(1)
        self.add_admin.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "admin", None, QtGui.QApplication.UnicodeUTF8))
        self.add_admin.setHorizontalHeaderItem(0,headerItem)
        self.rem_admin.setRowCount(1)
        self.rem_admin.clear()
        self.rem_admin.setColumnCount(1)
        self.rem_admin.setRowCount(1)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("FredWindow", "admin", None, QtGui.QApplication.UnicodeUTF8))
        self.rem_admin.setHorizontalHeaderItem(0,headerItem1)
        self.textLabel13.setText(QtGui.QApplication.translate("FredWindow", "pasword", None, QtGui.QApplication.UnicodeUTF8))

