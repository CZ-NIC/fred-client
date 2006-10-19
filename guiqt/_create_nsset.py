# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_nsset.ui'
#
# Created: Čt říj 19 16:26:25 2006
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



        self.id = QLineEdit(self,"id")
        self.id.setGeometry(QRect(180,110,360,22))

        self.tech = QTable(self,"tech")
        self.tech.setNumCols(self.tech.numCols() + 1)
        self.tech.horizontalHeader().setLabel(self.tech.numCols() - 1,self.__tr("contact"))
        self.tech.setNumRows(self.tech.numRows() + 1)
        self.tech.verticalHeader().setLabel(self.tech.numRows() - 1,self.__tr("1"))
        self.tech.setGeometry(QRect(180,140,360,110))
        self.tech.setNumRows(1)
        self.tech.setNumCols(1)
        self.tech.setShowGrid(1)
        self.tech.setFocusStyle(QTable.SpreadSheet)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,110,160,20))

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,10,530,90))
        self.textLabel1.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,140,160,20))

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,250,160,20))

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(10,590,160,20))

        self.cltrid = QLineEdit(self,"cltrid")
        self.cltrid.setGeometry(QRect(180,590,360,22))

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(10,560,160,20))

        self.auth_info = QLineEdit(self,"auth_info")
        self.auth_info.setGeometry(QRect(180,560,360,22))

        self.frame_dns = QFrame(self,"frame_dns")
        self.frame_dns.setGeometry(QRect(10,280,530,270))
        self.frame_dns.setFrameShape(QFrame.Panel)
        self.frame_dns.setFrameShadow(QFrame.Raised)

        self.languageChange()

        self.resize(QSize(574,638).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.tech,SIGNAL("currentChanged(int,int)"),self.tech_current_changed)
        self.connect(self.tech,SIGNAL("valueChanged(int,int)"),self.tech_value_changed)

        self.setTabOrder(self.id,self.tech)
        self.setTabOrder(self.tech,self.auth_info)
        self.setTabOrder(self.auth_info,self.cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Create NSSET panel"))
        self.id.setText(QString.null)
        self.tech.horizontalHeader().setLabel(0,self.__tr("contact"))
        self.tech.verticalHeader().setLabel(0,self.__tr("1"))
        self.textLabel2.setText(self.__tr("<b>nsset ID</b>"))
        self.textLabel1.setText(self.__tr("<h2>create_nsset</h2>\n"
"The EPP \"create\" command is used to create an instance of an object.\n"
"An object can be created for an indefinite period of time, or an\n"
"object can be created for a specific validity period."))
        self.textLabel3.setText(self.__tr("<b>tech. contact</b>"))
        self.textLabel4.setText(self.__tr("<b>dns</b>"))
        self.textLabel5.setText(self.__tr("clTRID"))
        self.textLabel6.setText(self.__tr("auth. for transfer"))


    def tech_current_changed(self,a0,a1):
        print "ccregWindow.tech_current_changed(int,int): Not implemented yet"

    def tech_value_changed(self,a0,a1):
        print "ccregWindow.tech_value_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ccregWindow",s,c)
