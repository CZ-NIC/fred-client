# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, random, math
import dircache # jen pro testování. v ostré verzi to nebude

import eppdoc
import eppdoc_client
from translate import _T, encoding

from session_base import *
from session_transfer import ManagerTransfer, human_readable

from eppdoc import nic_cz_version as eppdoc_nic_cz_version


COLOR = 1
SEPARATOR = '-'*60
OMMIT_ERROR = 1

class ManagerCommand(ManagerTransfer):
    """EPP client support.
    This class manage creations of the EPP documents.
    """

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

    def __parse_command_params__(self, command_name, cmdline, interactive):
        "Check if parameters are valid. Params save into dict for use to assembling EPP document."
        errors, example, stop = self._epp_cmd.parse_cmd(command_name, cmdline, self._conf, interactive, self._session[VERBOSE])
        if errors: self._errors.extend(errors)
        if example: self.append_note('${BOLD}%s:${NORMAL}\n%s'%(_T('Example of input'),example.encode(encoding)))
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
            m = re.match('(raw|src)[-_](a|c)',command_name)
            if m: command_name = 'raw-%s'%('command','answer')[m.group(2)=='a']
            if command_name in ('q','exit'): command_name = 'quit'
            if command_name in self._available_session_commands:
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
        for name,params,explain,ex in self._session_commands:
            if name == command_name:
                notice = explain
                examples = ex
                if len(params):
                    command_line = '%s [param]'%name
                    command_help = '%s: (%s)'%(_T('Available values'),', '.join(params))
                else:
                    command_line = name
                break
        return command_line, command_help, notice, examples

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
            else:
                command_line, command_help, notice, examples = self.__get_help_session_detail__(command_name)
            patt = re.compile("^(\S)",re.MULTILINE)
            patt_sub = "   \\1"
            #
            self.append_note('%s:'%_T('DESCRIPTION'),'BOLD')
            self.append_note('${WHITE}%s${NORMAL}'%patt.sub(patt_sub,notice))
            #
            self.append_note('\n%s:'%_T('SYNTAX'),'BOLD')
            self.append_note('    '+command_line)
            #
            self.append_note('\n%s:'%_T('OPTIONS'),'BOLD')
            self.append_note(patt.sub(patt_sub,command_help))
            #
            self.append_note('\n%s:'%_T('EXAMPLES'),'BOLD')
            self.append_note(patt.sub(patt_sub,'\n'.join(examples)))
            #
            command_name='.'
        return command_name

    def epp_command(self, cmdline):
        'Find EPP command in input and check if is known.'
        command_name = cmdline
        m=re.match('(!)?\s*(\S+)',cmdline)
        if m:
            if m.group(2) in self._available_commands: ## .replace('_','-')
                command_name = m.group(2)
                all_is_OK, stop = self.__parse_command_params__(command_name, cmdline, m.group(1))
                if stop == 2: return 'q' # User press Ctrl+C or Ctrl+D
                if all_is_OK:
                    cmd_params = self._epp_cmd.get_params()
                    if re.match('check_',cmd_params.get('command',[''])[0]):
                        # Save order of names for sorting answer (check_...).
                        self._session[SORT_BY_COLUMNS] = cmd_params.get('name',[])
                    self.create_command_with_params(command_name, cmd_params)
                else:
                    self.append_error(self._epp_cmd.get_errors()) # any problems on the command line occurrs
            else:
                self.append_note('%s: %s'%(_T("Unknown command"),cmdline.encode(encoding)))
                self.append_note('(%s: ${BOLD}help${NORMAL})'%_T('For list all commands type'))
                self._epp_cmd.help_check_name(self._notes, cmdline)
        return command_name

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
        self.reset_round()
        cmd = EPP_command = command.strip()
        # Možnost zadání pomlčky místo podtržítka:
        m = re.match('(\S+)(.*)',cmd)
        if m: EPP_command = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if cmd == '!': cmd = '? !'
        # help
        help, help_item = None,None
        m = re.match('(h(?:elp)?)(?:$|\s+(\S+))',cmd)
        if m:
            help, help_item = m.groups()
        else:
            m = re.match('(\?)(?:$|\s*(\S+))',cmd)
            if m: help, help_item = m.groups()
        if help:
            self.display_help(help_item, command)
        elif re.match('(raw|src)[-_]',cmd):
            # Zobrazení 'surových' dat - zdrojová data
            # raw-cmd; raw-a[nswer] e[pp]; raw-answ [dict]
            m = re.match('(?:raw|src)[-_](\w+)(?:\s+(\w+))?',cmd)
            if m:
                self.append_note(SEPARATOR)
                if m.group(1)[0]=='c' and self._raw_cmd:
                    # zobrazit EPP příkaz, který se poslal serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted command'),'BOLD')
                        edoc = eppdoc_client.Message()
                        edoc.parse_xml(self._raw_cmd)
                        self.__put_raw_into_note__(edoc.create_data())
                    else: # e epp
                        self.append_note(_T('Command source'),'BOLD')
                        self.append_note(human_readable(self._raw_cmd),'GREEN')
                if m.group(1)[0]=='a' and (self._dict_answer or self._raw_answer): # a answer
                    # zobrazit odpověd serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted answer'),'BOLD')
                        self.__put_raw_into_note__(self._dict_answer)
                    else: # e epp
                        self.append_note(_T('Answer source'),'BOLD')
                        self.__put_raw_into_note__(human_readable(self._raw_answer))
        elif re.match('send',cmd):
            self._raw_cmd = ''
            # Posílání již vytvořených souborů na server
            filepath = '.'
            m = re.match('send\s*(\S+)',command)
            if m:
                filepath = m.group(1)
            if os.path.isdir(filepath):
                # zobrazit adresář
                self.append_note('%s: %s'%(_T('Dir list'),filepath))
                try:
                    stuff = dircache.listdir(filepath)
                except OSError, (no, msg):
                    stuff = 'OSError: [%d] %s'%(no, msg)
                self.append_note(str(stuff))
            else:
                command_name, xmldoc = self.load_filename(filepath)
                if command_name == 'login' and not self.is_connected():
                    self.connect() # connect to the host
        # DISABLED
        #elif re.match('connect',cmd):
        #    if self.is_connected():
        #        self.append_note(_T('You are connected already. Type disconnect for close connection.'))
        #    else:
        #        self.connect() # připojení k serveru
        #        command_name = 'connect'
        #elif re.match('disconnect',cmd):
        #    if self.is_connected():
        #        if self.is_online(''):
        #            self.send_logout()
        #        else:
        #            self.close()
        #        self.append_note(_T("You has been disconnected."))
        #    else:
        #        self.append_note(_T("You are not connected."))
        elif re.match('confirm',cmd):
            m = re.match('confirm\s+(\S+)',cmd)
            if m:
                self.set_confirm(m.group(1))
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Confirm is'),{False:'OFF',True:'ON'}[self._session[CONFIRM_SEND_COMMAND]]))
        elif re.match('config\s*(.*)',cmd):
            self.manage_config(re.match('config\s*(.*)',cmd).groups())
        elif re.match('validate',cmd):
            m = re.match('validate\s+(\S+)',cmd)
            if m:
                self._session[VALIDATE] = (0,1)[m.group(1).lower()=='on']
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Validation process is'),{False:'OFF',True:'ON'}[self._session[VALIDATE]]))
        elif re.match('colors',cmd):
            m = re.match('colors\s+(\S+)',cmd)
            if m:
                self._session[COLORS] = (0,1)[m.group(1).lower()=='on']
                colored_output.set_mode(self._session[COLORS])
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Colors mode is'),{False:'OFF',True:'ON'}[self._session[COLORS]]))
        elif re.match('verbose',cmd):
            m = re.match('verbose\s+(\S+)',cmd)
            if m:
                self.__init_verbose__(m.group(1))
            self.append_note('%s: ${BOLD}%d${NORMAL}'%(_T('Verbose mode is'),self._session[VERBOSE]))
        elif re.match('license',cmd):
            body, error = load_file(make_filepath('LICENSE'))
            if error: self.append_error(error)
            if body: self.append_note(self.convert_utf8(body))
        elif re.match('credits',cmd):
            body, error = load_file(make_filepath('CREDITS'))
            if error: self.append_error(error)
            if body: self.append_note(self.convert_utf8(body))
        elif re.match('poll[-_]ack',cmd):
            m = re.match('poll[-_]ack\s+(\S+)',cmd)
            if m:
                self._session[POLL_AUTOACK] = {False:0,True:1}[m.group(1) in ('on','ON')]
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('poll ack is'),{False:'OFF',True:'ON'}[self._session[POLL_AUTOACK]]))
        else:
            # příkazy pro EPP
            cmd = EPP_command
            if type(cmd) != unicode:
                try:
                    cmd = unicode(cmd, encoding)
                except UnicodeDecodeError, msg:
                    self.append_error('UnicodeDecodeError: %s'%msg)
                    cmd = unicode(repr(cmd), encoding)
            command_name = self.epp_command(cmd)
            if command_name != 'q': # User press Ctrl+C or Ctrl+D in interactive mode.
                self._raw_cmd = self._epp_cmd.get_xml()
                self.append_error(self._epp_cmd.fetch_errors()) # any problems on the command line occurrs
        return command_name, self._raw_cmd

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
        try:
            utext = text_utf8.decode('utf-8')
        except UnicodeDecodeError, msg:
            self.append_note('UnicodeDecodeError: %s'%msg)
            utext = ''
        return utext

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
            self.check_validator() # set validator OFF, if not supported.
            # prefix 4 ASCII znaků pro clTRID (pro každé sezení nový)
            self._session[CMD_ID] = 0
            self.defs[PREFIX] = ''.join([chr(random.randint(97,122)) for n in range(4)])
            self._epp_cmd.assemble_login(self.__next_clTRID__(), (eppdoc_nic_cz_version, self.defs[objURI], self.defs[extURI], self._session[LANG]))
            if self._epp_cmd._dct.has_key('username'):
                self._session[USERNAME] = self._epp_cmd._dct['username'][0] # for prompt info

    def get_value_from_dict(self, names, dct = None):
        """Returns safetly value form dict (treat missing keys).
        Parametr names can by str or list ro tuple.
        """
        if dct is None: dct = self._dct_answer
        return eppdoc.get_value_from_dict(dct, names)

    def automatic_login(self, no_outoupt=None):
        'Automatic login if all needed informations are known.'
        if self._session[ONLINE]: return # session is logged on already
        data = self.__get_connect_defaults__()
        if self.get_config_value('session', 'auto_login',OMMIT_ERROR) in ('no','off'): return # prohibited in config
        section_epp_login = 'epp_login'
        data.append(self.get_config_value(section_epp_login, 'username',OMMIT_ERROR))
        data.append(self.get_config_value(section_epp_login, 'password',OMMIT_ERROR))
        # Check if all values are present:
        if not (data[0] # host
            and data[1] # port
            and data[2] # privkey
            and data[3] # cert
            # 4 timeout
            and data[5] # username
            and data[6] # password
            ):
            return # no automatic login, some data missing
        self._epp_cmd.set_params({'username':[data[5]],'password':[data[6]]})
        self.reset_round()
        self.create_login()
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            self.append_note(_T('Login command sent to server'))
            self.send(epp_doc)          # odeslání dokumentu na server
            answer = self.receive()     # příjem odpovědi
            self.process_answer(answer) # zpracování odpovědi
            if not no_outoupt:
                self.display() # display errors or notes
                self.print_answer() # 2. departure from the rule to print answers
        else:
            self.append_error(self._epp_cmd.get_errors())
            self.display() # display errors or notes
            
        
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
    command_name, xml = m.create_eppdoc('create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 (0 d-name "d org." "street number city" +21321313 +734321 info@buzz.com) vat-test ssn-test notify@here.net')
    print m.is_epp_valid(xml)
    print xml
    m.display()
