#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import re, time
import sys, os, StringIO
import ConfigParser
from cgi import escape as escape_html
import terminal_controler
import translate
import session_config
import internal_variables
from subprocess import Popen, PIPE
"""
Class ManagerBase is a part of one Manager object  what provide client session.
This base class owns basic variables and functions needed for manage EPP XML 
document messages. For better orientatiton in the code are functions and data 
parted into several modules whitch every of them does a couple of similar actions.

This base class is aimed for manage configuration file and external application
xmllint for validate results.
Closer descendant is in session_transfer.py
"""
# Colored output
colored_output = terminal_controler.TerminalController()

# The column names for data holding by manager.
ONLINE, CMD_ID, LANG, POLL_AUTOACK, CONFIRM_SEND_COMMAND, \
   USERNAME, SESSION, HOST, COLORS, VALIDATE, VERBOSE, SORT_BY_COLUMNS, \
   NULL_VALUE, SKIP_VALUE, TRANSLATE_ANSWER_COLUMN_NAMES, OUTPUT_TYPE, CLTRID, \
   RECONNECT, ESCAPED_INPUT = range(19)
# The column names for default values
DEFS_LENGTH = 4
LANGS,objURI,extURI,PREFIX = range(DEFS_LENGTH)
OMIT_ERROR = 1

OUTPUT_TYPES = ('text','html','php','xml')

LOOP_NONE, LOOP_FIRST_STEP, LOOP_INSIDE, LOOP_LAST_STEP = range(4)

