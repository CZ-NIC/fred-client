# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sources.ui'
#
# Created: Tue Dec 12 14:10:25 2006
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_FredWindow(object):
    def setupUi(self, FredWindow):
        FredWindow.setObjectName("FredWindow")
        FredWindow.resize(QtCore.QSize(QtCore.QRect(0,0,613,518).size()).expandedTo(FredWindow.minimumSizeHint()))

        self.btn_close = QtGui.QPushButton(FredWindow)
        self.btn_close.setGeometry(QtCore.QRect(480,10,112,30))
        self.btn_close.setObjectName("btn_close")

        self.tabWidget = QtGui.QTabWidget(FredWindow)
        self.tabWidget.setGeometry(QtCore.QRect(10,50,590,450))
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.command = QtGui.QTextEdit(self.tab)
        self.command.setGeometry(QtCore.QRect(10,60,570,350))
        self.command.setObjectName("command")

        self.textLabel2 = QtGui.QLabel(self.tab)
        self.textLabel2.setGeometry(QtCore.QRect(10,10,570,40))
        self.textLabel2.setAlignment(QtCore.Qt.AlignTop)
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")
        self.tabWidget.addTab(self.tab,"")

        self.tab1 = QtGui.QWidget()
        self.tab1.setObjectName("tab1")

        self.response = QtGui.QTextEdit(self.tab1)
        self.response.setGeometry(QtCore.QRect(10,50,570,360))
        self.response.setObjectName("response")

        self.textLabel3 = QtGui.QLabel(self.tab1)
        self.textLabel3.setGeometry(QtCore.QRect(10,10,570,40))
        self.textLabel3.setAlignment(QtCore.Qt.AlignTop)
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")
        self.tabWidget.addTab(self.tab1,"")

        self.TabPage = QtGui.QWidget()
        self.TabPage.setObjectName("TabPage")

        self.command_line = QtGui.QLineEdit(self.TabPage)
        self.command_line.setGeometry(QtCore.QRect(10,50,560,22))
        self.command_line.setObjectName("command_line")

        self.textLabel4 = QtGui.QLabel(self.TabPage)
        self.textLabel4.setGeometry(QtCore.QRect(10,10,570,40))
        self.textLabel4.setAlignment(QtCore.Qt.AlignTop)
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")
        self.tabWidget.addTab(self.TabPage,"")

        self.retranslateUi(FredWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.btn_close,QtCore.SIGNAL("clicked()"),FredWindow.close)
        QtCore.QMetaObject.connectSlotsByName(FredWindow)

    def retranslateUi(self, FredWindow):
        FredWindow.setWindowTitle(QtGui.QApplication.translate("FredWindow", "Sources", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_close.setText(QtGui.QApplication.translate("FredWindow", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_close.setShortcut(QtGui.QApplication.translate("FredWindow", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("FredWindow", "This document was sent to the EPP server. If is empty, it has not been sent already.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("FredWindow", "Command XML", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("FredWindow", "This document was received from EPP server. If is empty, it has not been received already.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), QtGui.QApplication.translate("FredWindow", "Response XML", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("FredWindow", "This example was build from input. It can be used in fred_client console.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabPage), QtGui.QApplication.translate("FredWindow", "Command line", None, QtGui.QApplication.UnicodeUTF8))

