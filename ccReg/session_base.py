# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, time
import sys, os, commands
import ConfigParser
import terminal_controler
from translate import _T, encoding

# Colored output
colored_output = terminal_controler.TerminalController()

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE, CMD_ID, LANG, POLL_AUTOACK, CONFIRM_SEND_COMMAND = range(5)
# názvy sloupců pro defaultní hodnoty
DEFS_LENGTH = 4
LANGS,objURI,extURI,PREFIX = range(DEFS_LENGTH)

class ManagerBase:
    """This class holds buffers with error and note messages.
    Class collects messages and prepares them for output.
    """
    def __init__(self):
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._validate = 1 # automatické zapnutí validace EPP XML dokumentů
        #-----------------------------------------
        # Session data:
        #-----------------------------------------
        self._session = [
                0,      # ONLINE
                0,      # CMD_ID
                'en', # LANG
                0,       # POLL_AUTOACK
                1        # CONFIRM_SEND_COMMAND
                ]
        # defaults
        self.defs = ['']*DEFS_LENGTH
        self.defs[LANGS] = ('en','cs') # seznam dostupných jazyků
        self.defs[objURI] = []
        self.defs[extURI] = []
        self.defs[PREFIX] = '' # pro každé sezení nový prefix
        self._conf = None # <ConfigParser object>
        self._name_conf = '.ccReg.conf' # name of config file
        self._host = None # explicit defined host

    def is_logon(self):
        'Returns 0-offline,1-online.'
        return self._session[ONLINE]

    def is_confirm_cmd_name(self, command_name):
        'Returns 0-not conrifmation,1-need conrifmation.'
        return self._session[CONFIRM_SEND_COMMAND] and re.match('(create|update|delete|transfer|renew)',command_name)

    def set_confirm(self, type):
        'Set switch confirm_commands_before_send'
        self._session[CONFIRM_SEND_COMMAND] = (0,1)[type in ('on','ON')]
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Confirm has been set to'),('OFF','ON')[self._session[CONFIRM_SEND_COMMAND]]))

    def set_host(self,host):
        self._host = host

    def get_errors(self, sep='\n'):
        return sep.join(self._errors)

    def append_error(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._errors, msg, color)

    def append_note(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._notes, msg, color)

    def fetch_errors(self, sep='\n'):
        msg = join_unicode(self._errors, sep)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        msg = join_unicode(self._notes, sep)
        self._notes = []
        return msg

    def is_error(self):
        "Check if any error occurs."
        return len(self._errors)
        
    def is_note(self):
        "Check if any note is in the stack"
        return len(self._notes)

    def display(self):
        "Output all messages to stdout or log file."
        #TODO: log file
        if self.is_note():
            # hlášení, poznámka, hodnoty
            for text in self._notes:
                print_unicode(colored_output.render(text))
            self._notes = []
        if self.is_error():
            # chybová hlášení
            print colored_output.render('${RED}${BOLD}')
            for text in self._errors:
                print_unicode(colored_output.render(text))
            self._errors = []
            print colored_output.render('${NORMAL}')

    def welcome(self):
        "Welcome message for console modul."
        # frame:  - | |- -| |_ _|
        if encoding == 'cp852':
            frm=('\xcd','\xba','\xc9','\xbb','\xc8','\xbc')
        else:
            frm=[]
            for c in (u'\u2550',u'\u2551',u'\u2554',u'\u2557',u'\u255a',u'\u255d'):
                frm.append(c.encode('utf-8'))
        msg = _T('Welcome to the ccReg console')
        try:
            msglen = len(unicode(msg, encoding))
        except UnicodeDecodeError:
            msglen = len(msg) # (Problem with terminal encoding)
        welcome = '   %s   '%msg
        msglen+=6
        empty_row = '%s%s%s'%(frm[1],' '*msglen,frm[1])
        horizontal_line = frm[0]*msglen
        return '%s%s%s\n%s\n%s%s%s\n%s\n%s%s%s\n%s\n%s'%(frm[2],horizontal_line,frm[3],empty_row,frm[1],welcome,frm[1],empty_row,frm[4],horizontal_line,frm[5],
             'Version 1.0. Beta release.',
            _T('For help type "help" (or "h", "?")'))


    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[CMD_ID],time.strftime('%y-%m-%dat%H:%M:%S')))

    #---------------------------
    # config
    #---------------------------
    def manage_config(self, param):
        'Display config values or save config.'
        if param[0] == 'create':
            if self.__create_default_conf__():
                self.save_confing()
            else:
                self.append_error(_T('Create default config failed.'))
        else:
            print_unicode('%s:'%_T("Actual config is"))
            if not self._conf:
                print_unicode(_T('No config'))
                return
            for section in self._conf.sections():
                print colored_output.render('${BOLD}[%s]${NORMAL}'%section)
                for option in self._conf.options(section):
                    print_unicode(colored_output.render('\t${BOLD}%s${NORMAL} = %s'%(option,self._conf.get(section,option))))
    
    def __create_default_conf__(self):
        'Create default config file.'
        # aktuální adresář? filepath
        ok = 0
        modul_path,fn = os.path.split(__file__)
        root_path = os.path.normpath(os.path.join(modul_path,'..'))
        filepath = os.path.join(modul_path, 'default-config.txt')
        try:
            self._conf.read(filepath)
            ok = 1
        except ConfigParser.ParsingError, msg:
            self.append_error(msg)
        section = 'conect'
        if ok: ok = self._conf.has_section(section)
        if ok:
            # adjust pathnames
            option = 'ssl_cert'
            name = self.__get_config__(section, option)
            self._conf.set(section, option, os.path.join(root_path,name))
            option = 'ssl_key'
            name = self.__get_config__(section,option)
            self._conf.set(section, option, os.path.join(root_path,name))
            # schema = all-1.0.xsd
            seop = ('session','schema')
            name = self.__get_config__(seop[0], seop[1])
            self._conf.set(seop[0], seop[1], os.path.join(modul_path,'schemas',name))
            self._session[POLL_AUTOACK] = {False:0,True:1}[self.__get_config__(seop[0], 'poll_ack') in ('on','ON')]
        return ok

    def __get_config__(self,section,option,is_int=None):
        'Get value from config and catch exceptions.'
        value=None
        if not self._conf: return value
        try:
            value = self._conf.get(section,option)
        except ConfigParser.NoSectionError, msg:
            self.append_error('ConfigError: %s'%msg)
        except ConfigParser.NoOptionError, msg:
            self.append_error('ConfigError: %s'%msg)
        if is_int:
            try:
                value = int(value)
            except ValueError, msg:
                self.append_error('Config ${BOLD}%s:${NORMAL} %s.'%(option,msg))
                value = 0
        return value

    def save_confing(self):
        'Save conf file.'
        filepath = os.path.join(os.path.expanduser('~'),self._name_conf)
        try:
            fp = open(filepath,'w')
            self._conf.write(fp)
            fp.close()
            self.append_note(_T('Default config file saved. For more see help.'))
            self.append_note(filepath,('BOLD','GREEN'))
        except IOError, (no, msg):
            self.append_error('%s: [%d] %s'%(_T('Impossible saving conf file. Reason'),no,msg))

    def load_config(self):
        "Load config file and init internal variables. Returns 0 if fatal error occured."
        self._conf = ConfigParser.SafeConfigParser()
        if not self.__create_default_conf__():
            self.append_error(_T('Fatal error: Create default config failed.'))
            self.display() # display errors or notes
            return 0 # fatal error
        if os.name == 'posix':
            glob_conf = '/etc/%s'%self._name_conf
        else:
            # ALLUSERSPROFILE =	C:\Documents and Settings\All Users
            glob_conf = os.path.join(os.path.expandvars('$ALLUSERSPROFILE'),self._name_conf)
        self._conf.read([glob_conf, os.path.join(os.path.expanduser('~'),self._name_conf)])
        # set session variables
        section = 'session'
        lang = self.__get_config__(section,'lang')
        if lang in self.defs[LANGS]:
            self._session[LANG] = lang
        else:
            self.append_note('%s: ${BOLD}%s${NORMAL} %s'%(_T('This language code is not allowed'),lang,str(self.defs[LANGS])))
        self._session[CONFIRM_SEND_COMMAND] = {False:0,True:1}[self.__get_config__(section,'confirm_send_commands') == 'on']
        return 1 # OK

    #---------------------------
    # validation
    #---------------------------
    def set_validate(self, cmd):
        "Set feature of the manager - it will or not validate EPP documents. cmd='validate on/off'"
        if re.match('validate$',cmd):
            # jen zobrazení stavu
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Status: Validation is'),('OFF','ON')[self._validate]))
        else:
            # změna stavu
            self._validate = {False:0,True:1}[re.match('validate\s+on',cmd, re.I) is not None]
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Validation is set'),('OFF','ON')[self._validate]))

    def check_validator(self):
        'Check if exists external validator (xmllint).'
        ok = 0
        try:
            pipes = os.popen3('xmllint')
        except IOError, msg:
            self.append_note(str(msg),('RED','BOLD'))
        standr = pipes[1].read()
        errors = pipes[2].read()
        map(lambda f: f.close(), pipes)
        if len(standr) and not len(errors):
            ok = 1 # OK, support is enabled.
        else:
            try:
                uerr = errors.decode(encoding)
            except UnicodeDecodeError:
                uerr = repr(errors)
            self.append_note(uerr)
            self._validate = 0 # validator is automaticly switched off
            self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
        return ok
    
    def is_epp_valid(self, message):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._validate: return '' # validace je vypnutá
        tmpname = os.path.join(os.path.expanduser('~'),'eppdoc_tmp_test_validity.xml')
        try:
            open(tmpname,'w').write(message)
        except IOError, (no, msg):
            try:
                msg = msg.decode(encoding)
            except UnicodeDecodeError, error:
                msg = '(UnicodeDecodeError) '+repr(msg)
            self._validate = 0 # automatické vypnutí validace
            self.append_note('%s: [%d] %s'%(_T('Temporary file for verify XML EPP validity cannot been created. Reason'),no,msg))
            self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
            return '' # impossible save xml file needed for validation
        # kontrola validity XML
        schema_path = self.__get_config__('session','schema')
        if not schema_path:
            os.unlink(tmpname)
            return '' # schema path is not set
        try:
            pipes = os.popen3('xmllint --schema "%s" "%s"'%(schema_path, tmpname))
        except IOError, msg:
            self.append_note(str(msg),('RED','BOLD'))
        xmldoc = pipes[1].read() # unfortunately this doesnt work: ('...'-OK, ''-invalid)
        errors = pipes[2].read()
        map(lambda f: f.close(), pipes)
        os.unlink(tmpname)
        if re.search(' validates$', errors) or xmldoc == '':
            errors = '' # it seems be OK...
        else:
            if re.search('Schemas parser error',errors):
                # schema missing!
                self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
                self._validate = 0 # automatické vypnutí validace
                errors=''
        return errors

