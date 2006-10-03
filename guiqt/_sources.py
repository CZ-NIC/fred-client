# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sources.ui'
#
# Created: Út říj 3 13:09:05 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ccregWindow(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ccregWindow")



        self.btn_close = QPushButton(self,"btn_close")
        self.btn_close.setGeometry(QRect(480,10,112,30))

        self.message = QLabel(self,"message")
        self.message.setGeometry(QRect(10,10,460,30))

        self.tabWidget = QTabWidget(self,"tabWidget")
        self.tabWidget.setGeometry(QRect(10,50,590,450))

        self.tab = QWidget(self.tabWidget,"tab")

        self.command = QTextEdit(self.tab,"command")
        self.command.setGeometry(QRect(10,60,570,350))

        self.textLabel2 = QLabel(self.tab,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,10,570,40))
        self.textLabel2.setAlignment(QLabel.AlignTop)
        self.tabWidget.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget,"tab_2")

        self.response = QTextEdit(self.tab_2,"response")
        self.response.setGeometry(QRect(10,50,570,360))

        self.textLabel3 = QLabel(self.tab_2,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,10,570,40))
        self.textLabel3.setAlignment(QLabel.AlignTop)
        self.tabWidget.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget,"TabPage")

        self.command_line = QLineEdit(self.TabPage,"command_line")
        self.command_line.setGeometry(QRect(10,50,560,22))

        self.textLabel4 = QLabel(self.TabPage,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,10,570,40))
        self.textLabel4.setAlignment(QLabel.AlignTop)
        self.tabWidget.insertTab(self.TabPage,QString.fromLatin1(""))

        self.languageChange()

        self.resize(QSize(613,518).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.btn_close,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("Sources"))
        self.btn_close.setText(self.__tr("&Close"))
        self.btn_close.setAccel(self.__tr("Alt+C"))
        self.message.setText(self.__tr("command name"))
        self.textLabel2.setText(self.__tr("This document was sent to the EPP server. If is empty, it has not been sent already."))
        self.tabWidget.changeTab(self.tab,self.__tr("Command XML"))
        self.textLabel3.setText(self.__tr("This document was received from EPP server. If is empty, it has not been received already."))
        self.tabWidget.changeTab(self.tab_2,self.__tr("Response XML"))
        self.textLabel4.setText(self.__tr("This example was build from input. It can be used in ccreg_client console."))
        self.tabWidget.changeTab(self.TabPage,self.__tr("Command line"))


    def __tr(self,s,c = None):
        return qApp.translate("ccregWindow",s,c)
