# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_domain.ui'
#
# Created: Mon Jun 25 10:48:40 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,574,526).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,140,160,20))
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,170,160,20))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,200,160,20))
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,230,160,20))
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")

        self.textLabel7 = QtGui.QLabel(FredWindow)
        self.textLabel7.setGeometry(QtCore.QRect(10,480,160,20))
        self.textLabel7.setWordWrap(False)
        self.textLabel7.setObjectName("textLabel7")

        self.groupBox2_2 = QtGui.QGroupBox(FredWindow)
        self.groupBox2_2.setGeometry(QtCore.QRect(180,230,360,90))
        self.groupBox2_2.setObjectName("groupBox2_2")

        self.textLabel8 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel8.setGeometry(QtCore.QRect(10,20,130,20))
        self.textLabel8.setWordWrap(False)
        self.textLabel8.setObjectName("textLabel8")

        self.textLabel9 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel9.setGeometry(QtCore.QRect(10,50,130,20))
        self.textLabel9.setWordWrap(False)
        self.textLabel9.setObjectName("textLabel9")

        self.period_num = QtGui.QLineEdit(self.groupBox2_2)
        self.period_num.setGeometry(QtCore.QRect(150,50,200,22))
        self.period_num.setObjectName("period_num")

        self.period_unit = QtGui.QComboBox(self.groupBox2_2)
        self.period_unit.setGeometry(QtCore.QRect(150,20,85,22))
        self.period_unit.setObjectName("period_unit")

        self.textLabel10 = QtGui.QLabel(FredWindow)
        self.textLabel10.setGeometry(QtCore.QRect(10,450,160,20))
        self.textLabel10.setWordWrap(False)
        self.textLabel10.setObjectName("textLabel10")

        self.textLabel11 = QtGui.QLabel(FredWindow)
        self.textLabel11.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel11.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel11.setWordWrap(True)
        self.textLabel11.setObjectName("textLabel11")

        self.name = QtGui.QLineEdit(FredWindow)
        self.name.setGeometry(QtCore.QRect(180,110,360,22))
        self.name.setObjectName("name")

        self.registrant = QtGui.QLineEdit(FredWindow)
        self.registrant.setGeometry(QtCore.QRect(180,140,360,22))
        self.registrant.setObjectName("registrant")

        self.auth_info = QtGui.QLineEdit(FredWindow)
        self.auth_info.setGeometry(QtCore.QRect(180,170,360,22))
        self.auth_info.setEchoMode(QtGui.QLineEdit.Normal)
        self.auth_info.setObjectName("auth_info")

        self.nsset = QtGui.QLineEdit(FredWindow)
        self.nsset.setGeometry(QtCore.QRect(180,200,360,22))
        self.nsset.setObjectName("nsset")

        self.admin = QtGui.QTableWidget(FredWindow)
        self.admin.setGeometry(QtCore.QRect(180,330,360,110))
        self.admin.setObjectName("admin")

        self.cltrid = QtGui.QLineEdit(FredWindow)
        self.cltrid.setGeometry(QtCore.QRect(180,480,360,22))
        self.cltrid.setObjectName("cltrid")

        self.textLabel12 = QtGui.QLabel(FredWindow)
        self.textLabel12.setGeometry(QtCore.QRect(330,450,210,20))
        self.textLabel12.setWordWrap(False)
        self.textLabel12.setObjectName("textLabel12")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(10,330,160,20))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.val_ex_date = QtGui.QDateEdit(FredWindow)
        self.val_ex_date.setEnabled(False)
        self.val_ex_date.setGeometry(QtCore.QRect(220,450,97,22))
        self.val_ex_date.setObjectName("val_ex_date")

        self.check_val_ex_date = QtGui.QCheckBox(FredWindow)
        self.check_val_ex_date.setGeometry(QtCore.QRect(180,450,30,20))
        self.check_val_ex_date.setObjectName("check_val_ex_date")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.check_val_ex_date,QtCore.SIGNAL("toggled(bool)"),self.val_ex_date.setEnabled)
        QtCore.QObject.connect(self.admin,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.admin_value_changed)
        QtCore.QObject.connect(self.admin,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.admin_current_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.name,self.registrant)
        FredWindow.setTabOrder(self.registrant,self.auth_info)
        FredWindow.setTabOrder(self.auth_info,self.nsset)
        FredWindow.setTabOrder(self.nsset,self.period_unit)
        FredWindow.setTabOrder(self.period_unit,self.period_num)
        FredWindow.setTabOrder(self.period_num,self.admin)
        FredWindow.setTabOrder(self.admin,self.check_val_ex_date)
        FredWindow.setTabOrder(self.check_val_ex_date,self.val_ex_date)
        FredWindow.setTabOrder(self.val_ex_date,self.cltrid)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Create Domain panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "<b>domain name</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "<b>registrant</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "auth. for transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "nsset", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "period", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel7.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox2_2.setTitle(QtGui.QApplication.translate("FredWindow", "period", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8.setText(QtGui.QApplication.translate("FredWindow", "<b>unit</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel9.setText(QtGui.QApplication.translate("FredWindow", "<b>number</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel10.setText(QtGui.QApplication.translate("FredWindow", "valExDate", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel11.setText(QtGui.QApplication.translate("FredWindow", "<h2>create_domain</h2>\n"
        "The EPP \"create\" command is used to create an instance of an object.\n"
        "An object can be created for an indefinite period of time, or an\n"
        "object can be created for a specific validity period.", None, QtGui.QApplication.UnicodeUTF8))
        self.nsset.setToolTip(QtGui.QApplication.translate("FredWindow", "CZ", None, QtGui.QApplication.UnicodeUTF8))
        self.nsset.setWhatsThis(QtGui.QApplication.translate("FredWindow", "pokus", None, QtGui.QApplication.UnicodeUTF8))
        self.admin.clear()
        self.admin.setColumnCount(1)
        self.admin.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.admin.setVerticalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("FredWindow", "admin", None, QtGui.QApplication.UnicodeUTF8))
        self.admin.setHorizontalHeaderItem(0,headerItem1)
        self.textLabel12.setText(QtGui.QApplication.translate("FredWindow", "(required for <b>enum</b> domains)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "admin", None, QtGui.QApplication.UnicodeUTF8))

