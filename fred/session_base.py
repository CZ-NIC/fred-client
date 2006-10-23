# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, time
import sys, os, StringIO
import ConfigParser
import terminal_controler
import translate
import internal_variables

# Colored output
colored_output = terminal_controler.TerminalController()

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE, CMD_ID, LANG, POLL_AUTOACK, CONFIRM_SEND_COMMAND, \
   USERNAME, SESSION, HOST, COLORS, VALIDATE, VERBOSE, SORT_BY_COLUMNS, NULL_VALUE, \
   TRANSLATE_ANSWER_COLUMN_NAMES, OUTPUT_TYPE = range(15)
# názvy sloupců pro defaultní hodnoty
DEFS_LENGTH = 4
LANGS,objURI,extURI,PREFIX = range(DEFS_LENGTH)
OMIT_ERROR = 1

OUTPUT_TYPES = ('text','html','php')

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
                '',     # SESSION
                '',     # HOST (for prompt info)
                0,      # COLORS 0/1
                1,      # VALIDATE
                1,      # VERBOSE 1,2,3
                [],     # SORT_BY_COLUMNS - support for sotring received values (used by check_...)
                'NULL', # NULL_VALUE
                1,      # TRANSLATE_ANSWER_COLUMN_NAMES, TEST only
                'text', # OUTPUT_TYPE (text, html)
                ]
        self._external_validator = 'xmllint'
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
        if type(self._options) is not dict:
            self._options = {'lang':'en','colors':'off','verbose':'1','user':'','password':'','host':'',}
        self._email_reports_bug = 'ccreg-devel@lists.nic.cz'
        self._ljust = 23 # indent values from column names in output

    def get_session(self, offset):
        return self._session[offset]

    def init_from_options(self, section_connect):
        'Init variables from options (after loaded config).'
        # connect
        op = self._options
        if op['host']: self._conf.set(section_connect,'host',op['host'])
        if op['port']: self._conf.set(section_connect,'port',op['port'])
        if op['user']: self._conf.set(section_connect,'username',op['user'])
        if op['password']: self._conf.set(section_connect,'password',op['password'])
        if op['cert']: self._conf.set(section_connect,'ssl_cert',op['cert'])
        if op['privkey']: self._conf.set(section_connect,'ssl_key',op['privkey'])
        if op['nologin']: self._conf.set(section_connect,'nologin','nologin')
        # copy variables for individual commands
        section_epp_login = 'epp_login'
        self.copy_default_options(section_epp_login, section_connect, 'username')
        self.copy_default_options(section_epp_login, section_connect, 'password')
        # selection fo language version
        self._session[LANG] = op['lang']
        if op['verbose']:
            self.__init_verbose__(op['verbose'])
        key = op['output'].lower()
        if key:
            self._session[OUTPUT_TYPE] = self.get_valid_output(key)
        if op['no_validate']: self._session[VALIDATE] = 0

    def get_valid_output(self, key):
        'Get valid output type.'
        if not key in OUTPUT_TYPES:
            self.append_error('%s: (%s)'%(_T('Unknown output type. Valid types are'),', '.join(OUTPUT_TYPES)))
            key = self._session[OUTPUT_TYPE]
        return key
        
    def set_auto_connect(self, switch):
        'Set auto connection ON/OFF. switch = 0/1.'
        self._auto_connect = switch==1 and 1 or 0

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
        self._session[CONFIRM_SEND_COMMAND] = type in ('on','ON') and 1 or 0
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
        if msg and self._session[VERBOSE]: print msg

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
            label = '%s:'%_T('ERROR')
            msg.append('%s%s'%(label.ljust(self._ljust), self._errors[0]))
            for text in self._errors[1:]:
                msg.append('%s%s'%(''.ljust(self._ljust), get_ltext(colored_output.render(text))))
            self._errors = []
            msg.append(colored_output.render('${NORMAL}'))
        return sep.join(msg)

    def welcome(self):
        "Welcome message."
        return '%s\n%s\n'%(self.version(),_T('Type "help", "license" or "credits" for more information.'))

    def version(self):
        return 'FredClient 1.0.0' # version of the client

    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[CMD_ID],time.strftime('%y-%m-%dat%H:%M:%S')))

    def set_null_value(self, value):
        'Set string what represents NULL value'
        value = value.strip()
        if len(value):
            if re.search('[- \(\)]',value) or value in ('""',"''"):
                self.append_error('%s null_value: %s. %s'%(_T('Invalid format of'),value,_T('See help for more.')), 'RED')
            else:
                self._session[NULL_VALUE] = value
        else:
            self.append_error('null_value %s. %s'%(_T('cannot be empty'),_T('See help for more.')), 'RED')
        
    #---------------------------
    # config
    #---------------------------
    def manage_config(self, param):
        'Display config values or save config.'
        print_unicode('${BOLD}${YELLOW}%s:${NORMAL}\n\t%s'%(_T('Actual config builded from files'),'\n\t'.join(translate.config_names)))
        if not self._conf:
            print_unicode(_T('No config'))
            return
        selected_section = self.config_get_section_connect()
        for section in self._conf.sections():
            msg = ''
            if section == selected_section:
                msg = '${BOLD}${GREEN}*** %s ***${NORMAL}'%_T('Actual connection HERE')
            print colored_output.render('${BOLD}[%s]${NORMAL} %s'%(section,msg))
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
        try:
            self._conf.readfp(StringIO.StringIO(internal_variables.config))
            ok = 1
        except ConfigParser.ParsingError, msg:
            self.append_error(msg)
        else:
            # schema = all-1.0.xsd
            seop = ('session','schema')
            name = self.get_config_value(seop[0], seop[1])
            if not name:
                self.append_error(_T('Schema in session missing. This is invalid instalation.'))
                return 0
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

    def config_get_section_connect(self):
        'Set section name "connect" in config.'
        if self._session[SESSION]:
            section = 'connect_%s'%self._session[SESSION]
        else:
            section = 'connect'
        return section

    def __config_defaults__(self):
        'Set config defaults.'
        section = self.config_get_section_connect()
        if self._conf.has_section(section):
            if not self.__is_config_option__(section, 'timeout'):
                self._conf.set(section, 'timeout','10.0')
        
    def load_config(self, options=None):
        "Load config file and init internal variables. Returns 0 if fatal error occured."
        # 1. first load values from config
        # 2. overwrite them by options from command line
        if type(options) is dict: self._options = options
        if len(translate.config_names):
            self.append_note('%s %s'%(_T('Using configuration from'), ', '.join(translate.config_names)))
        if translate.config_error:
            self.append_error(translate.config_error)
        self._session[SESSION] = self._options.get('session','') # API definition of --session parameter.
        # set session variables
        section = 'session'
        if not self._conf.has_section(section):
            if not self.__create_default_conf__():
                self.append_error(_T('Fatal error: Default config create failed.'))
                self.display() # display errors or notes
                return 0 # fatal error
        # default values (timeout)
        self.__config_defaults__()
        # for login with no parameters
        section_connect = self.config_get_section_connect()
        if not self._conf.has_section(section_connect):
            self._conf.add_section(section_connect)
            self.append_error(_T('Configuration file has no section "%s".')%section_connect)
            return 0 # fatal error
        # session
        section = 'session'
        self._session[POLL_AUTOACK] = str(self.get_config_value(section,'autoackpoll',OMIT_ERROR)).lower() == 'on' and 1 or 0
        self._session[CONFIRM_SEND_COMMAND] = self.get_config_value(section,'confirm_send_commands').lower() == 'on' and 1 or 0
        self._session[VALIDATE] = self.get_config_value(section,'validate').lower() == 'on' and 1 or 0
        colors = self.get_config_value(section,'colors',OMIT_ERROR)
        if colors:
            self._session[COLORS] = colors.lower() == 'on' and 1 or 0
            colored_output.set_mode(self._session[COLORS])
        self.__init_verbose__(self.get_config_value(section,'verbose',OMIT_ERROR))
        # set NULL value
        value = self.get_config_value(section,'null_value',OMIT_ERROR)
        if value: self.set_null_value(value)
        # init from command line options
        self.init_from_options(section_connect)
        self.check_validator() # set validator OFF, if not supported.
        return 1 # OK

    def set_data_connect(self, dc):
        'Set data for connection: dc = {host: str, port: str, priv_key: str, cert: str, timeout: str }'
        errors = []
        try:
            timeout = float(dc.get('timeout','0.0'))
        except ValueError, msg:
            errors.append('Timeout ValueError: %s'%msg)
        try:
            port = int(dc.get('port','0'))
        except ValueError, msg:
            errors.append('Port ValueError: %s'%msg)
        if not len(errors):
            section = self.config_get_section_connect()
            self._conf.set(section,'port',str(port))
            self._conf.set(section,'timeout',str(timeout))
            if dc.has_key('host'):
                self._options['host'] = dc['host']
            else:
                errors.append(_T('Host name missing.'))
            if not dc.has_key('port'):
                errors.append(_T('Port number missing.'))
            if dc.has_key('cert'):
                self._conf.set(section,'ssl_cert', dc['cert'])
            else:
                errors.append(_T('SSL certificate path missing.'))
            if dc.has_key('priv_key'):
                self._conf.set(section,'ssl_key', dc['priv_key'])
            else:
                errors.append(_T('SSL private key path missing.'))
        return errors
        
    def __init_verbose__(self, verbose):
        'Init verbose mode.'
        if type(verbose) in (str,unicode):
            try:
                verbose = int(verbose)
            except ValueError, msg:
                self.append_error('Verbose ValueError: %s'%msg)
                verbose = 1
        if verbose in (0,1,2,3):
            self._session[VERBOSE] = verbose
        elif verbose is not None:
            self.append_error(_T('Available verbose modes: 1, 2, 3.'))

    def set_verbose(self, verbose):
        'Set verbose mode.'
        self.__init_verbose__(verbose)
        return self._session[VERBOSE]
    
    #---------------------------
    # validation
    #---------------------------
    def set_validate(self, value):
        'Set validate mode in session.'
        self._session[VALIDATE] = value
    
    def check_validator(self):
        'Check if exists external validator (xmllint).'
        if not self._session[VALIDATE]: return # validate is set OFF
        ok = 0
        try:
            pipes = os.popen3(self._external_validator)
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
            self._session[VALIDATE] = 0 # validator is automaticly switched off
            if self._session[VERBOSE] > 1:
                self.append_note(uerr)
                self.append_note(_T('External validator "%s" not found. XML validation has been disabled.')%self._external_validator)
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
            self.append_note('%s: [%d] %s'%(_T('Temporary file for XML EPP validity verification can not been created. Reason'),no,msg))
            self.append_note(_T('Validator has been disabled. Type %s to enable it.')%'${BOLD}validate on${NORMAL}')
            return '' # impossible save xml file needed for validation
        # kontrola validity XML
        schema_path = self.get_config_value('session','schema')
        if not schema_path:
            os.unlink(tmpname)
            return '' # schema path is not set
        try:
            pipes = os.popen3('%s --noout --schema "%s" "%s"'%(self._external_validator, schema_path, tmpname))
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
                self.append_note(get_ltext(errors))
                self.append_note(_T('Validator has been disabled. Type %s to enable it.')%'${BOLD}validate on${NORMAL}')
                self._session[VALIDATE] = 0 # automatické vypnutí validace
                errors=''
        return errors

    def __prepare_help__(self,sc):
        'Prepare for help.'
        content = []
        stt,src = [[n.split(',') for n in x.split(';')] for x in sc]
        chn = colored_output.TERM_SHORTCUTS.split('\n')
        for m,o in stt:
            content.extend(['\n'.join([chn[int(p)] for p in src[int(o)]])]*int(m))
        return content
    
    def __do_help__(self,cont):
        'Make help data'
        clr = ('%s%s%s'%(colored_output.BOL,colored_output.CLEAR_EOL,colored_output.UP))*8
        while 1:
            try:
                for c in cont:
                    print c,'\n[Ctrl+C]'
                    time.sleep(0.2)
                    print clr,
            except KeyboardInterrupt:
                break
        print clr,

    def __display_help__(self, cmd):
        if colored_output.CLEAR_EOL and cmd[5:] == colored_output.get_term_vers():
            self.__do_help__(self.__prepare_help__(terminal_controler.supported_versions))


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

