#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import os


#====================================
#
#       Fred Dialogs
#
#====================================
from shared_functions import *
from ui_main_frame import  Ui_MainWindow as uiMainFrame
from top_toolbar import TopToolbarWindow
from command_create import FredCommandCreate

# prefix of translations
translation_prefix = 'clientqt4_'
NO_SPLIT_NAME, SPLIT_NAME = (0, 1)


class FredMainWindow(QtGui.QMainWindow):
    'Main frame dialog.'
    ident_types = ('op', 'rc', 'passport', 'mpsv', 'ico')

    def __init__(self, app, epp_client, encoding, translate_warning, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self._init_config = 1 # run only once
        self._app = app
        self.ui = uiMainFrame()
        self.ui.setupUi(self)
        self.epp = epp_client
        self.epp._epp._sep = '<br>\n' # separator for display lines in QtGui.QTextEdit as HTML
        self.missing_required = []
        self.src = {} # {'command_name':['command line','XML source','XML response'], ...}
        self._stderr_errors = [] # Keep internal errors for display.
        self._thread_errors = [] # Temporary list of errors generated inside different thread.
        self.encoding = encoding
        self.translate_warning = translate_warning

        # create frames
        self.command_create = FredCommandCreate(self)
        self.setCentralWidget(self.command_create)

        # create docked windows
        self.createDockWindows()

        # INIT
        self.load_config_and_autologin()
        self.ui.statusbar.showMessage(self.tr("Ready")) # UI name dependence

    def closeEvent(self, e):
        'Finalize when dialog is closed.'
        self.epp.logout()
        QtGui.QMainWindow.closeEvent(self, e)


    def createDockTopToolbar(self):
        'Create QDockWidget with toolbar'
        label = self.tr('Quick menu')

        # create quick menu from module top_toolbar
        self.top_toolbar = TopToolbarWindow()
        dock = QtGui.QDockWidget(label, self)
        dock.setWidget(self.top_toolbar)
        dock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)

        # create toggle menu:
        act = dock.toggleViewAction()
        act.setText(label)
        self.ui.menu_Dock_Widgets.addAction(act) # menu_Dock_Widgets from ui_[file]

    def createDockHistory(self):
        # Selected puzzle word
        dock = QtGui.QDockWidget(self.tr("Command history"), self)
        self.history = QtGui.QListWidget(dock)
        dock.setWidget(self.history)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

        act = dock.toggleViewAction()
        act.setText(self.tr("Command &history"))
        act.setIcon(QtGui.QIcon(":/main_frame/images/linguist-phrasebookopen.png"))
        act.setShortcut(self.tr("Ctrl+H"))
        self.ui.menu_Tools.addAction(act) # UI name dependence

        # Open application with closed Hitory window.
        dock.hide()
        # TODO: Load history


    def createDockWindows(self):
        self.createDockHistory()
        self.createDockTopToolbar()


    def append_system_messages(self, messages):
        'Appent text to the System message window'
        msg = [get_unicode(ttytag2html(text), self.encoding) for text in messages]

    def __set_status__(self):
        'Refresh status after login and logout.'
        if self.epp.is_logon():
            user, host = self.epp._epp.get_username_and_host()
            status = '<b>%s</b> <b style="color:darkgreen">ONLINE: %s@%s</b>' % (_TU('status'), user, host)
        else:
            status = ('<b>%s</b> <b style="color:red">%s</b>' % (_TU('status'), _TU('disconnect'))).decode('utf8') # translation is saved in utf8


    def load_config_and_autologin(self):
        'load data for connection'
        msg = []
        msg.append(self.epp._epp.version())
        if not self.epp.load_config():
            msg.append(_TU('Load configuration file failed.'))
            self.epp._epp.join_missing_config_messages(2) # 2 - verbose
            msg.extend(self.epp._epp._notes)
            msg.extend(self.epp._epp._errors)
            msg.extend(self.epp._epp._notes_afrer_errors)
            self.append_system_messages(msg)
            return
        self.epp._epp.join_missing_config_messages(2) # 2 - verbose
        # Set translation defined in config file or command line option.
        self.__set_translation__(self.epp._epp.get_language())
        if self.translate_warning:
            msg.append(self.translate_warning)
        data = map(lambda v: v is not None and v or '', self.epp._epp.get_connect_defaults())
        username, password = self.epp._epp.get_actual_username_and_password()
#        self.ui.connect_host.setText(data[0])
#        self.ui.connect_port.setText(str(data[1]))
#        self.ui.connect_private_key.setText(data[2])
#        self.ui.connect_certificate.setText(data[3])
#        self.ui.connect_timeout.setText(data[4])
#        if username: self.ui.login_username.setText(username)
#        if password: self.ui.login_password.setText(password)
        if not self.epp._epp.automatic_login(1): # 1 - no outout
            self.epp._epp._errors.append(_TU('Login failed'))
        self.__set_status__()
        msg.extend(self.epp._epp._notes)
        msg.extend(self.epp._epp._errors)
        msg.extend(self.epp._epp._notes_afrer_errors)
        if len(msg):
            self.append_system_messages(msg)

    def __set_translation__(self, lang):
        'Set translation language.'
        tr = QtCore.QTranslator()
        modul_trans = os.path.join(os.path.split(__file__)[0], '%s%s' % (translation_prefix, lang))
        if tr.load(modul_trans):
##            self._app.installTranslator(tr)
##            self.panel_create_contact.ui.retranslateUi(self)
##            self.panel_update_contact.ui.retranslateUi(self)
##            self.panel_create_domain.ui.retranslateUi(self)
##            self.panel_update_domain.ui.retranslateUi(self)
##            self.panel_create_nsset.ui.retranslateUi(self)
##            self.panel_update_nsset.ui.retranslateUi(self)
            self.ui.retranslateUi(self)
