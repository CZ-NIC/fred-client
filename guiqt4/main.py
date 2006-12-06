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
from create_contact import FredWindow as wndCreateContact
from update_contact import FredWindow as wndUpdateContact
from create_domain import FredWindow as wndCreateDomain
from update_domain import FredWindow as wndUpdateDomain
from create_nsset import FredWindow as wndCreateNsset
from update_nsset import FredWindow as wndUpdateNsset

import shared_fnc
shared_fnc.init_encoding(encoding) # INIT shared_fnc.py module

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

    def __mytr(self, text):
        return QtGui.QApplication.translate("FredWindow", text, None, QtGui.QApplication.UnicodeUTF8)

    def __add_scroll__(self, parent_frame, classWindow):
        'Add scrolled view window. Module must have class FredWindow.'
        scroll = QtGui.QScrollArea(parent_frame)
#        scroll.setFrameShape(QtGui.QFrame.NoFrame)
#        scroll.setFrameShadow(QtGui.QFrame.Raised)
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

    def display_error(self, messages, qs_label=None):
        'Display Warning dialog.'
        # about, warning, critical
        if not qs_label: qs_label = self.__mytr('Missing required')
        if type(messages) not in (list,tuple): messages = (messages,)
        QtGui.QMessageBox.critical(self, qs_label, u'<h2>%s:</h2>\n%s'%(qs_label, u'<br>\n'.join(map(lambda s: get_str(s).decode(encoding),messages))))

    def btn_close(self):
        'Handle click on button Close'
        label = self.__mytr('Close client')
        msg = self.__mytr('Do you wand realy close client?')
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
        getattr(self.ui,'%s_code'%prefix).setText(code)
        getattr(self.ui,'%s_msg'%prefix).setText('<br>\n'.join(msg))
        if not table and getattr(self.ui, '%s_table'%prefix, None):
            table = (2,(self.__mytr('name'),self.__mytr('value')),(140,260),None,None)
        if table:
            columns, labels, col_sizes, only_key, count_rows = table
            col_labels = labels
            wtab = getattr(self.ui, '%s_table'%prefix)
            data = dct_answer.get('data',{})
            for pos in range(columns):
                header = wtab.horizontalHeaderItem(pos)
                header.setText(col_labels[pos])
#                header.resizeSection(0,col_sizes[pos])
                wtab.horizontalHeader().resizeSection(0,col_sizes[pos])
#            header = wtab.horizontalHeaderItem(0) # (QTableWidgetItem) header
#            header.setText(0, col_labels[0], col_sizes[0])
#            if columns > 1:
#                header.setText(1, col_labels[1], col_sizes[1])
            if count_rows:
                wtab.setRowCount(int(data.get(count_rows,'0')))
            else:
                wtab.setRowCount(shared_fnc.count_data_rows(data))
            #....................................................
            column_keys = self.epp._epp.get_keys_sort_by_columns()
            if not column_keys:
                column_keys = map(lambda k:(k,1,k), data.keys()) # default (unsorted)
            #....................................................
            r=0
            for key,verbose,label in column_keys:
                if only_key and key != only_key: continue
                value = data.get(key)
                if value is None: continue
                # enum EditType { Never, OnTyping, WhenCurrent, Always }
                if columns > 1:
                    if not label: label = key
