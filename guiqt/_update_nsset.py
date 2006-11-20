# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_nsset.ui'
#
# Created: Po lis 20 12:33:51 2006
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



        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,110,160,20))

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,470,160,20))

        self.frame_add_dns = QFrame(self,"frame_add_dns")
        self.frame_add_dns.setGeometry(QRect(10,190,530,270))
        self.frame_add_dns.setFrameShape(QFrame.Panel)
        self.frame_add_dns.setFrameShadow(QFrame.Raised)

        self.line1_2 = QFrame(self,"line1_2")
        self.line1_2.setGeometry(QRect(10,140,530,20))
        self.line1_2.setFrameShape(QFrame.HLine)
        self.line1_2.setFrameShadow(QFrame.Sunken)
        self.line1_2.setFrameShape(QFrame.HLine)

        self.textLabel9 = QLabel(self,"textLabel9")
        self.textLabel9.setGeometry(QRect(10,10,530,90))
        self.textLabel9.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.textLabel10 = QLabel(self,"textLabel10")
        self.textLabel10.setGeometry(QRect(10,160,530,21))

        self.id = QLineEdit(self,"id")
        self.id.setGeometry(QRect(180,110,360,22))

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

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(10,650,160,100))
        self.textLabel5.setAlignment(QLabel.WordBreak | QLabel.AlignTop)

        self.line1_2_2_2 = QFrame(self,"line1_2_2_2")
        self.line1_2_2_2.setGeometry(QRect(10,970,530,20))
        self.line1_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QFrame.HLine)

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,610,530,30))

        self.textLabel7 = QLabel(self,"textLabel7")
        self.textLabel7.setGeometry(QRect(10,910,530,21))

        self.line1_2_2 = QFrame(self,"line1_2_2")
        self.line1_2_2.setGeometry(QRect(10,890,530,20))
        self.line1_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2.setFrameShape(QFrame.HLine)

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(10,990,160,20))

        self.auth_info = QLineEdit(self,"auth_info")
        self.auth_info.setGeometry(QRect(180,940,360,22))

        self.rem_name = QTable(self,"rem_name")
        self.rem_name.setNumCols(self.rem_name.numCols() + 1)
        self.rem_name.horizontalHeader().setLabel(self.rem_name.numCols() - 1,self.__tr("dns name"))
        self.rem_name.setGeometry(QRect(180,650,360,110))
        self.rem_name.setFrameShape(QTable.StyledPanel)
        self.rem_name.setFrameShadow(QTable.Sunken)
        self.rem_name.setNumRows(1)
        self.rem_name.setNumCols(1)
        self.rem_name.setShowGrid(1)
        self.rem_name.setFocusStyle(QTable.SpreadSheet)

        self.rem_tech = QTable(self,"rem_tech")
        self.rem_tech.setNumCols(self.rem_tech.numCols() + 1)
        self.rem_tech.horizontalHeader().setLabel(self.rem_tech.numCols() - 1,self.__tr("technical contact"))
        self.rem_tech.setGeometry(QRect(180,770,360,110))
        self.rem_tech.setFrameShape(QTable.StyledPanel)
        self.rem_tech.setFrameShadow(QTable.Sunken)
        self.rem_tech.setNumRows(1)
        self.rem_tech.setNumCols(1)
        self.rem_tech.setShowGrid(1)
        self.rem_tech.setFocusStyle(QTable.SpreadSheet)

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,770,160,100))
        self.textLabel4.setAlignment(QLabel.WordBreak | QLabel.AlignTop)

        self.textLabel8 = QLabel(self,"textLabel8")
        self.textLabel8.setGeometry(QRect(10,940,160,20))

        self.cltrid = QLineEdit(self,"cltrid")
        self.cltrid.setGeometry(QRect(180,990,360,22))

        self.line1 = QFrame(self,"line1")
        self.line1.setGeometry(QRect(10,590,530,20))
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setFrameShape(QFrame.HLine)

        self.languageChange()

        self.resize(QSize(574,1041).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.add_tech,SIGNAL("currentChanged(int,int)"),self.add_tech_current_changed)
        self.connect(self.add_tech,SIGNAL("valueChanged(int,int)"),self.add_tech_value_changed)
        self.connect(self.rem_name,SIGNAL("currentChanged(int,int)"),self.rem_dns_name_current_changed)
        self.connect(self.rem_name,SIGNAL("valueChanged(int,int)"),self.rem_dns_name_value_changed)
        self.connect(self.rem_tech,SIGNAL("currentChanged(int,int)"),self.rem_tech_current_changed)
        self.connect(self.rem_tech,SIGNAL("valueChanged(int,int)"),self.rem_tech_value_changed)

        self.setTabOrder(self.id,self.add_tech)
        self.setTabOrder(self.add_tech,self.rem_name)
        self.setTabOrder(self.rem_name,self.rem_tech)
        self.setTabOrder(self.rem_tech,self.auth_info)
        self.setTabOrder(self.auth_info,self.cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Update NSSET panel"))
        self.textLabel1.setText(self.__tr("<b>nsset ID</b>"))
        self.textLabel2.setText(self.__tr("technical contact"))
        self.textLabel9.setText(self.__tr("<h2>update_nsset</h2>\n"
"The EPP \"update\" command is used to update an instance of an existing object.\n"
"   Names what are not included into disclose list are set to opposite value of the disclose flag value."))
        self.textLabel10.setText(self.__tr("<h3>Add</h3>"))
        self.id.setText(QString.null)
        self.add_tech.horizontalHeader().setLabel(0,self.__tr("technical contact"))
        self.textLabel5.setText(self.__tr("dns name<br>(max 9 names)"))
        self.textLabel3.setText(self.__tr("<h3>Remove</h3>"))
        self.textLabel7.setText(self.__tr("<h3>Change</h3>"))
        self.textLabel6.setText(self.__tr("clTRID"))
        self.rem_name.horizontalHeader().setLabel(0,self.__tr("dns name"))
        self.rem_tech.horizontalHeader().setLabel(0,self.__tr("technical contact"))
        self.textLabel4.setText(self.__tr("technical contact"))
        self.textLabel8.setText(self.__tr("auth. for transfer"))


    def add_tech_current_changed(self,a0,a1):
        print "FredWindow.add_tech_current_changed(int,int): Not implemented yet"

    def add_tech_value_changed(self,a0,a1):
        print "FredWindow.add_tech_value_changed(int,int): Not implemented yet"

    def rem_dns_name_current_changed(self,a0,a1):
        print "FredWindow.rem_dns_name_current_changed(int,int): Not implemented yet"

    def rem_dns_name_value_changed(self,a0,a1):
        print "FredWindow.rem_dns_name_value_changed(int,int): Not implemented yet"

    def rem_tech_current_changed(self,a0,a1):
        print "FredWindow.rem_tech_current_changed(int,int): Not implemented yet"

    def rem_tech_value_changed(self,a0,a1):
        print "FredWindow.rem_tech_value_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("FredWindow",s,c)
