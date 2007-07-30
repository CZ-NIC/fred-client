# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_contact.ui'
#
# Created: Mon Jul 30 17:11:19 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,559,942).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.textLabel1 = QtGui.QLabel(FredWindow)
        self.textLabel1.setGeometry(QtCore.QRect(10,110,160,20))
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")

        self.update_contact_id = QtGui.QLineEdit(FredWindow)
        self.update_contact_id.setGeometry(QtCore.QRect(180,110,360,22))
        self.update_contact_id.setObjectName("update_contact_id")

        self.textLabel8 = QtGui.QLabel(FredWindow)
        self.textLabel8.setGeometry(QtCore.QRect(10,520,160,20))
        self.textLabel8.setWordWrap(False)
        self.textLabel8.setObjectName("textLabel8")

        self.update_contact_org = QtGui.QLineEdit(FredWindow)
        self.update_contact_org.setGeometry(QtCore.QRect(180,170,360,22))
        self.update_contact_org.setObjectName("update_contact_org")

        self.update_contact_name = QtGui.QLineEdit(FredWindow)
        self.update_contact_name.setGeometry(QtCore.QRect(180,140,360,22))
        self.update_contact_name.setObjectName("update_contact_name")

        self.update_contact_voice = QtGui.QLineEdit(FredWindow)
        self.update_contact_voice.setGeometry(QtCore.QRect(180,460,180,22))
        self.update_contact_voice.setObjectName("update_contact_voice")

        self.textLabel9 = QtGui.QLabel(FredWindow)
        self.textLabel9.setGeometry(QtCore.QRect(10,550,160,20))
        self.textLabel9.setWordWrap(False)
        self.textLabel9.setObjectName("textLabel9")

        self.textLabel7 = QtGui.QLabel(FredWindow)
        self.textLabel7.setGeometry(QtCore.QRect(380,460,160,20))
        self.textLabel7.setWordWrap(False)
        self.textLabel7.setObjectName("textLabel7")

        self.update_contact_email = QtGui.QLineEdit(FredWindow)
        self.update_contact_email.setGeometry(QtCore.QRect(180,520,360,22))
        self.update_contact_email.setObjectName("update_contact_email")

        self.update_contact_fax = QtGui.QLineEdit(FredWindow)
        self.update_contact_fax.setGeometry(QtCore.QRect(180,490,180,22))
        self.update_contact_fax.setObjectName("update_contact_fax")

        self.textLabel2 = QtGui.QLabel(FredWindow)
        self.textLabel2.setGeometry(QtCore.QRect(10,140,160,20))
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")

        self.disclose = QtGui.QCheckBox(FredWindow)
        self.disclose.setGeometry(QtCore.QRect(10,580,160,20))
        self.disclose.setObjectName("disclose")

        self.textLabel6 = QtGui.QLabel(FredWindow)
        self.textLabel6.setGeometry(QtCore.QRect(380,490,160,20))
        self.textLabel6.setWordWrap(False)
        self.textLabel6.setObjectName("textLabel6")

        self.update_contact_auth_info = QtGui.QLineEdit(FredWindow)
        self.update_contact_auth_info.setGeometry(QtCore.QRect(180,550,360,22))
        self.update_contact_auth_info.setEchoMode(QtGui.QLineEdit.Normal)
        self.update_contact_auth_info.setObjectName("update_contact_auth_info")

        self.textLabel5 = QtGui.QLabel(FredWindow)
        self.textLabel5.setGeometry(QtCore.QRect(10,460,160,20))
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")

        self.textLabel4 = QtGui.QLabel(FredWindow)
        self.textLabel4.setGeometry(QtCore.QRect(10,490,160,20))
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")

        self.textLabel18 = QtGui.QLabel(FredWindow)
        self.textLabel18.setGeometry(QtCore.QRect(10,10,530,90))
        self.textLabel18.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textLabel18.setWordWrap(True)
        self.textLabel18.setObjectName("textLabel18")

        self.textLabel3 = QtGui.QLabel(FredWindow)
        self.textLabel3.setGeometry(QtCore.QRect(10,170,160,20))
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")

        self.groupBox8 = QtGui.QGroupBox(FredWindow)
        self.groupBox8.setGeometry(QtCore.QRect(10,200,531,250))
        self.groupBox8.setObjectName("groupBox8")

        self.textLabel13 = QtGui.QLabel(self.groupBox8)
        self.textLabel13.setGeometry(QtCore.QRect(10,50,160,20))
        self.textLabel13.setWordWrap(False)
        self.textLabel13.setObjectName("textLabel13")

        self.textLabel16 = QtGui.QLabel(self.groupBox8)
        self.textLabel16.setGeometry(QtCore.QRect(10,180,160,20))
        self.textLabel16.setWordWrap(False)
        self.textLabel16.setObjectName("textLabel16")

        self.textLabel17 = QtGui.QLabel(self.groupBox8)
        self.textLabel17.setGeometry(QtCore.QRect(10,20,160,20))
        self.textLabel17.setWordWrap(False)
        self.textLabel17.setObjectName("textLabel17")

        self.update_contact_sp = QtGui.QLineEdit(self.groupBox8)
        self.update_contact_sp.setGeometry(QtCore.QRect(180,180,330,22))
        self.update_contact_sp.setObjectName("update_contact_sp")

        self.update_contact_pc = QtGui.QLineEdit(self.groupBox8)
        self.update_contact_pc.setGeometry(QtCore.QRect(180,210,330,22))
        self.update_contact_pc.setObjectName("update_contact_pc")

        self.update_contact_cc = QtGui.QLineEdit(self.groupBox8)
        self.update_contact_cc.setGeometry(QtCore.QRect(180,50,50,22))
        self.update_contact_cc.setObjectName("update_contact_cc")

        self.update_contact_city = QtGui.QLineEdit(self.groupBox8)
        self.update_contact_city.setGeometry(QtCore.QRect(180,20,330,22))
        self.update_contact_city.setObjectName("update_contact_city")

        self.update_contact_street = QtGui.QTableWidget(self.groupBox8)
        self.update_contact_street.setGeometry(QtCore.QRect(180,80,330,87))
        self.update_contact_street.setShowGrid(True)
        self.update_contact_street.setObjectName("update_contact_street")

        self.textLabel14 = QtGui.QLabel(self.groupBox8)
        self.textLabel14.setGeometry(QtCore.QRect(10,80,160,20))
        self.textLabel14.setWordWrap(False)
        self.textLabel14.setObjectName("textLabel14")

        self.textLabel15 = QtGui.QLabel(self.groupBox8)
        self.textLabel15.setGeometry(QtCore.QRect(10,210,160,20))
        self.textLabel15.setWordWrap(False)
        self.textLabel15.setObjectName("textLabel15")

        self.grp_disclose = QtGui.QGroupBox(FredWindow)
        self.grp_disclose.setEnabled(False)
        self.grp_disclose.setGeometry(QtCore.QRect(180,580,360,151))
        self.grp_disclose.setObjectName("grp_disclose")

        self.update_contact_disclose_flag = QtGui.QComboBox(self.grp_disclose)
        self.update_contact_disclose_flag.setGeometry(QtCore.QRect(190,20,85,22))
        self.update_contact_disclose_flag.setObjectName("update_contact_disclose_flag")

        self.update_contact_disclose_email = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_email.setGeometry(QtCore.QRect(190,90,160,20))
        self.update_contact_disclose_email.setObjectName("update_contact_disclose_email")

        self.update_contact_disclose_notify_email = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_notify_email.setGeometry(QtCore.QRect(190,120,160,20))
        self.update_contact_disclose_notify_email.setObjectName("update_contact_disclose_notify_email")

        self.update_contact_disclose_voice = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_voice.setGeometry(QtCore.QRect(190,60,160,20))
        self.update_contact_disclose_voice.setObjectName("update_contact_disclose_voice")

        self.update_contact_disclose_vat = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_vat.setGeometry(QtCore.QRect(10,90,160,20))
        self.update_contact_disclose_vat.setObjectName("update_contact_disclose_vat")

        self.update_contact_disclose_ident = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_ident.setGeometry(QtCore.QRect(10,120,160,20))
        self.update_contact_disclose_ident.setObjectName("update_contact_disclose_ident")

        self.update_contact_disclose_fax = QtGui.QCheckBox(self.grp_disclose)
        self.update_contact_disclose_fax.setGeometry(QtCore.QRect(10,60,160,20))
        self.update_contact_disclose_fax.setObjectName("update_contact_disclose_fax")

        self.groupBox2_2 = QtGui.QGroupBox(FredWindow)
        self.groupBox2_2.setGeometry(QtCore.QRect(180,770,360,90))
        self.groupBox2_2.setObjectName("groupBox2_2")

        self.textLabel19 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel19.setGeometry(QtCore.QRect(10,50,130,20))
        self.textLabel19.setWordWrap(False)
        self.textLabel19.setObjectName("textLabel19")

        self.textLabel20 = QtGui.QLabel(self.groupBox2_2)
        self.textLabel20.setGeometry(QtCore.QRect(10,20,130,20))
        self.textLabel20.setWordWrap(False)
        self.textLabel20.setObjectName("textLabel20")

        self.update_contact_ssn_number = QtGui.QLineEdit(self.groupBox2_2)
        self.update_contact_ssn_number.setGeometry(QtCore.QRect(150,50,200,22))
        self.update_contact_ssn_number.setObjectName("update_contact_ssn_number")

        self.update_contact_ssn_type = QtGui.QComboBox(self.groupBox2_2)
        self.update_contact_ssn_type.setGeometry(QtCore.QRect(150,20,201,26))
        self.update_contact_ssn_type.setObjectName("update_contact_ssn_type")

        self.update_contact_notify_email = QtGui.QLineEdit(FredWindow)
        self.update_contact_notify_email.setGeometry(QtCore.QRect(180,870,360,22))
        self.update_contact_notify_email.setObjectName("update_contact_notify_email")

        self.update_contact_cltrid = QtGui.QLineEdit(FredWindow)
        self.update_contact_cltrid.setGeometry(QtCore.QRect(180,900,360,22))
        self.update_contact_cltrid.setObjectName("update_contact_cltrid")

        self.textLabel10 = QtGui.QLabel(FredWindow)
        self.textLabel10.setGeometry(QtCore.QRect(10,740,160,20))
        self.textLabel10.setWordWrap(False)
        self.textLabel10.setObjectName("textLabel10")

        self.textLabel21 = QtGui.QLabel(FredWindow)
        self.textLabel21.setGeometry(QtCore.QRect(10,770,160,20))
        self.textLabel21.setWordWrap(False)
        self.textLabel21.setObjectName("textLabel21")

        self.textLabel12 = QtGui.QLabel(FredWindow)
        self.textLabel12.setGeometry(QtCore.QRect(10,870,160,20))
        self.textLabel12.setWordWrap(False)
        self.textLabel12.setObjectName("textLabel12")

        self.textLabel11 = QtGui.QLabel(FredWindow)
        self.textLabel11.setGeometry(QtCore.QRect(10,900,160,20))
        self.textLabel11.setWordWrap(False)
        self.textLabel11.setObjectName("textLabel11")

        self.update_contact_vat = QtGui.QLineEdit(FredWindow)
        self.update_contact_vat.setGeometry(QtCore.QRect(180,740,360,22))
        self.update_contact_vat.setObjectName("update_contact_vat")

        self.retranslateUi(FredWindow)
        QtCore.QObject.connect(self.disclose,QtCore.SIGNAL("toggled(bool)"),self.grp_disclose.setEnabled)
        QtCore.QObject.connect(self.disclose,QtCore.SIGNAL("toggled(bool)"),self.grp_disclose.setEnabled)
        QtCore.QObject.connect(self.update_contact_street,QtCore.SIGNAL("currentCellChanged(int,int,int,int)"),FredWindow.street_current_changed)
        QtCore.QObject.connect(self.update_contact_street,QtCore.SIGNAL("cellChanged(int,int)"),FredWindow.street_value_changed)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)
        FredWindow.setTabOrder(self.update_contact_id,self.update_contact_name)
        FredWindow.setTabOrder(self.update_contact_name,self.update_contact_org)
        FredWindow.setTabOrder(self.update_contact_org,self.update_contact_city)
        FredWindow.setTabOrder(self.update_contact_city,self.update_contact_cc)
        FredWindow.setTabOrder(self.update_contact_cc,self.update_contact_street)
        FredWindow.setTabOrder(self.update_contact_street,self.update_contact_sp)
        FredWindow.setTabOrder(self.update_contact_sp,self.update_contact_pc)
        FredWindow.setTabOrder(self.update_contact_pc,self.update_contact_voice)
        FredWindow.setTabOrder(self.update_contact_voice,self.update_contact_fax)
        FredWindow.setTabOrder(self.update_contact_fax,self.update_contact_email)
        FredWindow.setTabOrder(self.update_contact_email,self.update_contact_auth_info)
        FredWindow.setTabOrder(self.update_contact_auth_info,self.disclose)
        FredWindow.setTabOrder(self.disclose,self.update_contact_disclose_flag)
        FredWindow.setTabOrder(self.update_contact_disclose_flag,self.update_contact_disclose_fax)
        FredWindow.setTabOrder(self.update_contact_disclose_fax,self.update_contact_disclose_voice)
        FredWindow.setTabOrder(self.update_contact_disclose_voice,self.update_contact_disclose_email)
        FredWindow.setTabOrder(self.update_contact_disclose_email,self.update_contact_vat)
        FredWindow.setTabOrder(self.update_contact_vat,self.update_contact_ssn_type)
        FredWindow.setTabOrder(self.update_contact_ssn_type,self.update_contact_ssn_number)
        FredWindow.setTabOrder(self.update_contact_ssn_number,self.update_contact_notify_email)
        FredWindow.setTabOrder(self.update_contact_notify_email,self.update_contact_cltrid)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Update Contact panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("FredWindow", "<b>contact ID</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel8.setText(QtGui.QApplication.translate("FredWindow", "email", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_org.setToolTip(QtGui.QApplication.translate("FredWindow", "CZ", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_org.setWhatsThis(QtGui.QApplication.translate("FredWindow", "pokus", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_name.setToolTip(QtGui.QApplication.translate("FredWindow", "CZ", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_name.setWhatsThis(QtGui.QApplication.translate("FredWindow", "pokus", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel9.setText(QtGui.QApplication.translate("FredWindow", "auth. for transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel7.setText(QtGui.QApplication.translate("FredWindow", "+420.123456789", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "name", None, QtGui.QApplication.UnicodeUTF8))
        self.disclose.setText(QtGui.QApplication.translate("FredWindow", "disclose", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel6.setText(QtGui.QApplication.translate("FredWindow", "+420.123456789", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("FredWindow", "voice (phone number)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "fax", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel18.setText(QtGui.QApplication.translate("FredWindow", "<h2>update_contact</h2>\n"
        "The EPP \"update\" command is used to update an instance of an existing object.\n"
        "   Names what are not included into disclose list are set to opposite value of the disclose flag value.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "organisation name", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox8.setTitle(QtGui.QApplication.translate("FredWindow", "address", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel13.setText(QtGui.QApplication.translate("FredWindow", "<b>country code</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel16.setText(QtGui.QApplication.translate("FredWindow", "state or province", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel17.setText(QtGui.QApplication.translate("FredWindow", "<b>city</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_street.setRowCount(1)
        self.update_contact_street.clear()
        self.update_contact_street.setColumnCount(1)
        self.update_contact_street.setRowCount(1)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("FredWindow", "street", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_street.setHorizontalHeaderItem(0,headerItem)
        self.textLabel14.setText(QtGui.QApplication.translate("FredWindow", "street (<b>required min. 1</b>)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel15.setText(QtGui.QApplication.translate("FredWindow", "<b>postal code</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.grp_disclose.setTitle(QtGui.QApplication.translate("FredWindow", "disclose", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_email.setText(QtGui.QApplication.translate("FredWindow", "email", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_notify_email.setText(QtGui.QApplication.translate("FredWindow", "notify email", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_voice.setText(QtGui.QApplication.translate("FredWindow", "voice", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_vat.setText(QtGui.QApplication.translate("FredWindow", "VAT", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_ident.setText(QtGui.QApplication.translate("FredWindow", "ident", None, QtGui.QApplication.UnicodeUTF8))
        self.update_contact_disclose_fax.setText(QtGui.QApplication.translate("FredWindow", "fax", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel19.setText(QtGui.QApplication.translate("FredWindow", "number", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel20.setText(QtGui.QApplication.translate("FredWindow", "type", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel10.setText(QtGui.QApplication.translate("FredWindow", "value-added tax", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel21.setText(QtGui.QApplication.translate("FredWindow", "social security number", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel12.setText(QtGui.QApplication.translate("FredWindow", "notify email", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel11.setText(QtGui.QApplication.translate("FredWindow", "clTRID", None, QtGui.QApplication.UnicodeUTF8))

