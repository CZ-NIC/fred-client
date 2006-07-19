# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
import random
import dircache # jen pro testování. v ostré verzi to nebude

import eppdoc
import eppdoc_client
from translate import _T

from session_base import *
from session_transfer import ManagerTransfer

from eppdoc import nic_cz_version as eppdoc_nic_cz_version


COLOR = 1
SEPARATOR = '-'*60

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
        errors, example = self._epp_cmd.parse_cmd(command_name, cmdline, self._conf, interactive)
        if errors: self._errors.extend(errors)
        if example: self.append_note('${BOLD}%s:${NORMAL}\n%s'%(_T('Example of input'),example))
        return (len(errors) == 0)

    def get_default_params_from_config(self, command_name):
        'Returns dict with default parameters from config.'
        return self._epp_cmd.get_default_params_from_config(self._conf, command_name)
    
    #==================================================
    #
    # main creation command functions
    #
    #==================================================
    def make_help(self, command_name):
        "Make help for chosen command."
        if command_name:
            m = re.match('(\S+)', command_name)
            if m:command_name = m.group(1)
        if command_name and command_name != 'command':
            # s parametrem - zobrazí se help na vybraný příkaz
            self.append_note('%s: ${BOLD}${GREEN}%s${NORMAL}'%(_T("Help for command"),command_name))
            command_line,command_help,notice, examples = self._epp_cmd.get_help(command_name)
            if command_line: self.append_note('%s: %s\n'%(_T('Usage'),command_line))
            if command_help: self.append_note(command_help)
            if notice:       self.append_note('\n${WHITE}%s${NORMAL}'%notice)
            if len(examples): self.append_note('\n${BOLD}%s:${NORMAL}\n%s'%(_T('Examples'),'\n'.join(examples)))
            command_name='.'
        else:
            # bez parametru - zobrazí se přehled helpu
            if command_name == 'command':
                self.append_note(_T('Instead "command" Select one from this list bellow:'))
                command_name='.'
            self.append_note('\n${BOLD}${GREEN}%s:${NORMAL}\n%s'%(_T("Available EPP commands"),", ".join(self._available_commands)))
            self.append_note(_T('Type "?command" (or "h(elp) command") for mode details about parameters.'))
            self.append_note(_T('To start the interactive mode of input the command params type: ${BOLD}!command${NORMAL}'))
            self.append_note(_T('For stop interactive input type ! instead of value (or more "!" for leave sub-scope)'))
        return command_name

    def make_help_session(self, command_name):
        # Když je dotaz na help
        if not command_name or command_name != '.':
            self.append_note(_T("""\n${BOLD}${GREEN}Session commands:${NORMAL}
${BOLD}connect${NORMAL} (or directly login) ${CYAN}# connect to the server (for test only)${NORMAL}
${BOLD}lang${NORMAL} cs ${CYAN}# set language of the incomming server messages. It MUST be set BEFORE send login! Later has no effect.${NORMAL}
${BOLD}validate${NORMAL} [on/off] ${CYAN}# set validation or display actual setting${NORMAL}
${BOLD}poll-ack${NORMAL} [on/off] ${CYAN}# send "poll ack" straight away after "poll req"${NORMAL}
${BOLD}raw-c${NORMAL}[ommand] [xml]/${BOLD}d${NORMAL}[ict] ${CYAN}# display raw command${NORMAL} (instead of raw you can also type ${BOLD}src${NORMAL})
${BOLD}raw-a${NORMAL}[nswer] [xml]/${BOLD}d${NORMAL}[ict]  ${CYAN}# display raw answer${NORMAL}
${BOLD}confirm${NORMAL} ${BOLD}on${NORMAL}/[off]  ${CYAN}# confirm editable commands befor sending to the server${NORMAL}
${BOLD}config${NORMAL} ${CYAN}# display actual config${NORMAL}
${BOLD}config${NORMAL} ${BOLD}create${NORMAL} ${CYAN}# create default config file in user home folder.${NORMAL}
${BOLD}send${NORMAL} [filename] ${CYAN}# send selected file to the server (for test only). If param is not valid file the command shows folder.${NORMAL}
"""))

    def epp_command(self, cmdline):
        'Find EPP command in input and check if is known.'
        command_name = cmdline
        m=re.match('(!)?\s*(\S+)',cmdline)
        if m:
            if m.group(2).replace('_','-') in self._available_commands:
                command_name = m.group(2)
                if self.__parse_command_params__(command_name, cmdline, m.group(1)):
                    self.create_command_with_params(command_name, self._epp_cmd.get_params())
                else:
                    self.append_error(self._epp_cmd.get_errors()) # any problems on the command line occurrs
            else:
                self.append_note(_T("Unknown EPP command: %s.")%cmdline)
                self.append_note('(%s: ${BOLD}help${NORMAL})'%_T('For more type'))
                self._epp_cmd.help_check_name(self._notes, cmdline)
        return command_name

    def is_online(self, command_name):
        'Check if session is online.'
        return self._session[ONLINE] or command_name in ('hello','login')
        
    def create_command_with_params(self, command_name, dct_params):
        "Create EPP command. Check if session is loggend or not."
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
        cmd = command.strip()
        # Možnost zadání pomlčky místo podtržítka:
        m = re.match('(\S+)(.*)',cmd)
        if m: cmd = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        # help
        help, help_item = None,None
        m = re.match('(h(?:elp)?)(?:$|\s+(\S+))',cmd)
        if m:
            help, help_item = m.groups()
        else:
            m = re.match('(\?)(?:$|\s*(\S+))',cmd)
            if m: help, help_item = m.groups()
        if help:
            self.make_help_session(self.make_help(help_item))
        elif re.match('lang(\s+\w+)?',cmd):
            # nastavení zazykové verze
            m = re.match('lang\s+(\w+)',cmd)
            if m:
                lang = m.group(1)
                if lang in self.defs[LANGS]:
                    self._session[LANG] = lang
                    self.append_note('%s: "${BOLD}%s${NORMAL}"'%(_T('Session language was set to'),lang))
                else:
                    self.append_error('%s: "${BOLD}%s${NORMAL}"'%(_T('Unknown language code'),lang))
            else:
                self.append_note('%s: "${BOLD}%s${NORMAL}". %s: %s'%(_T('Session language is'),self._session[LANG],_T('Available values'),str(self.defs[LANGS])))
        elif re.match('(raw|src)[-_]',cmd):
            # Zobrazení 'surových' dat - zdrojová data
            # raw-cmd; raw-a[nswer] e[pp]; raw-answ [dict]
            m = re.match('(?:raw|src)[-_](\w+)(?:\s+(\w+))?',cmd)
            if m:
                self.append_note(SEPARATOR)
                if m.group(1)[0]=='c' and self._raw_cmd:
                    # zobrazit EPP příkaz, který se poslal serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted command'),('GREEN','BOLD'))
                        edoc = eppdoc_client.Message()
                        edoc.parse_xml(self._raw_cmd)
                        self.__put_raw_into_note__(edoc.create_data())
                    else: # e epp
                        self.append_note(_T('Command source'),('GREEN','BOLD'))
                        self.append_note(self._raw_cmd,'GREEN')
                if m.group(1)[0]=='a' and (self._dict_answer or self._raw_answer): # a answer
                    # zobrazit odpověd serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted answer'),('GREEN','BOLD'))
                        self.__put_raw_into_note__(self._dict_answer)
                    else: # e epp
                        self.append_note(_T('Answer source'),('GREEN','BOLD'))
                        self.__put_raw_into_note__(self._raw_answer)
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
                self.append_note(stuff)
            else:
                command_name, xmldoc = self.load_filename(filepath)
        elif re.match('connect',cmd):
            self.connect() # připojení k serveru
        elif re.match('confirm',cmd):
            m = re.match('confirm\s+(\S+)',cmd)
            if m:
                self.set_confirm(m.group(1))
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('Confirm is'),{False:'OFF',True:'ON'}[self._session[CONFIRM_SEND_COMMAND]]))
        elif re.match('config\s*(.*)',cmd):
            self.manage_config(re.match('config\s*(.*)',cmd).groups())
        elif re.match('validate',cmd):
            self.set_validate(cmd) # set validation of created EPP document
        elif re.match('poll[-_]ack',cmd):
            m = re.match('poll[-_]ack\s+(\S+)',cmd)
            if m:
                self._session[POLL_AUTOACK] = {False:0,True:1}[m.group(1) in ('on','ON')]
            self.append_note('%s: ${BOLD}%s${NORMAL}'%(_T('poll ack is'),{False:'OFF',True:'ON'}[self._session[POLL_AUTOACK]]))
        else:
            # příkazy pro EPP
            command_name = self.epp_command(cmd)
            self._raw_cmd = self._epp_cmd.get_xml()
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


if __name__ == '__main__':
    # Test
    m = ManagerCommand()
    m._session[0]=1 # login simulation
    command_name, xml = m.create_eppdoc('create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 (0 d-name "d org." "street number city" +21321313 +734321 info@buzz.com) vat-test ssn-test notify@here.net')
    print m.is_epp_valid(xml)
    print xml
    m.display()
