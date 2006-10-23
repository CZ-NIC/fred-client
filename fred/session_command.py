# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, random, math
import dircache # jen pro testování. v ostré verzi to nebude

import eppdoc
import eppdoc_client
from translate import encoding

from session_base import *
from session_transfer import ManagerTransfer, human_readable

from eppdoc import nic_cz_version as eppdoc_nic_cz_version


COLOR = 1
SEPARATOR = '-'*60

class ManagerCommand(ManagerTransfer):
    """EPP client support.
    This class manage creations of the EPP documents.
    """

    def __init__(self):
        ManagerTransfer.__init__(self)
        # SESSION_COMMANDS: (
        #   (command_name,command_name,command_name)
        #   function
        #   (parameters,parameters)
        #   'Description'
        #   (example, example)
        # )
        self._session_commands = (
            (('!',), None, (_T('command'),'EPP command',), _T('Start the interactive mode of the input command params.'), ('!create_domain',)),
            (('colors',), self.__session_colors__, (_T('switch'),'on','off'), _T('Turn on/off colored output.'), ('colors on',)),
            (('config',), self.manage_config, (), _T('Display or create config file.'), ('config',)),
            (('confirm',), self.__session_confirm__, (_T('switch'),'on','off'), _T('Set on/off confirmation for sending editable commands to the server.'), ('confirm off',)),
            #(('connect',), self.__session_connect__, (), _T('Make connection between client and server without login.'), ()),
            #(('disconnect',), self.__session_disconnect__, (), _T('Disconnect from the EPP server.'), ()),
            (('credits',), self.__session_credits__, (), _T('Display credits.'), ()),
            (('help','h','?'), None, (), _T('Display this help or command details.'), ('help update_nsset','? update_nsset','h update_nsset')),
            (('license',), self.__session_license__, (), _T('Display license.'), ()),
            (('null_value','null'), self.__session_null__, (), _T("""
Set representation of the value what is used to mean nothing. Default is NULL.
This value we use if we want to skip over any column in the command parameters. 
Type NULL means we did not put any value in contrast to '' or "" where we put
value of zero length. See help for more details."""), ('null None','null EMPTY',)),
            (('output',), self.__session_output__, [_T('type')], _T('Display output in type.'), ('output html',)),
            (('autoackpoll',), self.__session_poll_ack__, (_T('switch'),'on','off'), _T('Send "poll ack" straight away after "poll req".'), ('autoackpoll on',)),
            (('quit','q','exit'), None, (), _T('Quit the client. Same effect has "q" or "exit".'), ()),
            (('raw-answer','raw-a','src-answer','src-a'), self.__session_raw_answer__, (_T('switch'),'d','dict',), _T('Display XML source of the EPP answer.'), ('raw-a','raw-a d','src-a','src-a d')),
            (('raw-command','raw-c','src-command','src-c'), self.__session_raw_command__, (_T('switch'),'d','dict',), _T('Display XML source of the EPP command.'), ('raw-c','raw-c d','src-c','src-c d')),
            (('send',), self.__session_send__, (_T('filename'),_T('any filename'),), _T('Send any file to the server. If filename missing command shows actual folder.'), ('send mydoc.xml',)),
            (('validate',), self.__session_validate__, (_T('switch'),'on','off'), _T('Set on/off external validation of the XML documents.'), ('validate off',)),
            (('verbose',), self.__session_verbose__, (_T('switch'),'1','2','3'), _T('Set verbose mode: 1 - brief (default); 2 - full; 3 - full & XML sources.'), ('verbose 2',)),
        )
        self._session_commands[8][2].extend(OUTPUT_TYPES) # Warning! Index 8 must be changed, if any command add.
        # Here is definition of commands  what will not be displayed in the help
        # because we don't make panic to common user.
        # They are used for test or debug only.
        self._hidden_commands = ('answer-cols','hidden','colors','config','null_value','raw-command','raw-answer','send','output')
        self._pattern_session_commands = [] # for recognize command
        self._available_session_commands = [] # for display list of command names
        for n,f,p,e,x in self._session_commands:
            if n[0] not in self._hidden_commands:
                self._available_session_commands.append(n[0])
            self._pattern_session_commands.extend(n)

    def __put_raw_into_note__(self, data):
        "Use pprint for displaying structured data (dict, XML-EPP)."
        if data is None:
            self.append_note(_T('No data'),('RED','BOLD'))
        elif type(data) == dict:
            # Parsed data into dict
            self.append_note(eppdoc.prepare_display(data,COLOR))
        else:
            # XML EPP doc. only for better display
            edoc = eppdoc_client.Message()
            edoc.parse_xml(data)
            if edoc.is_error():
                self.append_note(data,'GREEN') # při parsování se vyskytly chyby
            else:
                self.append_note(edoc.get_xml(),'GREEN')

    def __parse_command_params__(self, command_name, cmdline, interactive=None):
        "Check if parameters are valid. Params save into dict for use to assembling EPP document."
        errors, example, stop = self._epp_cmd.parse_cmd(command_name, cmdline, self._conf, interactive, self._session[VERBOSE], self._session[NULL_VALUE])
        if errors: self._errors.extend(errors)
        if example: self.append_note('${BOLD}%s:${NORMAL}\n%s'%(_T('Command to issue'),example.encode(encoding)))
        return (len(errors) == 0), stop

    def get_default_params_from_config(self, command_name):
        'Returns dict with default parameters from config.'
        return self._epp_cmd.get_default_params_from_config(self._conf, command_name)
    
    #==================================================
    #
    # main creation command functions
    #
    #==================================================
    def display_help(self, command_name, command):
        'Display help (build for display)'
        if command_name:
            # help command
            type = ''
            if command_name in self._pattern_session_commands:
                type = 'session'
            else:
                command_name = command_name.replace('-','_')
                if command_name in self._available_commands:
                    type = 'EPP'
            if type:
                self.__make_help_details__(command_name, type)
            else:
                self.append_note('%s "%s".'%(_T('No help available for'),command_name))
                self.__display_help__(command)
        else:
            # help content
            self.append_note('%s\n\n${BOLD}%s:${NORMAL}\n%s\n\n${BOLD}%s:${NORMAL}\n%s\n\n%s %s'%(
            _T('Type "help command" to get help on particular command.'),
            _T('Available session commands'),
            __make_help_columns__(self._available_session_commands, 2.0),
            _T('Available EPP commands'),
            __make_help_columns__(self._available_commands, 3.0),
            _T('Report bugs to'), self._email_reports_bug
            ))

    def __get_help_session_detail__(self, command_name):
        'Returns set of details of the session command.'
        command_line = command_help = notice = ''
        examples = ()
        for names,func,params,explain,ex in self._session_commands:
            if command_name in names:
                notice = explain
                examples = ex
                command_line = names[0]
                if len(names)>1:
                    command_line += ' (${BOLD}%s:${NORMAL} %s)'%(_T('synonyms'),', '.join(names[1:]))
                if len(params):
                    command_line += ' [%s]'%params[0]
                    command_help = '%s:  %s'%(params[0],', '.join(params[1:]))
                break
        return command_line, command_help, notice, examples

    def __repalce_static_null_examples__(self, examples):
        'Replace static NULL examples to defined variable NULL_VALUE'
        if self._session[NULL_VALUE] != 'NULL':
            ex = []
            for e in examples:
                ex.append(re.sub('NULL',self._session[NULL_VALUE],e))
        else:
            ex = examples
        return ex
        
    def __make_help_details__(self, command_name, type):
        "Make help for chosen command."
        if command_name:
            m = re.match('(\S+)', command_name)
            if m:command_name = m.group(1)
        if command_name:
            # s parametrem - zobrazí se help na vybraný příkaz
            self.append_note('%s: ${BOLD}${GREEN}%s${NORMAL}'%(_T("Help for command"),command_name))
            if type == 'EPP':
                command_line, command_help, notice, examples = self._epp_cmd.get_help(command_name)
                examples = self.__repalce_static_null_examples__(examples)
            else:
                command_line, command_help, notice, examples = self.__get_help_session_detail__(command_name)
            patt = re.compile("^(\S)",re.MULTILINE)
            patt_sub = "    \\1"
            #
            self.append_note('%s:'%_T('DESCRIPTION'),'BOLD')
            self.append_note('${WHITE}%s${NORMAL}'%patt.sub(patt_sub,notice))
            #
            self.append_note('\n%s:'%_T('SYNTAX'),'BOLD')
            self.append_note('    %s'%command_line)
            #
            self.append_note('\n%s:'%_T('OPTIONS'),'BOLD')
            self.append_note(patt.sub(patt_sub,command_help))
            #
            self.append_note('\n%s:'%_T('EXAMPLES'),'BOLD')
            self.append_note(patt.sub(patt_sub,'\n'.join(examples)))
            #
            command_name='.'
        return command_name

    def epp_command(self, cmdline, raw_command):
        'Find EPP command in input and check if is known.'
        command_name = cmdline
        stop = 0
        m=re.match('(!)?\s*(\S+)',cmdline)
        if m:
            if m.group(2) in self._available_commands:
                command_name = m.group(2)
                all_is_OK, stop = self.__parse_command_params__(command_name, cmdline, m.group(1))
                if stop == 2: return 'q',1 # User press Ctrl+C or Ctrl+D
                if all_is_OK:
                    if not stop:
                        # create document if only 'stop' was not occured.
                        cmd_params = self._epp_cmd.get_params()
                        self.create_command_with_params(command_name, cmd_params)
                else:
                    self.append_error(self._epp_cmd.get_errors()) # any problems on the command line occurrs
            else:
                self.append_note('%s: %s'%(_T("Unknown command"),raw_command.encode(encoding)))
                self.append_note('(%s: ${BOLD}help${NORMAL})'%_T('For list all commands type'))
                self._epp_cmd.help_check_name(self._notes, cmdline)
        return command_name, stop

    def is_online(self, command_name):
        'Check if session is online.'
        return self._session[ONLINE] or command_name in ('hello','login')
        
    def create_command_with_params(self, command_name, dct_params):
        "Create EPP command. Check if session is loggend or not."
        # for build example later
        dct_params['command'] = [command_name]
        dct_params[command_name] = [command_name]
        self._epp_cmd.set_params(dct_params) # set params from API (or one's own)
        self._raw_cmd = ''
        if command_name in ('login','hello'):
            getattr(self,'create_%s'%command_name)()
        else:
            # if attr exists had been check in epp_command() or in API module.
            getattr(self._epp_cmd, "assemble_%s"%command_name)(self.__next_clTRID__())

    def create_eppdoc(self, command):
        "Dispatch command line from user and set internal variables or create EPP document."
        command_name = ''
        command_params = ''
        stop = 0
        self.reset_round()
        cmd = EPP_command = session_command = command.strip()
        match = re.match('!+\s+(.+)',cmd)
        if match: cmd = '!%s'%match.group(1) # removing whitespaces after exclamation
        # Možnost zadání pomlčky místo podtržítka:
        m = re.match('(\S+)(.*)',cmd)
        if m:
            EPP_command = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
            session_command = m.group(1)
            command_params = m.group(2)
        if cmd == '!':
            self.append_note(_T('Missing command name. For start interactive mode type command name after exclamation. For mode type help !.'))
            return command_name, self._raw_cmd, 0
        # help
        help, help_item = None,None
        m = re.match('(h(?:elp)?)(?:$|\s+(\S+))',cmd)
        if m:
            help, help_item = m.groups()
        else:
            m = re.match('(\?)(?:$|\s*(\S+))',cmd)
            if m: help, help_item = m.groups()
        # Resolve three command types: 1. help; 2. session command; 3. EPP command
        if help:
            # 1. help
            self.display_help(help_item, command)
        elif session_command in self._pattern_session_commands:
            # 2. Session commands
            for names,func,p,e,x in self._session_commands:
                if session_command in names:
                    if func:
                        name = func(command_params.strip())
                        if name is not None: command_name = name
        elif session_command in self._hidden_commands:
            # undocumented hidden commands for TEST purpose
            if session_command == 'answer-cols':
                self.__session_translate_column_names__(command_params.strip())
            elif session_command == 'hidden':
                self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Hidden commands are'),', '.join(self._hidden_commands)))
        else:
            # 3. EPP commands
            cmd = EPP_command
            if type(cmd) != unicode:
                try:
                    cmd = unicode(cmd, encoding)
                except UnicodeDecodeError, msg:
                    self.append_error('UnicodeDecodeError: %s'%msg)
                    cmd = unicode(repr(cmd), encoding)
            command_name, stop = self.epp_command(cmd, command)
            if command_name != 'q': # User press Ctrl+C or Ctrl+D in interactive mode.
                self._raw_cmd = self._epp_cmd.get_xml()
                self.append_error(self._epp_cmd.fetch_errors()) # any problems on the command line occurrs
        return command_name, self._raw_cmd, stop

    def load_filename(self, filepath):
        'Load file and returs name of EPP command.'
        if os.path.isfile(filepath):
            self.append_note('%s: %s'%(_T('Load file'),filepath))
            self._raw_cmd = self._epp_cmd.load_xml_doc(filepath)
            errors = self._epp_cmd.fetch_errors()
            if errors: self.append_note(errors)
            command_name = self.grab_command_name_from_xml(self._raw_cmd)
        else:
            self.append_note('%s: %s'%(_T('Not found'),filepath))
            command_name = ''
        return command_name, self._raw_cmd

    def convert_utf8(self, text_utf8):
        'Convert str in UTF-8 to unicode.'
        error = utext = ''
        try:
            utext = text_utf8.decode('utf-8')
        except UnicodeDecodeError, msg:
            error = 'UnicodeDecodeError: %s'%msg
        return utext, error

    def get_credits(self):
        'Returs credits'
        body, error = load_file(make_filepath('CREDITS'))
        if error:
            report = error
        else:
            report, error = self.convert_utf8(body)
            if error: report += '\n'+error
        return report
        
        
    #==================================================
    #
    #    Session commands
    #
    #==================================================
    def __session_translate_column_names__(self, param):
        'Set translation of column names in server answer.'
        # TEST only
        if param: self._session[TRANSLATE_ANSWER_COLUMN_NAMES] = re.match('(y(es)?|on|1)',param,re.I) and 1 or 0
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Translation of answer column names is'),self._session[TRANSLATE_ANSWER_COLUMN_NAMES] and 'ON' or 'OFF'))

    def __session_confirm__(self, param):
        'Set confirm value'
        if param:
            self.set_confirm(param)
        else:
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Confirm is'),self._session[CONFIRM_SEND_COMMAND] and 'ON' or 'OFF'))

    def __session_null__(self, param):
        'Set NULL value'
        if param: self.set_null_value(param)
        self.append_note('null_value %s: ${BOLD}%s${NORMAL}'%(_T('is'),self._session[NULL_VALUE]))

    def __session_validate__(self, param):
        'Set validate value'
        if param: self.set_validate(param.lower()=='on' and 1 or 0)
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Validation process is'),self._session[VALIDATE] and 'ON' or 'OFF'))
        
    def __session_connect__(self, param):
        'Run connection process'
        if self.is_connected():
            self.append_note(_T('You are connected already. Type disconnect for close connection.'))
        else:
            self.connect() # připojení k serveru
        return 'connect' # Need for fred_console.py where must be displayed server answer.

    def __session_disconnect__(self, param):
        'Run connection process'
        if self.is_connected():
            if self.is_online(''):
                self.send_logout()
            else:
                self.close()
            self.append_note(_T("You has been disconnected."))
        else:
            self.append_note(_T("You are not connected."))

    def __session_colors__(self, param):
        'Set colors mode'
        if param:
            self._session[COLORS] = param.lower()=='on' and 1 or 0
            colored_output.set_mode(self._session[COLORS])
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Colors mode is'),self._session[COLORS] and 'ON' or 'OFF'))

    def __session_verbose__(self, param):
        'Set verbose mode'
        if param: self.__init_verbose__(param)
        self.append_note('%s: ${BOLD}%d${NORMAL}'%(_T('Verbose mode is'),self._session[VERBOSE]))

    def __session_license__(self, param):
        'Display license'
        body, error = load_file(make_filepath('LICENSE'))
        if error: self.append_error(error)
        if body:
            text, error = self.convert_utf8(body)
            if error: self.append_note(error)
            self.append_note(text)
            

    def __session_credits__(self, param):
        'Display credits'
        body, error = load_file(make_filepath('CREDITS'))
        if error: self.append_error(error)
        if body:
            text, error = self.convert_utf8(body)
            if error: self.append_note(error)
            self.append_note(text)

    def __session_poll_ack__(self, param):
        'Set poll acknowledge'
        if param: self._session[POLL_AUTOACK] = param in ('on','ON') and 1 or 0
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('poll-autoack is'),self._session[POLL_AUTOACK] and 'ON' or 'OFF'))

    def __session_output__(self, param):
        'Set output type'
        if param:
            self._session[OUTPUT_TYPE] = self.get_valid_output(param)
            self.get_valid_output(param)
        self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('output type is'),self._session[OUTPUT_TYPE]))
        
    def __session_send__(self, param):
        'Send any file to the EPP server.'
        command_name = None
        if not param: param = '.'
        if os.path.isdir(param):
            # zobrazit adresář
            self.append_note('%s: %s'%(_T('Dir list'),param))
            try:
                stuff = dircache.listdir(param)
            except OSError, (no, msg):
                stuff = 'OSError: [%d] %s'%(no, msg)
            self.append_note(str(stuff))
        else:
            command_name, xmldoc = self.load_filename(param)
            if command_name == 'login' and not self.is_connected():
                self.connect() # connect to the host
        return command_name

    def __session_raw_answer__(self, param):
        'Display XML answer source.'
        self.append_note(SEPARATOR)
        if param and param[0]=='d': # d dict
            self.append_note(_T('Interpreted answer'),'BOLD')
            self.__put_raw_into_note__(self._dict_answer)
        else: # e epp
            self.append_note(_T('Answer source'),'BOLD')
            self.__put_raw_into_note__(human_readable(self._raw_answer))

    def __session_raw_command__(self, param):
        'Display XML command source.'
        self.append_note(SEPARATOR)
        if param and param[0]=='d': # d dict
            self.append_note(_T('Interpreted command'),'BOLD')
            edoc = eppdoc_client.Message()
            edoc.parse_xml(self._raw_cmd)
            self.__put_raw_into_note__(edoc.create_data())
        else: # e epp
            self.append_note(_T('Command source'),'BOLD')
            self.append_note(human_readable(self._raw_cmd),'GREEN')

        
    #==================================================
    #
    #    EPP commands
    #
    #==================================================
    def create_hello(self):
        'Create EPP document hello'
        if self._auto_connect and not self.is_connected():
            if not self.connect(): return # connect fails
        self._epp_cmd.assemble_hello()

    def create_login(self):
        'Create EPP document login'
        if self._session[ONLINE]:
            # klient je už zalogován
            self.append_note(_T('You are logged already.'))
        else:
            if self._auto_connect and not self.is_connected():
                # commection MUST be created BEFOR assembling login because of tags
                # <objURI> and <extURI>
                if not self.connect(): return # connect fails
            # prefix 4 ASCII znaků pro clTRID (pro každé sezení nový)
            self._session[CMD_ID] = 0
            self.defs[PREFIX] = ''.join([chr(random.randint(97,122)) for n in range(4)])
            self._epp_cmd.assemble_login(self.__next_clTRID__(), (eppdoc_nic_cz_version, self.defs[objURI], self.defs[extURI], self._session[LANG]))
            if self._epp_cmd._dct.has_key('username'):
                self._session[USERNAME] = self._epp_cmd._dct['username'][0] # for prompt info

    #==================================================

    def get_value_from_dict(self, names, dct = None):
        """Returns safetly value form dict (treat missing keys).
        Parametr names can by str or list ro tuple.
        """
        if dct is None: dct = self._dct_answer
        return eppdoc.get_value_from_dict(dct, names)

    def automatic_login(self, no_outoupt=None):
        'Automatic login if all needed informations are known.'
        if self._session[ONLINE]: return 1 # session is logged on already
        data = self.get_connect_defaults()
        if self.get_config_value(self.config_get_section_connect(), 'nologin', OMIT_ERROR): return 1
        section_epp_login = 'epp_login'
        username = self.get_config_value(section_epp_login, 'username',OMIT_ERROR)
        password = self.get_config_value(section_epp_login, 'password',OMIT_ERROR)
        # Check if all values are present:
        missing = []
        if not data[0]: missing.append(_T('host missing'))
        if not data[1]: missing.append(_T('port missing'))
        if not data[2]: missing.append(_T('private key missing'))
        if not data[3]: missing.append(_T('certificate missing'))
        if not username: missing.append(_T('username missing'))
        if not password: missing.append(_T('password missing'))
        if len(missing):
            self.append_error('%s:'%_T('Automatic login stopped'))
            map(self.append_error, missing)
            return 0
        self._epp_cmd.set_params({'username':[username],'password':[password]})
        self.display() # display errors or notes
        ok=0
        self.reset_round()
        self.create_login()
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            if self._session[VERBOSE] > 1: self.append_note(_T('Login command sent to the server'))
            self.send(epp_doc)          # odeslání dokumentu na server
            answer = self.receive()     # příjem odpovědi
            self.process_answer(answer) # zpracování odpovědi
            if not no_outoupt:
                self.display() # display errors or notes
                self.print_answer() # 2. departure from the rule to print answers
            ok = self._dct_answer.get('code',0) == 1000 and 1 or 0
        else:
            self.append_error(self._epp_cmd.get_errors())
            self.display() # display errors or notes
        return ok
            
        
