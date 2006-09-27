# -*- coding: utf-8 -*-
import sys, re

try:
    from qt import *
    from qttable import *
    from dialog import main_dialog
    import create_contact
    import sources
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
    elif wt in (QRadioButton, QCheckBox):
        dct[key] = (0,1)[widget.isOn() == True]
    elif wt == QDateEdit:
        dct[key] = '%s'%widget.date().toString(Qt.ISODate) # QDate; Qt.ISODate='YYYY-MM-DD'
    elif wt == QComboBox:
        dct[key] = '%s'%widget.currentText()
    elif wt == QTable:
        data = []
        for r in range(widget.numRows()):
            data.append(('%s'%widget.text(r,0).utf8()).strip())
        dct[key] = data
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
        self.src = {} # {'command_name':['command line','XML source','XML response'], ...}
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
        self.renew_domain_period_num.setValidator(QIntValidator(self.renew_domain_period_num))
        # scrolled windows:
        self.panel_create_contact = self.__add_scroll__(self.frame_create_contact, create_contact, 'create_contact')
        self.panel_create_contact.create_contact_street.horizontalHeader().setLabel(0, _T('street'), 320)
        # current date
        curd = QDate().currentDate()
        self.renew_domain_cur_exp_date.setDate(curd)
        self.renew_domain_val_ex_date.setDate(curd)

    def __add_scroll__(self, parent_frame, module, name):
        'Add scrolled view panel. Module must have class panel.'
        scroll = QScrollView(parent_frame, 'scroll_%s'%name)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setFrameShadow(QFrame.Raised)
        scroll.setGeometry(parent_frame.geometry())
        panel = module.panel(scroll)
        scroll.addChild(panel)
        scroll.show()
        return panel
        
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
        if type(messages) not in (list,tuple): messages = (messages,)
        print "!!! messages:",type(messages),messages
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
        # save sources
        self.src[prefix] = (self.epp._epp.get_command_line(),self.epp._epp._raw_cmd,self.epp._epp._raw_answer)
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
            # TODO: mela by se asi omezit velikost raw_answer (???)
            self.src[key] = (self.epp._epp.get_command_line(),self.epp._epp._raw_cmd,self.epp._epp._raw_answer)
            # náhrada za __display_answer__()
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
        d = {}
        p = self.panel_create_contact
        for key in ('id', 'name', 'email', 'city', 'cc', 'pw','org','sp', 'street',
                        'pc', 'voice', 'fax', 'vat', 'notify_email', 'cltrid'):
            append_key(d, key, getattr(p,'create_contact_%s'%key))
        #... disclose ................
        disclose = {}
        for key in ('flag','name','org','addr','voice','fax','email'):
            append_key(disclose, key, getattr(p,'create_contact_disclose_%s'%key))
        d['disclose'] = {
            'flag': {'yes':'y'}.get(disclose['flag'],'n'),
            'data': [k for k,v in disclose.items() if v == 1]}
        #.... ssn .........................
        ssn={}
        for key in ('type','number'):
            append_key(ssn, key, getattr(p,'create_contact_ssn_%s'%key))
        if ssn.has_key('number'): d['ssn'] = ssn
        if self.__check_required__(d, ('id', 'name', 'email', 'city', 'cc')):
            try:
                self.answer = self.epp.create_contact(d['id'], d['name'], d['email'], 
                    d['city'], d['cc'], d.get('pw'),
                    d.get('org'), d.get('street'), d.get('sp'), d.get('pc'), 
                    d.get('voice'), d.get('fax'), d.get('disclose'), d.get('vat'), 
                    d.get('ssn'), d.get('notify_email'), d.get('cltrid'))
            except ccReg.ccRegError, msg:
                pass
##                print "!!!???",msg
##                print dir(msg)
##                self.display_error(msg.args, _T('Validation error'))
##            else:
            self.__display_answer__('create_contact')
        else:
            self.display_error(self.missing_required)
        

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
        d = {}
        append_key(d,'name', self.renew_domain_name)
        append_key(d,'cur_exp_date', self.renew_domain_cur_exp_date)
        if self.renew_domain_val_ex_date.isEnabled():
            append_key(d,'val_ex_date', self.renew_domain_val_ex_date)
        append_key(d,'cltrid', self.renew_domain_cltrid)
        period = {}
        append_key(period,'num', self.renew_domain_period_num)
        append_key(period,'unit', self.renew_domain_period_unit)
        if self.__check_required__(d, ('name','cur_exp_date')):
            if period.has_key('num'):
                period['unit'] = {'year':'y'}.get(period['unit'],'m')
            else:
                period = None
            try:
                self.answer = self.epp.renew_domain(d['name'], d['cur_exp_date'], period, d.get('val_ex_date'), d.get('cltrid'))
            except ccReg.ccRegError, msg:
                self.display_error(msg, _T('Validation error'))
            else:
                self.__display_answer__('renew_domain')
        else:
            self.display_error(self.missing_required)

    def list_contact(self):
        self.__share_list__('list_contact', _T('contact'))

    def list_nsset(self):
        self.__share_list__('list_nsset', _T('nsset'))

    def list_domain(self):
        self.__share_list__('list_domain', _T('domain'))

    #==============================
    # Sources
    #==============================
    def __display_sources__(self, command_name):
        'Display sources of command'
        wnd = sources.panel(self)
        if self.src.has_key(command_name):
            src = self.src[command_name]
            wnd.command_line.setText(ccReg.session_base.get_unicode(src[0]))
            wnd.command.setText(ccReg.session_transfer.human_readable(ccReg.session_base.get_unicode(src[1])))
            wnd.response.setText(ccReg.session_transfer.human_readable(ccReg.session_base.get_unicode(src[2])))
        else:
            wnd.command_line.setText(_T('Sources are not available now. Run command at first.'))
        wnd.show()
        
    def source_login(self):
        self.__display_sources__('login')
    def source_logout(self):
        self.__display_sources__('logout')
    def source_poll(self):
        self.__display_sources__('poll')
    def source_hello(self):
        self.__display_sources__('hello')
    def source_check_contact(self):
        self.__display_sources__('check_contact')
    def source_info_contact(self):
        self.__display_sources__('info_contact')
    def source_create_contact(self):
        self.__display_sources__('create_contact')
    def source_update_contact(self):
        self.__display_sources__('update_contact')
    def source_delete_contact(self):
        self.__display_sources__('delete_contact')
    def source_transfer_contact(self):
        self.__display_sources__('transfer_contact')
    def source_list_contact(self):
        self.__display_sources__('list_contact')
    def source_check_nsset(self):
        self.__display_sources__('check_nsset')
    def source_info_nsset(self):
        self.__display_sources__('info_nsset')
    def source_create_nsset(self):
        self.__display_sources__('create_nsset')
    def source_update_nsset(self):
        self.__display_sources__('update_nsset')
    def source_delete_nsset(self):
        self.__display_sources__('delete_nsset')
    def source_list_nsset(self):
        self.__display_sources__('list_nsset')
    def source_check_domain(self):
        self.__display_sources__('check_domain')
    def source_info_domain(self):
        self.__display_sources__('info_domain')
    def source_create_domain(self):
        self.__display_sources__('create_domain')
    def source_update_domain(self):
        self.__display_sources__('update_domain')
    def source_delete_domain(self):
        self.__display_sources__('delete_domain')
    def source_transfer_domain(self):
        self.__display_sources__('transfer_domain')
    def source_renew_domain(self):
        self.__display_sources__('renew_domain')
    def source_list_domain(self):
        self.__display_sources__('list_domain')


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
