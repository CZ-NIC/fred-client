#!/usr/bin/env python
import sys
import os
import re

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
    except ImportError, e:
        sys.stderr.writelines(
            ( 'Missing module: ',str(e),'\n',
             'For runnig this application you need install fred module. See README and INSATLL.\n'
            ) )
        sys.exit(-1)


#------------------------------------
# INIT language
#------------------------------------
from fred.translate import encoding, options, option_errors, get_valid_lang
if not (options.has_key('lang_option') or options.has_key('lang_environ')):
    locale_lang = '%s'%QtCore.QLocale.system().name().toAscii()
    lang, error = get_valid_lang(locale_lang[:2], 'QtCore.QLocale.system().name()')
    if error:
        fred.translate.warning += '\n%s'%error
    else:
        options['lang'] = options['lang_environ'] = lang
        fred.translate.install_translation(options['lang'])


#====================================
#
#       Fred Dialogs
#
#====================================
from ui_main import Ui_FredWindow as uiMainFrame
from create_contact import FredWindow as wndCreateContact
from update_contact import FredWindow as wndUpdateContact
from create_domain import FredWindow as wndCreateDomain
from update_domain import FredWindow as wndUpdateDomain
from create_nsset import FredWindow as wndCreateNsset
from update_nsset import FredWindow as wndUpdateNsset
from sources import FredWindow as wndSources

# prefix of translations
translation_prefix = 'clientqt_'
SPLIT_NAME = 1

#class InitClient(QtCore.QThread):
#    'Run load config in separate thread.'
#    def __init__(self, parent=None):
#        QtCore.QThread.__init__(self, parent)
#        self.parent = parent
#    def run(self):
#        'load data for connection'
#        self.parent.load_config_and_autologin()

