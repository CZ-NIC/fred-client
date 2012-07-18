# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'command_create.ui'
#
# Created: Fri Apr 20 15:53:54 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_CommandCreate(object):
    def setupUi(self, CommandCreate):
        CommandCreate.setObjectName("CommandCreate")
        CommandCreate.resize(QtCore.QSize(QtCore.QRect(0, 0, 660, 430).size()).expandedTo(CommandCreate.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(CommandCreate)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.command_create = QtGui.QLabel(CommandCreate)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5), QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.command_create.sizePolicy().hasHeightForWidth())
        self.command_create.setSizePolicy(sizePolicy)
        self.command_create.setObjectName("command_create")
        self.vboxlayout.addWidget(self.command_create)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(CommandCreate)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.cbox_action = QtGui.QComboBox(CommandCreate)
        self.cbox_action.setObjectName("cbox_action")
        self.hboxlayout.addWidget(self.cbox_action)

        self.label_2 = QtGui.QLabel(CommandCreate)
        self.label_2.setObjectName("label_2")
        self.hboxlayout.addWidget(self.label_2)

        self.cbox_object = QtGui.QComboBox(CommandCreate)
        self.cbox_object.setObjectName("cbox_object")
        self.hboxlayout.addWidget(self.cbox_object)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.frm_panel = QtGui.QFrame(CommandCreate)
        self.frm_panel.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frm_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.frm_panel.setObjectName("frm_panel")
        self.vboxlayout.addWidget(self.frm_panel)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.btn_run = QtGui.QPushButton(CommandCreate)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0), QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_run.sizePolicy().hasHeightForWidth())
        self.btn_run.setSizePolicy(sizePolicy)
        self.btn_run.setObjectName("btn_run")
        self.hboxlayout1.addWidget(self.btn_run)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi(CommandCreate)
        QtCore.QObject.connect(self.cbox_action, QtCore.SIGNAL("currentIndexChanged(int)"), CommandCreate.changeAction)
        QtCore.QObject.connect(self.cbox_object, QtCore.SIGNAL("currentIndexChanged(int)"), CommandCreate.changeObject)
        QtCore.QObject.connect(self.btn_run, QtCore.SIGNAL("clicked()"), CommandCreate.pushRunButton)
        QtCore.QMetaObject.connectSlotsByName(CommandCreate)

    def retranslateUi(self, CommandCreate):
        CommandCreate.setWindowTitle(QtGui.QApplication.translate("CommandCreate", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.command_create.setText(QtGui.QApplication.translate("CommandCreate", "Command definition", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CommandCreate", "Action:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CommandCreate", "Object:", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_run.setText(QtGui.QApplication.translate("CommandCreate", "Run", None, QtGui.QApplication.UnicodeUTF8))
