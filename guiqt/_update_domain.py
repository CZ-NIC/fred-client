# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_domain.ui'
#
# Created: Po říj 23 10:24:04 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable


class FredWindow(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("FredWindow")



        self.rem_admin = QTable(self,"rem_admin")
        self.rem_admin.setNumCols(self.rem_admin.numCols() + 1)
        self.rem_admin.horizontalHeader().setLabel(self.rem_admin.numCols() - 1,self.__tr("admin"))
        self.rem_admin.setGeometry(QRect(180,460,360,110))
        self.rem_admin.setFrameShape(QTable.StyledPanel)
        self.rem_admin.setFrameShadow(QTable.Sunken)
        self.rem_admin.setNumRows(1)
        self.rem_admin.setNumCols(1)
        self.rem_admin.setShowGrid(1)
        self.rem_admin.setFocusStyle(QTable.SpreadSheet)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,10,530,90))
        self.textLabel2.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,110,160,20))

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,160,530,21))

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(10,190,160,20))

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(10,430,530,30))

        self.textLabel7 = QLabel(self,"textLabel7")
        self.textLabel7.setGeometry(QRect(10,460,160,20))

        self.textLabel8 = QLabel(self,"textLabel8")
        self.textLabel8.setGeometry(QRect(10,700,530,21))

        self.textLabel10 = QLabel(self,"textLabel10")
        self.textLabel10.setGeometry(QRect(10,870,160,20))

        self.rem_status = QCheckBox(self,"rem_status")
        self.rem_status.setGeometry(QRect(10,590,150,20))

        self.add_status = QCheckBox(self,"add_status")
        self.add_status.setGeometry(QRect(10,320,150,20))

        self.grp_rem_status = QButtonGroup(self,"grp_rem_status")
        self.grp_rem_status.setEnabled(0)
        self.grp_rem_status.setGeometry(QRect(180,580,360,90))

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

        self.line2 = QFrame(self,"line2")
        self.line2.setGeometry(QRect(10,410,530,20))
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setFrameShape(QFrame.HLine)

        self.line3 = QFrame(self,"line3")
        self.line3.setGeometry(QRect(10,680,530,20))
        self.line3.setFrameShape(QFrame.HLine)
        self.line3.setFrameShadow(QFrame.Sunken)
        self.line3.setFrameShape(QFrame.HLine)

        self.line1 = QFrame(self,"line1")
        self.line1.setGeometry(QRect(10,140,530,20))
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setFrameShape(QFrame.HLine)

        self.name = QLineEdit(self,"name")
        self.name.setGeometry(QRect(180,110,360,22))

        self.add_admin = QTable(self,"add_admin")
        self.add_admin.setNumCols(self.add_admin.numCols() + 1)
        self.add_admin.horizontalHeader().setLabel(self.add_admin.numCols() - 1,self.__tr("admin"))
        self.add_admin.setGeometry(QRect(180,190,360,110))
        self.add_admin.setFrameShape(QTable.StyledPanel)
        self.add_admin.setFrameShadow(QTable.Sunken)
        self.add_admin.setNumRows(1)
        self.add_admin.setNumCols(1)
        self.add_admin.setShowGrid(1)
        self.add_admin.setFocusStyle(QTable.SpreadSheet)

        self.grp_add_status = QButtonGroup(self,"grp_add_status")
        self.grp_add_status.setEnabled(0)
        self.grp_add_status.setGeometry(QRect(180,310,360,90))

        self.add_ok = QCheckBox(self.grp_add_status,"add_ok")
        self.add_ok.setGeometry(QRect(10,40,70,20))

        self.add_clientUpdateProhibited = QCheckBox(self.grp_add_status,"add_clientUpdateProhibited")
        self.add_clientUpdateProhibited.setGeometry(QRect(140,20,210,20))

        self.add_clientDeleteProhibited = QCheckBox(self.grp_add_status,"add_clientDeleteProhibited")
        self.add_clientDeleteProhibited.setGeometry(QRect(140,40,210,20))

        self.add_clientTransferProhibited = QCheckBox(self.grp_add_status,"add_clientTransferProhibited")
        self.add_clientTransferProhibited.setGeometry(QRect(140,60,210,20))

        self.add_linked = QCheckBox(self.grp_add_status,"add_linked")
        self.add_linked.setGeometry(QRect(10,20,70,20))

        self.cltrid = QLineEdit(self,"cltrid")
        self.cltrid.setGeometry(QRect(180,870,360,22))

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(330,840,210,20))

        self.textLabel9 = QLabel(self,"textLabel9")
        self.textLabel9.setGeometry(QRect(10,840,160,20))

        self.val_ex_date = QDateEdit(self,"val_ex_date")
        self.val_ex_date.setEnabled(0)
        self.val_ex_date.setGeometry(QRect(220,840,97,22))

        self.check_val_ex_date = QCheckBox(self,"check_val_ex_date")
        self.check_val_ex_date.setGeometry(QRect(180,840,30,20))

        self.line4 = QFrame(self,"line4")
        self.line4.setGeometry(QRect(10,820,530,20))
        self.line4.setFrameShape(QFrame.HLine)
        self.line4.setFrameShadow(QFrame.Sunken)
        self.line4.setFrameShape(QFrame.HLine)

        self.chg_registrant = QLineEdit(self,"chg_registrant")
        self.chg_registrant.setGeometry(QRect(180,760,360,22))

        self.chg_pw = QLineEdit(self,"chg_pw")
        self.chg_pw.setGeometry(QRect(180,790,360,22))

        self.textLabel12 = QLabel(self,"textLabel12")
        self.textLabel12.setGeometry(QRect(10,760,160,20))

        self.textLabel13 = QLabel(self,"textLabel13")
        self.textLabel13.setGeometry(QRect(10,790,160,20))

        self.textLabel11 = QLabel(self,"textLabel11")
        self.textLabel11.setGeometry(QRect(10,730,160,20))

        self.chg_nsset = QLineEdit(self,"chg_nsset")
        self.chg_nsset.setGeometry(QRect(180,730,360,22))

        self.languageChange()

        self.resize(QSize(574,918).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.add_status,SIGNAL("toggled(bool)"),self.grp_add_status.setEnabled)
        self.connect(self.rem_status,SIGNAL("toggled(bool)"),self.grp_rem_status.setEnabled)
        self.connect(self.add_admin,SIGNAL("valueChanged(int,int)"),self.add_admin_value_changed)
        self.connect(self.add_admin,SIGNAL("currentChanged(int,int)"),self.add_admin_current_changed)
        self.connect(self.rem_admin,SIGNAL("currentChanged(int,int)"),self.rem_admin_current_changed)
        self.connect(self.rem_admin,SIGNAL("valueChanged(int,int)"),self.rem_admin_value_changed)
        self.connect(self.check_val_ex_date,SIGNAL("toggled(bool)"),self.val_ex_date.setEnabled)

        self.setTabOrder(self.name,self.add_admin)
        self.setTabOrder(self.add_admin,self.add_status)
        self.setTabOrder(self.add_status,self.add_linked)
        self.setTabOrder(self.add_linked,self.add_ok)
        self.setTabOrder(self.add_ok,self.add_clientUpdateProhibited)
        self.setTabOrder(self.add_clientUpdateProhibited,self.add_clientDeleteProhibited)
        self.setTabOrder(self.add_clientDeleteProhibited,self.add_clientTransferProhibited)
        self.setTabOrder(self.add_clientTransferProhibited,self.rem_admin)
        self.setTabOrder(self.rem_admin,self.rem_status)
        self.setTabOrder(self.rem_status,self.rem_linked)
        self.setTabOrder(self.rem_linked,self.rem_ok)
        self.setTabOrder(self.rem_ok,self.rem_clientUpdateProhibited)
        self.setTabOrder(self.rem_clientUpdateProhibited,self.rem_clientDeleteProhibited)
        self.setTabOrder(self.rem_clientDeleteProhibited,self.rem_clientTransferProhibited)
        self.setTabOrder(self.rem_clientTransferProhibited,self.chg_nsset)
        self.setTabOrder(self.chg_nsset,self.chg_registrant)
        self.setTabOrder(self.chg_registrant,self.chg_pw)
        self.setTabOrder(self.chg_pw,self.check_val_ex_date)
        self.setTabOrder(self.check_val_ex_date,self.val_ex_date)
        self.setTabOrder(self.val_ex_date,self.cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Update domain panel"))
        self.rem_admin.horizontalHeader().setLabel(0,self.__tr("admin"))
        self.textLabel2.setText(self.__tr("<h2>update_domain</h2>\n"
"The EPP \"update\" command is used to update an instance of an existing object.\n"
"   Names what are not included into disclose list are set to opposite value of the disclose flag value."))
        self.textLabel3.setText(self.__tr("<b>domain name</b>"))
        self.textLabel4.setText(self.__tr("<h3>Add</h3>"))
        self.textLabel5.setText(self.__tr("admin handle"))
        self.textLabel6.setText(self.__tr("<h3>Remove</h3>"))
        self.textLabel7.setText(self.__tr("admin handle"))
        self.textLabel8.setText(self.__tr("<h3>Change</h3>"))
        self.textLabel10.setText(self.__tr("clTRID"))
        self.rem_status.setText(self.__tr("status"))
        self.add_status.setText(self.__tr("status"))
        self.grp_rem_status.setTitle(self.__tr("status"))
        self.rem_linked.setText(self.__tr("linked"))
        self.rem_ok.setText(self.__tr("ok"))
        self.rem_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.rem_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.rem_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.name.setText(QString.null)
        self.add_admin.horizontalHeader().setLabel(0,self.__tr("admin"))
        self.grp_add_status.setTitle(self.__tr("status"))
        self.add_ok.setText(self.__tr("ok"))
        self.add_clientUpdateProhibited.setText(self.__tr("clientUpdateProhibited"))
        self.add_clientDeleteProhibited.setText(self.__tr("clientDeleteProhibited"))
        self.add_clientTransferProhibited.setText(self.__tr("clientTransferProhibited"))
        self.add_linked.setText(self.__tr("linked"))
        self.textLabel1.setText(self.__tr("(required for <b>enum</b> domains)"))
        self.textLabel9.setText(self.__tr("valExDate"))
        self.check_val_ex_date.setText(QString.null)
        self.textLabel12.setText(self.__tr("registrant"))
        self.textLabel13.setText(self.__tr("pasword"))
        self.textLabel11.setText(self.__tr("nsset"))


    def add_admin_current_changed(self,a0,a1):
        print "FredWindow.add_admin_current_changed(int,int): Not implemented yet"

    def add_admin_value_changed(self,a0,a1):
        print "FredWindow.add_admin_value_changed(int,int): Not implemented yet"

    def rem_admin_current_changed(self,a0,a1):
        print "FredWindow.rem_admin_current_changed(int,int): Not implemented yet"

    def rem_admin_value_changed(self,a0,a1):
        print "FredWindow.rem_admin_value_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("FredWindow",s,c)
