# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_contact.ui'
#
# Created: Út zář 26 20:19:11 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable


class panel(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("panel")



        self.textLabel3_2_6_5 = QLabel(self,"textLabel3_2_6_5")
        self.textLabel3_2_6_5.setGeometry(QRect(10,230,160,20))

        self.textLabel3_2_6 = QLabel(self,"textLabel3_2_6")
        self.textLabel3_2_6.setGeometry(QRect(10,110,160,20))

        self.textLabel3_2_6_3 = QLabel(self,"textLabel3_2_6_3")
        self.textLabel3_2_6_3.setGeometry(QRect(10,170,160,20))

        self.textLabel3_2_6_6_2 = QLabel(self,"textLabel3_2_6_6_2")
        self.textLabel3_2_6_6_2.setGeometry(QRect(10,290,160,20))

        self.textLabel3_2_6_6_2_2 = QLabel(self,"textLabel3_2_6_6_2_2")
        self.textLabel3_2_6_6_2_2.setGeometry(QRect(10,320,160,20))

        self.create_contact_name = QLineEdit(self,"create_contact_name")
        self.create_contact_name.setGeometry(QRect(180,140,360,22))

        self.create_contact_city = QLineEdit(self,"create_contact_city")
        self.create_contact_city.setGeometry(QRect(180,200,360,22))

        self.create_contact_cc = QLineEdit(self,"create_contact_cc")
        self.create_contact_cc.setGeometry(QRect(180,230,360,22))

        self.create_contact_org = QLineEdit(self,"create_contact_org")
        self.create_contact_org.setGeometry(QRect(180,290,360,22))

        self.textLabel3_2_6_6_2_4 = QLabel(self,"textLabel3_2_6_6_2_4")
        self.textLabel3_2_6_6_2_4.setGeometry(QRect(10,450,160,20))

        self.textLabel3_2_6_6_2_6_3 = QLabel(self,"textLabel3_2_6_6_2_6_3")
        self.textLabel3_2_6_6_2_6_3.setGeometry(QRect(10,690,160,20))

        self.textLabel3_2_6_6_2_5 = QLabel(self,"textLabel3_2_6_6_2_5")
        self.textLabel3_2_6_6_2_5.setGeometry(QRect(10,480,160,20))

        self.create_contact_sp = QLineEdit(self,"create_contact_sp")
        self.create_contact_sp.setGeometry(QRect(180,420,360,22))

        self.textLabel3_2_6_6_2_6 = QLabel(self,"textLabel3_2_6_6_2_6")
        self.textLabel3_2_6_6_2_6.setGeometry(QRect(10,510,160,20))

        self.textLabel3_2_6_6_2_6_2 = QLabel(self,"textLabel3_2_6_6_2_6_2")
        self.textLabel3_2_6_6_2_6_2.setGeometry(QRect(10,540,160,20))

        self.create_contact_voice = QLineEdit(self,"create_contact_voice")
        self.create_contact_voice.setGeometry(QRect(180,480,360,22))

        self.create_contact_cltrid = QLineEdit(self,"create_contact_cltrid")
        self.create_contact_cltrid.setGeometry(QRect(180,850,360,22))

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setGeometry(QRect(180,540,360,140))

        self.textLabel3_2_6_6_2_6_2_2 = QLabel(self.groupBox2,"textLabel3_2_6_6_2_6_2_2")
        self.textLabel3_2_6_6_2_6_2_2.setGeometry(QRect(10,20,160,20))

        self.create_contact_disclose_flag = QComboBox(0,self.groupBox2,"create_contact_disclose_flag")
        self.create_contact_disclose_flag.setGeometry(QRect(190,20,85,22))

        self.create_contact_disclose_name = QCheckBox(self.groupBox2,"create_contact_disclose_name")
        self.create_contact_disclose_name.setGeometry(QRect(10,50,160,20))

        self.create_contact_disclose_org = QCheckBox(self.groupBox2,"create_contact_disclose_org")
        self.create_contact_disclose_org.setGeometry(QRect(190,50,160,20))

        self.create_contact_disclose_addr = QCheckBox(self.groupBox2,"create_contact_disclose_addr")
        self.create_contact_disclose_addr.setGeometry(QRect(10,80,160,20))

        self.create_contact_disclose_voice = QCheckBox(self.groupBox2,"create_contact_disclose_voice")
        self.create_contact_disclose_voice.setGeometry(QRect(190,80,160,20))

        self.create_contact_disclose_fax = QCheckBox(self.groupBox2,"create_contact_disclose_fax")
        self.create_contact_disclose_fax.setGeometry(QRect(10,110,160,20))

        self.create_contact_disclose_email = QCheckBox(self.groupBox2,"create_contact_disclose_email")
        self.create_contact_disclose_email.setGeometry(QRect(190,110,160,20))

        self.textLabel3_2_6_6_2_6_4 = QLabel(self,"textLabel3_2_6_6_2_6_4")
        self.textLabel3_2_6_6_2_6_4.setGeometry(QRect(10,820,160,20))

        self.textLabel3_2_6_6_2_6_2_3 = QLabel(self,"textLabel3_2_6_6_2_6_2_3")
        self.textLabel3_2_6_6_2_6_2_3.setGeometry(QRect(10,720,160,20))

        self.textLabel3_2_6_6_2_3 = QLabel(self,"textLabel3_2_6_6_2_3")
        self.textLabel3_2_6_6_2_3.setGeometry(QRect(10,420,160,20))

        self.textLabel3_2_6_6_2_6_5 = QLabel(self,"textLabel3_2_6_6_2_6_5")
        self.textLabel3_2_6_6_2_6_5.setGeometry(QRect(10,850,160,20))

        self.create_contact_fax = QLineEdit(self,"create_contact_fax")
        self.create_contact_fax.setGeometry(QRect(180,510,360,22))

        self.groupBox2_2 = QGroupBox(self,"groupBox2_2")
        self.groupBox2_2.setGeometry(QRect(180,720,360,90))

        self.textLabel3_2_6_6_2_6_2_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2_2.setGeometry(QRect(10,50,130,20))

        self.textLabel3_2_6_6_2_6_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2.setGeometry(QRect(10,20,130,20))

        self.create_contact_ssn_type = QComboBox(0,self.groupBox2_2,"create_contact_ssn_type")
        self.create_contact_ssn_type.setGeometry(QRect(150,20,85,22))

        self.create_contact_ssn_number = QLineEdit(self.groupBox2_2,"create_contact_ssn_number")
        self.create_contact_ssn_number.setGeometry(QRect(150,50,200,22))

        self.create_contact_pc = QLineEdit(self,"create_contact_pc")
        self.create_contact_pc.setGeometry(QRect(180,450,360,22))

        self.create_contact_notify_email = QLineEdit(self,"create_contact_notify_email")
        self.create_contact_notify_email.setGeometry(QRect(180,820,360,22))

        self.textLabel3_2_6_4 = QLabel(self,"textLabel3_2_6_4")
        self.textLabel3_2_6_4.setGeometry(QRect(10,200,160,20))

        self.create_contact_email = QLineEdit(self,"create_contact_email")
        self.create_contact_email.setGeometry(QRect(180,170,360,22))

        self.textLabel3_2_6_6 = QLabel(self,"textLabel3_2_6_6")
        self.textLabel3_2_6_6.setGeometry(QRect(10,260,160,20))

        self.create_contact_pw = QLineEdit(self,"create_contact_pw")
        self.create_contact_pw.setGeometry(QRect(180,260,360,22))
        self.create_contact_pw.setEchoMode(QLineEdit.Password)

        self.textLabel3_2_6_2 = QLabel(self,"textLabel3_2_6_2")
        self.textLabel3_2_6_2.setGeometry(QRect(10,140,160,20))

        self.create_contact_street = QTable(self,"create_contact_street")
        self.create_contact_street.setNumCols(self.create_contact_street.numCols() + 1)
        self.create_contact_street.horizontalHeader().setLabel(self.create_contact_street.numCols() - 1,self.__tr("street"))
        self.create_contact_street.setGeometry(QRect(180,320,360,87))
        self.create_contact_street.setNumRows(3)
        self.create_contact_street.setNumCols(1)
        self.create_contact_street.setShowGrid(1)
        self.create_contact_street.setFocusStyle(QTable.SpreadSheet)

        self.create_contact_id = QLineEdit(self,"create_contact_id")
        self.create_contact_id.setGeometry(QRect(180,110,360,22))

        self.textLabel1_2_3_7_3_3 = QLabel(self,"textLabel1_2_3_7_3_3")
        self.textLabel1_2_3_7_3_3.setGeometry(QRect(10,10,530,90))
        self.textLabel1_2_3_7_3_3.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.create_contact_vat = QLineEdit(self,"create_contact_vat")
        self.create_contact_vat.setGeometry(QRect(180,690,360,22))

        self.languageChange()

        self.resize(QSize(574,892).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.setTabOrder(self.create_contact_id,self.create_contact_name)
        self.setTabOrder(self.create_contact_name,self.create_contact_email)
        self.setTabOrder(self.create_contact_email,self.create_contact_city)
        self.setTabOrder(self.create_contact_city,self.create_contact_cc)
        self.setTabOrder(self.create_contact_cc,self.create_contact_pw)
        self.setTabOrder(self.create_contact_pw,self.create_contact_org)
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
        self.textLabel3_2_6_5.setText(self.__tr("<b>country code</b>"))
        self.textLabel3_2_6.setText(self.__tr("<b>contact ID</b>"))
        self.textLabel3_2_6_3.setText(self.__tr("<b>email</b>"))
        self.textLabel3_2_6_6_2.setText(self.__tr("organisation name"))
        self.textLabel3_2_6_6_2_2.setText(self.__tr("street"))
        self.textLabel3_2_6_6_2_4.setText(self.__tr("postal code"))
        self.textLabel3_2_6_6_2_6_3.setText(self.__tr("value-added tax"))
        self.textLabel3_2_6_6_2_5.setText(self.__tr("voice (phone number)"))
        self.textLabel3_2_6_6_2_6.setText(self.__tr("fax"))
        self.textLabel3_2_6_6_2_6_2.setText(self.__tr("disclose"))
        self.groupBox2.setTitle(self.__tr("disclose"))
        self.textLabel3_2_6_6_2_6_2_2.setText(self.__tr("flag"))
        self.create_contact_disclose_flag.clear()
        self.create_contact_disclose_flag.insertItem(self.__tr("yes"))
        self.create_contact_disclose_flag.insertItem(self.__tr("no"))
        self.create_contact_disclose_name.setText(self.__tr("name"))
        self.create_contact_disclose_org.setText(self.__tr("organisation"))
        self.create_contact_disclose_addr.setText(self.__tr("address"))
        self.create_contact_disclose_voice.setText(self.__tr("voice"))
        self.create_contact_disclose_fax.setText(self.__tr("fax"))
        self.create_contact_disclose_email.setText(self.__tr("email"))
        self.textLabel3_2_6_6_2_6_4.setText(self.__tr("notify email"))
        self.textLabel3_2_6_6_2_6_2_3.setText(self.__tr("social security number"))
        self.textLabel3_2_6_6_2_3.setText(self.__tr("state or province"))
        self.textLabel3_2_6_6_2_6_5.setText(self.__tr("clTRID"))
        self.groupBox2_2.setTitle(self.__tr("social security number"))
        self.textLabel3_2_6_6_2_6_2_2_2_2.setText(self.__tr("number"))
        self.textLabel3_2_6_6_2_6_2_2_2.setText(self.__tr("type"))
        self.create_contact_ssn_type.clear()
        self.create_contact_ssn_type.insertItem(self.__tr("op"))
        self.create_contact_ssn_type.insertItem(self.__tr("rc"))
        self.create_contact_ssn_type.insertItem(self.__tr("passport"))
        self.create_contact_ssn_type.insertItem(self.__tr("mpsv"))
        self.create_contact_ssn_type.insertItem(self.__tr("ico"))
        self.textLabel3_2_6_4.setText(self.__tr("<b>city</b>"))
        self.textLabel3_2_6_6.setText(self.__tr("password"))
        self.textLabel3_2_6_2.setText(self.__tr("<b>name</b>"))
        self.create_contact_street.horizontalHeader().setLabel(0,self.__tr("street"))
        self.create_contact_id.setText(QString.null)
        self.textLabel1_2_3_7_3_3.setText(self.__tr("<h2>create_contact</h2>\n"
"The EPP \"create\" command is used to create an instance of an object.\n"
"An object can be created for an indefinite period of time, or an\n"
"object can be created for a specific validity period."))


    def __tr(self,s,c = None):
        return qApp.translate("panel",s,c)