#                    wtab.setItem(r, 0, QTableItem(wtab, QTableItem.OnTyping, label.decode(encoding)))
                    wtab.setItem(r, 0, QtGui.QTableWidgetItem(label.decode(encoding))) ## , QtGui.QTableWidgetItem.OnTyping
                    r = self.__inset_into_table__(wtab, value, 1, r)
                else:
                    r = self.__inset_into_table__(wtab, value, 0, r)
                r+=1
        else:
            getattr(self.ui,'%s_data'%prefix).setText('<pre>%s</pre>'%self.epp._epp.get_answer_udata())
        # save sources
        self.src[prefix] = (
            self.epp._epp.get_command_line().decode(encoding),
            self.epp._epp._raw_cmd.decode(self.epp._epp._epp_cmd.encoding),
            self.epp._epp._raw_answer.decode(self.epp._epp._epp_response.encoding),
            )
        # toggle widget to the response tab
        # TODO: jeste neni dokoncena kompatibilita...
        getattr(self.ui,'%s_response'%prefix).setCurrentPage(1)
        self.__set_status__()

    def __inset_into_table__(self, wtab, value, c, r):
        'Used by __display_answer__()'
        if type(value) in (list,tuple):
            if len(value):
                wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(value[0]))) ## , QtGui.QTableWidgetItem.OnTyping
                for v in value[1:]:
                    r+=1
                    wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(v))) ## , QtGui.QTableWidgetItem.OnTyping
        else:
            wtab.setItem(r, c, QtGui.QTableWidgetItem(get_unicode(value))) ## , QtGui.QTableWidgetItem.OnTyping
        return r


    def __set_status__(self):
        'Refresh status after login and logout.'
        if self.epp.is_logon():
            user, host = self.epp._epp.get_username_and_host()
            status = '<b>%s</b> <b style="color:darkgreen">ONLINE: %s@%s</b>'%(self.__mytr('status'), user, host)
        else:
            status = ('<b>%s</b> <b style="color:red">%s</b>'%(self.__mytr('status'),self.__mytr('disconnect'))).decode('utf8') # translation is saved in utf8
        self.ui.status.setText(status)
    
    def check_is_online(self):
        'Check online. True - online / False - offline.'
        ret = self.epp.is_logon()
        if not ret: self.display_error(self.__mytr('You are not logged. First do login.'))
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
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        try:
            getattr(self.epp,key)(d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__(key,(1,(label,),(380,),'list','count'))

    def __share_transfer__(self, key):
        'Shared for transfer commands.'
        if not self.check_is_online(): return
        d = {}
        append_key(d,'name', getattr(self,'%s_name'%key))
        append_key(d,'auth_info', getattr(self,'%s_password'%key))
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        if self.__check_required__(d, (('name',self.__mytr('name')),('auth_info',self.__mytr('Authorization info')))):
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
        append_key(d,'name', getattr(self,'%s_name'%key))
        append_key(d,'cltrid', getattr(self,'%s_cltrid'%key))
        if self.__check_required__(d, (('name',self.__mytr('name')),)):
            if extends == SPLIT_NAME:
                d['name'] = re.split('\s+',d['name']) # need for check commands
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
            self.display_error(self.__mytr('You are logged already.'))
            return
        d = {}
        append_key(d,'username',self.login_username)
        append_key(d,'password',self.login_password)
        append_key(d,'new_password',self.login_new_password)
        append_key(d,'cltrid',self.login_cltrid)
        if self.__check_required__(d, (('username',self.__mytr('username')),('password',self.__mytr('password')))):
            # Definition from welcome panel:
            dc = {}
            append_key(dc,'host',       self.connect_host)
            append_key(dc,'port',       self.connect_port)
            append_key(dc,'ssl_key',    self.connect_private_key)
            append_key(dc,'ssl_cert',   self.connect_certificate)
            append_key(dc,'timeout',    self.connect_timeout)
            self.epp.set_data_connect(dc)
            try:
                self.epp.login(d['username'], d['password'], d.get('new_password'), d.get('cltrid'))
            except fred.FredError, err:
                self.epp._epp._errors.extend(err.args)
                self.epp._epp._errors.append(self.__mytr('Process login failed.'))
            self.__display_answer__('login')
        else:
            self.display_error(self.missing_required)

    def logout(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d,'cltrid',self.logout_cltrid)
        try:
            self.epp.logout(d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__('logout')

    def poll(self):
        if not self.check_is_online(): return
        d = {}
        append_key(d, 'op', self.poll_op_ack)
        append_key(d, 'msg_id', self.poll_msg_id)
        append_key(d,'cltrid',self.poll_cltrid)
        d['op'] = ('req','ack')[d['op']]
        try:
            self.epp.poll(d['op'], d.get('msg_id'), d.get('cltrid'))
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__('poll')

    def hello(self):
        try:
            self.epp.hello()
        except fred.FredError, err:
            self.epp._epp._errors.extend(err.args)
        self.__display_answer__('hello')


    def delete_contact(self):
        pass
    def delete_domain(self):
        pass
    def delete_nsset(self):
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

    def credits(self):
        pass


def get_unicode(text):
    'Convert to unicode and catch problems with conversion.'
    if type(text) not in (str, unicode): text = str(text)
    if type(text) == str:
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = repr(text)
    return text


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
