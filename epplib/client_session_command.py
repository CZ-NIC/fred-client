# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
##import time
import random
import dircache # jen pro testování. v ostré verzi to nebude
from gettext import gettext as _T
from client_session_base import *
from client_session_transfer import ManagerTransfer
import client_eppdoc
import client_eppdoc_test
from eppdoc import nic_cz_version as eppdoc_nic_cz_version

SEPARATOR = '-'*60

class ManagerCommand(ManagerTransfer):
    """EPP client support.
    This class manage creations of the EPP documents.
    """
        
    def __check_EPP_command__(self, command_name, cmdline):
        "Check if parameters are valid."
        errors = self._epp_cmd.parse_cmd(command_name, cmdline)
        if errors: self._errors.extend(errors)
        return (len(errors) == 0)

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
            command_line,command_help,notice = self._epp_cmd.get_help(command_name)
            if command_line: self.append_note('%s: %s\n'%(_T('Usage'),command_line))
            if command_help: self.append_note(command_help)
            if notice:       self.append_note('\n${WHITE}%s${NORMAL}'%notice)
            command_name='.'
        else:
            # bez parametru - zobrazí se přehled helpu
            if command_name == 'command':
                self.append_note(_T('Instead "command" Select one from this list bellow:'))
                command_name='.'
            self.append_note('\n${BOLD}${GREEN}%s:${NORMAL}\n%s'%(_T("Available EPP commands"),", ".join(self._available_commands)))
            self.append_note(_T('Type "help command" for mode details.'))
        return command_name

    def make_help_session(self, command_name):
        # Když je dotaz na help
        if not command_name or command_name != '.':
            self.append_note(_T("""\n${BOLD}${GREEN}Session commands:${NORMAL}
${BOLD}connect${NORMAL} (or directly login) ${CYAN}# connect to the server${NORMAL}
${BOLD}lang${NORMAL} cs ${CYAN}# set language${NORMAL}
${BOLD}validate${NORMAL} on/off (or validate for see actual value) ${CYAN}# set validation${NORMAL}
${BOLD}raw-c${NORMAL}[ommand] e[pp]/[dict] ${CYAN}# display raw command${NORMAL} (instead of raw you can also type ${BOLD}src${NORMAL})
${BOLD}raw-a${NORMAL}[nswer] e[pp]/[dict]  ${CYAN}# display raw answer${NORMAL}
"""))

    def epp_command(self, cmdline):
        'Find EPP command in input.'
        cmd=None
        m=re.match('(\S+)',cmdline)
        if m:
            if m.group(1).replace('_','-') in self._available_commands:
                self.command_inside_session(m.group(1), cmdline)
            else:
                self.append_note(_T("Unknown EPP command: %s.")%cmdline)
                self.append_note('(%s: ${BOLD}help${NORMAL})'%_T('For more type'))
                self._epp_cmd.help_check_name(self._notes, cmdline)

    def command_inside_session(self, command_name, cmdline):
        'Process EPP command inside session.'
        # Příkazy EPP
        # Pokud se příkaz našel, tak se provede pokračuje do stavu 2.
        if self._session[ONLINE] or command_name in ('hello','login'):
