# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'top_toolbar.ui'
#
# Created: Fri Apr 20 16:21:08 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_topToolbar(object):
    def setupUi(self, topToolbar):
        topToolbar.setObjectName("topToolbar")
        topToolbar.resize(QtCore.QSize(QtCore.QRect(0, 0, 750, 58).size()).expandedTo(topToolbar.minimumSizeHint()))

        self.hboxlayout = QtGui.QHBoxLayout(topToolbar)
        self.hboxlayout.setMargin(2)
        self.hboxlayout.setSpacing(12)
        self.hboxlayout.setObjectName("hboxlayout")

        self.toolButton = QtGui.QToolButton(topToolbar)
        self.toolButton.setEnabled(True)
        self.toolButton.setIcon(QtGui.QIcon(":/top_toolbar/images/system-run.png"))
        self.toolButton.setPopupMode(QtGui.QToolButton.DelayedPopup)
        self.toolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolButton.setAutoRaise(True)
        self.toolButton.setObjectName("toolButton")
        self.hboxlayout.addWidget(self.toolButton)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.btn_check_domain = QtGui.QToolButton(topToolbar)
        self.btn_check_domain.setIcon(QtGui.QIcon(":/top_toolbar/images/help-browser.svg"))
        self.btn_check_domain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_check_domain.setObjectName("btn_check_domain")
        self.hboxlayout.addWidget(self.btn_check_domain)

        self.btn_info_domain = QtGui.QToolButton(topToolbar)
        self.btn_info_domain.setIcon(QtGui.QIcon(":/top_toolbar/images/linguist-phrasebookopen.png"))
        self.btn_info_domain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_info_domain.setObjectName("btn_info_domain")
        self.hboxlayout.addWidget(self.btn_info_domain)

        self.btn_create_domain = QtGui.QToolButton(topToolbar)
        self.btn_create_domain.setIcon(QtGui.QIcon(":/top_toolbar/images/applications-internet.svg"))
        self.btn_create_domain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_create_domain.setObjectName("btn_create_domain")
        self.hboxlayout.addWidget(self.btn_create_domain)

        self.btn_update_domain = QtGui.QToolButton(topToolbar)
        self.btn_update_domain.setIcon(QtGui.QIcon(":/top_toolbar/images/network-idle.svg"))
        self.btn_update_domain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_update_domain.setObjectName("btn_update_domain")
        self.hboxlayout.addWidget(self.btn_update_domain)

        self.btn_renew_domain = QtGui.QToolButton(topToolbar)
        self.btn_renew_domain.setIcon(QtGui.QIcon(":/top_toolbar/images/go-home.svg"))
        self.btn_renew_domain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_renew_domain.setObjectName("btn_renew_domain")
        self.hboxlayout.addWidget(self.btn_renew_domain)

        self.retranslateUi(topToolbar)
        QtCore.QObject.connect(self.btn_check_domain, QtCore.SIGNAL("clicked()"), topToolbar.check_domain)
        QtCore.QObject.connect(self.btn_info_domain, QtCore.SIGNAL("clicked()"), topToolbar.info_domain)
        QtCore.QObject.connect(self.btn_create_domain, QtCore.SIGNAL("clicked()"), topToolbar.create_domain)
        QtCore.QObject.connect(self.btn_update_domain, QtCore.SIGNAL("clicked()"), topToolbar.update_domain)
        QtCore.QObject.connect(self.btn_renew_domain, QtCore.SIGNAL("clicked()"), topToolbar.renew_domain)
        QtCore.QMetaObject.connectSlotsByName(topToolbar)

    def retranslateUi(self, topToolbar):
        topToolbar.setWindowTitle(QtGui.QApplication.translate("topToolbar", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("topToolbar", "Run command", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_check_domain.setText(QtGui.QApplication.translate("topToolbar", "Check domain", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_info_domain.setText(QtGui.QApplication.translate("topToolbar", "Info domain", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_create_domain.setText(QtGui.QApplication.translate("topToolbar", "Create domain", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_update_domain.setText(QtGui.QApplication.translate("topToolbar", "Update domain", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_renew_domain.setText(QtGui.QApplication.translate("topToolbar", "Renew domain", None, QtGui.QApplication.UnicodeUTF8))

import main_frame_rc
