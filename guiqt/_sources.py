# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sources.ui'
#
# Created: Út říj 3 09:55:47 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ccregWindow(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ccregWindow")



        self.tabWidget = QTabWidget(self,"tabWidget")
        self.tabWidget.setGeometry(QRect(10,50,590,360))

        self.tab = QWidget(self.tabWidget,"tab")

        self.command = QTextEdit(self.tab,"command")
        self.command.setGeometry(QRect(10,10,570,310))
        self.tabWidget.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget,"tab_2")

        self.response = QTextEdit(self.tab_2,"response")
        self.response.setGeometry(QRect(8,13,570,300))
        self.tabWidget.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget,"TabPage")

        self.command_line = QLineEdit(self.TabPage,"command_line")
        self.command_line.setGeometry(QRect(10,20,560,22))
        self.tabWidget.insertTab(self.TabPage,QString.fromLatin1(""))

        self.btn_close = QPushButton(self,"btn_close")
        self.btn_close.setGeometry(QRect(480,10,112,30))

        self.languageChange()

        self.resize(QSize(613,431).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Sources"))
        self.tabWidget.changeTab(self.tab,self.__tr("Command XML"))
        self.tabWidget.changeTab(self.tab_2,self.__tr("Response XML"))
        self.tabWidget.changeTab(self.TabPage,self.__tr("Command line"))
        self.btn_close.setText(self.__tr("&Close"))
        self.btn_close.setAccel(self.__tr("Alt+C"))


    def __tr(self,s,c = None):
        return qApp.translate("ccregWindow",s,c)
