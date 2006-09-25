# -*- coding: utf-8 -*-
import sys, re

try:
    from qt import *
    from qttable import *
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
SPLIT_NAME = 1

def append_key(dct, key, widget):
    'Append value if has been typed.'
    wt = type(widget)
    if wt in (QLineEdit, QTextEdit):
        value = ('%s'%widget.text().utf8()).strip()
        if value: dct[key] = value
    elif wt == QRadioButton:
        dct[key] = (0,1)[widget.isOn() == True]
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
        # validators
        self.connect_port.setValidator(QIntValidator(self.connect_port))
        self.connect_timeout.setValidator(QDoubleValidator(0.0, 999.0, 2, self.connect_timeout))
        self.poll_msg_id.setValidator(QIntValidator(self.poll_msg_id))

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
        'Finalize when dialog is closed.'
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

    #----------------------------------
    # Shared functions for handlers
    #----------------------------------
    def __share_list__(self, key, label):
        'Shared for all check commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        try:
            self.answer = getattr(self.epp,key)(d.get('cltrid'))
        except ccReg.ccRegError, msg:
            self.display_error(msg, _T('Validation error'))
        else:
            wtab = getattr(self, '%s_table'%key)
            data = self.answer.get('data',{})
            header = wtab.horizontalHeader()
            header.setLabel(0, label, 380) ## 416
            wtab.setNumRows(int(data.get('count','0')))
            r=0
            for name in data.get('list',[]):
                # enum EditType { Never, OnTyping, WhenCurrent, Always }
                wtab.setItem(r, 0, QTableItem(wtab, QTableItem.OnTyping, name))
                r+=1
        # toggle widget to the response tab
        getattr(self,'%s_response'%key).setCurrentPage(1)


    def __share_transfer__(self, key):
        'Shared for transfer commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self,'%s_name'%key))
        append_key(d,'passw', getattr(self,'%s_password'%key))
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        if self.__check_required__(d, ('name','passw')):
            try:
                self.answer = getattr(self.epp,key)(d['name'], d['passw'], d.get('cltrid'))
            except ccReg.ccRegError, msg:
                self.display_error(msg, _T('Validation error'))
            else:
                self.__display_answer__(key)
        else:
            self.display_error(self.missing_required)

    def __share_command__(self, key, extends=0):
        'Shared for command handlers check, info, delete.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self,'%s_name'%key))
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        if self.__check_required__(d, ('name',)):
            if extends == SPLIT_NAME:
                d['name'] = re.split('\s+',d['name']) # need for check commands
            try:
                self.answer = getattr(self.epp,key)(d['name'], d.get('cltrid'))
            except ccReg.ccRegError, msg:
                self.display_error(msg, _T('Validation error'))
            else:
                self.__display_answer__(key)
        else:
            self.display_error(self.missing_required)

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
        d = {}
        append_key(d, 'op', self.poll_op_ack)
        append_key(d, 'msg_id', self.poll_msg_id)
        append_key(d,'cltrid',self.poll_cltrid)
        d['op'] = ('req','ack')[d['op']]
        try:
            self.answer = self.epp.poll(d['op'], d.get('msg_id'), d.get('cltrid'))
        except ccReg.ccRegError, msg:
            self.display_error(msg, _T('Validation error'))
        else:
            self.__display_answer__('poll')

    def hello(self):
        try:
            self.answer = self.epp.hello()
        except ccReg.ccRegError, msg:
            self.display_error(msg, _T('Validation error'))
        else:
            self.__display_answer__('hello')

    def check_contact(self):
        self.__share_command__('check_contact',SPLIT_NAME)

    def check_nsset(self):
        self.__share_command__('check_nsset',SPLIT_NAME)

    def check_domain(self):
        self.__share_command__('check_domain',SPLIT_NAME)

    def info_contact(self):
        self.__share_command__('info_contact')

    def info_nsset(self):
        self.__share_command__('info_nsset')

    def info_domain(self):
        self.__share_command__('info_domain')

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
        self.__share_command__('delete_contact')

    def delete_nsset(self):
        self.__share_command__('delete_nsset')

    def delete_domain(self):
        self.__share_command__('delete_domain')

    def transfer_contact(self):
        self.__share_transfer__('transfer_contact')

    def transfer_domain(self):
        self.__share_transfer__('transfer_domain')

    def renew_domain(self):
        if not self.check_is_online(): return

    def list_contact(self):
        self.__share_list__('list_contact', _T('contact'))

    def list_nsset(self):
        self.__share_list__('list_nsset', _T('nsset'))

    def list_domain(self):
        self.__share_list__('list_domain', _T('domain'))

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