class ManagerBase:
    """This class holds buffers with error and note messages.
    Class collects messages and prepares them for output.
    """
    def __init__(self, cwd=None):
        self._cwd = cwd
        self._notes = [] # notes or warnings, it are show first, before errors
        self._errors = [] # error messages
        self._notes_afrer_errors = [] # notes witch must be displayed after error messages
        self._sep = '\n' # separator of the messages
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
                'SKIP', # SKIP_VALUE
                1,      # TRANSLATE_ANSWER_COLUMN_NAMES, TEST only
                'text', # OUTPUT_TYPE (text, html)
                None,   # CLTRID
                'yes',  # RECONNECT
                0,      # ESCAPED_INPUT
                ]
        self._external_validator = 'xmllint'
        # defaults
        self.defs = ['']*DEFS_LENGTH
        self.defs[PREFIX] = '' # new prefix for every new session
        self._conf = None ## <ConfigParser object> from session_config.py
        self._auto_connect = 1 # auto connection during login or hello
        self._options = translate.options # parameters from command line
        if type(self._options) is not dict:
            self._options = {'lang':'en','colors':'off','verbose':'1','user':'','password':'','host':'',}
        self._email_reports_bug = 'fred@nic.cz'
        # Used in detailed help:
        self._ljust = 25      # indent description column from names
        self._indent_left = 2 # indent from left border
        self._section_epp_login = 'epp_login' # section name in config for username and password
        # name for home folder; for share (etc) is mofified from this name
        self._config_name = '.%s' % internal_variables.config_name
        self._config_used_files = []
        self._message_missing_config = [] # messages with missing config filenames
        self.run_as_unittest = 0 # it can set variables for unittest: validate server answer
        self._loop_status = LOOP_NONE # indicator of the loop list commands
        self._is_history = 1 # switch for activate/deactivate message history

    def get_cwd(self):
        return self._cwd

    def get_session(self, offset):
        return self._session[offset]
        
    def get_language(self):
        return self._session[LANG]

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
        self.copy_default_options(self._section_epp_login, section_connect, 'username')
        self.copy_default_options(self._section_epp_login, section_connect, 'password')
        if op['verbose']:
            self.parse_verbose_value(op['verbose'])
        key = op['output'].lower()
        if key:
            self._session[OUTPUT_TYPE] = self.get_valid_output(key)
        if op['no_validate']: self._session[VALIDATE] = 0
        self.__init_versions_from_options__(op)
        # We need reconfigure defaults by values fom config or options:
        self.defs[objURI] = self._epp_cmd.get_objURI()
        self.defs[extURI] = self._epp_cmd.get_extURI()
        if op['cltrid']:
            self._session[CLTRID] = op['cltrid']

    def fill_missing_required(self, section_connect):
        'Fill missing required values by defaults.'
        for key in ('port','timeout'):
            if self.get_config_value(section_connect,key,OMIT_ERROR) is None:
                self._conf.set(section_connect,key,str(internal_variables.required_defaults[key]))
        
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
        value = type.upper()
        if value in ('ON','OFF'):
            self._session[CONFIRM_SEND_COMMAND] = value == 'ON' and 1 or 0
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Command confirmation has been set to'),self._session[CONFIRM_SEND_COMMAND] and 'ON' or 'OFF'))
        else:
            self.append_error('%s %s'%(_T('Invalid Command confirmation parametr'),type))
            self._notes_afrer_errors.append(_T("Type 'help confirm' to get more information about confirm commands."))

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

    def fetch_notes_afrer_errors(self, sep='\n'):
        msg = join_unicode(self._notes_afrer_errors, sep)
        self._notes_afrer_errors = []
        return msg

    def is_error(self):
        "Check if any error occurs."
        return len(self._errors)
        
    def is_note(self):
        "Check if any note is in the stack"
        return len(self._notes)

    def get_init_php(self):
        'Get part of PHP code what have to put as a first into output.'
        return """
$fred_client_notes = array();  // notes occuring during communication
$fred_client_errors = array(); // errors occuring during communication
"""
        
    def display(self):
        "Output all messages to stdout or log file."
        msg = self.get_messages()
        if msg and self._session[VERBOSE]: print msg

    def get_messages(self, sep='\n'):
        """Same as display but returns as local string.
        In xml output mode collect only errors.
        """
        #TODO: log file
        msg = []
        is_php = self._session[OUTPUT_TYPE] == 'php'
        is_xml = self._session[OUTPUT_TYPE] == 'xml'
        is_html = self._session[OUTPUT_TYPE] == 'html'
        xml_close_tag = 0

        if is_xml:
            if self.is_note() or self.is_error() or self._notes_afrer_errors:
                msg.append('<?xml version="1.0" encoding="%s"?>'%translate.encoding)
                msg.append('<FredClient>')
                xml_close_tag = 1

        if self.is_note():
            # report, note, values
            if is_xml:
                msg.append('<notes>')
            elif is_html:
                msg.append('<div class="notes">')

            for text in self._notes:
                if is_php:
                    msg.append('$fred_client_notes[] = %s;'%php_string(text))
                elif is_xml:
                    msg.append('\t<note>%s</note>'%strip_colors(text))
                elif is_html:
                    msg.append(escape_html(strip_colors(text)))
                else:
                    msg.append(get_ltext(colored_output.render(text)))
            if is_xml:
                msg.append('</notes>')
            elif is_html:
                msg.append('</div>')
            self._notes = []

        if self.is_error():
            # error messages
            if is_xml:
                msg.append('<errors>')
            elif is_html:
                msg.append('<div class="errors">')

            if is_php:
                msg.append('$fred_client_errors[] = %s;'%php_string(self._errors[0]))
            elif is_xml:
                msg.append('\t<error>%s</error>'%strip_colors(self._errors[0]))
            elif is_html:
                msg.append(escape_html(strip_colors(self._errors[0])))
            else:
                if len(msg) and msg[-1] != '': msg.append('')
                self._errors[-1] += colored_output.render('${NORMAL}')
                label = _T('ERROR')
                msg.append('%s%s: %s'%(colored_output.render('${RED}${BOLD}'),label, self._errors[0]))

            for text in self._errors[1:]:
                if is_php:
                    msg.append('$fred_client_errors[] = %s;'%php_string(text))
                elif is_xml:
                    msg.append('\t<error>%s</error>'%strip_colors(text))
                elif is_html:
                    msg.append(escape_html(strip_colors(text)))
                else:
                    msg.append(get_ltext(text))

            if is_xml:
                msg.append('</errors>')
            elif is_html:
                msg.append('</div>')
            self._errors = []

        if len(self._notes_afrer_errors):
            if is_xml:
                msg.append('<remarks>')
            elif is_html:
                msg.append('<div class="remark">')

            if is_php:
                msg.extend(map(lambda s: '$fred_client_notes[] = %s;'%php_string(s), self._notes_afrer_errors))
            elif is_xml:
                msg.extend(map(lambda s: '\t<remark>%s</remark>'%strip_colors(s), self._notes_afrer_errors))
            elif is_html:
                msg.extend(map(lambda s: escape_html(strip_colors(s)), self._notes_afrer_errors))
            else:
                msg.extend(map(get_ltext, self._notes_afrer_errors))
            self._notes_afrer_errors = []

            if is_xml:
                msg.append('</remarks>')
            elif is_html:
                msg.append('</div>')

        if xml_close_tag:
            msg.append('</FredClient>')
        
        return sep.join(map(get_ltext, msg))

    def welcome(self):
        "Welcome message."
        return '%s\n%s\n'%(self.version(),_T('Type "help", "license" or "credits" for more information.'))

    def version(self):
        return 'FredClient %s'%internal_variables.fred_version # version of the client

    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        if self._session[CLTRID]:
            # if user defines his own identificator
            cltrid = self._session[CLTRID]
            if re.search('%\d*d',cltrid):
                # insert ID client transaction
                cltrid = cltrid%self._session[CMD_ID]
        else:
            cltrid = ('%s%03d#%s'%(self.defs[PREFIX], self._session[CMD_ID], time.strftime('%y-%m-%dat%H:%M:%S')))
        return cltrid

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

    def set_skip_value(self, value):
        'Set string what represents SKIP value'
        value = value.strip()
        if len(value):
            if re.search('[- \(\)]',value) or value in ('""',"''"):
                self.append_error('%s skip_value: %s. %s'%(_T('Invalid format of'),value,_T('See help for more.')), 'RED')
            else:
                self._session[SKIP_VALUE] = value
        else:
            self.append_error('skip_value %s. %s'%(_T('cannot be empty'),_T('See help for more.')), 'RED')

    def skip_element(self, value):
        "True if value is SKIP for skipping EPP element"
        return self._session[SKIP_VALUE] == value

    #---------------------------
    # config
    #---------------------------
    def manage_config(self, param):
        'Display config values or save config.'
        if len(self._config_used_files):
            print_unicode('${BOLD}${YELLOW}%s:${NORMAL}\n\t%s'%(_T('Actual config builded from files'),'\n\t'.join(self._config_used_files)))
        else:
            print_unicode('${BOLD}${RED}%s${NORMAL}'%_T('No configuration file. Defaults used instead it.'))
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

    def __init_versions_from_config__(self, section):
        'Overwrite default schema versions by values from config (if any)'
        pref = 'schema_version_%s'
        for key in self._epp_cmd.get_schema_names(): ## ('contact','nsset','domain','enum','fred','epp'):
            name = pref%key
            value = self.get_config_value(section, name, OMIT_ERROR)
            if value:
                # overwtite schema version
                self._epp_cmd.set_schema_version(key, value)
                self._epp_response.set_schema_version(key, value)
        ## print "CONFIG schema_version:\n",'\n'.join( ['\t%s: %s'%(k,v) for k,v in self._epp_cmd.schema_version.items()])

    def __init_versions_from_options__(self, options):
        """Overwrite default schema versions by values from command line option (if any)
        versions:  contact:1.0,nsset:1.1,domain:1.1
        """
        versions = options.get('versions')
        if not versions: return
        names = self._epp_cmd.get_schema_names()
        for item in versions.split(','):
            data = item.split(':')
            if len(data) == 2:
                key, value = data
                if key in names:
                    # overwtite schema version
                    self._epp_cmd.set_schema_version(key, value)
                    self._epp_response.set_schema_version(key, value)
                else:
                    self.append_error(_T('Invalid version name %s. It must be one from (%s).')%(key, ', '.join(names)))
            else:
                self.append_error('%s: %s'%(_T('Invalid version format'),item))

    def get_actual_username_and_password(self):
        'Returns tuple (username, password) what was used to login'
        return (
            self.get_config_value(self._section_epp_login,'username',OMIT_ERROR),
            self.get_config_value(self._section_epp_login,'password',OMIT_ERROR),
        )

    def get_logins_and_passwords(self, max=1):
        """Returns logins and password for externals (unittest):
        [('username','password'), ...]
        Parameter max means how many logins are returned.
        """
        logins = []
        section  = self.config_get_section_connect()
        # default names are: username, password
        logins.append((self.get_config_value(section, 'username'), self.get_config_value(section, 'password')))
        # next continue: username2, password2
        for n in range(2,max+1):
            username = self.get_config_value(section, 'username%d'%n)
            password = self.get_config_value(section, 'password%d'%n)
            if not (username is None or password is None):
                logins.append((username, password))
        return logins
        

    def get_config_value(self, section, option, omit_errors=0):
        'Get value from config and catch exceptions.'
        value=None
        if not self._conf: return value
        try:
            value = self._conf.get(section,option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.InterpolationMissingOptionError), msg:
            if not omit_errors:
                # disabled text as error type (text ERROR not displayed)
                #self.append_error('ConfigError: %s (%s, %s)'%(msg,section,option))
                self.append_note('Warning: Problem in configuration file. %s (%s, %s)'%(msg,section,option), ('RED','BOLD'))
        return value

    def config_get_section_connect(self):
        'Set section name "connect" in config.'
        if self._session[SESSION]:
            section = 'connect_%s'%self._session[SESSION]
        else:
            section = 'connect'
        return section

    def join_missing_config_messages(self, verbose = None):
        'Join missing config message, if is any.'
        if verbose is None: verbose = self._session[VERBOSE]
        if verbose > 1 and  len(self._message_missing_config):
            self._errors.extend(self._message_missing_config)

    def load_config(self, options=None):
        "Load config file and init internal variables. Returns 0 if fatal error occured."
        oldcwd = os.getcwd()
        if self.get_cwd():
            os.chdir(self.get_cwd())
        # 1. first load values from config
        # 2. overwrite them by options from command line
        #
        # keep options in Manager instance
        if type(options) is dict: self._options = options
        
        if self._options.has_key('command') and len(self._options['command']):
            # Disable writting history in one-command-line mode.
            # It is usefull in cases fred_client is called by php page and
            # it is not privileges for write history.
            self._is_history = 0
            
        # Load configuration file:
        self._conf, self._config_used_files, config_errors, self._message_missing_config =\
                session_config.main(self._config_name, self._options, self._session[VERBOSE], OMIT_ERROR)
        
        language = self._session[LANG]
        # language from environment and configuration file:
        if len(self._options.get('lang','')):
            language = self._options['lang']
        # overwrite config by option from command line:
        if self._options.has_key('lang_option'):
            language = self._options['lang_option']
        
        self.set_language(language) # set translation
        
        if len(self._config_used_files):
            self.append_note('%s %s'%(_T('Using configuration from'), ', '.join(self._config_used_files)))
        if len(config_errors):
            self._errors.extend(config_errors)
            os.chdir(oldcwd)
            return 0 # Errors occured during parsing config. Error of missing file not included!
        self._session[SESSION] = self._options.get('session','') # API definition of --session parameter.
        # set session variables
        section = 'session'
        if not self._conf.has_section(section):
            if not self.__create_default_conf__():
                self.append_error(_T('Fatal error: Default config create failed.'))
                self.display() # display errors or notes
                os.chdir(oldcwd)
                return 0 # fatal error
            if self._options['session'] != '':
                self.append_error(_T('Session "%s" without effect. No configuration file.')%self._options['session'])
                os.chdir(oldcwd)
                return 0
        # for login with no parameters
        section_connect = self.config_get_section_connect()
        if not self._conf.has_section(section_connect):
            self._conf.add_section(section_connect)
            partname = section_connect[8:]
            if partname == '': partname = section_connect
            self.append_error(_T('Configuration file has no section "%s".')%partname)
            os.chdir(oldcwd)
            return 0 # fatal error
        # session
        section = 'session'
        self._session[POLL_AUTOACK] = str(self.get_config_value(section,'poll_autoack',OMIT_ERROR)).lower() == 'on' and 1 or 0
        self._session[CONFIRM_SEND_COMMAND] = self.get_config_value(section,'confirm_send_commands').lower() == 'on' and 1 or 0
        self._session[VALIDATE] = self.get_config_value(section,'validate').lower() == 'on' and 1 or 0
        colors = self.get_config_value(section,'colors',OMIT_ERROR)
        if colors:
            self._session[COLORS] = colors.lower() == 'on' and 1 or 0
            colored_output.set_mode(self._session[COLORS])
        escaped_input = self.get_config_value(section,'escaped_input',OMIT_ERROR)
        if escaped_input:
            self._session[ESCAPED_INPUT] = escaped_input.lower() == 'on' and 1 or 0
        self.parse_verbose_value(self.get_config_value(section,'verbose',OMIT_ERROR))
        # set NULL value
        value = self.get_config_value(section,'null_value',OMIT_ERROR)
        if value: self.set_null_value(value)
        # set SKIP value
        value = self.get_config_value(section,'skip_value',OMIT_ERROR)
        if value: self.set_skip_value(value)
        self.__init_versions_from_config__(section_connect)
        # init from command line options
        self.init_from_options(section_connect)
        self.fill_missing_required(section_connect)
        if self._session[VALIDATE]:
            # set validator OFF, if not supported.
            self.check_validator(1) # 1 - silent (no error message)
        # try get individual for specific connect
        cltrid = self.get_config_value(section_connect, 'cltrid', OMIT_ERROR)
        if not cltrid:
            # shared for all session if individual was not defined
            cltrid = self.get_config_value(section, 'cltrid', OMIT_ERROR)
        if cltrid and len(cltrid):
            self._session[CLTRID] = cltrid
            
        reconnect = self.get_config_value(section, 'reconnect', OMIT_ERROR)
        if reconnect == 'no':
            self._session[RECONNECT] = None
        
        os.chdir(oldcwd)
        return 1 # OK

    def parse_verbose_value(self, verbose):
        'Init verbose mode.'
        if verbose is None: return self._session[VERBOSE]
        nverb = None
        if type(verbose) in (str,unicode):
            try:
                nverb = int(verbose)
            except ValueError, msg:
                self.append_error('%s %s'%(_T('Invalid verbose parametr'),verbose))
                # self.append_error(_T('Valid verbose level is: 1, 2, 3.'))
                self._notes_afrer_errors.append(_T("Type 'help verbose' to get more information about verbose levels."))
                return None
        elif type(verbose) is int: nverb = verbose
        if nverb in (0,1,2,3):
            self._session[VERBOSE] = nverb
        else:
            self.append_error(_T('Verbose level is out of range. Available values are 1, 2, 3.'))
            self._notes_afrer_errors.append(_T("Type 'help verbose' to get more information about verbose levels."))
            nverb = None
        return nverb

    def set_verbose(self, verbose):
        'Set verbose mode.'
        self.parse_verbose_value(verbose)
        return self._session[VERBOSE]

    def remove_notes_from_no_text_ouptut(self):
        """In special output mode (xml, html, php) we don't need display notes.
        """
        if self._session[OUTPUT_TYPE] != 'text' and self._session[VERBOSE] < 2:
            self._notes = []
            self._notes_afrer_errors = []
    
    #---------------------------
    # validation
    #---------------------------
    def set_validate(self, value):
        'Set validate mode in session.'
        self._session[VALIDATE] = value
        if value: self.check_validator()
    
    def check_validator(self, silent=0):
        'Check if exists external validator (xmllint).'
        ok = 0
        try:
            procs = Popen(self._external_validator, shell=True, stdin=PIPE, 
                          stdout=PIPE, stderr=PIPE)
            # pipes: (p.stdin, p.stdout, p.stderr)
            pipes = (procs.stdin, procs.stdout, procs.stderr)
        except IOError, msg:
            self.append_note('check_validator: %s'%str(msg),('RED','BOLD'))
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
            if not silent:
                # appent error to output if only not silent mode
                self.append_note(uerr)
                self.append_note(_T('External validator "%s" not found. XML validation has been disabled.')%self._external_validator)
        return ok

    def __get_actual_schema_path__(self):
        'Returns schema path. Try first in individual connect section than share in session.'
        schema_path = self.get_config_value(self.config_get_section_connect(),'schema',OMIT_ERROR)
        if not schema_path:
            # if schema is not defined for server get share default
            schema_path = self.get_config_value('session','schema')
        if not os.path.isabs(schema_path) and self.get_cwd():
            return os.path.normpath(os.path.join(self.get_cwd(), schema_path))
        return schema_path
    
    def is_epp_valid(self, message, note=''):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._session[VALIDATE]: return '' # validation is disabled
        if message=='':
            return _T('XML document is empty.')
        # check validation of the XML
        schema_path = self.__get_actual_schema_path__()
        if not schema_path: return '' # schema path is not set
        command = '%s --noout --schema "%s" -'%(self._external_validator, schema_path)
        if self._session[VERBOSE] > 2 \
            and self._loop_status == LOOP_NONE \
            and self._session[OUTPUT_TYPE] != 'xml':
            self.append_note(_T('Client-side validation command:'), 'BOLD')
            self.append_note(get_ltext(command))
        try:
            procs = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            # pipes: (p.stdin, p.stdout, p.stderr)
            pipes = (procs.stdin, procs.stdout, procs.stderr)
            pipes[0].write(message)
            pipes[0].close()
        except IOError, msg:
            self.append_note(str(msg),('RED','BOLD'))
        limit = 5 # maximal allowed steps for reading xmllint error result.
        while limit > 0:
            # wait for finishing validation process
            time.sleep(0.2)
            try:
                errors = pipes[2].read()
                break
            except IOError, msg:
                pass
            limit -= 1
        if not limit:
            errors = _T('Reading xmllint errors result failed.')
            if note: errors += self._sep + note
        map(lambda f: f.close(), pipes)
        if re.search(' validates$', errors):
            errors = '' # it seems be OK...
        else:
            # text 'nen\xa1...' is encoded in cp852 and is used for check localized message in MS Windows
            if re.search('command not found',errors) \
                or re.search('nen\xa1 n\xa0zvem vnit\xfdn\xa1ho ani vn\xd8j\xe7\xa1ho p\xfd\xa1kazu',errors) \
                or re.search('Schemas parser error',errors):
                # schema missing!
                self.append_note(_T('Warning: Client-side validation failed.'))
                if self._session[VERBOSE] > 1: self.append_note(get_ltext(errors))
                self._notes_afrer_errors.append(_T("Client-side validation has been disabled. Type '%s' to enable it.")%'${BOLD}validate on${NORMAL}')
                self._session[VALIDATE] = 0 # disable validation automaticly
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

    def check_schemas(self, name, local_obj, server_obj):
        """Check schema version and write diferrences to the standard error list.
        for example:
        name = 'objURI'
        local_obj = self.defs[objURI]
        server_obj = dct['objURI']
        """
        locals, servers  = self.check_schema_versions(local_obj, server_obj)
        if len(locals) or len(servers):
            self.append_error(_T('Different %s schema version.')%name)
            self.append_error(_TP('Client schema version is%s\t%s%sand on the server is%s\t%s','Client schema versions are%s\t%s%sand on the server are%s\t%s',len(locals))%(
                self._sep, ('%s\t'%self._sep).join(locals), 
                self._sep, self._sep, ('%s\t'%self._sep).join(servers))
            )

    def check_schema_versions(self, local_schema, server_schema):
        """Check versions between local and server schemas. Returns differences.
        local_schema / server_schema:
            ['http://www.nic.cz/xml/epp/contact-1.1', 'http://www.nic.cz/xml/epp/domain-1.1',  ... ]
            ['http://www.nic.cz/xml/epp/enumval-1.0']
        server_schema are in unicode
        """
        return (
            [get_ltext(name) for name in local_schema if name not in server_schema], # local names what are not on the server
            [get_ltext(name) for name in server_schema if name not in local_schema], # server names what are not eqal with local version
        )
        

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
    if type(text) is str:
        ltext = colored_output.render(text)
    elif type(text) is int:
        ltext = str(text)
    else:
        # unicode
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

    
def php_string(value):
    'Returns escaped string for place into PHP variable.'
    if type(value) in (str,unicode):
        text = get_ltext(value).strip().replace('\\n', '\n')
        ret = "'%s'" % text.replace(r'\ '[:-1], r'\\ '[:-1]).replace(r"'", r"\'")
    elif type(value) in (list, tuple):
        items=[]
        for n in value:
            items.append(php_string(n))
        ret = 'array(%s)'%', '.join(items)
    else:
        ret = value # int or float
    return ret

def strip_colors(text):
    'Remove ${COLOR} from text'
    return re.sub(r'\$\{[A-Z]+\}', '', text)

def decamell(text):
    'Make camell type text to text with unit separator: nameType -> name_type'
    return re.sub('([A-Z])', '_\\1', text).lower()

    
if __name__ == '__main__':
    mb = ManagerBase()
    mb._conf = ConfigParser.SafeConfigParser()
    mb.__create_default_conf__()
    mb.display()
    for section in mb._conf.sections():
        print '[%s]'%section
        for item in mb._conf.items(section):
            print '\t%s = %s'%item