def make_filepath(filename):
    modul_path,fn = os.path.split(__file__)
    return os.path.join(modul_path, filename)

def load_file(filename):
    'Returs body and error if any occurs.'
    body = error = ''
    try:
        body = open(filename).read()
    except IOError, (errnum, msg):
        error = 'IOError: %d. %s (%s)'%(errnum,msg,filename)
    return body, error

def __make_help_columns__(names,fcols,padding=26):
    'Make columns from list of names. Param cols must be float.'
    length = int(math.ceil(len(names)/fcols))
    return '\n'.join([''.join(map(lambda s: s.ljust(padding), names[i::length])) for i in range(length)])


if __name__ == '__main__':
    # Test
    m = ManagerCommand()
    m._session[0]=1 # login simulation
##    command_name, xml, stop = m.create_eppdoc('create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 (0 d-name "d org." "street number city" +21321313 +734321 info@buzz.com) vat-test ssn-test notify@here.net')
    # Test na disclose
    disclose = "(n (org fax email))"
    print 'disclose:',disclose
    command_name, xml, stop = m.create_eppdoc("create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword 'Firma s.r.o.' 'Narodni trida 1230/12' '' 12000 +420.222745111 +420.222745111 %s"%disclose)
    print m.is_epp_valid(xml)
    print xml
    m.display()