##        if 1: # Tady se vypíná kontrola zalogování:
            # když je klient zalogován, tak se volá EPP příkaz
            # výjimky pro příkazy hello a login
            fnc_name = "create_%s"%command_name
            if hasattr(self, fnc_name):
                # Speciální příprava vstupních dat pro příkaz
                getattr(self, fnc_name)(cmdline)
            else:
                if self.__check_EPP_command__(command_name, cmdline):
                    # pokud jsou parametry vpořádku, tak se může vygenerovat EPP command
                    # funkce assemble_...() použije na sestavení dokumentu data uložená ve
                    # slovníku self._epp_cmd._dct_params, kam je uložila funkce self._epp_cmd.parse_cmd()
                    # volaná ve funkci self.__check_EPP_command__()
                    getattr(self._epp_cmd, "assemble_%s"%command_name)(self.__next_clTRID__())
            self.append_error(self._epp_cmd.get_errors())
        else:
            self.append_note(_T('You are not logged. You must login before working.\nType login'))

    def create_eppdoc(self, command, is_test=0):
        "Dispatch command line from user and set internal variables or create EPP document."
        xml_doc = ''
        self._notes = []
        self._epp_cmd.reset()
        cmd = command.strip()
        # Možnost zadání pomlčky místo podtržítka:
        m = re.match('(\S+)(.*)',cmd)
        if m: cmd = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        # help
        m = re.match(r'(?:\?|h(?:elp)?)(?:\s+(.+)|$)', cmd)
        if m:
            command_name = self.make_help(m.group(1))
            self.make_help_session(command_name)
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
                self.append_note('%s: "${BOLD}%s${NORMAL}"'%(_T('Session language is'),self._session[LANG]))
        elif re.match('(raw|src)[-_]',cmd):
            # Zobrazení 'surových' dat - zdrojová data
            # raw-cmd; raw-a[nswer] e[pp]; raw-answ [dict]
            m = re.match('(?:raw|src)[-_](\w+)(?:\s+(\w+))?',cmd)
            if m:
                self.append_note(SEPARATOR)
                if m.group(1)[0]=='c' and self._raw_cmd: # c cmd, command
                    # zobrazit EPP příkaz, který se poslal serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted command'),('GREEN','BOLD'))
                        edoc = client_eppdoc.Message()
                        edoc.parse_xml(self._raw_cmd)
                        self.__put_raw_into_note__(edoc.create_data())
                    else: # e epp
                        self.append_note(_T('Command source'),('GREEN','BOLD'))
                        self.__put_raw_into_note__(self._raw_cmd)
                if m.group(1)[0]=='a' and self._dict_answer: # a answer
                    # zobrazit odpověd serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted answer'),('GREEN','BOLD'))
                        self.__put_raw_into_note__(self._dict_answer)
                    else: # e epp
                        self.append_note(_T('Answer source'),('GREEN','BOLD'))
                        self.__put_raw_into_note__(self._raw_answer)
                self.display()
        elif is_test and re.match('ex[-_]',cmd):
            # TEST Poslání souboru z adresáře examples
            m = re.match('ex[-_](.+)',command)
            if m:
                # odeslat zkušební soubor
                filename = m.group(1)
                try:
                    xml_doc = open('epplib/examples/%s'%filename,'rb').read()
                except IOError, (no, msg):
                    self.append_error('IOError: [%d] %s'%(no, msg))
                self.append_error(self._epp_cmd.get_errors())
            else:
                # vypsat seznam dostupných souborů
                self.append_note('List of examples:')
                self.append_note(dircache.listdir('epplib/examples/'))
                self.display()
        elif is_test and re.match('err[-_]',cmd):
            # TEST Testovací příkazy
            m = re.match('(\S+)',command)
            key = client_eppdoc_test.get_test_key(m.group(1))
            if not key:
                m = re.match('err[-_](.+)',command)
                if m:
                    key = m.group(1)
                    xml_doc = self._epp_cmd.load_xml_doc(key,'epplib/testy')
                    # TODO: proč to neukládá zdroj?
##                    self._command_sent = xml_doc
                else:
                    self.append_note('List of test:')
                    self.append_note(dircache.listdir('epplib/testy/'))
            self.append_error(self._epp_cmd.get_errors())
        elif re.match('connect',cmd):
            self.connect() # připojení k serveru
            self.display()
        elif re.match('validate',cmd):
            self.set_validate(cmd) # set validation of created EPP document
        else:
            # příkazy pro EPP
            self.epp_command(cmd)
            self._raw_cmd = xml_doc = self._epp_cmd.get_xml()
            if xml_doc: invalid_epp = self.is_epp_valid(xml_doc)
            if xml_doc and invalid_epp:
                # Pokud EPP dokument není validní, tak se výstup zruší
                self.append_error(_T('EPP document is not valid'),'BOLD')
                self.append_error(invalid_epp)
                self.append_error(self._raw_cmd,'CYAN')
                self.append_error(_T('Command was NOT sent to EPP server.'),('RED','BOLD'))
                xml_doc=''
        if xml_doc: self._raw_cmd = xml_doc # aby byl k dispozici raw, když se neodešle
        return xml_doc

    #==================================================
    #
    #    EPP commands
    #
    #==================================================
    def create_login(self, cmdline):
        'Create EPP document login'
        if self._session[ONLINE]:
            # klient je už zalogován
            self.append_note(_T('You are logged already.'))
        else:
            # klient se zaloguje
            # prefix 4 ASCII znaků pro clTRID (pro každé sezení nový)
            self.defs[PREFIX] = ''.join([chr(random.randint(97,122)) for n in range(4)])
            if self.__check_EPP_command__('login', cmdline):
                self._epp_cmd.assemble_login(self.__next_clTRID__(), (eppdoc_nic_cz_version, self.defs[objURI], self._session[LANG]))

if __name__ == '__main__':
    # Test
    m = ManagerCommand()
    m._session[0]=1 # login simulation
    xml = m.create_eppdoc('create-contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Long beach" "On the Road") VA 20166-6503 +1.7035555555 +1.7035555556 0 d-name "d org." "Street No. City" +21321313 +734321 info@buzz.com vat-test ssn-test notify@here.net')
    if not m.is_epp_valid(xml):
        print xml
    m.display()
