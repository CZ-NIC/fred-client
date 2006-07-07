# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, time
import sys, os, commands
from gettext import gettext as _T
import ConfigParser
import terminal_controler

# Colored output
colored_output = terminal_controler.TerminalController()

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE,CMD_ID,LANG,POLL_AUTOACK = range(4)
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
                 0 # ONLINE
                ,0 # CMD_ID
                ,'en' # LANG
                ,1 # POLL_AUTOACK
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
        if sys.stdout.encoding == 'cp852':
            frm=('\xcd','\xba','\xc9','\xbb','\xc8','\xbc')
            corr=(6,0)
        else:
            frm=[]
            for c in (u'\u2550',u'\u2551',u'\u2554',u'\u2557',u'\u255a',u'\u255d'):
                frm.append(c.encode('utf-8'))
            corr=(10,4)
        welcome = '%s   %s   %s'%(frm[1],_T('Welcome to the EPP client'),frm[1])
        sp = '%s   %s   %s'%(frm[1],' '*(len(welcome)-2-corr[0]),frm[1])
        sep = frm[0]*(len(welcome)-2-corr[1])
        return '%s%s%s\n%s\n%s\n%s\n%s%s%s\n%s'%(frm[2],sep,frm[3],sp,welcome,sp,frm[4],sep,frm[5],_T('For help type "help" (or "h", "?")'))


    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[CMD_ID],time.strftime('%y-%m-%dat%H:%M:%S')))

    #---------------------------
    # config
    #---------------------------
    def __create_default_conf__(self):
        'Create default config file.'
        # aktuální adresář? filepath
        ok = 0
        modul_path = os.path.dirname(__file__)
        if modul_path: modul_path+= '/'
        root_path = os.path.normpath(modul_path+'../')
        if root_path: root_path += '/'
        filepath = '%sdefault-config.txt'%modul_path
        try:
            self._conf.read(filepath)
            ok = 1
        except ConfigParser.ParsingError, msg:
            self.append_error(msg)
        section = 'conect'
        if ok: ok = self._conf.has_section(section)
        if ok:
            # adjust pathnames
            #root_path = os.path.split(modul_path)[0]
            option = 'ssl_cert'
            name = self.__get_config__(section, option)
            self._conf.set(section, option, '%s%s'%(root_path,name))
            option = 'ssl_key'
            name = self.__get_config__(section,option)
            self._conf.set(section, option, '%s%s'%(root_path,name))
            # schema = all-1.0.xsd
            seop = ('session','schema')
            name = self.__get_config__(seop[0], seop[1])
            self._conf.set(seop[0], seop[1], '%sschemas/%s'%(modul_path,name))
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

    def __save_conf__(self):
        'Save conf file.'
        try:
            fp = open(os.path.expanduser('~/%s'%self._name_conf),'w')
            self._conf.write(fp)
            fp.close()
            self.append_note(_T('Default config file saved. For more see help.'))
        except IOError, (no, msg):
            self.append_error('%s: [%d] %s'%(_T('Impossible saving conf file. Reason'),no,msg))

    def load_config(self):
        "Load config file and init internal variables. Returns 0 if fatal error occured."
        self._conf = ConfigParser.SafeConfigParser()
        if os.name == 'posix':
            glob_conf = '/etc/%s'%self._name_conf
        else:
            # ALLUSERSPROFILE =	C:\Documents and Settings\All Users
            glob_conf = os.path.expandvars('$ALLUSERSPROFILE/%s'%self._name_conf)
        self._conf.read([glob_conf, os.path.expanduser('~/%s'%self._name_conf)])
        if not self._conf.has_section('session'):
            if not self.__create_default_conf__():
                self.append_error(_T('Fatal error: Create default config failed.'))
                self.display() # display errors or notes
                return 0 # fatal error
            # self.__save_conf__() automatické uložení configu (vypnuto)
        # set session variables
        section = 'session'
        lang = self.__get_config__(section,'lang')
        if lang in self.defs[LANGS]:
            self._session[LANG] = lang
        else:
            self.append_note('%s: ${BOLD}%s${NORMAL} %s'%(_T('This language code is not allowed'),lang,str(self.defs[LANGS])))
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
            self._validate = (1,0)[re.match('validate\s+on',cmd, re.I)==None]
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
            self.append_note(errors.encode(sys.stdout.encoding))
            self._validate = 0 # validator is automaticly switched off
            self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
        return ok
    
    def is_epp_valid(self, message):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._validate: return '' # validace je vypnutá
        tmpname = os.path.expanduser('~/eppdoc_tmp_test_validity.xml')
        try:
            open(tmpname,'w').write(message)
        except IOError, (no, msg):
            try:
                msg = msg.decode(sys.stdout.encoding)
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
        c = '${%s}'%(color or 'YELLOW') # default
    list_of_messages.append('%s%s${NORMAL}'%(c,msg))

def join_unicode(u_list, sep='\n'):
    'Convert str objects to unicode and catch errors.'
    out=[]
    for row in u_list:
        if type(row) == str:
            try:
                row = row.decode(sys.stdout.encoding)
            except UnicodeDecodeError, error:
                row = '(UnicodeDecodeError) '+repr(row)
        out.append(row)
    return sep.join(out)

def print_unicode(text):
    'Print text and catch problems with unicode.'
    try:
        print text
    except UnicodeEncodeError, msg:
        print colored_output.render('${RED}${BOLD}%s:${NORMAL} %s'%(_T('No unicode. Display raw'),repr(re.sub('\x1b[^m]*m','',text))))

def get_unicode(text):
    'Convert to unicode and catch problems with conversion.'
    if type(text) == str:
        try:
            text = text.decode(sys.stdout.encoding)
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

