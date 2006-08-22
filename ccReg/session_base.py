# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, time
import sys, os, commands
import ConfigParser
import terminal_controler
import translate
##from translate import _T, encoding, options, config

_T = translate._T

# Colored output
colored_output = terminal_controler.TerminalController()

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE, CMD_ID, LANG, POLL_AUTOACK, CONFIRM_SEND_COMMAND, \
    USERNAME, NAME, HOST, COLORS, VALIDATE, VERBOSE = range(11)
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
        #-----------------------------------------
        # Session data:
        #-----------------------------------------
        self._session = [
                0,      # ONLINE
                0,      # CMD_ID
                'en',   # LANG
                0,      # POLL_AUTOACK
                1,      # CONFIRM_SEND_COMMAND
                '',     # USERNAME (for prompt info)
                '',     # NAME
                '',     # HOST (for prompt info)
                0,      # COLORS 0/1
                1,      # VALIDATE
                1,      # VERBOSE 1,2,3
                ]
        # defaults
        self.defs = ['']*DEFS_LENGTH
        # Values objURI a extURI are loaded from greeting message.
        self.defs[objURI] = ['http://www.nic.cz/xml/epp/contact-1.0',
                'http://www.nic.cz/xml/epp/domain-1.0',
                'http://www.nic.cz/xml/epp/nsset-1.0']
        self.defs[extURI] = ['http://www.nic.cz/xml/epp/enumval-1.0']
        self.defs[PREFIX] = '' # pro každé sezení nový prefix
        self._conf = translate.config # <ConfigParser object> from translate module
        self._auto_connect = 1 # auto connection during login or hello
        self._options = translate.options # parameters from command line

    def get_session(self, offset):
        return self._session[offset]
        
    def init_options(self):
        'Init variables from options (after loaded config).'
        self._session[LANG] = self._options['lang']
        if self._options['colors']:
            colored_output.set_mode(1)
            self._session[COLORS] = 1
        if self._options['verbose']:
            self.__init_verbose__(self._options['verbose'])
        
    def set_auto_connect(self, switch):
        'Set auto connection ON/OFF. switch = 0/1.'
        self._auto_connect = {False:0,True:1}[switch==1]

    def is_logon(self):
        'Returns 0-offline,1-online.'
        return self._session[ONLINE]

    def get_username_and_host(self):
        'Returns username and host.'
        return self._session[USERNAME], self._session[HOST]
        
    def is_confirm_cmd_name(self, command_name):
        'Returns 0-not conrifmation,1-need conrifmation.'
        return self._session[CONFIRM_SEND_COMMAND] and re.match('(create|update|delete|transfer|renew)',command_name)

    def set_confirm(self, type):
        'Set switch confirm_commands_before_send'
        self._session[CONFIRM_SEND_COMMAND] = (0,1)[type in ('on','ON')]
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Confirm has been set to'),('OFF','ON')[self._session[CONFIRM_SEND_COMMAND]]))

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
        msg = self.get_messages()
        if msg: print msg

    def get_messages(self, sep='\n'):
        'Same as display but returns as local string.'
        #TODO: log file
        msg = []
        if self.is_note():
            # hlášení, poznámka, hodnoty
            for text in self._notes:
                msg.append(get_ltext(colored_output.render(text)))
            self._notes = []
        if self.is_error():
            # chybová hlášení
            msg.append(colored_output.render('${RED}${BOLD}'))
            for text in self._errors:
                msg.append(get_ltext(colored_output.render(text)))
            self._errors = []
            msg.append(colored_output.render('${NORMAL}'))
        return sep.join(msg)

    def welcome(self):
        "Welcome message."
        return _T('ccRegClient 1.1\nType "help", "license" or "credits" for more information.')

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
                    print_unicode(colored_output.render('\t${BOLD}%s${NORMAL} = %s'%(option,str(self.get_config_value(section,option)))))

    def copy_default_options(self, section, section_default, option):
        'Copy default options where they missing.'
        value = self.get_config_value(section, option, 1)
        if not value:
            value = self.get_config_value(section_default, option, 1)
            if value:
                if not self._conf.has_section(section): self._conf.add_section(section)
                self._conf.set(section, option, value)

    def __create_default_conf__(self):
        'Create default config file.'
        ok = 0
        modul_path,fn = os.path.split(__file__)
        root_path = os.path.normpath(os.path.join(modul_path,'..'))
        filepath = os.path.join(modul_path, 'default-config.txt')
        try:
            self._conf.read(filepath)
            ok = 1
        except ConfigParser.ParsingError, msg:
            self.append_error(msg)
        else:
            # schema = all-1.0.xsd
            seop = ('session','schema')
            name = self.get_config_value(seop[0], seop[1])
            self._conf.set(seop[0], seop[1], os.path.join(modul_path,'schemas',name))
            # make copy if need
            new_section = ''
            section = self.config_get_section_connect()
            if section != 'connect':
                new_section = section
                section = 'connect'
            # adjust pathnames
            modul_path,fn = os.path.split(__file__)
            root_path = os.path.normpath(os.path.join(modul_path,'certificates'))
            self._conf.set(section, 'dir', root_path)
            if new_section:
                # copy default values into new connection
                self._conf.add_section(new_section)
                for option in ('host','port','ssl_key','ssl_cert','dir'):
                    self.copy_default_options(new_section, section, option)
        return ok 

    def __is_config_option__(self, section, option):
        'Returns if exists key in config.'
        ret = False
        if self._conf.has_section(section):
            ret = self._conf.has_option(section, option)
        return ret

    def get_config_value(self, section, option, omit_errors=0, is_int=None):
        'Get value from config and catch exceptions.'
        value=None
        if not self._conf: return value
        try:
            value = self._conf.get(section,option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.InterpolationMissingOptionError), msg:
            if not omit_errors: self.append_error('ConfigError: %s (%s, %s)'%(msg,section,option))
        if is_int:
            if value is None:
                value = 0
            else:
                try:
                    value = int(value)
                except ValueError, msg:
                    self.append_error('Config ${BOLD}%s:${NORMAL} %s.'%(option,msg))
        return value

    def save_confing(self):
        'Save conf file.'
        filepath = os.path.join(os.path.expanduser('~'),translate.config_name)
        try:
            fp = open(filepath,'w')
            self._conf.write(fp)
            fp.close()
            self.append_note(_T('Default config file saved. For more see help.'))
            self.append_note(filepath,'GREEN')
        except IOError, (no, msg):
            self.append_error('%s: [%d] %s'%(_T('Impossible saving conf file. Reason'),no,msg))

    def config_get_section_connect(self):
        'Set section name "connect" in config.'
        if self._session[NAME]:
            section = 'connect_%s'%self._session[NAME]
        else:
            section = 'connect'
        return section

    def __config_defaults__(self):
        'Set config defaults.'
        section = self.config_get_section_connect()
        if self._conf.has_section(section):
            if not self.__is_config_option__(section, 'timeout'):
                self._conf.set(section, 'timeout','0.0')
        
    def load_config(self, session=''):
        "Load config file and init internal variables. Returns 0 if fatal error occured."
        if not self._conf:
            self.append_error(translate.config_error)
            self.display() # display errors or notes
            return 0 # fatal error
        if session: self._session[NAME] = session # API definition of --session parameter.
        # set session variables
        section = 'session'
        if not self._conf.has_section(section):
            if not self.__create_default_conf__():
                self.append_error(_T('Fatal error: Create default config failed.'))
                self.display() # display errors or notes
                return 0 # fatal error
        # default values (timeout)
        self.__config_defaults__()
        # for login with no parameters
        section = self.config_get_section_connect()
        section_epp_login = 'epp_login'
        self.copy_default_options(section_epp_login, section, 'username')
        self.copy_default_options(section_epp_login, section, 'password')
        # overwrite from options (command line)
        if self._conf.has_section(section_epp_login):
            if self._options['user']: self._conf.set(section_epp_login,'username',self._options['user'])
            if self._options['password']: self._conf.set(section_epp_login,'password',self._options['password'])
        # session
        section = 'session'
        self._session[POLL_AUTOACK] = {False:0,True:1}[self.get_config_value(section,'poll_ack').lower() == 'on']
        self._session[CONFIRM_SEND_COMMAND] = {False:0,True:1}[self.get_config_value(section,'confirm_send_commands').lower() == 'on']
        self._session[VALIDATE] = {False:0,True:1}[self.get_config_value(section,'validate').lower() == 'on']
        colors = self.get_config_value(section,'colors',1)
        if colors:
            self._session[COLORS] = (0,1)[colors.lower() == 'on']
            colored_output.set_mode(self._session[COLORS])
        self.__init_verbose__(self.get_config_value(section,'verbose',1))
        # init vrom command line options
        self.init_options()
        return 1 # OK

    def __init_verbose__(self, verbose):
        'Init verbose mode.'
        if verbose:
            try:
                verbose = int(verbose)
                if verbose in (1,2,3):
                    self._session[VERBOSE] = verbose
                else:
                    self.append_error(_T('Verbose mode can be set only to 1 or 2 or 3.'))
            except ValueError, msg:
                self.append_error('Verbose ValueError: %s'%msg)

    #---------------------------
    # validation
    #---------------------------
    def check_validator(self):
        'Check if exists external validator (xmllint).'
        if not self._session[VALIDATE]: return # validate is set OFF
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
                uerr = errors.decode(translate.encoding)
            except UnicodeDecodeError:
                uerr = repr(errors)
            self.append_note(uerr)
            self._session[VALIDATE] = 0 # validator is automaticly switched off
            self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
        return ok
    
    def is_epp_valid(self, message):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._session[VALIDATE]: return '' # validace je vypnutá
        tmpname = os.path.join(os.path.expanduser('~'),'eppdoc_tmp_test_validity.xml')
        try:
            open(tmpname,'w').write(message)
        except IOError, (no, msg):
            try:
                msg = msg.decode(translate.encoding)
            except UnicodeDecodeError, error:
                msg = '(UnicodeDecodeError) '+repr(msg)
            self._session[VALIDATE] = 0 # automatické vypnutí validace
            self.append_note('%s: [%d] %s'%(_T('Temporary file for verify XML EPP validity cannot been created. Reason'),no,msg))
            self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
            return '' # impossible save xml file needed for validation
        # kontrola validity XML
        schema_path = self.get_config_value('session','schema')
        if not schema_path:
            os.unlink(tmpname)
            return '' # schema path is not set
        try:
            pipes = os.popen3('xmllint --noout --schema "%s" "%s"'%(schema_path, tmpname))
        except IOError, msg:
            self.append_note(str(msg),('RED','BOLD'))
        errors = pipes[2].read()
        map(lambda f: f.close(), pipes)
        os.unlink(tmpname)
        if re.search(' validates$', errors):
            errors = '' # it seems be OK...
        else:
            if re.search('command not found',errors) \
                or re.search(u'není názvem vnitřního ani vnějšího příkazu'.encode('cp852'),errors) \
                or re.search('Schemas parser error',errors):
                # schema missing!
                self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
                self._session[VALIDATE] = 0 # automatické vypnutí validace
                errors=''
        return errors

def append_with_colors(list_of_messages, msg, color):
    "Used by Manager::append_error() and Manager::append_note() functions"
    if color:
        if type(color) in (list, tuple):
            c = ''.join(['${%s}'%c for c in color])
        else:
            c = '${%s}'%(color or 'WHITE') # default color
        list_of_messages.append('%s%s${NORMAL}'%(c,msg))
    else:
        list_of_messages.append(msg)

def join_unicode(u_list, sep='\n'):
    'Convert str objects to unicode and catch errors.'
    out=[]
    for row in u_list:
        if type(row) == str:
            try:
                row = row.decode(translate.encoding)
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
            ltext = text.encode(translate.encoding)
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
            text = text.decode(translate.encoding)
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

