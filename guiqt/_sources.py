# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sources.ui'
#
# Created: St zář 27 10:55:56 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class panel(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("panel")



        self.response = QTextEdit(self,"response")
        self.response.setGeometry(QRect(20,390,560,250))

        self.command = QTextEdit(self,"command")
        self.command.setGeometry(QRect(20,110,560,240))

        self.command_line = QLineEdit(self,"command_line")
        self.command_line.setGeometry(QRect(20,60,560,22))

        self.btn_close = QPushButton(self,"btn_close")
        self.btn_close.setGeometry(QRect(470,10,112,30))

        self.textLabel3_2 = QLabel(self,"textLabel3_2")
        self.textLabel3_2.setGeometry(QRect(20,90,150,20))

        self.textLabel3_2_2 = QLabel(self,"textLabel3_2_2")
        self.textLabel3_2_2.setGeometry(QRect(20,370,150,20))

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(20,40,150,20))

        self.languageChange()

        self.resize(QSize(600,661).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.btn_close,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("Sources"))
        self.btn_close.setText(self.__tr("&Close"))
        self.btn_close.setAccel(self.__tr("Alt+C"))
        self.textLabel3_2.setText(self.__tr("Command XML"))
        self.textLabel3_2_2.setText(self.__tr("Response XML"))
        self.textLabel3.setText(self.__tr("Command line"))


    def __tr(self,s,c = None):
        return qApp.translate("panel",s,c)
