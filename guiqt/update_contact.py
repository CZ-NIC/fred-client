# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_contact.ui'
#
# Created: Pá zář 29 15:49:02 2006
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



        self.textLabel3_2_6 = QLabel(self,"textLabel3_2_6")
        self.textLabel3_2_6.setGeometry(QRect(10,110,160,20))

        self.textLabel3_2_6_6_2 = QLabel(self,"textLabel3_2_6_6_2")
        self.textLabel3_2_6_6_2.setGeometry(QRect(10,340,160,20))

        self.update_contact_name = QLineEdit(self,"update_contact_name")
        self.update_contact_name.setGeometry(QRect(180,340,360,22))

        self.update_contact_org = QLineEdit(self,"update_contact_org")
        self.update_contact_org.setGeometry(QRect(180,370,360,22))

        self.textLabel3_2_6_6_2_7 = QLabel(self,"textLabel3_2_6_6_2_7")
        self.textLabel3_2_6_6_2_7.setGeometry(QRect(10,370,160,20))

        self.textLabel3_2_6_6_2_6 = QLabel(self,"textLabel3_2_6_6_2_6")
        self.textLabel3_2_6_6_2_6.setGeometry(QRect(10,690,160,20))

        self.textLabel3_2_6_6_2_5 = QLabel(self,"textLabel3_2_6_6_2_5")
        self.textLabel3_2_6_6_2_5.setGeometry(QRect(10,660,160,20))

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        self.textLabel2_2.setGeometry(QRect(380,690,160,20))

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(380,660,160,20))

        self.textLabel3_2_6_6_2_6_4_2 = QLabel(self,"textLabel3_2_6_6_2_6_4_2")
        self.textLabel3_2_6_6_2_6_4_2.setGeometry(QRect(10,720,160,20))

        self.textLabel3_2_6_6 = QLabel(self,"textLabel3_2_6_6")
        self.textLabel3_2_6_6.setGeometry(QRect(10,750,160,20))

        self.textLabel3_2_6_6_2_6_3 = QLabel(self,"textLabel3_2_6_6_2_6_3")
        self.textLabel3_2_6_6_2_6_3.setGeometry(QRect(10,930,160,20))

        self.textLabel3_2_6_6_2_6_5 = QLabel(self,"textLabel3_2_6_6_2_6_5")
        self.textLabel3_2_6_6_2_6_5.setGeometry(QRect(10,1090,160,20))

        self.textLabel3_2_6_6_2_6_4 = QLabel(self,"textLabel3_2_6_6_2_6_4")
        self.textLabel3_2_6_6_2_6_4.setGeometry(QRect(10,1060,160,20))

        self.groupBox8 = QGroupBox(self,"groupBox8")
        self.groupBox8.setGeometry(QRect(10,400,531,250))

        self.textLabel3_2_6_5 = QLabel(self.groupBox8,"textLabel3_2_6_5")
        self.textLabel3_2_6_5.setGeometry(QRect(10,50,160,20))

        self.textLabel3_2_6_6_2_2 = QLabel(self.groupBox8,"textLabel3_2_6_6_2_2")
        self.textLabel3_2_6_6_2_2.setGeometry(QRect(10,80,160,20))

        self.textLabel3_2_6_6_2_4 = QLabel(self.groupBox8,"textLabel3_2_6_6_2_4")
        self.textLabel3_2_6_6_2_4.setGeometry(QRect(10,210,160,20))

        self.textLabel3_2_6_6_2_3 = QLabel(self.groupBox8,"textLabel3_2_6_6_2_3")
        self.textLabel3_2_6_6_2_3.setGeometry(QRect(10,180,160,20))

        self.textLabel3_2_6_6_2_3_2 = QLabel(self.groupBox8,"textLabel3_2_6_6_2_3_2")
        self.textLabel3_2_6_6_2_3_2.setGeometry(QRect(10,20,160,20))

        self.update_contact_street = QTable(self.groupBox8,"update_contact_street")
        self.update_contact_street.setNumCols(self.update_contact_street.numCols() + 1)
        self.update_contact_street.horizontalHeader().setLabel(self.update_contact_street.numCols() - 1,self.__tr("street"))
        self.update_contact_street.setGeometry(QRect(180,80,330,87))
        self.update_contact_street.setNumRows(3)
        self.update_contact_street.setNumCols(1)
        self.update_contact_street.setShowGrid(1)
        self.update_contact_street.setFocusStyle(QTable.SpreadSheet)

        self.update_contact_sp = QLineEdit(self.groupBox8,"update_contact_sp")
        self.update_contact_sp.setGeometry(QRect(180,180,330,22))

        self.update_contact_pc = QLineEdit(self.groupBox8,"update_contact_pc")
        self.update_contact_pc.setGeometry(QRect(180,210,330,22))

        self.update_contact_cc = QLineEdit(self.groupBox8,"update_contact_cc")
        self.update_contact_cc.setGeometry(QRect(180,50,50,22))

        self.update_contact_city = QLineEdit(self.groupBox8,"update_contact_city")
        self.update_contact_city.setGeometry(QRect(180,20,330,22))

        self.update_contact_voice = QLineEdit(self,"update_contact_voice")
        self.update_contact_voice.setGeometry(QRect(180,660,180,22))

        self.update_contact_fax = QLineEdit(self,"update_contact_fax")
        self.update_contact_fax.setGeometry(QRect(180,690,180,22))

        self.update_contact_email = QLineEdit(self,"update_contact_email")
        self.update_contact_email.setGeometry(QRect(180,720,360,22))

        self.update_contact_pw = QLineEdit(self,"update_contact_pw")
        self.update_contact_pw.setGeometry(QRect(180,750,360,22))
        self.update_contact_pw.setEchoMode(QLineEdit.Normal)

        self.update_contact_vat = QLineEdit(self,"update_contact_vat")
        self.update_contact_vat.setGeometry(QRect(180,930,360,22))

        self.checkBox_rem = QCheckBox(self,"checkBox_rem")
        self.checkBox_rem.setGeometry(QRect(10,240,150,20))

        self.checkBox_add = QCheckBox(self,"checkBox_add")
        self.checkBox_add.setGeometry(QRect(10,140,150,20))

        self.grp_disclose = QGroupBox(self,"grp_disclose")
        self.grp_disclose.setEnabled(0)
        self.grp_disclose.setGeometry(QRect(180,780,360,140))

        self.update_contact_disclose_flag = QComboBox(0,self.grp_disclose,"update_contact_disclose_flag")
        self.update_contact_disclose_flag.setGeometry(QRect(190,20,85,22))

        self.update_contact_disclose_name = QCheckBox(self.grp_disclose,"update_contact_disclose_name")
        self.update_contact_disclose_name.setGeometry(QRect(10,50,160,20))

        self.update_contact_disclose_addr = QCheckBox(self.grp_disclose,"update_contact_disclose_addr")
        self.update_contact_disclose_addr.setGeometry(QRect(10,80,160,20))

        self.update_contact_disclose_fax = QCheckBox(self.grp_disclose,"update_contact_disclose_fax")
        self.update_contact_disclose_fax.setGeometry(QRect(10,110,160,20))

        self.update_contact_disclose_org = QCheckBox(self.grp_disclose,"update_contact_disclose_org")
        self.update_contact_disclose_org.setGeometry(QRect(190,50,160,20))

        self.update_contact_disclose_voice = QCheckBox(self.grp_disclose,"update_contact_disclose_voice")
        self.update_contact_disclose_voice.setGeometry(QRect(190,80,160,20))

        self.update_contact_disclose_email = QCheckBox(self.grp_disclose,"update_contact_disclose_email")
        self.update_contact_disclose_email.setGeometry(QRect(190,110,160,20))

        self.disclose = QCheckBox(self,"disclose")
        self.disclose.setGeometry(QRect(10,780,160,20))

        self.grp_add = QButtonGroup(self,"grp_add")
        self.grp_add.setEnabled(0)
        self.grp_add.setGeometry(QRect(180,140,360,90))

        self.add_clientTransferProhibited = QCheckBox(self.grp_add,"add_clientTransferProhibited")
        self.add_clientTransferProhibited.setGeometry(QRect(140,60,210,20))

        self.add_clientDeleteProhibited = QCheckBox(self.grp_add,"add_clientDeleteProhibited")
        self.add_clientDeleteProhibited.setGeometry(QRect(140,40,210,20))

        self.add_clientUpdateProhibited = QCheckBox(self.grp_add,"add_clientUpdateProhibited")
        self.add_clientUpdateProhibited.setGeometry(QRect(140,20,210,20))

        self.add_linked = QCheckBox(self.grp_add,"add_linked")
        self.add_linked.setGeometry(QRect(10,20,70,20))

        self.add_ok = QCheckBox(self.grp_add,"add_ok")
        self.add_ok.setGeometry(QRect(10,40,70,20))

        self.grp_remove = QButtonGroup(self,"grp_remove")
        self.grp_remove.setEnabled(0)
        self.grp_remove.setGeometry(QRect(180,240,360,90))

        self.rem_linked = QCheckBox(self.grp_remove,"rem_linked")
        self.rem_linked.setGeometry(QRect(10,20,70,20))

        self.rem_ok = QCheckBox(self.grp_remove,"rem_ok")
        self.rem_ok.setGeometry(QRect(10,40,70,20))

        self.rem_clientUpdateProhibited = QCheckBox(self.grp_remove,"rem_clientUpdateProhibited")
        self.rem_clientUpdateProhibited.setGeometry(QRect(140,20,210,20))

        self.rem_clientDeleteProhibited = QCheckBox(self.grp_remove,"rem_clientDeleteProhibited")
        self.rem_clientDeleteProhibited.setGeometry(QRect(140,40,210,20))

        self.rem_clientTransferProhibited = QCheckBox(self.grp_remove,"rem_clientTransferProhibited")
        self.rem_clientTransferProhibited.setGeometry(QRect(140,60,210,20))

        self.update_contact_id = QLineEdit(self,"update_contact_id")
        self.update_contact_id.setGeometry(QRect(180,110,360,22))

        self.update_contact_cltrid = QLineEdit(self,"update_contact_cltrid")
        self.update_contact_cltrid.setGeometry(QRect(180,1090,360,22))

        self.update_contact_notify_email = QLineEdit(self,"update_contact_notify_email")
        self.update_contact_notify_email.setGeometry(QRect(180,1060,360,22))

        self.textLabel1_2_3_7_3_3 = QLabel(self,"textLabel1_2_3_7_3_3")
        self.textLabel1_2_3_7_3_3.setGeometry(QRect(10,10,530,90))
        self.textLabel1_2_3_7_3_3.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.groupBox2_2 = QGroupBox(self,"groupBox2_2")
        self.groupBox2_2.setGeometry(QRect(180,960,360,90))

        self.textLabel3_2_6_6_2_6_2_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2_2.setGeometry(QRect(10,50,130,20))

        self.textLabel3_2_6_6_2_6_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2.setGeometry(QRect(10,20,130,20))

        self.update_contact_ssn_type = QComboBox(0,self.groupBox2_2,"update_contact_ssn_type")
        self.update_contact_ssn_type.setGeometry(QRect(150,20,85,22))

        self.update_contact_ssn_number = QLineEdit(self.groupBox2_2,"update_contact_ssn_number")
        self.update_contact_ssn_number.setGeometry(QRect(150,50,200,22))

        self.textLabel3_2_6_6_2_6_2_3 = QLabel(self,"textLabel3_2_6_6_2_6_2_3")
        self.textLabel3_2_6_6_2_6_2_3.setGeometry(QRect(10,960,160,20))

        self.languageChange()

        self.resize(QSize(574,1135).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.disclose,SIGNAL("toggled(bool)"),self.grp_disclose.setEnabled)
        self.connect(self.checkBox_add,SIGNAL("toggled(bool)"),self.grp_add.setEnabled)
        self.connect(self.checkBox_rem,SIGNAL("toggled(bool)"),self.grp_remove.setEnabled)
        self.connect(self.disclose,SIGNAL("toggled(bool)"),self.grp_disclose.setEnabled)

        self.setTabOrder(self.update_contact_id,self.checkBox_add)
        self.setTabOrder(self.checkBox_add,self.add_linked)
        self.setTabOrder(self.add_linked,self.add_ok)
        self.setTabOrder(self.add_ok,self.add_clientUpdateProhibited)
        self.setTabOrder(self.add_clientUpdateProhibited,self.add_clientDeleteProhibited)
        self.setTabOrder(self.add_clientDeleteProhibited,self.add_clientTransferProhibited)
        self.setTabOrder(self.add_clientTransferProhibited,self.checkBox_rem)
        self.setTabOrder(self.checkBox_rem,self.rem_linked)
        self.setTabOrder(self.rem_linked,self.rem_ok)
        self.setTabOrder(self.rem_ok,self.rem_clientUpdateProhibited)
        self.setTabOrder(self.rem_clientUpdateProhibited,self.rem_clientDeleteProhibited)
        self.setTabOrder(self.rem_clientDeleteProhibited,self.rem_clientTransferProhibited)
        self.setTabOrder(self.rem_clientTransferProhibited,self.update_contact_name)
        self.setTabOrder(self.update_contact_name,self.update_contact_org)
        self.setTabOrder(self.update_contact_org,self.update_contact_city)
        self.setTabOrder(self.update_contact_city,self.update_contact_cc)
        self.setTabOrder(self.update_contact_cc,self.update_contact_street)
        self.setTabOrder(self.update_contact_street,self.update_contact_sp)
        self.setTabOrder(self.update_contact_sp,self.update_contact_pc)
        self.setTabOrder(self.update_contact_pc,self.update_contact_voice)
        self.setTabOrder(self.update_contact_voice,self.update_contact_fax)
        self.setTabOrder(self.update_contact_fax,self.update_contact_email)
        self.setTabOrder(self.update_contact_email,self.update_contact_pw)
        self.setTabOrder(self.update_contact_pw,self.disclose)
        self.setTabOrder(self.disclose,self.update_contact_disclose_flag)
        self.setTabOrder(self.update_contact_disclose_flag,self.update_contact_disclose_name)
        self.setTabOrder(self.update_contact_disclose_name,self.update_contact_disclose_addr)
        self.setTabOrder(self.update_contact_disclose_addr,self.update_contact_disclose_fax)
        self.setTabOrder(self.update_contact_disclose_fax,self.update_contact_disclose_org)
        self.setTabOrder(self.update_contact_disclose_org,self.update_contact_disclose_voice)
        self.setTabOrder(self.update_contact_disclose_voice,self.update_contact_disclose_email)
        self.setTabOrder(self.update_contact_disclose_email,self.update_contact_vat)
        self.setTabOrder(self.update_contact_vat,self.update_contact_ssn_type)
        self.setTabOrder(self.update_contact_ssn_type,self.update_contact_ssn_number)
        self.setTabOrder(self.update_contact_ssn_number,self.update_contact_notify_email)
        self.setTabOrder(self.update_contact_notify_email,self.update_contact_cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Update Contact panel"))
        self.textLabel3_2_6.setText(self.__tr("<b>contact ID</b>"))
        self.textLabel3_2_6_6_2.setText(self.__tr("name"))
        QToolTip.add(self.update_contact_name,self.__tr("CZ"))
        QWhatsThis.add(self.update_contact_name,self.__tr("pokus"))
        QToolTip.add(self.update_contact_org,self.__tr("CZ"))
        QWhatsThis.add(self.update_contact_org,self.__tr("pokus"))
        self.textLabel3_2_6_6_2_7.setText(self.__tr("organisation name"))
        self.textLabel3_2_6_6_2_6.setText(self.__tr("fax"))
        self.textLabel3_2_6_6_2_5.setText(self.__tr("voice (phone number)"))
        self.textLabel2_2.setText(self.__tr("+420.123456789"))
        self.textLabel2.setText(self.__tr("+420.123456789"))
        self.textLabel3_2_6_6_2_6_4_2.setText(self.__tr("email"))
        self.textLabel3_2_6_6.setText(self.__tr("password"))
        self.textLabel3_2_6_6_2_6_3.setText(self.__tr("value-added tax"))
        self.textLabel3_2_6_6_2_6_5.setText(self.__tr("clTRID"))
        self.textLabel3_2_6_6_2_6_4.setText(self.__tr("notify email"))
        self.groupBox8.setTitle(self.__tr("address"))
        self.textLabel3_2_6_5.setText(self.__tr("<b>country code</b>"))
        self.textLabel3_2_6_6_2_2.setText(self.__tr("street"))
        self.textLabel3_2_6_6_2_4.setText(self.__tr("postal code"))
        self.textLabel3_2_6_6_2_3.setText(self.__tr("state or province"))
        self.textLabel3_2_6_6_2_3_2.setText(self.__tr("<b>city</b>"))
        self.update_contact_street.horizontalHeader().setLabel(0,self.__tr("street"))
        self.update_contact_cc.setText(QString.null)
        self.update_contact_cc.setInputMask(QString.null)
        self.update_contact_voice.setInputMask(QString.null)
        self.update_contact_fax.setInputMask(QString.null)
        self.checkBox_rem.setText(self.__tr("remove"))
        self.checkBox_add.setText(self.__tr("add"))
        self.grp_disclose.setTitle(self.__tr("disclose"))
        self.update_contact_disclose_flag.clear()
        self.update_contact_disclose_flag.insertItem(self.__tr("yes"))
        self.update_contact_disclose_flag.insertItem(self.__tr("no"))
        self.update_contact_disclose_name.setText(self.__tr("name"))
        self.update_contact_disclose_addr.setText(self.__tr("address"))
        self.update_contact_disclose_fax.setText(self.__tr("fax"))
        self.update_contact_disclose_org.setText(self.__tr("organisation"))
        self.update_contact_disclose_voice.setText(self.__tr("voice"))
        self.update_contact_disclose_email.setText(self.__tr("email"))
        self.disclose.setText(self.__tr("disclose"))
        self.grp_add.setTitle(self.__tr("add"))
        self.add_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.add_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.add_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.add_linked.setText(self.__tr("linked"))
        self.add_ok.setText(self.__tr("ok"))
        self.grp_remove.setTitle(self.__tr("remove"))
        self.rem_linked.setText(self.__tr("linked"))
        self.rem_ok.setText(self.__tr("ok"))
        self.rem_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.rem_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.rem_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.update_contact_id.setText(QString.null)
        self.textLabel1_2_3_7_3_3.setText(self.__tr("<h2>update_contact</h2>\n"
"The EPP \"update\" command is used to update an instance of an existing object.\n"
"   Names what are not included into disclose list are set to opposite value of the disclose flag value."))
        self.groupBox2_2.setTitle(self.__tr("social security number"))
        self.textLabel3_2_6_6_2_6_2_2_2_2.setText(self.__tr("number"))
        self.textLabel3_2_6_6_2_6_2_2_2.setText(self.__tr("type"))
        self.update_contact_ssn_type.clear()
        self.update_contact_ssn_type.insertItem(self.__tr("op"))
        self.update_contact_ssn_type.insertItem(self.__tr("rc"))
        self.update_contact_ssn_type.insertItem(self.__tr("passport"))
        self.update_contact_ssn_type.insertItem(self.__tr("mpsv"))
        self.update_contact_ssn_type.insertItem(self.__tr("ico"))
        self.textLabel3_2_6_6_2_6_2_3.setText(self.__tr("social security number"))


    def __tr(self,s,c = None):
        return qApp.translate("panel",s,c)
