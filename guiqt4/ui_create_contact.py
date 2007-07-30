# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_contact.ui'
#
# Created: Mon Jul 30 17:11:12 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,574,901).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(10,230,160,20))
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,170,160,20))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.textLabel7 = QtGui.QLabel(FredWindow)
        self.textLabel7.setGeometry(QtCore.QRect(10,510,160,20))
        self.textLabel7.setWordWrap(False)
        self.textLabel7.setObjectName("textLabel7")

        self.textLabel14 = QtGui.QLabel(FredWindow)
        self.textLabel14.setGeometry(QtCore.QRect(10,200,160,20))
        self.textLabel14.setWordWrap(False)
        self.textLabel14.setObjectName("textLabel14")

        self.textLabel15 = QtGui.QLabel(FredWindow)
        self.textLabel15.setGeometry(QtCore.QRect(10,260,160,20))
        self.textLabel15.setWordWrap(False)
        self.textLabel15.setObjectName("textLabel15")

        self.textLabel16 = QtGui.QLabel(FredWindow)
        self.textLabel16.setGeometry(QtCore.QRect(10,140,160,20))
        self.textLabel16.setWordWrap(False)
        self.textLabel16.setObjectName("textLabel16")

        self.textLabel18 = QtGui.QLabel(FredWindow)
        self.textLabel18.setGeometry(QtCore.QRect(10,290,160,20))
        self.textLabel18.setWordWrap(False)
        self.textLabel18.setObjectName("textLabel18")

        self.textLabel19 = QtGui.QLabel(FredWindow)
        self.textLabel19.setGeometry(QtCore.QRect(10,480,160,20))
        self.textLabel19.setWordWrap(False)
        self.textLabel19.setObjectName("textLabel19")

        self.textLabel20 = QtGui.QLabel(FredWindow)
        self.textLabel20.setGeometry(QtCore.QRect(380,480,160,20))
        self.textLabel20.setWordWrap(False)
        self.textLabel20.setObjectName("textLabel20")

        self.textLabel21 = QtGui.QLabel(FredWindow)
        self.textLabel21.setGeometry(QtCore.QRect(380,510,160,20))
        self.textLabel21.setWordWrap(False)
        self.textLabel21.setObjectName("textLabel21")

        self.textLabel17 = QtGui.QLabel(FredWindow)
        self.textLabel17.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel17.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel17.setWordWrap(True)
        self.textLabel17.setObjectName("textLabel17")

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")

        self.create_contact_id = QtGui.QLineEdit(FredWindow)
        self.create_contact_id.setGeometry(QtCore.QRect(180,110,360,22))
        self.create_contact_id.setObjectName("create_contact_id")

        self.create_contact_name = QtGui.QLineEdit(FredWindow)
        self.create_contact_name.setGeometry(QtCore.QRect(180,140,360,22))
        self.create_contact_name.setObjectName("create_contact_name")

        self.create_contact_email = QtGui.QLineEdit(FredWindow)
        self.create_contact_email.setGeometry(QtCore.QRect(180,170,360,22))
        self.create_contact_email.setObjectName("create_contact_email")

        self.create_contact_org = QtGui.QLineEdit(FredWindow)
        self.create_contact_org.setGeometry(QtCore.QRect(180,290,360,22))
        self.create_contact_org.setObjectName("create_contact_org")

        self.create_contact_street = QtGui.QTableWidget(FredWindow)
        self.create_contact_street.setGeometry(QtCore.QRect(180,320,360,87))
        self.create_contact_street.setShowGrid(True)
        self.create_contact_street.setObjectName("create_contact_street")

        self.create_contact_sp = QtGui.QLineEdit(FredWindow)
        self.create_contact_sp.setGeometry(QtCore.QRect(180,420,360,22))
        self.create_contact_sp.setObjectName("create_contact_sp")

        self.create_contact_pc = QtGui.QLineEdit(FredWindow)
        self.create_contact_pc.setGeometry(QtCore.QRect(180,450,360,22))
        self.create_contact_pc.setObjectName("create_contact_pc")

        self.create_contact_voice = QtGui.QLineEdit(FredWindow)
        self.create_contact_voice.setGeometry(QtCore.QRect(180,480,180,22))
        self.create_contact_voice.setObjectName("create_contact_voice")

        self.create_contact_fax = QtGui.QLineEdit(FredWindow)
        self.create_contact_fax.setGeometry(QtCore.QRect(180,510,180,22))
        self.create_contact_fax.setObjectName("create_contact_fax")

        self.create_contact_city = QtGui.QLineEdit(FredWindow)
        self.create_contact_city.setGeometry(QtCore.QRect(180,200,360,22))
        self.create_contact_city.setObjectName("create_contact_city")

        self.create_contact_cc = QtGui.QLineEdit(FredWindow)
        self.create_contact_cc.setGeometry(QtCore.QRect(180,230,50,22))
        self.create_contact_cc.setObjectName("create_contact_cc")

        self.create_contact_auth_info = QtGui.QLineEdit(FredWindow)
        self.create_contact_auth_info.setGeometry(QtCore.QRect(180,260,360,22))
        self.create_contact_auth_info.setEchoMode(QtGui.QLineEdit.Normal)
        self.create_contact_auth_info.setObjectName("create_contact_auth_info")

        self.disclose = QtGui.QCheckBox(FredWindow)
        self.disclose.setGeometry(QtCore.QRect(10,540,160,20))
        self.disclose.setObjectName("disclose")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,450,160,20))
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")

        self.textLabel10 = QtGui.QLabel(FredWindow)
        self.textLabel10.setGeometry(QtCore.QRect(10,420,160,20))
        self.textLabel10.setWordWrap(False)
        self.textLabel10.setObjectName("textLabel10")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,320,160,20))
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")

        self.groupBox2 = QtGui.QGroupBox(FredWindow)
        self.groupBox2.setEnabled(False)
        self.groupBox2.setGeometry(QtCore.QRect(180,540,360,151))
        self.groupBox2.setObjectName("groupBox2")

        self.textLabel22 = QtGui.QLabel(self.groupBox2)
        self.textLabel22.setGeometry(QtCore.QRect(10,20,160,20))
        self.textLabel22.setWordWrap(False)
        self.textLabel22.setObjectName("textLabel22")

        self.create_contact_disclose_flag = QtGui.QComboBox(self.groupBox2)
        self.create_contact_disclose_flag.setGeometry(QtCore.QRect(190,20,85,22))
        self.create_contact_disclose_flag.setObjectName("create_contact_disclose_flag")

        self.create_contact_disclose_email = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_email.setGeometry(QtCore.QRect(190,90,160,20))
        self.create_contact_disclose_email.setObjectName("create_contact_disclose_email")

        self.create_contact_disclose_notify_email = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_notify_email.setGeometry(QtCore.QRect(190,120,160,20))
        self.create_contact_disclose_notify_email.setObjectName("create_contact_disclose_notify_email")

        self.create_contact_disclose_voice = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_voice.setGeometry(QtCore.QRect(190,60,160,20))
        self.create_contact_disclose_voice.setObjectName("create_contact_disclose_voice")

        self.create_contact_disclose_vat = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_vat.setGeometry(QtCore.QRect(10,90,160,20))
        self.create_contact_disclose_vat.setObjectName("create_contact_disclose_vat")

        self.create_contact_disclose_ident = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_ident.setGeometry(QtCore.QRect(10,120,160,20))
        self.create_contact_disclose_ident.setObjectName("create_contact_disclose_ident")

        self.create_contact_disclose_fax = QtGui.QCheckBox(self.groupBox2)
        self.create_contact_disclose_fax.setGeometry(QtCore.QRect(10,60,160,20))
        self.create_contact_disclose_fax.setObjectName("create_contact_disclose_fax")

        self.groupBox2_2 = QtGui.QGroupBox(FredWindow)
        self.groupBox2_2.setGeometry(QtCore.QRect(180,730,360,90))
        self.groupBox2_2.setObjectName("groupBox2_2")

        self.textLabel12 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel12.setGeometry(QtCore.QRect(10,50,130,20))
        self.textLabel12.setWordWrap(False)
        self.textLabel12.setObjectName("textLabel12")

        self.textLabel13 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel13.setGeometry(QtCore.QRect(10,20,130,20))
        self.textLabel13.setWordWrap(False)
        self.textLabel13.setObjectName("textLabel13")

        self.create_contact_ssn_number = QtGui.QLineEdit(self.groupBox2_2)
        self.create_contact_ssn_number.setGeometry(QtCore.QRect(150,50,200,22))
        self.create_contact_ssn_number.setObjectName("create_contact_ssn_number")

        self.create_contact_ssn_type = QtGui.QComboBox(self.groupBox2_2)
        self.create_contact_ssn_type.setGeometry(QtCore.QRect(150,20,201,26))
        self.create_contact_ssn_type.setObjectName("create_contact_ssn_type")

        self.create_contact_notify_email = QtGui.QLineEdit(FredWindow)
        self.create_contact_notify_email.setGeometry(QtCore.QRect(180,830,360,22))
        self.create_contact_notify_email.setObjectName("create_contact_notify_email")

        self.create_contact_cltrid = QtGui.QLineEdit(FredWindow)
        self.create_contact_cltrid.setGeometry(QtCore.QRect(180,860,360,22))
        self.create_contact_cltrid.setObjectName("create_contact_cltrid")

        self.textLabel11 = QtGui.QLabel(FredWindow)
        self.textLabel11.setGeometry(QtCore.QRect(10,860,160,20))
        self.textLabel11.setWordWrap(False)
        self.textLabel11.setObjectName("textLabel11")

        self.textLabel8 = QtGui.QLabel(FredWindow)
        self.textLabel8.setGeometry(QtCore.QRect(10,830,160,20))
        self.textLabel8.setWordWrap(False)
        self.textLabel8.setObjectName("textLabel8")

        self.textLabel9 = QtGui.QLabel(FredWindow)
        self.textLabel9.setGeometry(QtCore.QRect(10,730,160,20))
        self.textLabel9.setWordWrap(False)
        self.textLabel9.setObjectName("textLabel9")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(10,700,160,20))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.create_contact_vat = QtGui.QLineEdit(FredWindow)
        self.create_contact_vat.setGeometry(QtCore.QRect(180,700,360,22))
        self.create_contact_vat.setObjectName("create_contact_vat")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.disclose,QtCore.SIGNAL("toggled(bool)"),self.groupBox2.setEnabled)
        QtCore.QObject.connect(self.create_contact_street,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.street_current_changed)
        QtCore.QObject.connect(self.create_contact_street,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.street_value_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.create_contact_id,self.create_contact_name)
        FredWindow.setTabOrder(self.create_contact_name,self.create_contact_email)
        FredWindow.setTabOrder(self.create_contact_email,self.create_contact_city)
        FredWindow.setTabOrder(self.create_contact_city,self.create_contact_cc)
        FredWindow.setTabOrder(self.create_contact_cc,self.create_contact_auth_info)
        FredWindow.setTabOrder(self.create_contact_auth_info,self.create_contact_org)
        FredWindow.setTabOrder(self.create_contact_org,self.create_contact_street)
        FredWindow.setTabOrder(self.create_contact_street,self.create_contact_sp)
        FredWindow.setTabOrder(self.create_contact_sp,self.create_contact_pc)
        FredWindow.setTabOrder(self.create_contact_pc,self.create_contact_voice)
        FredWindow.setTabOrder(self.create_contact_voice,self.create_contact_fax)
        FredWindow.setTabOrder(self.create_contact_fax,self.create_contact_disclose_flag)
        FredWindow.setTabOrder(self.create_contact_disclose_flag,self.create_contact_disclose_fax)
        FredWindow.setTabOrder(self.create_contact_disclose_fax,self.create_contact_disclose_voice)
        FredWindow.setTabOrder(self.create_contact_disclose_voice,self.create_contact_disclose_email)
        FredWindow.setTabOrder(self.create_contact_disclose_email,self.create_contact_vat)
        FredWindow.setTabOrder(self.create_contact_vat,self.create_contact_ssn_type)
        FredWindow.setTabOrder(self.create_contact_ssn_type,self.create_contact_ssn_number)
        FredWindow.setTabOrder(self.create_contact_ssn_number,self.create_contact_notify_email)
        FredWindow.setTabOrder(self.create_contact_notify_email,self.create_contact_cltrid)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Create Contact panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "<b>country code</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "<b>email</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel7.setText(QtGui.QApplication.translate("FredWindow", "fax", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel14.setText(QtGui.QApplication.translate("FredWindow", "<b>city</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel15.setText(QtGui.QApplication.translate("FredWindow", "auth. for transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel16.setText(QtGui.QApplication.translate("FredWindow", "<b>name</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel18.setText(QtGui.QApplication.translate("FredWindow", "organisation name", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel19.setText(QtGui.QApplication.translate("FredWindow", "voice (phone number)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel20.setText(QtGui.QApplication.translate("FredWindow", "+420.123456789", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel21.setText(QtGui.QApplication.translate("FredWindow", "+420.123456789", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel17.setText(QtGui.QApplication.translate("FredWindow", "<h2>create_contact</h2>\n"
        "The EPP \"create\" command is used to create an instance of an object.\n"
        "An object can be created for an indefinite period of time, or an\n"
        "object can be created for a specific validity period.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "<b>contact ID</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_org.setToolTip(QtGui.QApplication.translate("FredWindow", "CZ", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_org.setWhatsThis(QtGui.QApplication.translate("FredWindow", "pokus", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_street.setRowCount(1)
        self.create_contact_street.clear()
        self.create_contact_street.setColumnCount(1)
        self.create_contact_street.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "street", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_street.setHorizontalHeaderItem(0,headerItem)
        self.create_contact_cc.setText(QtGui.QApplication.translate("FredWindow", "CZ", None, QtGui.QApplication.UnicodeUTF8))
        self.disclose.setText(QtGui.QApplication.translate("FredWindow", "disclose", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "<b>postal code</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel10.setText(QtGui.QApplication.translate("FredWindow", "state or province", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "street (<b>required min. 1</b>)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel22.setText(QtGui.QApplication.translate("FredWindow", "disclose", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_email.setText(QtGui.QApplication.translate("FredWindow", "email", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_notify_email.setText(QtGui.QApplication.translate("FredWindow", "notify email", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_voice.setText(QtGui.QApplication.translate("FredWindow", "voice", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_vat.setText(QtGui.QApplication.translate("FredWindow", "VAT", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_ident.setText(QtGui.QApplication.translate("FredWindow", "ident", None, QtGui.QApplication.UnicodeUTF8))
        self.create_contact_disclose_fax.setText(QtGui.QApplication.translate("FredWindow", "fax", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox2_2.setTitle(QtGui.QApplication.translate("FredWindow", "social security number", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel12.setText(QtGui.QApplication.translate("FredWindow", "number", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel13.setText(QtGui.QApplication.translate("FredWindow", "type", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel11.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8.setText(QtGui.QApplication.translate("FredWindow", "notify email", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel9.setText(QtGui.QApplication.translate("FredWindow", "social security number", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "value-added tax", None, QtGui.QApplication.UnicodeUTF8))

