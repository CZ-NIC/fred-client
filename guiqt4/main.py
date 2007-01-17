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
import sys, traceback
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
NO_SPLIT_NAME, SPLIT_NAME = (0,1)

class RunEPPCommunication(QtCore.QThread):
    'Run Epp communication in separate thread'

    def __init__(self, fred_client, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.client = fred_client
        self.command_name = ''
        self.params = None

    def set_command(self, name, params = None):
        self.command_name = name
        self.params = params

    def run(self):
        'Run EPP command.'
        exception_msg = ''
        try:
            self.client._epp.api_command(self.command_name, self.params)
        except fred.FredError, err:
            self.client._epp._errors.extend(err.args)
        except:
            # stderr is redirected into Internal Error Log window
            sys.stderr.write(get_exception())
        self.emit(QtCore.SIGNAL("epp_command_finished()"))

class RedirectOutput:
    'Redirect output to the window or list.'
    def __init__(self, wndEdit, list_messages = None):
        self.wndEdit = wndEdit
        self.list_messages = list_messages
    def write(self, message):
        if self.wndEdit is not None:
            self.wndEdit.insertPlainText(message)
        if self.list_messages is not None:
            self.list_messages.append(message)


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
        self.epp._epp._sep = '<br>\n' # separator for display lines in QtGui.QTextEdit as HTML
        self.missing_required = []
        self.src = {} # {'command_name':['command line','XML source','XML response'], ...}
        self._stderr_errors = [] # Keep internal errors for display.
        self._thread_errors = [] # Temporary list of errors generated inside different thread.
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
        # Class for running EPP communication in separate thread
        self.thread_epp = RunEPPCommunication(self.epp)
        self.connect(self.thread_epp, QtCore.SIGNAL("epp_command_finished()"), self.process_answer)
        # Window handlers of the 'Send command' buttons:
        self._btn_send = [obj for name, obj in self.ui.__dict__.items() if re.match('send_',name)]
        # Redirect output and errors:
        sys.stdout = RedirectOutput(self.ui.system_messages)
        sys.stderr  = RedirectOutput(None, self._thread_errors)
        # INIT
        self.load_config_and_autologin()

    def write(self, message):
        'Catch error messages from stderr.'
        self._stderr_errors.append(message)
        self.display_error(_TU('Some internal error occured. See <b>Error log</b> on the first panel. Reset application else some unexpected behavior can occurs.'), _TU('Internal error'))

    def append_system_messages(self, messages):
        'Appent text to the System message window'
        msg = [get_unicode(ttytag2html(text)) for text in messages]
        self.ui.system_messages.insertHtml(u'<br>\n'.join(msg))

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
        modul_trans = os.path.join(os.path.split(__file__)[0],'%s%s'%(translation_prefix, lang))
        if tr.load(modul_trans):
            self._app.installTranslator(tr)
            self.panel_create_contact.ui.retranslateUi(self)
            self.panel_update_contact.ui.retranslateUi(self)
            self.panel_create_domain.ui.retranslateUi(self)
            self.panel_update_domain.ui.retranslateUi(self)
            self.panel_create_nsset.ui.retranslateUi(self)
            self.panel_update_nsset.ui.retranslateUi(self)
            self.ui.retranslateUi(self)

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
        if not qs_label: qs_label = _TU('Missing required')
        if type(messages) not in (list,tuple): messages = (messages,)
        if not_critical:
            pass
        dialog_type = not_critical and 'information' or 'critical'
        getattr(QtGui.QMessageBox,dialog_type)(self, qs_label, u'<h2>%s:</h2>\n%s'%(qs_label, u'<br>\n'.join(map(lambda s: get_str(s).decode(encoding),messages))))

    def system_messages_changed(self):
        """Called if System messsage windows is changed.
        It means any error occurs. Function toggle to the first tab page for
        give a notice to user about some problem.
        """
        # DISABLED:
        # self.ui.tabWidget.setCurrentWidget (self.ui.tabWidget.widget(0)) # Set to Welcome page on the main panel.

    def btn_close(self):
        'Handle click on button Close'
        label = _TU('Close client')
        msg = _TU('Do you wand realy close client?')
        if QtGui.QMessageBox.warning(self, label, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            QtGui.QWidget.close(self)

    def closeEvent(self, e):
        'Finalize when dialog is closed.'
        self.epp.logout()
        QtGui.QWidget.closeEvent(self, e)

    def process_answer(self):
        'Process answer and catch exceptions.'
        if len(self._thread_errors):
            # erorrs catched in command thread
            self.write('\n'.join(self._thread_errors))
            self._thread_errors = [] # reset temporaty list
        try:
            self.display_answer()
        except:
            self.write(get_exception())
        self.__set_status__()
        self.enable_send_buttons()

    def display_answer(self):
        'Display answer from EPP server.'
        # self.epp._epp._dct_answer {
        #    'code': int
        #    'command': unicode
        #    'reason': unicode
        #    'errors': [str, str, ...]
        #    'data': { key: str }
        # }
        dct_answer = self.epp._epp._dct_answer
        command_name = dct_answer['command']
        if not command_name:
            # if command was not sent or created
            command_name = self.thread_epp.command_name
        matches = re.match('(\w+):(.+)', command_name)
        # convert value: contact:list -> list_contact
        if matches: command_name = '%s_%s'%(matches.group(2),matches.group(1))
        errors = []
        notes = self.epp._epp.fetch_notes()
        error = self.epp._epp.fetch_errors()
        notes_afrer_errors = self.epp._epp.fetch_notes_afrer_errors()
        #
        if(error): errors.append(error)
        if len(dct_answer.get('errors',[])):
            errors.extend(dct_answer['errors'])
        code = '<b>code:</b> %d'%dct_answer.get('code',0)
        msg = []
        reason = dct_answer.get('reason','')
        if reason:
            if type(reason) is str: reason = reason.decode(encoding)
            msg.append(reason)
        if len(notes):
            if type(notes) not in (list, tuple): notes = (notes,)
            msg.append(ttytag2html('\n'.join(notes)))
        if len(errors):
            if type(errors) not in (list, tuple): errors = (errors,)
            msg.append('<b style="color:red">%s</b>'%ttytag2html('\n'.join(errors)))
        if len(notes_afrer_errors):
            if type(notes_afrer_errors) not in (list, tuple): notes_afrer_errors = (notes_afrer_errors,)
            msg.append(ttytag2html('\n'.join(notes_afrer_errors)))
        getattr(self.ui,'%s_code'%command_name).setText(QtCore.QString(code))
        getattr(self.ui,'%s_msg'%command_name).setHtml(u'<br>\n'.join(map(get_unicode,msg)))
        # Prepare data headers and resolve widget type:
        if re.match('list_', command_name):
            matches = re.match('\w+_(.+)',command_name)
            label  = matches and matches.group(1) or ''
            table = (1,(label,),(380,),'list','count')
        elif command_name == 'credit_info':
            table = (2,(_TU('zone'),_TU('credit')),(140,260),None,None)
        elif getattr(self.ui, '%s_table'%command_name, None):
            table = (2,(_TU('name'),_TU('value')),(140,260),None,None)
        else:
            table = None
        # Modify status tags in info answers:
        self.epp._epp.reduce_info_status(dct_answer['command'], self.epp._epp._dct_answer['data'])
        # Display results:
        if table:
            # display in QTableWidget
            columns, labels, col_sizes, only_key, count_rows = table
            wtab = getattr(self.ui, '%s_table'%command_name)
            data = dct_answer.get('data',{})
            if re.match('\w+:check',dct_answer.get('command')):
                # overwrite number status by reason message
                data = overwrite_status_by_reason_message(data)
            for pos in range(columns):
                header = wtab.horizontalHeaderItem(pos)
                header.setText(labels[pos])
                wtab.horizontalHeader().resizeSection(pos,col_sizes[pos])
            if count_rows:
                wtab.setRowCount(int(data.get(count_rows,'0')))
            else:
                wtab.setRowCount(count_data_rows(data))
            #....................................................
            column_keys = self.epp._epp.get_keys_sort_by_columns()
            if not column_keys:
                column_keys = map(lambda k:(k,1,k), data.keys()) # default (unsorted)
            #....................................................
            if command_name == 'info_nsset':
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
                    wtab.setItem(r, 0, QtGui.QTableWidgetItem(get_unicode(label)))
                    r = self.__inset_into_table__(wtab, value, 1, r)
                else:
                    r = self.__inset_into_table__(wtab, value, 0, r)
                r+=1
        else:
            getattr(self.ui,'%s_data'%command_name).setHtml('<pre>%s</pre>'%self.epp._epp.get_answer_udata())
        # save sources
        self.src[command_name] = (
            self.epp._epp.get_command_line().decode(encoding),
            self.epp._epp._raw_cmd.decode(self.epp._epp._epp_cmd.encoding),
            self.epp._epp._raw_answer.decode(self.epp._epp._epp_response.encoding),
            )
        # toggle widget to the response tab
        q_tab_widget = getattr(self.ui,'%s_response'%command_name)
        page = q_tab_widget.widget(1)
        if page:
            q_tab_widget.setCurrentWidget (page)

    def __set_send_buttons__(self, is_enable=False):
        'Enabled/disabled all "Send command" buttons.'
        for btn in self._btn_send:
            btn.setEnabled(is_enable)
    def enable_send_buttons(self):
        self.__set_send_buttons__(True)
    def disable_send_buttons(self):
        self.__set_send_buttons__(False)

    def __inset_into_table__(self, wtab, value, c, r):
        'Used by display_answer()'
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
            status = '<b>%s</b> <b style="color:darkgreen">ONLINE: %s@%s</b>'%(_TU('status'), user, host)
        else:
            status = ('<b>%s</b> <b style="color:red">%s</b>'%(_TU('status'),_TU('disconnect'))).decode('utf8') # translation is saved in utf8
        self.ui.status.setText(status)
    
    def check_is_online(self):
        'Check online. True - online / False - offline.'
        ret = self.epp.is_logon()
        if not ret: self.display_error(_TU('You are not logged. First do login.'), _TU('Offline'))
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
        self.disable_send_buttons()
        self.thread_epp.set_command(key, d)
        self.thread_epp.start()

    def __share_transfer__(self, key):
        'Shared for transfer commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self.ui,'%s_name'%key))
        append_key(d,'auth_info', getattr(self.ui,'%s_password'%key))
        append_key(d,'cltrid', getattr(self.ui,'%s_cltrid'%key))
        if self.__check_required__(d, (('name',_TU('name')),('auth_info',_TU('Authorization info')))):
            self.disable_send_buttons()
            self.thread_epp.set_command(key, d)
            self.thread_epp.start()
        else:
            self.display_error(self.missing_required)

    def __share_command__(self, key, extends=0, anchor = 'name'):
        'Shared for command handlers check, info, delete.'
        if not self.check_is_online(): return
        d = {}
        append_key(d, anchor, getattr(self.ui,'%s_%s'%(key,anchor)))
        append_key(d,'cltrid', getattr(self.ui,'%s_cltrid'%key))
        if self.__check_required__(d, ((anchor, _TU('name')),)):
            if extends == SPLIT_NAME:
                d[anchor] = re.split('[,;\s]+', d[anchor]) # need for check commands
            self.disable_send_buttons()
            self.thread_epp.set_command(key, d)
            self.thread_epp.start()
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
            self.display_error(_TU('You are logged already.'), _TU('Invalid command usage'))
            return
        d = {}
        append_key(d,'username',self.ui.login_username)
        append_key(d,'password',self.ui.login_password)
        append_key(d,'new_password',self.ui.login_new_password)
        append_key(d,'cltrid',self.ui.login_cltrid)
        if self.__check_required__(d, (('username',_TU('username')),('password',_TU('password')))):
            # Definition from welcome panel:
            self.disable_send_buttons()
            dc = {}
            append_key(dc,'host',       self.ui.connect_host)
            append_key(dc,'port',       self.ui.connect_port)
            append_key(dc,'ssl_key',    self.ui.connect_private_key)
            append_key(dc,'ssl_cert',   self.ui.connect_certificate)
            append_key(dc,'timeout',    self.ui.connect_timeout)
            self.epp.set_data_connect(dc)
            self.disable_send_buttons()
            self.thread_epp.set_command('login', d)
            self.thread_epp.start()
        else:
            self.display_error(self.missing_required)

    def logout(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid',self.ui.logout_cltrid)
        self.disable_send_buttons()
        self.thread_epp.set_command('logout', d)
        self.thread_epp.start()

    def poll(self):
        'Send poll'
        if not self.check_is_online(): return
        d = {}
        append_key(d, 'op', self.ui.poll_op_ack)
        append_key(d, 'msg_id', self.ui.poll_msg_id)
        append_key(d,'cltrid',self.ui.poll_cltrid)
        d['op'] = ('req','ack')[d['op']]
        self.disable_send_buttons()
        self.thread_epp.set_command('poll', d)
        self.thread_epp.start()

    def hello(self):
        'Send hello'
        self.disable_send_buttons()
        self.thread_epp.set_command('hello')
        self.thread_epp.start()

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
                    ('id',_TU('contact ID')), 
                    ('name',_TU('name')), 
                    ('email',_TU('email')), 
                    ('city',_TU('city')), 
                    ('cc',_TU('country code')))
                    ):
            d['contact_id'] = d['id'] # compatibility with API
            self.disable_send_buttons()
            self.thread_epp.set_command('create_contact', d)
            self.thread_epp.start()
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
        if self.__check_required__(d, (('id',_TU('NSSET ID')), ('dns',_TU('dns')), ('tech',_TU('tech. contact')))):
            self.disable_send_buttons()
            self.thread_epp.set_command('create_nsset', d)
            self.thread_epp.start()
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
        if self.__check_required__(d, (('name',_TU('name')), ('registrant',_TU('registrant')))):
            self.disable_send_buttons()
            self.thread_epp.set_command('create_domain', d)
            self.thread_epp.start()
        else:
            self.display_error(self.missing_required)

    def update_contact(self):
        if not self.check_is_online(): return
        d = {}
        p = self.panel_update_contact.ui
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
            self.epp._epp._errors.append(_TU('In a part of address must be set both city and country code. For disabled this part leave both empty.'))
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
        if self.__check_required__(d, (('id',_TU('Contact ID')),)) and len(d) > 1:
            d['contact_id'] = d['id'] # compatibility with API
            self.disable_send_buttons()
            self.thread_epp.set_command('update_contact', d)
            self.thread_epp.start()
        else:
            if len(d) == 1:
                self.missing_required.append(_TU('No values to update.'))
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
        if len(add): d['add'] = add
        #................................
        rem = {}
        for key in ('name','tech'):
            append_key(rem, key, getattr(panel.ui, 'rem_%s'%key))
        if len(rem): d['rem'] = rem
        #................................
        chg = {}
        append_key(chg, 'auth_info', getattr(panel.ui, 'auth_info'))
        if len(chg): d['chg'] = chg
        if self.__check_required__(d, (('id',_TU('NSSET ID')),)) and len(d) > 1:
            self.disable_send_buttons()
            self.thread_epp.set_command('update_nsset', d)
            self.thread_epp.start()
        else:
            if len(d) == 1:
                self.missing_required.append(_TU('No values to update.'))
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
        if len(add): d['add'] = add['admin']
        #................................
        rem = {}
        for key in ('admin',):
            append_key(rem, key, getattr(p, 'rem_%s'%key))
        if len(rem): d['rem'] = rem['admin']
        #................................
        chg = {}
        for key in ('nsset','registrant','auth_info'):
            append_key(chg, key, getattr(p, 'chg_%s'%key))
        if len(chg): d['chg'] = chg
        #................................
        if p.val_ex_date.isEnabled():
            append_key(d, 'val_ex_date', p.val_ex_date)
        if self.__check_required__(d, (('name',_TU('domain name')),)) and len(d) > 1:
            self.disable_send_buttons()
            self.thread_epp.set_command('update_domain', d)
            self.thread_epp.start()
        else:
            if len(d) == 1:
                self.missing_required.append(_TU('No values to update.'))
            self.display_error(self.missing_required)

    def delete_contact(self):
        self.__share_command__('delete_contact', NO_SPLIT_NAME, 'id')

    def delete_nsset(self):
        self.__share_command__('delete_nsset', NO_SPLIT_NAME, 'id')

    def delete_domain(self):
        self.__share_command__('delete_domain')

    def sendauthinfo_contact(self):
        self.__share_command__('sendauthinfo_contact', NO_SPLIT_NAME, 'id')

    def sendauthinfo_nsset(self):
        self.__share_command__('sendauthinfo_nsset', NO_SPLIT_NAME, 'id')

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
        if self.__check_required__(d, (('name',_TU('domain name')),('cur_exp_date',_TU('Expiration date')))):
            if period.has_key('num'):
                period['unit'] = ('y','m')[period['unit']]
            else:
                period = None
            self.disable_send_buttons()
            self.thread_epp.set_command('renew_domain', d)
            self.thread_epp.start()
        else:
            self.display_error(self.missing_required)

    def credit_info(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid', self.ui.credit_info_cltrid)
        self.disable_send_buttons()
        self.thread_epp.set_command('credit_info', d)
        self.thread_epp.start()

    def list_contact(self):
        self.__share_list__('list_contact', _TU('contact'))

    def list_nsset(self):
        self.__share_list__('list_nsset', _TU('nsset'))

    def list_domain(self):
        self.__share_list__('list_domain', _TU('domain'))

    def technical_test(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'id', self.ui.technical_test_id)
        append_key(d,'name', self.ui.technical_test_name)
        append_key(d,'cltrid', self.ui.technical_test_cltrid)
        if self.__check_required__(d, (('id',_TU('NSSET ID')),('name',_TU('domain name')))):
            self.disable_send_buttons()
            self.thread_epp.set_command('technical_test', d)
            self.thread_epp.start()
        else:
            self.display_error(self.missing_required)


    #==============================
    # Sources
    #==============================
    def __display_sources__(self, command_name):
        'Display sources of command'
        wnd = wndSources(self)
        if self.src.has_key(command_name):
            #wnd.ui.message.setText(u'%s %s'%(command_name,_TU('sources'))) ## u'<b>%s</b> %s'
            src = self.src[command_name]
            wnd.ui.command_line.setText(src[0])
            wnd.ui.command.setPlainText(QtCore.QString(fred.session_transfer.human_readable(src[1])))
            wnd.ui.response.setPlainText(QtCore.QString(fred.session_transfer.human_readable(src[2])))
        else:
            #wnd.ui.message.setText(u'%s %s'%(command_name,_TU('Sources are not available now. Run command at first.')))
            pass
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
    def source_credit_info(self):
        self.__display_sources__('credit_info')
    def source_technical_test(self):
        self.__display_sources__('technical_test')

    def __display_text_wnd__(self, text, label=''):
        'Display window with any text'
        wnd = QtGui.QDialog(self)
        wnd.setWindowTitle(label)
        wnd.setModal(True)
        layout = QtGui.QVBoxLayout(wnd)
        edit = QtGui.QTextEdit(wnd)
        layout.addWidget(edit)
        edit.setPlainText(text)
        btn = QtGui.QPushButton(_TU('Close'),wnd)
        layout.addWidget(btn)
        wnd.connect(btn,QtCore.SIGNAL("clicked()"),wnd.close)
        edit.setMinimumSize(500, 300)
        wnd.show()

    def credits(self):
        'Display credits'
        self.__display_text_wnd__(self.epp._epp.get_credits(), _TU('Credits'))

    def show_errorlog(self):
        'Display error logs'
        if len(self._stderr_errors):
            text = ''.join(self._stderr_errors)
        else:
            text = _TU('(No record.)')
        self.__display_text_wnd__(text, _TU('Internal errors'))
        
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
        if type(qtstr) not in (str, unicode): qtstr = str(qtstr)
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
    'Convert tty tags to the html tags.'
    # ${BOLD}, ${NORMAL}, ${COLOR}
    text = re.sub('\$\{BOLD\}(.*?)\$\{NORMAL\}','<b>\\1</b>',text)
    text = text.replace('${NORMAL}','</span>')
    text = re.sub('\$\{(\w+)\}','<span style="color:\\1">',text)
    return text

def get_exception():
    'Fetch excption for recording.'
    msg = ['Traceback (most recent call last):']
    ex = sys.exc_info()
    sys.exc_clear()
    for trace in traceback.extract_tb(ex[2]):
        msg.append(' File "%s", line %d, in %s'%(trace[0], trace[1], trace[2]))
        msg.append('    %s'%trace[3])
    msg.append('%s: %s'%(ex[0], ex[1]))
    return '\n'.join(msg)

def main(argv, lang):
    path = os.path.dirname(__file__)
    if path: os.chdir(path) # needs for correct load resources - images and translation
    epp = fred.Client()
    app = QtGui.QApplication(sys.argv)
    window = FredMainWindow(app, epp)
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

