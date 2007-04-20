# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_frame.ui'
#
# Created: Fri Apr 20 16:33:34 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,800,600).size()).expandedTo(MainWindow.minimumSizeHint()))
        MainWindow.setWindowIcon(QtGui.QIcon("icon.png"))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,800,22))
        self.menubar.setObjectName("menubar")

        self.menu_Edit = QtGui.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")

        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")

        self.menu_Windows = QtGui.QMenu(self.menubar)
        self.menu_Windows.setObjectName("menu_Windows")

        self.menu_Dock_Widgets = QtGui.QMenu(self.menu_Windows)
        self.menu_Dock_Widgets.setObjectName("menu_Dock_Widgets")

        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")

        self.menu_Tools = QtGui.QMenu(self.menubar)
        self.menu_Tools.setObjectName("menu_Tools")

        self.menu_Run_command = QtGui.QMenu(self.menu_Tools)
        self.menu_Run_command.setObjectName("menu_Run_command")

        self.menu_Info = QtGui.QMenu(self.menu_Run_command)
        self.menu_Info.setObjectName("menu_Info")

        self.menu_Registrant = QtGui.QMenu(self.menu_Run_command)
        self.menu_Registrant.setObjectName("menu_Registrant")

        self.menu_Create = QtGui.QMenu(self.menu_Run_command)
        self.menu_Create.setObjectName("menu_Create")

        self.menu_Update = QtGui.QMenu(self.menu_Run_command)
        self.menu_Update.setObjectName("menu_Update")

        self.menu_Delete = QtGui.QMenu(self.menu_Run_command)
        self.menu_Delete.setObjectName("menu_Delete")

        self.menu_Transfer = QtGui.QMenu(self.menu_Run_command)
        self.menu_Transfer.setObjectName("menu_Transfer")

        self.menuSend_Auth_Info = QtGui.QMenu(self.menu_Run_command)
        self.menuSend_Auth_Info.setObjectName("menuSend_Auth_Info")

        self.menu_List = QtGui.QMenu(self.menu_Run_command)
        self.menu_List.setObjectName("menu_List")

        self.menu_Check = QtGui.QMenu(self.menu_Run_command)
        self.menu_Check.setObjectName("menu_Check")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.action_Connect = QtGui.QAction(MainWindow)
        self.action_Connect.setCheckable(False)
        self.action_Connect.setIcon(QtGui.QIcon(":/main_frame/images/linguist-next.png"))
        self.action_Connect.setObjectName("action_Connect")

        self.action_Load_configuration = QtGui.QAction(MainWindow)
        self.action_Load_configuration.setIcon(QtGui.QIcon(":/main_frame/images/open.png"))
        self.action_Load_configuration.setObjectName("action_Load_configuration")

        self.action_Save_configuration = QtGui.QAction(MainWindow)
        self.action_Save_configuration.setIcon(QtGui.QIcon(":/main_frame/images/save.png"))
        self.action_Save_configuration.setObjectName("action_Save_configuration")

        self.action_Quit = QtGui.QAction(MainWindow)
        self.action_Quit.setIcon(QtGui.QIcon(":/main_frame/images/exit.png"))
        self.action_Quit.setObjectName("action_Quit")

        self.actionCut = QtGui.QAction(MainWindow)
        self.actionCut.setIcon(QtGui.QIcon(":/main_frame/images/cut.png"))
        self.actionCut.setObjectName("actionCut")

        self.action_Copy = QtGui.QAction(MainWindow)
        self.action_Copy.setIcon(QtGui.QIcon(":/main_frame/images/copy.png"))
        self.action_Copy.setObjectName("action_Copy")

        self.action_Paste = QtGui.QAction(MainWindow)
        self.action_Paste.setIcon(QtGui.QIcon(":/main_frame/images/paste.png"))
        self.action_Paste.setObjectName("action_Paste")

        self.action_Preferences = QtGui.QAction(MainWindow)
        self.action_Preferences.setIcon(QtGui.QIcon(":/main_frame/images/textjustify.png"))
        self.action_Preferences.setObjectName("action_Preferences")

        self.actionShow_history = QtGui.QAction(MainWindow)
        self.actionShow_history.setCheckable(True)
        self.actionShow_history.setIcon(QtGui.QIcon(":/main_frame/images/linguist-phrasebookopen.png"))
        self.actionShow_history.setObjectName("actionShow_history")

        self.action_About = QtGui.QAction(MainWindow)
        self.action_About.setIcon(QtGui.QIcon(":/main_frame/images/linguist-phrasebookopen.png"))
        self.action_About.setObjectName("action_About")

        self.action_Change_log = QtGui.QAction(MainWindow)
        self.action_Change_log.setIcon(QtGui.QIcon(":/main_frame/images/linguist-editfind.png"))
        self.action_Change_log.setObjectName("action_Change_log")

        self.action_About_client = QtGui.QAction(MainWindow)
        self.action_About_client.setObjectName("action_About_client")

        self.action_Disconnect = QtGui.QAction(MainWindow)
        self.action_Disconnect.setCheckable(False)
        self.action_Disconnect.setChecked(False)
        self.action_Disconnect.setEnabled(False)
        self.action_Disconnect.setIcon(QtGui.QIcon(":/main_frame/images/linguist-prev.png"))
        self.action_Disconnect.setObjectName("action_Disconnect")

        self.action_Toolbars = QtGui.QAction(MainWindow)
        self.action_Toolbars.setObjectName("action_Toolbars")

        self.actionAbout_Qt = QtGui.QAction(MainWindow)
        self.actionAbout_Qt.setIcon(QtGui.QIcon(":/main_frame/images/qt.png"))
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")

        self.action_hello = QtGui.QAction(MainWindow)
        self.action_hello.setObjectName("action_hello")

        self.action_login = QtGui.QAction(MainWindow)
        self.action_login.setObjectName("action_login")

        self.action_logout = QtGui.QAction(MainWindow)
        self.action_logout.setObjectName("action_logout")

        self.action_poll = QtGui.QAction(MainWindow)
        self.action_poll.setObjectName("action_poll")

        self.action_technical_test = QtGui.QAction(MainWindow)
        self.action_technical_test.setObjectName("action_technical_test")

        self.action_check_contact = QtGui.QAction(MainWindow)
        self.action_check_contact.setObjectName("action_check_contact")

        self.action_check_nsset = QtGui.QAction(MainWindow)
        self.action_check_nsset.setObjectName("action_check_nsset")

        self.action_check_domain = QtGui.QAction(MainWindow)
        self.action_check_domain.setObjectName("action_check_domain")

        self.action_renew_domain = QtGui.QAction(MainWindow)
        self.action_renew_domain.setObjectName("action_renew_domain")

        self.action_info_contact = QtGui.QAction(MainWindow)
        self.action_info_contact.setObjectName("action_info_contact")

        self.action_info_nsset = QtGui.QAction(MainWindow)
        self.action_info_nsset.setObjectName("action_info_nsset")

        self.action_info_domain = QtGui.QAction(MainWindow)
        self.action_info_domain.setObjectName("action_info_domain")

        self.action_create_contact = QtGui.QAction(MainWindow)
        self.action_create_contact.setObjectName("action_create_contact")

        self.action_create_nsset = QtGui.QAction(MainWindow)
        self.action_create_nsset.setObjectName("action_create_nsset")

        self.action_create_domain = QtGui.QAction(MainWindow)
        self.action_create_domain.setObjectName("action_create_domain")

        self.action_update_contact = QtGui.QAction(MainWindow)
        self.action_update_contact.setObjectName("action_update_contact")

        self.action_update_nsset = QtGui.QAction(MainWindow)
        self.action_update_nsset.setObjectName("action_update_nsset")

        self.action_update_domain = QtGui.QAction(MainWindow)
        self.action_update_domain.setObjectName("action_update_domain")

        self.action_delete_contact = QtGui.QAction(MainWindow)
        self.action_delete_contact.setObjectName("action_delete_contact")

        self.action_delete_nsset = QtGui.QAction(MainWindow)
        self.action_delete_nsset.setObjectName("action_delete_nsset")

        self.action_delete_domain = QtGui.QAction(MainWindow)
        self.action_delete_domain.setObjectName("action_delete_domain")

        self.action_transfer_contact = QtGui.QAction(MainWindow)
        self.action_transfer_contact.setObjectName("action_transfer_contact")

        self.action_transfer_nsset = QtGui.QAction(MainWindow)
        self.action_transfer_nsset.setObjectName("action_transfer_nsset")

        self.action_transfer_domain = QtGui.QAction(MainWindow)
        self.action_transfer_domain.setObjectName("action_transfer_domain")

        self.action_sendauthinfo_contact = QtGui.QAction(MainWindow)
        self.action_sendauthinfo_contact.setObjectName("action_sendauthinfo_contact")

        self.action_sendauthinfo_nsset = QtGui.QAction(MainWindow)
        self.action_sendauthinfo_nsset.setObjectName("action_sendauthinfo_nsset")

        self.action_sendauthinfo_domain = QtGui.QAction(MainWindow)
        self.action_sendauthinfo_domain.setObjectName("action_sendauthinfo_domain")

        self.action_list_contact = QtGui.QAction(MainWindow)
        self.action_list_contact.setObjectName("action_list_contact")

        self.action_list_nsset = QtGui.QAction(MainWindow)
        self.action_list_nsset.setObjectName("action_list_nsset")

        self.action_list_domain = QtGui.QAction(MainWindow)
        self.action_list_domain.setObjectName("action_list_domain")

        self.actionCommand_history = QtGui.QAction(MainWindow)
        self.actionCommand_history.setObjectName("actionCommand_history")

        self.actionCommand_toolbar = QtGui.QAction(MainWindow)
        self.actionCommand_toolbar.setObjectName("actionCommand_toolbar")
        self.menu_Edit.addAction(self.actionCut)
        self.menu_Edit.addAction(self.action_Copy)
        self.menu_Edit.addAction(self.action_Paste)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Preferences)
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addAction(self.action_Change_log)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.action_About_client)
        self.menu_Help.addAction(self.actionAbout_Qt)
        self.menu_Windows.addAction(self.menu_Dock_Widgets.menuAction())
        self.menu_File.addAction(self.action_Connect)
        self.menu_File.addAction(self.action_Disconnect)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Load_configuration)
        self.menu_File.addAction(self.action_Save_configuration)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Info.addAction(self.action_info_contact)
        self.menu_Info.addAction(self.action_info_nsset)
        self.menu_Info.addAction(self.action_info_domain)
        self.menu_Registrant.addAction(self.action_hello)
        self.menu_Registrant.addAction(self.action_login)
        self.menu_Registrant.addAction(self.action_logout)
        self.menu_Registrant.addAction(self.action_poll)
        self.menu_Registrant.addAction(self.action_technical_test)
        self.menu_Create.addAction(self.action_create_contact)
        self.menu_Create.addAction(self.action_create_nsset)
        self.menu_Create.addAction(self.action_create_domain)
        self.menu_Update.addAction(self.action_update_contact)
        self.menu_Update.addAction(self.action_update_nsset)
        self.menu_Update.addAction(self.action_update_domain)
        self.menu_Delete.addAction(self.action_delete_contact)
        self.menu_Delete.addAction(self.action_delete_nsset)
        self.menu_Delete.addAction(self.action_delete_domain)
        self.menu_Transfer.addAction(self.action_transfer_contact)
        self.menu_Transfer.addAction(self.action_transfer_nsset)
        self.menu_Transfer.addAction(self.action_transfer_domain)
        self.menuSend_Auth_Info.addAction(self.action_sendauthinfo_contact)
        self.menuSend_Auth_Info.addAction(self.action_sendauthinfo_nsset)
        self.menuSend_Auth_Info.addAction(self.action_sendauthinfo_domain)
        self.menu_List.addAction(self.action_list_contact)
        self.menu_List.addAction(self.action_list_nsset)
        self.menu_List.addAction(self.action_list_domain)
        self.menu_Check.addAction(self.action_check_contact)
        self.menu_Check.addAction(self.action_check_nsset)
        self.menu_Check.addAction(self.action_check_domain)
        self.menu_Run_command.addAction(self.menu_Registrant.menuAction())
        self.menu_Run_command.addAction(self.menu_Check.menuAction())
        self.menu_Run_command.addAction(self.menu_Info.menuAction())
        self.menu_Run_command.addAction(self.menu_Create.menuAction())
        self.menu_Run_command.addAction(self.menu_Update.menuAction())
        self.menu_Run_command.addAction(self.menu_Delete.menuAction())
        self.menu_Run_command.addAction(self.menu_Transfer.menuAction())
        self.menu_Run_command.addAction(self.menuSend_Auth_Info.menuAction())
        self.menu_Run_command.addAction(self.action_renew_domain)
        self.menu_Run_command.addAction(self.menu_List.menuAction())
        self.menu_Tools.addAction(self.menu_Run_command.menuAction())
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())
        self.menubar.addAction(self.menu_Windows.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.action_Quit,QtCore.SIGNAL("activated()"),MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Fred client", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Edit.setTitle(QtGui.QApplication.translate("MainWindow", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Windows.setTitle(QtGui.QApplication.translate("MainWindow", "&Windows", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Dock_Widgets.setTitle(QtGui.QApplication.translate("MainWindow", "&Dock Widgets", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Tools.setTitle(QtGui.QApplication.translate("MainWindow", "&Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Run_command.setTitle(QtGui.QApplication.translate("MainWindow", "&Choose command", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Info.setTitle(QtGui.QApplication.translate("MainWindow", "&Info", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Registrant.setTitle(QtGui.QApplication.translate("MainWindow", "&Registrant", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Create.setTitle(QtGui.QApplication.translate("MainWindow", "&Create", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Update.setTitle(QtGui.QApplication.translate("MainWindow", "&Update", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Delete.setTitle(QtGui.QApplication.translate("MainWindow", "&Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Transfer.setTitle(QtGui.QApplication.translate("MainWindow", "&Transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSend_Auth_Info.setTitle(QtGui.QApplication.translate("MainWindow", "Send &Auth. Info", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_List.setTitle(QtGui.QApplication.translate("MainWindow", "&List", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Check.setTitle(QtGui.QApplication.translate("MainWindow", "&Check", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Connect.setText(QtGui.QApplication.translate("MainWindow", "&Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Connect.setShortcut(QtGui.QApplication.translate("MainWindow", "F2", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Load_configuration.setText(QtGui.QApplication.translate("MainWindow", "&Load configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save_configuration.setText(QtGui.QApplication.translate("MainWindow", "&Save configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save_configuration.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setText(QtGui.QApplication.translate("MainWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCut.setText(QtGui.QApplication.translate("MainWindow", "Cu&t", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCut.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+X", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Copy.setText(QtGui.QApplication.translate("MainWindow", "&Copy", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Copy.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+C", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Paste.setText(QtGui.QApplication.translate("MainWindow", "&Paste", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Paste.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+V", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Preferences.setText(QtGui.QApplication.translate("MainWindow", "&Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_history.setText(QtGui.QApplication.translate("MainWindow", "Show &history", None, QtGui.QApplication.UnicodeUTF8))
        self.action_About.setText(QtGui.QApplication.translate("MainWindow", "&Fred client help", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Change_log.setText(QtGui.QApplication.translate("MainWindow", "&Change log", None, QtGui.QApplication.UnicodeUTF8))
        self.action_About_client.setText(QtGui.QApplication.translate("MainWindow", "&About client", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Disconnect.setText(QtGui.QApplication.translate("MainWindow", "&Disconnect", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Disconnect.setShortcut(QtGui.QApplication.translate("MainWindow", "F3", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Toolbars.setText(QtGui.QApplication.translate("MainWindow", "&Toolbars", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Qt.setText(QtGui.QApplication.translate("MainWindow", "About &Qt", None, QtGui.QApplication.UnicodeUTF8))
        self.action_hello.setText(QtGui.QApplication.translate("MainWindow", "&Hello", None, QtGui.QApplication.UnicodeUTF8))
        self.action_login.setText(QtGui.QApplication.translate("MainWindow", "&Login", None, QtGui.QApplication.UnicodeUTF8))
        self.action_logout.setText(QtGui.QApplication.translate("MainWindow", "L&ogout", None, QtGui.QApplication.UnicodeUTF8))
        self.action_poll.setText(QtGui.QApplication.translate("MainWindow", "&Poll", None, QtGui.QApplication.UnicodeUTF8))
        self.action_technical_test.setText(QtGui.QApplication.translate("MainWindow", "&Technical test", None, QtGui.QApplication.UnicodeUTF8))
        self.action_check_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_check_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_check_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_renew_domain.setText(QtGui.QApplication.translate("MainWindow", "&Renew domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_info_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_info_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_info_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_create_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_create_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_create_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_update_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_update_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_update_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_transfer_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_transfer_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_transfer_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_sendauthinfo_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_sendauthinfo_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_sendauthinfo_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.action_list_contact.setText(QtGui.QApplication.translate("MainWindow", "&Contact", None, QtGui.QApplication.UnicodeUTF8))
        self.action_list_nsset.setText(QtGui.QApplication.translate("MainWindow", "&NSSET", None, QtGui.QApplication.UnicodeUTF8))
        self.action_list_domain.setText(QtGui.QApplication.translate("MainWindow", "&Domain", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCommand_history.setText(QtGui.QApplication.translate("MainWindow", "Command &history", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCommand_toolbar.setText(QtGui.QApplication.translate("MainWindow", "Command &toolbar", None, QtGui.QApplication.UnicodeUTF8))

import main_frame_rc