class FredMainWindow(QtGui.QDialog):
    'Main frame dialog.'
    ident_types = ('op','rc','passport','mpsv','ico')

    def __init__(self, app, epp_client, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._init_config = 1 # run only once
        self._app = app
        self.ui = uiMainFrame()
        self.ui.setupUi(self)
        self.setFixedSize(694,656)
        self.epp = epp_client
        self.missing_required = []
        self.src = {} # {'command_name':['command line','XML source','XML response'], ...}
        #--------------------------------------        
        # scrolled windows
        #--------------------------------------        
        self.panel_create_contact = self.__add_scroll__(self.ui.frame_create_contact, wndCreateContact)
        self.panel_update_contact = self.__add_scroll__(self.ui.frame_update_contact, wndUpdateContact)
        self.panel_create_domain = self.__add_scroll__(self.ui.frame_create_domain, wndCreateDomain)
        self.panel_update_domain = self.__add_scroll__(self.ui.frame_update_domain, wndUpdateDomain)
        self.panel_create_nsset = self.__add_scroll__(self.ui.frame_create_nsset, wndCreateNsset)
        self.panel_update_nsset = self.__add_scroll__(self.ui.frame_update_nsset, wndUpdateNsset)
        #--------------------------------------        
        # validators
        #--------------------------------------        
        self.ui.connect_port.setValidator(QtGui.QIntValidator(self.ui.connect_port))
        self.ui.connect_timeout.setValidator(QtGui.QDoubleValidator(0.0, 999.0, 2, self.ui.connect_timeout))
        self.ui.poll_msg_id.setValidator(QtGui.QIntValidator(self.ui.poll_msg_id))
        self.ui.renew_domain_period_num.setValidator(QtGui.QIntValidator(self.ui.renew_domain_period_num))
        w = self.panel_create_domain.ui.period_num
        w.setValidator(QtGui.QIntValidator(w))
        #--------------------------------------        
        # current date
        #--------------------------------------        
        curd = QtCore.QDate().currentDate()
        self.ui.renew_domain_cur_exp_date.setDate(curd)
        self.ui.renew_domain_val_ex_date.setDate(curd)
        self.panel_create_domain.ui.val_ex_date.setDate(curd)
        self.panel_update_domain.ui.val_ex_date.setDate(curd)
        # INIT
        self.load_config_and_autologin()
        #init_thread = InitClient(self)
        #init_thread.start()
        

    def load_config_and_autologin(self):
        'load data for connection'
        msg = []
        msg.append(self.epp._epp.version())
        if not self.epp.load_config():
            msg.append(_T('Load configuration file failed.'))
            msg.extend(self.epp._epp._notes)
            msg.extend(self.epp._epp._errors)
            msg.extend(self.epp._epp._notes_afrer_errors)
#            self.display_error(msg, self.__tr('Load configuration file failed.'))
            self.ui.system_messages.insertHtml(get_unicode('<br>\n'.join(msg)))
            return
        # Set translation defined in config file or command line option.
        self.__set_translation__(self.epp._epp.get_language())
        if fred.translate.warning: msg.append(fred.translate.warning)
        data = map(lambda v: v is not None and v or '', self.epp._epp.get_connect_defaults())
        username, password = self.epp._epp.get_actual_username_and_password()
        self.ui.connect_host.setText(data[0])
        self.ui.connect_port.setText(str(data[1]))
        self.ui.connect_private_key.setText(data[2])
        self.ui.connect_certificate.setText(data[3])
        self.ui.connect_timeout.setText(data[4])
        if username: self.ui.login_username.setText(username)
        if password: self.ui.login_password.setText(password)
        if not self.epp._epp.automatic_login(1): # 1 - no outout
            self.epp._epp._errors.append(_T('Login failed'))
        self.__set_status__()
        msg.extend(self.epp._epp._notes)
        msg.extend(self.epp._epp._errors)
        msg.extend(self.epp._epp._notes_afrer_errors)
        if len(msg):
#            msg = map(lambda t: re.sub('\$\{\w+\}','',t), msg) # remove terminal color tags
#            print '!!! msg=',msg
            msg = [ttytag2html(text) for text in msg]
            self.ui.system_messages.insertHtml(get_unicode('<br>\n'.join(msg)))
#            self.display_error(msg, self.__tr('Init client'), len(self.epp._epp._errors)==0)

    def __set_translation__(self, lang):
        'Set translation language.'
        tr = QtCore.QTranslator()
        modul_trans = os.path.join(os.path.split(__file__)[0],'%s%s'%(translation_prefix, lang))
        if tr.load(modul_trans):
            self._app.installTranslator(tr)
            self.ui.retranslateUi(self)

#    def event(self, event):
#        print LABEL_EVENT.get(event.type(),event.type()) #+++
#        return QtGui.QWidget.event(self, event)
#    def event(self, event):
#        #print LABEL_EVENT.get(event.type(),event.type()) #+++
#        try:
#            if self._init_config and event.type() == QtCore.QEvent.ActivationChange:
#                self._init_config = 0 # run only once
#                self.load_config_and_autologin()
#        except AttributeError, e:
#            pass
#        return QtGui.QWidget.event(self, event)

    def __tr(self, text):
        return QtGui.QApplication.translate("FredWindow", text, None, QtGui.QApplication.UnicodeUTF8)

    def __add_scroll__(self, parent_frame, classWindow):
        'Add scrolled view window. Module must have class FredWindow.'
        scroll = QtGui.QScrollArea(parent_frame)
        #scroll.setFrameShape(QtGui.QFrame.NoFrame)
        #scroll.setFrameShadow(QtGui.QFrame.Raised)
        scroll.setGeometry(parent_frame.geometry())
        panel = classWindow(scroll)
        scroll.setWidget(panel)
        return panel

    def __check_required__(self, data, required):
        'Returns True if all required data were set. Othervise list of missing names.'
        self.missing_required = []
        for key, label in required:
            if not data.has_key(key) or len(data[key])==0:
                self.missing_required.append(label) # key
        return len(self.missing_required) == 0

    def display_error(self, messages, qs_label=None, not_critical=False):
        'Display Warning dialog.'
        # about, warning, critical
        if not qs_label: qs_label = self.__tr('Missing required')
        if type(messages) not in (list,tuple): messages = (messages,)
        if not_critical:
            pass
        dialog_type = not_critical and 'information' or 'critical'
        getattr(QtGui.QMessageBox,dialog_type)(self, qs_label, u'<h2>%s:</h2>\n%s'%(qs_label, u'<br>\n'.join(map(lambda s: get_str(s).decode(encoding),messages))))
        #QtGui.QMessageBox.critical(self, qs_label, u'<h2>%s:</h2>\n%s'%(qs_label, u'<br>\n'.join(map(lambda s: get_str(s).decode(encoding),messages))))

    def btn_close(self):
        'Handle click on button Close'
        label = self.__tr('Close client')
        msg = self.__tr('Do you wand realy close client?')
        if QtGui.QMessageBox.warning(self, label, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            QtGui.QWidget.close(self)

    def closeEvent(self, e):
        'Finalize when dialog is closed.'
        self.epp.logout()
        QtGui.QWidget.closeEvent(self, e)

    def __display_answer__(self, prefix, table=None):
        'Display answer from EPP server.'
        # self.epp._epp._dct_answer {
        #    'code': int
        #    'command': unicode
        #    'reason': unicode
        #    'errors': [str, str, ...]
        #    'data': { key: str }
        # }
        dct_answer = self.epp._epp._dct_answer
        errors = []
        error = self.epp._epp.fetch_errors()
        if(error): errors.append(error)
        if len(dct_answer.get('errors',[])):
            errors.extend(dct_answer['errors'])
        code = '<b>code:</b> %d'%dct_answer.get('code',0)
        msg = []
        reason = dct_answer.get('reason','')
        if reason:
            if type(reason) is str: reason = reason.decode(encoding)
            msg.append(reason)
        if len(errors):
            msg.append('<b style="color:red">%s</b>'%'\n'.join(errors))
        getattr(self.ui,'%s_code'%prefix).setText(QtCore.QString(code))
        getattr(self.ui,'%s_msg'%prefix).setHtml(u'<br>\n'.join(map(get_unicode,msg)))
        if not table and getattr(self.ui, '%s_table'%prefix, None):
            table = (2,(self.__tr('name'),self.__tr('value')),(140,260),None,None)
        if table:
            columns, labels, col_sizes, only_key, count_rows = table
            wtab = getattr(self.ui, '%s_table'%prefix)
            data = dct_answer.get('data',{})
            if re.match('\w+:check',dct_answer.get('command')):
                # overwrite number status by reason message
                data = overwrite_status_by_reason_message(data)
            for pos in range(columns):
                header = wtab.horizontalHeaderItem(pos)
                header.setText(labels[pos])
                wtab.horizontalHeader().resizeSection(pos,col_sizes[pos])
                #QTableWidget.setResizeMode(0, QtGui.QHeaderView.Stretch)
            if count_rows:
                wtab.setRowCount(int(data.get(count_rows,'0')))
            else:
                wtab.setRowCount(count_data_rows(data))
            #....................................................
            column_keys = self.epp._epp.get_keys_sort_by_columns()
            if not column_keys:
                column_keys = map(lambda k:(k,1,k), data.keys()) # default (unsorted)
            #....................................................
            if prefix == 'info_nsset':
                # implode nsset
                nsset = []
                for ns in data.get('nsset:ns',[]):
                    sns = join_key_and_values(ns)
                    if sns: nsset.append(sns)
                if len(nsset): data['nsset:ns'] = nsset
            #....................................................
            r=0
            for key,verbose,label in column_keys:
                if only_key and key != only_key: continue
                value = data.get(key)
                if value is None: continue
                if columns > 1:
                    if not label: label = key
                    wtab.setItem(r, 0, QtGui.QTableWidgetItem(label.decode(encoding)))
                    r = self.__inset_into_table__(wtab, value, 1, r)
                else:
                    r = self.__inset_into_table__(wtab, value, 0, r)
                r+=1
        else:
            getattr(self.ui,'%s_data'%prefix).setHtml('<pre>%s</pre>'%self.epp._epp.get_answer_udata())
        # save sources
        self.src[prefix] = (
            self.epp._epp.get_command_line().decode(encoding),
            self.epp._epp._raw_cmd.decode(self.epp._epp._epp_cmd.encoding),
            self.epp._epp._raw_answer.decode(self.epp._epp._epp_response.encoding),
            )
        # toggle widget to the response tab
        q_tab_widget = getattr(self.ui,'%s_response'%prefix)
        page = q_tab_widget.widget(1)
        if page:
            q_tab_widget.setCurrentWidget (page)
        self.__set_status__()
        #self.__set_send_button__(prefix,True) # enabled 'Send command' button

    def __set_send_button__(self, key, is_enable=False):
        'Enabled/disabled "Send command" button'
        #getattr(self.ui,'send_%s'%key).setEnabled(is_enable)

    def __inset_into_table__(self, wtab, value, c, r):
        'Used by __display_answer__()'
        if type(value) in (list,tuple):
            if len(value):
                wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(value[0])))
                for v in value[1:]:
                    r+=1
                    wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(v)))
        else:
            wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(value)))
        return r

    def __set_status__(self):
        'Refresh status after login and logout.'
        if self.epp.is_logon():
            user, host = self.epp._epp.get_username_and_host()
            status = '<b>%s</b> <b style="color:darkgreen">ONLINE: %s@%s</b>'%(self.__tr('status'), user, host)
        else:
            status = ('<b>%s</b> <b style="color:red">%s</b>'%(self.__tr('status'),self.__tr('disconnect'))).decode('utf8') # translation is saved in utf8
        self.ui.status.setText(status)
    
    def check_is_online(self):
        'Check online. True - online / False - offline.'
        ret = self.epp.is_logon()
        if not ret: self.display_error(self.__tr('You are not logged. First do login.'), self.__tr('Offline'))
        return ret

    #-----------------------------------------------
    #
    # Shared functions for handlers
    #
    #-----------------------------------------------
    def __share_list__(self, key, label):
        'Shared for all check commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid', getattr(self.ui,'%s_cltrid'%key))
        self.__set_send_button__(key)
        try:
            getattr(self.epp,key)(d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__(key,(1,(label,),(380,),'list','count'))

    def __share_transfer__(self, key):
        'Shared for transfer commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self.ui,'%s_name'%key))
        append_key(d,'auth_info', getattr(self.ui,'%s_password'%key))
        append_key(d,'cltrid', getattr(self.ui,'%s_cltrid'%key))
        if self.__check_required__(d, (('name',self.__tr('name')),('auth_info',self.__tr('Authorization info')))):
            try:
                getattr(self.epp,key)(d['name'], d['auth_info'], d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__(key)
        else:
            self.display_error(self.missing_required)

    def __share_command__(self, key, extends=0):
        'Shared for command handlers check, info, delete.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self.ui,'%s_name'%key))
        append_key(d,'cltrid', getattr(self.ui,'%s_cltrid'%key))
        if self.__check_required__(d, (('name',self.__tr('name')),)):
            self.__set_send_button__(key)
            if extends == SPLIT_NAME:
                d['name'] = re.split('[,;\s]+',d['name']) # need for check commands
            try:
                getattr(self.epp,key)(d['name'], d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            # 'info_contact' => 'contact:info'
            tmp = key.split('_')
            if len(tmp) == 2:
                self.epp._epp.reduce_info_status('%s:%s'%(tmp[1],tmp[0]), self.epp._epp._dct_answer['data'])
            self.__display_answer__(key)
        else:
            self.display_error(self.missing_required)

    def __append_update_status__(self, p, d, wnd_name, key_name=''):
        'Used by update_contact()'
        wnd = getattr(p,'%s_ok'%wnd_name,None)
        if wnd and wnd.isEnabled():
            dct = {}
            for key in (map(lambda s: '%s_%s'%(wnd_name,s), self.epp_status)):
                append_key(dct, key, getattr(p,key))
            data = [k[4:] for k,v in dct.items() if v == 1]
            if len(data):
                if key_name:
                    d[key_name] = data
                else:
                    d[wnd_name] = data

    def __disclose__(self, dct, flag, wnd, prefix='%s'):
        'Save checked checkboxes into dct.'
        if flag.isEnabled():
            disclose = {}
            for key in ('flag','name','org','addr','voice','fax','email'):
                append_key(disclose, key, getattr(wnd, prefix%key))
            dct['disclose'] = {
                'flag': disclose['flag'] == 0 and 'y' or 'n',
                'data': [k for k,v in disclose.items() if v == 1]}
 
    #==============================
    #
    #   Widgets handlers
    #
    #==============================
    def login(self):
        if self.epp.is_logon():
            self.display_error(self.__tr('You are logged already.'))
            return
        d = {}
        append_key(d,'username',self.ui.login_username)
        append_key(d,'password',self.ui.login_password)
        append_key(d,'new_password',self.ui.login_new_password)
        append_key(d,'cltrid',self.ui.login_cltrid)
        if self.__check_required__(d, (('username',self.__tr('username')),('password',self.__tr('password')))):
            # Definition from welcome panel:
            self.__set_send_button__('login')
            dc = {}
            append_key(dc,'host',       self.ui.connect_host)
            append_key(dc,'port',       self.ui.connect_port)
            append_key(dc,'ssl_key',    self.ui.connect_private_key)
            append_key(dc,'ssl_cert',   self.ui.connect_certificate)
            append_key(dc,'timeout',    self.ui.connect_timeout)
            self.epp.set_data_connect(dc)
            try:
                self.epp.login(d['username'], d['password'], d.get('new_password'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
                self.epp._epp._errors.append(_T('Process login failed.'))
            self.__display_answer__('login')
        else:
            self.display_error(self.missing_required)

    def logout(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid',self.ui.logout_cltrid)
        self.__set_send_button__('logout')
        try:
            self.epp.logout(d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__('logout')

    def poll(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d, 'op', self.ui.poll_op_ack)
        append_key(d, 'msg_id', self.ui.poll_msg_id)
        append_key(d,'cltrid',self.ui.poll_cltrid)
        d['op'] = ('req','ack')[d['op']]
        self.__set_send_button__('poll')
        try:
            self.epp.poll(d['op'], d.get('msg_id'), d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__('poll')

    def hello(self):
        self.__set_send_button__('hello')
#        import time #!!!
#        print 'TIME...!!!'
#        time.sleep(5) #!!!
#        print 'TIME DONE!!!'
        try:
            self.epp.hello()
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
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
        p = self.panel_create_contact.ui
        for key in ('id', 'name', 'email', 'city', 'cc', 'auth_info','org','sp', 'street',
                        'pc', 'voice', 'fax', 'vat', 'notify_email', 'cltrid'):
            append_key(d, key, getattr(p,'create_contact_%s'%key))
        #... disclose ................
        self.__disclose__(d, p.create_contact_disclose_flag, p, 'create_contact_disclose_%s')
        #.... ident .........................
        ident={}
        for key in ('type','number'):
            append_key(ident, key, getattr(p,'create_contact_ssn_%s'%key))
        ident['type'] = FredMainWindow.ident_types[ident['type']]
        if ident.has_key('number'): d['ident'] = ident
        if self.__check_required__(d, (
                    ('id',self.__tr('contact ID')), 
                    ('name',self.__tr('name')), 
                    ('email',self.__tr('email')), 
                    ('city',self.__tr('city')), 
                    ('cc',self.__tr('country code')))
                    ):
            self.__set_send_button__('create_contact')
            try:
                self.epp.create_contact(d['id'], d['name'], d['email'], 
                    d['city'], d['cc'], d.get('auth_info'),
                    d.get('org'), d.get('street'), d.get('sp'), d.get('pc'), 
                    d.get('voice'), d.get('fax'), d.get('disclose'), d.get('vat'), 
                    d.get('ident'), d.get('notify_email'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('create_contact')
        else:
            self.display_error(self.missing_required)
        

    def create_nsset(self):
        if not self.check_is_online(): return
        d = {}
        panel = self.panel_create_nsset
        for key in ('id', 'tech', 'auth_info', 'cltrid'):
            append_key(d, key, getattr(panel.ui, key))
        dns = []
        for wnd in panel.dns_sets:
            dset = {}
            for key in ('name','addr'):
                append_key(dset, key, getattr(wnd.ui, key))
            if dset.has_key('name'): dns.append(dset)
        d['dns'] = dns
        if self.__check_required__(d, (('id',self.__tr('NSSET ID')), ('dns',self.__tr('dns')), ('tech',self.__tr('tech. contact')))):
            self.__set_send_button__('create_nsset')
            try:
                self.epp.create_nsset(d['id'], d['dns'], d['tech'], d.get('auth_info'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('create_nsset')
        else:
            self.display_error(self.missing_required)


    def create_domain(self):
        if not self.check_is_online(): return
        d = {}
        p = self.panel_create_domain.ui
        for key in ('name', 'registrant', 'auth_info', 'nsset', 'admin','cltrid'):
            append_key(d, key, getattr(p,key))
        #... period ....................
        period = {}
        append_key(period,'num', p.period_num)
        append_key(period,'unit', p.period_unit)
        period['unit'] = ('y','m')[period['unit']]
        if period.has_key('num'): d['period'] = period
        #...............................
        if p.val_ex_date.isEnabled():
            append_key(d,'val_ex_date', self.renew_domain_val_ex_date)
        if self.__check_required__(d, (('name',self.__tr('name')), ('registrant',self.__tr('registrant')))):
            self.__set_send_button__('create_domain')
            try:
                self.epp.create_domain(d['name'], d['registrant'], 
                    d.get('auth_info'), d.get('nsset'), d.get('period'), d.get('admin'), 
                    d.get('val_ex_date'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('create_domain')
        else:
            self.display_error(self.missing_required)

    def update_contact(self):
        if not self.check_is_online(): return
        d = {}
        p = self.panel_update_contact.ui
##        self.__append_update_status__(p, d, 'add')
##        self.__append_update_status__(p, d, 'rem')
        for key in ('id', 'cltrid'):
            append_key(d, key, getattr(p,'update_contact_%s'%key))
        chg={}
        for key in ('voice', 'fax', 'email', 'auth_info', 'vat', 'notify_email'):
            append_key(chg, key, getattr(p,'update_contact_%s'%key))
        postal_info = {}
        for key in ('name', 'org'):
            append_key(postal_info, key, getattr(p,'update_contact_%s'%key))
        #... address ................
        addr = {}
        for key in ('city', 'cc', 'street', 'sp', 'pc'):
            append_key(addr, key, getattr(p,'update_contact_%s'%key))
        if addr.has_key('city') and addr.has_key('cc'):
            postal_info['addr'] = addr
        else:
            self.epp._epp._errors.append(self.__tr('In a part of address must be set both city and country code. For disabled this part leave both empty.'))
        if len(postal_info): chg['postal_info'] = postal_info
        #... disclose ................
        self.__disclose__(chg, p.update_contact_disclose_flag, p, 'update_contact_disclose_%s')
        #.... ident .........................
        ident={}
        for key in ('type','number'):
            append_key(ident, key, getattr(p,'update_contact_ssn_%s'%key))
        ident['type'] = FredMainWindow.ident_types[ident['type']]
        if ident.has_key('number'): chg['ident'] = ident
        if len(chg): d['chg'] = chg
        if self.__check_required__(d, (('id',self.__tr('Contact ID')),)) and len(d) > 1:
            self.__set_send_button__('update_contact')
            try:
                self.epp.update_contact(d['id'], d.get('chg'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('update_contact')
        else:
            if len(d) == 1:
                self.missing_required.append(self.__tr('No values to update.'))
            self.display_error(self.missing_required)

    def update_nsset(self):
        if not self.check_is_online(): return
        d = {}
        panel = self.panel_update_nsset
        for key in ('id', 'cltrid'):
            append_key(d, key, getattr(panel.ui, key))
        #................................
        add = {}
        dns = []
        for wnd in panel.dns_sets:
            dset = {}
            for key in ('name','addr'):
                append_key(dset, key, getattr(wnd.ui, key))
            if dset.has_key('name'): dns.append(dset)
        if len(dns): add['dns'] = dns
        for key in ('tech',):
            append_key(add, key, getattr(panel.ui, 'add_%s'%key))
##        self.__append_update_status__(p, add, 'add', 'status')
        if len(add): d['add'] = add
        #................................
        rem = {}
        for key in ('name','tech'):
            append_key(rem, key, getattr(panel.ui, 'rem_%s'%key))
##        self.__append_update_status__(p, rem, 'rem', 'status')
        if len(rem): d['rem'] = rem
        #................................
        chg = {}
        append_key(chg, 'auth_info', getattr(panel.ui, 'auth_info'))
        if len(chg): d['chg'] = chg
        if self.__check_required__(d, (('id',self.__tr('NSSET ID')),)) and len(d) > 1:
            self.__set_send_button__('update_nsset')
            try:
                self.epp.update_nsset(d['id'], d.get('add'), d.get('rem'), d.get('chg'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('update_nsset')
        else:
            if len(d) == 1:
                self.missing_required.append(self.__tr('No values to update.'))
            self.display_error(self.missing_required)

    def update_domain(self):
        if not self.check_is_online(): return
        d = {}
        p = self.panel_update_domain.ui
        for key in ('name', 'cltrid'):
            append_key(d, key, getattr(p, key))
        #................................
        add = {}
        for key in ('admin',):
            append_key(add, key, getattr(p, 'add_%s'%key))
##        self.__append_update_status__(p, add, 'add', 'status')
##        if len(add): d['add'] = add
        if len(add): d['add'] = add['admin']
        #................................
        rem = {}
        for key in ('admin',):
            append_key(rem, key, getattr(p, 'rem_%s'%key))
##        self.__append_update_status__(p, rem, 'rem', 'status')
##        if len(rem): d['rem'] = rem
        if len(rem): d['rem'] = rem['admin']
        #................................
        chg = {}
        for key in ('nsset','registrant','auth_info'):
            append_key(chg, key, getattr(p, 'chg_%s'%key))
        if len(chg): d['chg'] = chg
        #................................
        if p.val_ex_date.isEnabled():
            append_key(d, 'val_ex_date', p.val_ex_date)
        if self.__check_required__(d, (('name',self.__tr('domain name')),)) and len(d) > 1:
            self.__set_send_button__('update_domain')
            try:
                self.epp.update_domain(d['name'], d.get('add'), d.get('rem'), d.get('chg'), d.get('val_ex_date'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('update_domain')
        else:
            if len(d) == 1:
                self.missing_required.append(self.__tr('No values to update.'))
            self.display_error(self.missing_required)

    def delete_contact(self):
        self.__share_command__('delete_contact')

    def delete_nsset(self):
        self.__share_command__('delete_nsset')

    def delete_domain(self):
        self.__share_command__('delete_domain')

    def sendauthinfo_contact(self):
        self.__share_command__('sendauthinfo_contact')

    def sendauthinfo_nsset(self):
        self.__share_command__('sendauthinfo_nsset')

    def sendauthinfo_domain(self):
        self.__share_command__('sendauthinfo_domain')
        
    def transfer_contact(self):
        self.__share_transfer__('transfer_contact')

    def transfer_domain(self):
        self.__share_transfer__('transfer_domain')

    def renew_domain(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', self.ui.renew_domain_name)
        append_key(d,'cur_exp_date', self.ui.renew_domain_cur_exp_date)
        if self.ui.renew_domain_val_ex_date.isEnabled():
            append_key(d,'val_ex_date', self.ui.renew_domain_val_ex_date)
        append_key(d,'cltrid', self.ui.renew_domain_cltrid)
        period = {}
        append_key(period,'num', self.ui.renew_domain_period_num)
        append_key(period,'unit', self.ui.renew_domain_period_unit)
        if self.__check_required__(d, (('name',self.__tr('domain name')),('cur_exp_date',self.__tr('')))):
            self.__set_send_button__('renew_domain')
            if period.has_key('num'):
                period['unit'] = ('y','m')[period['unit']]
            else:
                period = None
            try:
                self.epp.renew_domain(d['name'], d['cur_exp_date'], period, d.get('val_ex_date'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
            self.__display_answer__('renew_domain')
        else:
            self.display_error(self.missing_required)

    def list_contact(self):
        self.__share_list__('list_contact', self.__tr('contact'))

    def list_nsset(self):
        self.__share_list__('list_nsset', self.__tr('nsset'))

    def list_domain(self):
        self.__share_list__('list_domain', self.__tr('domain'))

    #==============================
    # Sources
    #==============================
    def __display_sources__(self, command_name):
        'Display sources of command'
        wnd = wndSources(self)
        if self.src.has_key(command_name):
            wnd.ui.message.setText(u'%s %s'%(command_name,self.__tr('sources'))) ## u'<b>%s</b> %s'
            src = self.src[command_name]
            wnd.ui.command_line.setText(src[0])
            wnd.ui.command.setPlainText(QtCore.QString(fred.session_transfer.human_readable(src[1])))
            wnd.ui.response.setPlainText(QtCore.QString(fred.session_transfer.human_readable(src[2])))
        else:
            wnd.ui.message.setText(u'%s %s'%(command_name,self.__tr('Sources are not available now. Run command at first.')))
        wnd.setModal(True)
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
    def source_sendauthinfo_contact(self):
        self.__display_sources__('sendauthinfo_contact')
    def source_sendauthinfo_nsset(self):
        self.__display_sources__('sendauthinfo_nsset')
    def source_sendauthinfo_domain(self):
        self.__display_sources__('sendauthinfo_domain')
        
    def credits(self):
        'Display credits'
        wnd = QtGui.QDialog(self)
        wnd.setWindowTitle(self.__tr('Credits'))
        wnd.setModal(True)
        layout = QtGui.QVBoxLayout(wnd)
        edit = QtGui.QTextEdit(wnd)
        layout.addWidget(edit)
        edit.setPlainText(self.epp._epp.get_credits())
        btn = QtGui.QPushButton(self.__tr('Close'),wnd)
        layout.addWidget(btn)
        wnd.connect(btn,QtCore.SIGNAL("clicked()"),wnd.close)
        edit.setMinimumSize(500, 300)
        wnd.show()

def overwrite_status_by_reason_message(data):
    """Modification for object:check answers:
    Data must be dict type and source like this:
        cid:test                 1
        cid:test:reason     Available
    is modified to:
        cid:test                 Available
    """
    msg = {}
    patt_reason = re.compile('.+:reason', re.I)
    for key,status in data.items():
        if patt_reason.match(key): continue
        reason = data.get('%s:reason'%key)
        if reason:
            msg[key] = reason
        else:
            msg[key] = status
    return msg

def get_str(qtstr):
    'Translate QString. Trip whitespaces at the begining and end. Returns string in local charset.'
    if type(qtstr) is QtCore.QString:
        text = unicode(qtstr.trimmed().toUtf8(),'utf8').encode(encoding)
    else:
        if type(qtstr) is unicode:
            text = qtstr.encode(encoding)
        else:
            text = qtstr
    return text

def get_unicode(text):
    'Convert to unicode and catch problems with conversion.'
    if type(text) not in (str, unicode): text = str(text)
    if type(text) == str:
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = repr(text)
    return text

def append_key(dct, key, widget):
    'Append value if has been typed.'
    wt = type(widget)
    if wt == QtGui.QLineEdit:
        value = get_str(widget.text())
        if value: dct[key] = value
    elif wt == QtGui.QTextEdit:
        value = get_str(widget.toPlainText())
        if value: dct[key] = value
    elif wt in (QtGui.QRadioButton, QtGui.QCheckBox):
        dct[key] = widget.isChecked() and 1 or 0
    elif wt == QtGui.QDateEdit:
        dct[key] = '%s'%widget.date().toString(QtCore.Qt.ISODate) # QDate; Qt.ISODate='YYYY-MM-DD'
    elif wt == QtGui.QComboBox:
        dct[key] = widget.currentIndex()
    elif wt == QtGui.QTableWidget:
        data = []
        for r in range(widget.rowCount()):
            tbl_item = widget.item(r,0)
            if not tbl_item: continue
            value = get_str(tbl_item.text())
            if len(value): data.append(value)
        if len(data): dct[key] = data
    else:
        print "INTERNAL ERROR: Unknown type widget:",type(widget)
        
def count_data_rows(dct):
    size = 0
    for v in dct.values():
        if type(v) in (list,tuple):
            ln = len(v)
            size += ln
            if ln == 0: size += 1
        else:
            size += 1
    return size

def join_key_and_values(value):
    'Join key and values'
    # [u'ns2.test.cz', [u'127.289.30.63',u'127.289.30.63',]]
    if type(value) in (list, tuple):
        if len(value) == 2 and type(value[0]) in (str, unicode):
            key, addr = value
            value = '%s %s'%(key, join_items(addr))
        else:
            value = join_items(value)
    return value

def join_items(value):
    'Join items into string'
    if type(value) in (list, tuple):
        items = []
        for item in value:
            text = join_items(item)
            if text: items.append(text)
        if len(items):
            if len(items) > 1:
                value = u'(%s)'%u', '.join(items) 
            else:
                value = items[0]
        else:
            value = u''
    return value

def ttytag2html(text):
    # ${BOLD}, ${NORMAL}, ${COLOR}
    text = re.sub('\$\{BOLD\}(.*?)\$\{NORMAL\}','<b>\\1</b>',text)
    text = text.replace('${NORMAL}','</span>')
    text = re.sub('\$\{(\w+)\}','<span style="color:\\1">',text)
    return text

def main(argv, lang):
    path = os.path.dirname(__file__)
    if path: os.chdir(path) # needs for correct load resources - images and translation
    epp = fred.Client()
    app = QtGui.QApplication(sys.argv)
    window = FredMainWindow(app, epp)
    window.show()
    sys.exit(app.exec_())

# === FOR TEST ONLY === !!!
#PyQt4.QtCore.QChildEvent
#PyQt4.QtCore.QEvent
#QEvent::
#LABEL_EVENT = {
#    8: 'FocusIn - Widget gains keyboard focus.',
#    10: 'Enter - Mouse enters widget\'s boundaries.',
#    11: 'Leave - Mouse leaves widget\'s boundaries.',
#    12: 'Paint - Screen update necessary (QPaintEvent).',
#    13: 'Move',
#    14: 'Resize - Widget\'s size changed (QResizeEvent).',
#    17: 'Show - Widget was shown on screen (QShowEvent).',
#    18: 'Hide - Widget was hidden (QHideEvent).',
#    19: 'Close - Widget was closed (QCloseEvent).',
#    24: 'WindowActivate', ##!!!
#    25: 'WindowDeactivate - Window was deactivated.',
#    26: 'ShowToParent - A child widget has been shown.',
#    27: 'HideToParent - A child widget has been hidden.',
#    33: 'WindowTitleChange',
#    68: 'ChildAdded',
#    69: 'ChildPolished',
#    70: '70 nenasel jsem v tabulce',
#    71: 'ChildRemoved - An object loses a child (QChildEvent).',
#    74: 'PolishRequest - The widget should be polished.',
#    75: 'Polish - The widget is polished.',
#    76: 'LayoutRequest',
#    77: 'Widget layout needs to be redone.',
#    99: 'ActivationChange - A widget\'s top-level window activation state has changed.', #!!!
#    110: 'ToolTip - A tooltip was requested (QHelpEvent).',
#    }

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

