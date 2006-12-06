#!/usr/bin/env python
import sys
import os

#====================================
#
#       PyQt4
#
#====================================
try:
    from PyQt4 import QtGui, QtCore
except ImportError, e:
    sys.stderr.writelines(
        ( 'Missing module: ',str(e),'\n',
          'For runnig this application you need install PyQt4 module. For more see README and INSATLL.\n'
          ) )
    sys.exit(-1)


#====================================
#
#       Fred API
#
#====================================
# first try import from standard library path
try:
    import fred
except ImportError:
    # and than from relative path
    sys.path.insert(0,'../')
    try:
        import fred
    except ImportError, msg:
        sys.stderr.writelines(
            ( 'Missing module: ',str(e),'\n',
             'For runnig this application you need install fred module. See README and INSATLL.\n'
            ) )
        sys.exit(-1)
from fred.translate import encoding, options, option_errors

#====================================
#
#       Fred Dialogs
#
#====================================
from ui_main import Ui_FredWindow
from shared_fnc import *
init_encoding(encoding) # INIT shared_fnc.py module

# prefix of translations
translation_prefix = 'clientqt_'
SPLIT_NAME = 1

class FredWindow(QtGui.QDialog):
    'Main frame dialog.'
    ident_types = ('op','rc','passport','mpsv','ico')

    def __init__(self, epp_client, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FredWindow()
        self.ui.setupUi(self)
        self.setFixedSize(694,656)
        self.epp = epp_client
        self.missing_required = []
        self.src = {} # {'command_name':['command line','XML source','XML response'], ...}
        #--------------------------------------        
        # load data for connection
        #--------------------------------------        
        data = map(lambda v: v is not None and v or '', self.epp._epp.get_connect_defaults())
        username = self.epp._epp.get_config_value(self.epp._epp._section_epp_login, 'username',1)
        password = self.epp._epp.get_config_value(self.epp._epp._section_epp_login, 'password',1)
        self.ui.connect_host.setText(data[0])
        self.ui.connect_port.setText(str(data[1]))
        self.ui.connect_private_key.setText(data[2])
        self.ui.connect_certificate.setText(data[3])
        self.ui.connect_timeout.setText(data[4])
        if username: self.ui.login_username.setText(username)
        if password: self.ui.login_password.setText(password)


    def delete_contact(self):
        pass
    def delete_domain(self):
        pass
    def delete_nsset(self):
        pass


    def hello(self):
        pass


    def check_contact(self):
        pass
    def check_domain(self):
        pass
    def check_nsset(self):
        pass


    def info_contact(self):
        pass
    def info_domain(self):
        pass
    def info_nsset(self):
        pass


    def list_contact(self):
        pass
    def list_domain(self):
        pass
    def list_nsset(self):
        pass

    def login(self):
        pass
    def logout(self):
        pass

    def poll(self):
        pass

    def transfer_contact(self):
        pass
    def transfer_domain(self):
        pass

    def create_contact(self):
        pass
    def create_domain(self):
        pass
    def create_nsset(self):
        pass

    def update_contact(self):
        pass
    def update_domain(self):
        pass
    def update_nsset(self):
        pass

    def renew_domain(self):
        pass

    def sendauthinfo_contact(self):
        pass
    def sendauthinfo_nsset(self):
        pass
    def sendauthinfo_domain(self):
        pass


    def source_login(self):
        pass
    def source_logout(self):
        pass
    def source_poll(self):
        pass
    def source_hello(self):
        pass
    def source_check_contact(self):
        pass
    def source_info_contact(self):
        pass
    def source_create_contact(self):
        pass
    def source_update_contact(self):
        pass
    def source_delete_contact(self):
        pass
    def source_transfer_contact(self):
        pass
    def source_list_contact(self):
        pass
    def source_check_nsset(self):
        pass
    def source_info_nsset(self):
        pass
    def source_create_nsset(self):
        pass
    def source_update_nsset(self):
        pass
    def source_delete_nsset(self):
        pass
    def source_list_nsset(self):
        pass
    def source_check_domain(self):
        pass
    def source_info_domain(self):
        pass
    def source_create_domain(self):
        pass
    def source_update_domain(self):
        pass
    def source_delete_domain(self):
        pass
    def source_transfer_domain(self):
        pass
    def source_renew_domain(self):
        pass
    def source_sendauthinfo_contact(self):
        pass
    def source_sendauthinfo_nsset(self):
        pass
    def source_sendauthinfo_domain(self):
        pass
    def source_list_domain(self):
        pass

    def btn_close(self):
        'Handle click on button Close'
        label = QtGui.QApplication.translate("FredWindow", "Close client", None, QtGui.QApplication.UnicodeUTF8)
        msg = QtGui.QApplication.translate("FredWindow", "Do you wand realy close client?", None, QtGui.QApplication.UnicodeUTF8)
        if QtGui.QMessageBox.warning(self, label, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            QtGui.QWidget.close(self)

    def closeEvent(self, e):
        'Finalize when dialog is closed.'
        self.epp.logout()
        QtGui.QWidget.closeEvent(self, e)

    def credits(self):
        pass


def main(argv, lang):
    epp = fred.Client()
    if not epp.load_config():
        epp._epp.display()
        return
    app = QtGui.QApplication(sys.argv)
    tr = QtCore.QTranslator()
    modul_trans = os.path.join(os.path.split(__file__)[0],'%s%s'%(translation_prefix,lang))
    if tr.load(modul_trans):
        app.installTranslator(tr)
    window = FredWindow(epp)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if msg_invalid:
        print msg_invalid
    elif options['version']:
        epp = fred.ClientSession()
        print epp.version()
    else:
        if option_errors:
            print option_errors
        else:
            main([], options['lang'])
