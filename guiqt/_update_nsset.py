# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_nsset.ui'
#
# Created: Čt říj 19 16:26:37 2006
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



        self.line1 = QFrame(self,"line1")
        self.line1.setGeometry(QRect(10,680,530,20))
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setFrameShape(QFrame.HLine)

        self.grp_rem_status = QButtonGroup(self,"grp_rem_status")
        self.grp_rem_status.setEnabled(0)
        self.grp_rem_status.setGeometry(QRect(180,980,360,90))

        self.rem_linked = QCheckBox(self.grp_rem_status,"rem_linked")
        self.rem_linked.setGeometry(QRect(10,20,70,20))

        self.rem_ok = QCheckBox(self.grp_rem_status,"rem_ok")
        self.rem_ok.setGeometry(QRect(10,40,70,20))

        self.rem_clientUpdateProhibited = QCheckBox(self.grp_rem_status,"rem_clientUpdateProhibited")
        self.rem_clientUpdateProhibited.setGeometry(QRect(140,20,210,20))

        self.rem_clientDeleteProhibited = QCheckBox(self.grp_rem_status,"rem_clientDeleteProhibited")
        self.rem_clientDeleteProhibited.setGeometry(QRect(140,40,210,20))

        self.rem_clientTransferProhibited = QCheckBox(self.grp_rem_status,"rem_clientTransferProhibited")
        self.rem_clientTransferProhibited.setGeometry(QRect(140,60,210,20))

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,110,160,20))

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,470,160,20))

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,700,530,30))

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,860,160,100))
        self.textLabel4.setAlignment(QLabel.WordBreak | QLabel.AlignTop)

        self.frame_add_dns = QFrame(self,"frame_add_dns")
        self.frame_add_dns.setGeometry(QRect(10,190,530,270))
        self.frame_add_dns.setFrameShape(QFrame.Panel)
        self.frame_add_dns.setFrameShadow(QFrame.Raised)

        self.line1_2 = QFrame(self,"line1_2")
        self.line1_2.setGeometry(QRect(10,140,530,20))
        self.line1_2.setFrameShape(QFrame.HLine)
        self.line1_2.setFrameShadow(QFrame.Sunken)
        self.line1_2.setFrameShape(QFrame.HLine)

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(10,1180,160,20))

        self.cltrid = QLineEdit(self,"cltrid")
        self.cltrid.setGeometry(QRect(180,1180,360,22))

        self.line1_2_2_2 = QFrame(self,"line1_2_2_2")
        self.line1_2_2_2.setGeometry(QRect(10,1160,530,20))
        self.line1_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QFrame.HLine)

        self.textLabel7 = QLabel(self,"textLabel7")
        self.textLabel7.setGeometry(QRect(10,1100,530,21))

        self.textLabel8 = QLabel(self,"textLabel8")
        self.textLabel8.setGeometry(QRect(10,1130,160,20))

        self.line1_2_2 = QFrame(self,"line1_2_2")
        self.line1_2_2.setGeometry(QRect(10,1080,530,20))
        self.line1_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2.setFrameShape(QFrame.HLine)

        self.textLabel9 = QLabel(self,"textLabel9")
        self.textLabel9.setGeometry(QRect(10,10,530,90))
        self.textLabel9.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.textLabel10 = QLabel(self,"textLabel10")
        self.textLabel10.setGeometry(QRect(10,160,530,21))

        self.id = QLineEdit(self,"id")
        self.id.setGeometry(QRect(180,110,360,22))

        self.auth_info = QLineEdit(self,"auth_info")
        self.auth_info.setGeometry(QRect(180,1130,360,22))

        self.grp_add_status = QButtonGroup(self,"grp_add_status")
        self.grp_add_status.setEnabled(0)
        self.grp_add_status.setGeometry(QRect(180,590,360,90))

        self.add_clientDeleteProhibited = QCheckBox(self.grp_add_status,"add_clientDeleteProhibited")
        self.add_clientDeleteProhibited.setGeometry(QRect(140,40,210,20))

        self.add_clientTransferProhibited = QCheckBox(self.grp_add_status,"add_clientTransferProhibited")
        self.add_clientTransferProhibited.setGeometry(QRect(140,60,210,20))

        self.add_clientUpdateProhibited = QCheckBox(self.grp_add_status,"add_clientUpdateProhibited")
        self.add_clientUpdateProhibited.setGeometry(QRect(140,20,210,20))

        self.add_linked = QCheckBox(self.grp_add_status,"add_linked")
        self.add_linked.setGeometry(QRect(10,20,70,20))

        self.add_ok = QCheckBox(self.grp_add_status,"add_ok")
        self.add_ok.setGeometry(QRect(10,40,70,20))

        self.add_status = QCheckBox(self,"add_status")
        self.add_status.setGeometry(QRect(10,600,150,20))

        self.rem_status = QCheckBox(self,"rem_status")
        self.rem_status.setGeometry(QRect(10,990,150,20))

        self.add_tech = QTable(self,"add_tech")
        self.add_tech.setNumCols(self.add_tech.numCols() + 1)
        self.add_tech.horizontalHeader().setLabel(self.add_tech.numCols() - 1,self.__tr("technical contact"))
        self.add_tech.setGeometry(QRect(180,470,360,110))
        self.add_tech.setFrameShape(QTable.StyledPanel)
        self.add_tech.setFrameShadow(QTable.Sunken)
        self.add_tech.setNumRows(1)
        self.add_tech.setNumCols(1)
        self.add_tech.setShowGrid(1)
        self.add_tech.setFocusStyle(QTable.SpreadSheet)

        self.rem_tech = QTable(self,"rem_tech")
        self.rem_tech.setNumCols(self.rem_tech.numCols() + 1)
        self.rem_tech.horizontalHeader().setLabel(self.rem_tech.numCols() - 1,self.__tr("technical contact"))
        self.rem_tech.setGeometry(QRect(180,860,360,110))
        self.rem_tech.setFrameShape(QTable.StyledPanel)
        self.rem_tech.setFrameShadow(QTable.Sunken)
        self.rem_tech.setNumRows(1)
        self.rem_tech.setNumCols(1)
        self.rem_tech.setShowGrid(1)
        self.rem_tech.setFocusStyle(QTable.SpreadSheet)

        self.rem_name = QTable(self,"rem_name")
        self.rem_name.setNumCols(self.rem_name.numCols() + 1)
        self.rem_name.horizontalHeader().setLabel(self.rem_name.numCols() - 1,self.__tr("dns name"))
        self.rem_name.setGeometry(QRect(180,740,360,110))
        self.rem_name.setFrameShape(QTable.StyledPanel)
        self.rem_name.setFrameShadow(QTable.Sunken)
        self.rem_name.setNumRows(1)
        self.rem_name.setNumCols(1)
        self.rem_name.setShowGrid(1)
        self.rem_name.setFocusStyle(QTable.SpreadSheet)

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(10,740,160,100))
        self.textLabel5.setAlignment(QLabel.WordBreak | QLabel.AlignTop)

        self.languageChange()

        self.resize(QSize(574,1224).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.add_status,SIGNAL("toggled(bool)"),self.grp_add_status.setEnabled)
        self.connect(self.rem_status,SIGNAL("toggled(bool)"),self.grp_rem_status.setEnabled)
        self.connect(self.add_tech,SIGNAL("currentChanged(int,int)"),self.add_tech_current_changed)
        self.connect(self.add_tech,SIGNAL("valueChanged(int,int)"),self.add_tech_value_changed)
        self.connect(self.rem_name,SIGNAL("currentChanged(int,int)"),self.rem_dns_name_current_changed)
        self.connect(self.rem_name,SIGNAL("valueChanged(int,int)"),self.rem_dns_name_value_changed)
        self.connect(self.rem_tech,SIGNAL("currentChanged(int,int)"),self.rem_tech_current_changed)
        self.connect(self.rem_tech,SIGNAL("valueChanged(int,int)"),self.rem_tech_value_changed)

        self.setTabOrder(self.id,self.add_tech)
        self.setTabOrder(self.add_tech,self.add_status)
        self.setTabOrder(self.add_status,self.add_linked)
        self.setTabOrder(self.add_linked,self.add_ok)
        self.setTabOrder(self.add_ok,self.add_clientUpdateProhibited)
        self.setTabOrder(self.add_clientUpdateProhibited,self.add_clientDeleteProhibited)
        self.setTabOrder(self.add_clientDeleteProhibited,self.add_clientTransferProhibited)
        self.setTabOrder(self.add_clientTransferProhibited,self.rem_name)
        self.setTabOrder(self.rem_name,self.rem_tech)
        self.setTabOrder(self.rem_tech,self.rem_status)
        self.setTabOrder(self.rem_status,self.rem_linked)
        self.setTabOrder(self.rem_linked,self.rem_ok)
        self.setTabOrder(self.rem_ok,self.rem_clientUpdateProhibited)
        self.setTabOrder(self.rem_clientUpdateProhibited,self.rem_clientDeleteProhibited)
        self.setTabOrder(self.rem_clientDeleteProhibited,self.rem_clientTransferProhibited)
        self.setTabOrder(self.rem_clientTransferProhibited,self.auth_info)
        self.setTabOrder(self.auth_info,self.cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Update NSSET panel"))
        self.grp_rem_status.setTitle(self.__tr("status"))
        self.rem_linked.setText(self.__tr("linked"))
        self.rem_ok.setText(self.__tr("ok"))
        self.rem_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.rem_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.rem_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.textLabel1.setText(self.__tr("<b>nsset ID</b>"))
        self.textLabel2.setText(self.__tr("technical contact"))
        self.textLabel3.setText(self.__tr("<h3>Remove</h3>"))
        self.textLabel4.setText(self.__tr("technical contact"))
        self.textLabel6.setText(self.__tr("clTRID"))
        self.textLabel7.setText(self.__tr("<h3>Change</h3>"))
        self.textLabel8.setText(self.__tr("auth. for transfer"))
        self.textLabel9.setText(self.__tr("<h2>update_nsset</h2>\n"
"The EPP \"update\" command is used to update an instance of an existing object.\n"
"   Names what are not included into disclose list are set to opposite value of the disclose flag value."))
        self.textLabel10.setText(self.__tr("<h3>Add</h3>"))
        self.id.setText(QString.null)
        self.grp_add_status.setTitle(self.__tr("status"))
        self.add_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.add_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.add_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.add_linked.setText(self.__tr("linked"))
        self.add_ok.setText(self.__tr("ok"))
        self.add_status.setText(self.__tr("status"))
        self.rem_status.setText(self.__tr("status"))
        self.add_tech.horizontalHeader().setLabel(0,self.__tr("technical contact"))
        self.rem_tech.horizontalHeader().setLabel(0,self.__tr("technical contact"))
        self.rem_name.horizontalHeader().setLabel(0,self.__tr("dns name"))
        self.textLabel5.setText(self.__tr("dns name<br>(max 9 names)"))


    def add_tech_current_changed(self,a0,a1):
        print "ccregWindow.add_tech_current_changed(int,int): Not implemented yet"

    def add_tech_value_changed(self,a0,a1):
        print "ccregWindow.add_tech_value_changed(int,int): Not implemented yet"

    def rem_dns_name_current_changed(self,a0,a1):
        print "ccregWindow.rem_dns_name_current_changed(int,int): Not implemented yet"

    def rem_dns_name_value_changed(self,a0,a1):
        print "ccregWindow.rem_dns_name_value_changed(int,int): Not implemented yet"

    def rem_tech_current_changed(self,a0,a1):
        print "ccregWindow.rem_tech_current_changed(int,int): Not implemented yet"

    def rem_tech_value_changed(self,a0,a1):
        print "ccregWindow.rem_tech_value_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ccregWindow",s,c)
