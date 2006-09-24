# -*- coding: utf-8 -*-
import sys, re

try:
    from qt import *
    from dialog import main_dialog
except ImportError, msg:
    print "ImportError:",msg
    print 'For runnig this application you need install qt module. See PyQt and Qt pages.'
    sys.exit(0)

# first try import from standard library path
try:
    import ccReg
except ImportError:
    # and than from relative path
    sys.path.append('../')
    try:
        import ccReg
    except ImportError, msg:
        print "ImportError:",msg
        print 'For runnig this application you need install ccReg module. See help.'
        sys.exit(0)

from ccReg.translate import _T, encoding, options, option_errors

# prefix of translations
translation_prefix = 'clientqt_'


def append_key(dct, key, widget, method=0):
    'Append value if has been typed.'
    if type(widget) in (QLineEdit, QTextEdit):
        value = ('%s'%widget.text().utf8()).strip()
        if value: dct[key] = value
    else:
        print "unknown type widget:",type(widget)


class CMainDialog(main_dialog):
    'Main frame dialog.'
    
    def __init__(self):
        main_dialog.__init__(self)
        self.epp = ccReg.Client()
        self.epp.load_config(options['session'])
        self.missing_required = []
        self.answer = {}
        # load data for connection
        data = self.epp._epp.get_connect_defaults()
        self.connect_host.setText(data[0]) 
        self.connect_port.setText(str(data[1]))
        self.connect_private_key.setText(data[2])
        self.connect_certificate.setText(data[3])
        self.connect_timeout.setText(data[4])
        self.login_username.setText(self.epp._epp.get_config_value('epp_login', 'username',1))
        self.login_password.setText(self.epp._epp.get_config_value('epp_login', 'password',1))
        
        
    def __check_required__(self, data, required):
        'Returns True if all required data were set. Othervise list of missing names.'
        self.missing_required = []
        for key in required:
            if not data.has_key(key) or len(data[key])==0:
                self.missing_required.append(key)
        return len(self.missing_required) == 0

    def display_error(self, messages, label=''):
        'Display Warning dialog.'
        # about, warning, critical
        if not label: label = _T('Missing required').decode(encoding)
        QMessageBox.critical(self, label, '<h2>%s:</h2>\n%s'%(label,'<br>\n'.join(map(lambda s: s.decode(encoding),messages))))

    def closeEvent(self,ce):
        self.epp.logout()
        ce.accept() ## ce.ignore <qt.QCloseEvent>

    def __display_answer__(self, prefix):
        'Display answer from EPP server.'
        # self.answer {
        #    'code': int
        #    'command': unicode
        #    'reason': unicode
        #    'errors': [str, str, ...]
        #    'data': { key: str }
        # }
        code = '<b>code:</b> %d'%self.answer.get('code',0)
        reason = self.answer.get('reason','')
        if type(reason) is str: reason = reason.decode(encoding)
        errors = self.answer.get('errors',[])
        if len(errors):
            reason += '<br>\n<b style="color:red">%s</b>'%'<br>\n'.join(errors)
        getattr(self,'%s_code'%prefix).setText(code)
        getattr(self,'%s_msg'%prefix).setText(reason)
        getattr(self,'%s_data'%prefix).setText('<pre>%s</pre>'%self.epp._epp.get_answer_udata())
        # toggle widget to the response tab
        getattr(self,'%s_response'%prefix).setCurrentPage(1)

    def __set_status__(self):
        'Refresh status after login and logout.'
        if self.epp.is_logon():
            status = '<b style="color:darkgreen">ONLINE: %s@%s</b>'%self.epp._epp.get_username_and_host()
        else:
            status = '<b style="color:red">%s</b>'%_T('disconnect')
        self.status.setText(status)
    
    def check_is_online(self):
        'Check online. True - online / False - offline.'
        ret = self.epp.is_logon()
        if not ret: self.display_error((_T('You are not logged. First do login.'),))
        return ret
    
    #==============================
    # Widgets handlers
    #==============================
    def login(self):
        if self.epp.is_logon():
            self.display_error((_T('You are logged already.'),))
            return
        d = {}
        append_key(d,'username',self.login_username)
        append_key(d,'password',self.login_password)
        append_key(d,'new-password',self.login_new_password)
        append_key(d,'cltrid',self.login_cltrid)
        if self.__check_required__(d, ('username','password')):
            # Definition from welcome panel:
            dc = {}
            append_key(dc,'host',       self.connect_host)
            append_key(dc,'port',       self.connect_port)
            append_key(dc,'priv_key',self.connect_private_key)
            append_key(dc,'cert',       self.connect_certificate)
            append_key(dc,'timeout',  self.connect_timeout)
            errors = self.epp.set_data_connect(dc)
            if errors:
                self.display_error(errors,_T('Invalid connection input'))
            else:
                try:
                    self.answer = self.epp.login(d['username'], d['password'], d.get('new-password'), d.get('cltrid'))
                except ccReg.ccRegError, msg:
                    self.display_error(msg, _T('Validation error'))
                else:
                    self.__display_answer__('login')
                    self.__set_status__()
        else:
            self.display_error(self.missing_required)

    def logout(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid',self.logout_cltrid)
        try:
            self.answer = self.epp.logout(d.get('cltrid'))
        except ccReg.ccRegError, msg:
            self.display_error(msg, _T('Validation error'))
        else:
            self.__display_answer__('logout')
            self.__set_status__()

    def poll(self):
        if not self.check_is_online(): return

    def hello(self):
        try:
            self.answer = self.epp.hello()
        except ccReg.ccRegError, msg:
            self.display_error(msg, _T('Validation error'))
        else:
            self.__display_answer__('hello')

    def check_contact(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name',self.check_contact_names)
        append_key(d,'cltrid',self.check_contact_cltrid)
        if self.__check_required__(d, ('name',)):
            try:
                self.answer = self.epp.check_contact(re.split('\s+',d['name']), d.get('cltrid'))
            except ccReg.ccRegError, msg:
                self.display_error(msg, _T('Validation error'))
            else:
                self.__display_answer__('check_contact')
        else:
            self.display_error(self.missing_required)

    def check_nsset(self):
        if not self.check_is_online(): return

    def check_domain(self):
        if not self.check_is_online(): return

    def info_contact(self):
        if not self.check_is_online(): return

    def info_nsset(self):
        if not self.check_is_online(): return

    def info_domain(self):
        if not self.check_is_online(): return

    def create_contact(self):
        if not self.check_is_online(): return

    def create_nsset(self):
        if not self.check_is_online(): return

    def create_domain(self):
        if not self.check_is_online(): return

    def update_contact(self):
        if not self.check_is_online(): return

    def update_nsset(self):
        if not self.check_is_online(): return

    def update_domain(self):
        if not self.check_is_online(): return

    def delete_contact(self):
        if not self.check_is_online(): return

    def delete_nsset(self):
        if not self.check_is_online(): return

    def delete_domain(self):
        if not self.check_is_online(): return

    def transfer_contact(self):
        if not self.check_is_online(): return

    def transfer_domain(self):
        if not self.check_is_online(): return

    def renew_domain(self):
        if not self.check_is_online(): return

    def list_contact(self):
        if not self.check_is_online(): return

    def list_nsset(self):
        if not self.check_is_online(): return

    def list_domain(self):
        if not self.check_is_online(): return

    def poll_op(self):
        if not self.check_is_online(): return

    #==============================


def main(argv, lang):
    app = QApplication(argv)
    tr = QTranslator()
    if tr.load(translation_prefix+lang):
        app.installTranslator(tr)
    form = CMainDialog()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()

    
if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    elif options['version']:
        epp = ccReg.ClientSession()
        print epp.version()
    else:
        if option_errors:
            print option_errors
        else:
            main([], options['lang'])