def append_with_colors(list_of_messages, msg, color):
    "Used by Manager::append_error() and Manager::append_note() functions"
    if type(color) in (list, tuple):
        c = ''.join(['${%s}'%c for c in color])
    else:
        c = '${%s}'%(color or 'WHITE') # default color
    list_of_messages.append('%s%s${NORMAL}'%(c,msg))

def join_unicode(u_list, sep='\n'):
    'Convert str objects to unicode and catch errors.'
    out=[]
    for row in u_list:
        if type(row) == str:
            try:
                row = row.decode(encoding)
            except UnicodeDecodeError, error:
                row = '(UnicodeDecodeError) '+repr(row)
        out.append(row)
    return sep.join(out)

def get_ltext(text):
    'Encode unicode to string in the local encoding.'
    if type(text) == str:
        ltext = colored_output.render(text)
    else:
        try:
            ltext = text.encode(encoding)
        except UnicodeEncodeError, msg:
            ltext = repr(re.sub('\x1b[^m]*m','',text))
        else:
            ltext = colored_output.render(ltext)
    return ltext

def print_unicode(text):
    'Print text and catch encoding problems with unicode.'
    print get_ltext(text)
        

def get_unicode(text):
    'Convert to unicode and catch problems with conversion.'
    if type(text) == str:
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = repr(re.sub('\$\{[A-Z]+\}','',text)) # remove color tags
    return text

if __name__ == '__main__':
    mb = ManagerBase()
    mb._conf = ConfigParser.SafeConfigParser()
    mb.__create_default_conf__()
    mb.display()
    for section in mb._conf.sections():
        print '[%s]'%section
        for item in mb._conf.items(section):
            print '\t%s = %s'%item

