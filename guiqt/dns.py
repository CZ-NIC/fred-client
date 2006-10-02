# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dns.ui'
#
# Created: Po říj 2 14:18:29 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable


class frame(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("frame")



        self.textLabel_address = QLabel(self,"textLabel_address")
        self.textLabel_address.setGeometry(QRect(10,40,130,20))

        self.name = QLineEdit(self,"name")
        self.name.setGeometry(QRect(150,10,340,22))

        self.addr = QTable(self,"addr")
        self.addr.setNumCols(self.addr.numCols() + 1)
        self.addr.horizontalHeader().setLabel(self.addr.numCols() - 1,self.__tr("address"))
        self.addr.setGeometry(QRect(150,40,340,110))
        self.addr.setFrameShape(QTable.StyledPanel)
        self.addr.setFrameShadow(QTable.Sunken)
        self.addr.setNumRows(1)
        self.addr.setNumCols(1)
        self.addr.setShowGrid(1)
        self.addr.setFocusStyle(QTable.SpreadSheet)

        self.label_dns_name = QLabel(self,"label_dns_name")
        self.label_dns_name.setGeometry(QRect(10,12,130,20))

        self.languageChange()

        self.resize(QSize(510,157).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.addr,SIGNAL("currentChanged(int,int)"),self.addr_current_changed)
        self.connect(self.addr,SIGNAL("valueChanged(int,int)"),self.addr_value_changed)


    def languageChange(self):
        self.setCaption(self.__tr("dns"))
        self.textLabel_address.setText(self.__tr("address"))
        self.addr.horizontalHeader().setLabel(0,self.__tr("address"))
        self.label_dns_name.setText(self.__tr("dns name"))


    def addr_current_changed(self,a0,a1):
        print "frame.addr_current_changed(int,int): Not implemented yet"

    def addr_value_changed(self,a0,a1):
        print "frame.addr_value_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("frame",s,c)
