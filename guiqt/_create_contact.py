# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_contact.ui'
#
# Created: Čt říj 19 16:26:19 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable


class ccregWindow(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("ccregWindow")



        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,230,160,20))

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,110,160,20))

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,170,160,20))

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,320,160,20))

        self.create_contact_name = QLineEdit(self,"create_contact_name")
        self.create_contact_name.setGeometry(QRect(180,140,360,22))

        self.create_contact_city = QLineEdit(self,"create_contact_city")
        self.create_contact_city.setGeometry(QRect(180,200,360,22))

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(10,450,160,20))

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(10,690,160,20))

        self.create_contact_sp = QLineEdit(self,"create_contact_sp")
        self.create_contact_sp.setGeometry(QRect(180,420,360,22))

        self.textLabel7 = QLabel(self,"textLabel7")
        self.textLabel7.setGeometry(QRect(10,510,160,20))

        self.create_contact_cltrid = QLineEdit(self,"create_contact_cltrid")
        self.create_contact_cltrid.setGeometry(QRect(180,850,360,22))

        self.textLabel8 = QLabel(self,"textLabel8")
        self.textLabel8.setGeometry(QRect(10,820,160,20))

        self.textLabel9 = QLabel(self,"textLabel9")
        self.textLabel9.setGeometry(QRect(10,720,160,20))

        self.textLabel10 = QLabel(self,"textLabel10")
        self.textLabel10.setGeometry(QRect(10,420,160,20))

        self.textLabel11 = QLabel(self,"textLabel11")
        self.textLabel11.setGeometry(QRect(10,850,160,20))

        self.groupBox2_2 = QGroupBox(self,"groupBox2_2")
        self.groupBox2_2.setGeometry(QRect(180,720,360,90))

        self.textLabel12 = QLabel(self.groupBox2_2,"textLabel12")
        self.textLabel12.setGeometry(QRect(10,50,130,20))

        self.textLabel13 = QLabel(self.groupBox2_2,"textLabel13")
        self.textLabel13.setGeometry(QRect(10,20,130,20))

        self.create_contact_ssn_type = QComboBox(0,self.groupBox2_2,"create_contact_ssn_type")
        self.create_contact_ssn_type.setGeometry(QRect(150,20,85,22))

        self.create_contact_ssn_number = QLineEdit(self.groupBox2_2,"create_contact_ssn_number")
        self.create_contact_ssn_number.setGeometry(QRect(150,50,200,22))

        self.create_contact_notify_email = QLineEdit(self,"create_contact_notify_email")
        self.create_contact_notify_email.setGeometry(QRect(180,820,360,22))

        self.textLabel14 = QLabel(self,"textLabel14")
        self.textLabel14.setGeometry(QRect(10,200,160,20))

        self.create_contact_email = QLineEdit(self,"create_contact_email")
        self.create_contact_email.setGeometry(QRect(180,170,360,22))

        self.textLabel15 = QLabel(self,"textLabel15")
        self.textLabel15.setGeometry(QRect(10,260,160,20))

        self.textLabel16 = QLabel(self,"textLabel16")
        self.textLabel16.setGeometry(QRect(10,140,160,20))

        self.create_contact_street = QTable(self,"create_contact_street")
        self.create_contact_street.setNumCols(self.create_contact_street.numCols() + 1)
        self.create_contact_street.horizontalHeader().setLabel(self.create_contact_street.numCols() - 1,self.__tr("street"))
        self.create_contact_street.setGeometry(QRect(180,320,360,87))
        self.create_contact_street.setNumRows(3)
        self.create_contact_street.setNumCols(1)
        self.create_contact_street.setShowGrid(1)
        self.create_contact_street.setFocusStyle(QTable.SpreadSheet)

        self.textLabel17 = QLabel(self,"textLabel17")
        self.textLabel17.setGeometry(QRect(10,10,530,90))
        self.textLabel17.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.create_contact_vat = QLineEdit(self,"create_contact_vat")
        self.create_contact_vat.setGeometry(QRect(180,690,360,22))

        self.create_contact_id = QLineEdit(self,"create_contact_id")
        self.create_contact_id.setGeometry(QRect(180,110,360,22))

        self.create_contact_auth_info = QLineEdit(self,"create_contact_auth_info")
        self.create_contact_auth_info.setGeometry(QRect(180,260,360,22))
        self.create_contact_auth_info.setEchoMode(QLineEdit.Normal)

        self.textLabel18 = QLabel(self,"textLabel18")
        self.textLabel18.setGeometry(QRect(10,290,160,20))

        self.create_contact_org = QLineEdit(self,"create_contact_org")
        self.create_contact_org.setGeometry(QRect(180,290,360,22))

        self.create_contact_pc = QLineEdit(self,"create_contact_pc")
        self.create_contact_pc.setGeometry(QRect(180,450,360,22))

        self.textLabel19 = QLabel(self,"textLabel19")
        self.textLabel19.setGeometry(QRect(10,480,160,20))

        self.create_contact_cc = QLineEdit(self,"create_contact_cc")
        self.create_contact_cc.setGeometry(QRect(180,230,50,22))

        self.textLabel20 = QLabel(self,"textLabel20")
        self.textLabel20.setGeometry(QRect(380,480,160,20))

        self.textLabel21 = QLabel(self,"textLabel21")
        self.textLabel21.setGeometry(QRect(380,510,160,20))

        self.create_contact_voice = QLineEdit(self,"create_contact_voice")
        self.create_contact_voice.setGeometry(QRect(180,480,180,22))

        self.create_contact_fax = QLineEdit(self,"create_contact_fax")
        self.create_contact_fax.setGeometry(QRect(180,510,180,22))

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setEnabled(0)
        self.groupBox2.setGeometry(QRect(180,540,360,140))

        self.create_contact_disclose_voice = QCheckBox(self.groupBox2,"create_contact_disclose_voice")
        self.create_contact_disclose_voice.setGeometry(QRect(190,80,160,20))

        self.create_contact_disclose_fax = QCheckBox(self.groupBox2,"create_contact_disclose_fax")
        self.create_contact_disclose_fax.setGeometry(QRect(10,110,160,20))

        self.create_contact_disclose_email = QCheckBox(self.groupBox2,"create_contact_disclose_email")
        self.create_contact_disclose_email.setGeometry(QRect(190,110,160,20))

        self.create_contact_disclose_name = QCheckBox(self.groupBox2,"create_contact_disclose_name")
        self.create_contact_disclose_name.setGeometry(QRect(10,50,160,20))

        self.create_contact_disclose_addr = QCheckBox(self.groupBox2,"create_contact_disclose_addr")
        self.create_contact_disclose_addr.setGeometry(QRect(10,80,160,20))

        self.create_contact_disclose_org = QCheckBox(self.groupBox2,"create_contact_disclose_org")
        self.create_contact_disclose_org.setGeometry(QRect(190,50,160,20))

        self.textLabel22 = QLabel(self.groupBox2,"textLabel22")
        self.textLabel22.setGeometry(QRect(10,20,160,20))

        self.create_contact_disclose_flag = QComboBox(0,self.groupBox2,"create_contact_disclose_flag")
        self.create_contact_disclose_flag.setGeometry(QRect(190,20,85,22))

        self.checkBox8 = QCheckBox(self,"checkBox8")
        self.checkBox8.setGeometry(QRect(10,540,160,20))

        self.languageChange()

        self.resize(QSize(574,892).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.checkBox8,SIGNAL("toggled(bool)"),self.groupBox2.setEnabled)

        self.setTabOrder(self.create_contact_id,self.create_contact_name)
        self.setTabOrder(self.create_contact_name,self.create_contact_email)
        self.setTabOrder(self.create_contact_email,self.create_contact_city)
        self.setTabOrder(self.create_contact_city,self.create_contact_cc)
        self.setTabOrder(self.create_contact_cc,self.create_contact_auth_info)
        self.setTabOrder(self.create_contact_auth_info,self.create_contact_org)
        self.setTabOrder(self.create_contact_org,self.create_contact_street)
        self.setTabOrder(self.create_contact_street,self.create_contact_sp)
        self.setTabOrder(self.create_contact_sp,self.create_contact_pc)
        self.setTabOrder(self.create_contact_pc,self.create_contact_voice)
        self.setTabOrder(self.create_contact_voice,self.create_contact_fax)
        self.setTabOrder(self.create_contact_fax,self.create_contact_disclose_flag)
        self.setTabOrder(self.create_contact_disclose_flag,self.create_contact_disclose_name)
        self.setTabOrder(self.create_contact_disclose_name,self.create_contact_disclose_addr)
        self.setTabOrder(self.create_contact_disclose_addr,self.create_contact_disclose_fax)
        self.setTabOrder(self.create_contact_disclose_fax,self.create_contact_disclose_org)
        self.setTabOrder(self.create_contact_disclose_org,self.create_contact_disclose_voice)
        self.setTabOrder(self.create_contact_disclose_voice,self.create_contact_disclose_email)
        self.setTabOrder(self.create_contact_disclose_email,self.create_contact_vat)
        self.setTabOrder(self.create_contact_vat,self.create_contact_ssn_type)
        self.setTabOrder(self.create_contact_ssn_type,self.create_contact_ssn_number)
        self.setTabOrder(self.create_contact_ssn_number,self.create_contact_notify_email)
        self.setTabOrder(self.create_contact_notify_email,self.create_contact_cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Create Contact panel"))
        self.textLabel1.setText(self.__tr("<b>country code</b>"))
        self.textLabel2.setText(self.__tr("<b>contact ID</b>"))
        self.textLabel3.setText(self.__tr("<b>email</b>"))
        self.textLabel4.setText(self.__tr("street"))
        self.textLabel5.setText(self.__tr("postal code"))
        self.textLabel6.setText(self.__tr("value-added tax"))
        self.textLabel7.setText(self.__tr("fax"))
        self.textLabel8.setText(self.__tr("notify email"))
        self.textLabel9.setText(self.__tr("social security number"))
        self.textLabel10.setText(self.__tr("state or province"))
        self.textLabel11.setText(self.__tr("clTRID"))
        self.groupBox2_2.setTitle(self.__tr("social security number"))
        self.textLabel12.setText(self.__tr("number"))
        self.textLabel13.setText(self.__tr("type"))
        self.create_contact_ssn_type.clear()
        self.create_contact_ssn_type.insertItem(self.__tr("op"))
        self.create_contact_ssn_type.insertItem(self.__tr("rc"))
        self.create_contact_ssn_type.insertItem(self.__tr("passport"))
        self.create_contact_ssn_type.insertItem(self.__tr("mpsv"))
        self.create_contact_ssn_type.insertItem(self.__tr("ico"))
        self.textLabel14.setText(self.__tr("<b>city</b>"))
        self.textLabel15.setText(self.__tr("auth. for transfer"))
        self.textLabel16.setText(self.__tr("<b>name</b>"))
        self.create_contact_street.horizontalHeader().setLabel(0,self.__tr("street"))
        self.textLabel17.setText(self.__tr("<h2>create_contact</h2>\n"
"The EPP \"create\" command is used to create an instance of an object.\n"
"An object can be created for an indefinite period of time, or an\n"
"object can be created for a specific validity period."))
        self.create_contact_id.setText(QString.null)
        self.textLabel18.setText(self.__tr("organisation name"))
        QToolTip.add(self.create_contact_org,self.__tr("CZ"))
        QWhatsThis.add(self.create_contact_org,self.__tr("pokus"))
        self.textLabel19.setText(self.__tr("voice (phone number)"))
        self.create_contact_cc.setText(self.__tr("CZ"))
        self.create_contact_cc.setInputMask(QString.null)
        self.textLabel20.setText(self.__tr("+420.123456789"))
        self.textLabel21.setText(self.__tr("+420.123456789"))
        self.create_contact_voice.setInputMask(QString.null)
        self.create_contact_fax.setInputMask(QString.null)
        self.groupBox2.setTitle(QString.null)
        self.create_contact_disclose_voice.setText(self.__tr("voice"))
        self.create_contact_disclose_fax.setText(self.__tr("fax"))
        self.create_contact_disclose_email.setText(self.__tr("email"))
        self.create_contact_disclose_name.setText(self.__tr("name"))
        self.create_contact_disclose_addr.setText(self.__tr("address"))
        self.create_contact_disclose_org.setText(self.__tr("organisation"))
        self.textLabel22.setText(self.__tr("disclose"))
        self.create_contact_disclose_flag.clear()
        self.create_contact_disclose_flag.insertItem(self.__tr("yes"))
        self.create_contact_disclose_flag.insertItem(self.__tr("no"))
        self.checkBox8.setText(self.__tr("disclose"))


    def __tr(self,s,c = None):
        return qApp.translate("ccregWindow",s,c)
