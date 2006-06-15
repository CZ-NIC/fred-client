# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
import time
import random
import dircache # jen pro testování. v ostré verzi to nebude
from gettext import gettext as _T
from client_session_base import *
import client_eppdoc
import client_eppdoc_test

SEPARATOR = '-'*60

class ManagerCommand(ManagerMessage):
    """EPP client support.
    This class manage creations of the EPP documents.
    """

    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[CMD_ID],time.strftime('%y-%m-%dat%H:%M:%S')))
        
    def __create_param__(self, command_name, cmd, parameter_names=(), data=()):
        """Supprot for create_...() functions with more than ONE parameter.
        command_name - name of EPP command
        cmd - parametres of commad
        parameter_names - names of parametres for help and number of required.
                          names in bracket are obligatory
        """
        m = re.match(r'%s\s+(.+)'%command_name, cmd)
        if m:
            min_required, max_allowed = count_required_params(parameter_names)
            params = re.split('\s+',m.group(1)) # rozdělení parametrů příkazu
            if max_allowed and len(params) < min_required:
                # kontrola na požadovaný počet zadaných parametrů
                self.append_note(_T('Function must have at least %d parametres.')%min_required)
            else:
                getattr(self._epp_cmd,'assemble_%s'%command_name)(self.__next_clTRID__(), params, data)
                if self._epp_cmd.is_error(): self._errors.extend(self._epp_cmd.fetch_errors())
        else:
            self.append_note(_T('Error: Parameter missing. Type: %s %s')%(command_name,', '.join(parameter_names)))

    #==================================================
    #
    # main creation command functions
    #
    #==================================================
    def help_command(self, command):
        # Když je dotaz na help
        self.append_note('${BOLD}${GREEN}%s${NORMAL}\n%s'%(_T("Available EPP commands:"),", ".join(self._available_commands)))
        self.append_note(_T("""${BOLD}${GREEN}Session commands:${NORMAL}
${BOLD}connect${NORMAL} (or directly login) ${CYAN}# connect to the server${NORMAL}
${BOLD}lang${NORMAL} cz ${CYAN}# set language${NORMAL}
${BOLD}validate${NORMAL} on/off (or validate for see actual value) ${CYAN}# set validation${NORMAL}
${BOLD}raw-c${NORMAL}[ommand] e[pp]/[dict] ${CYAN}# display raw command${NORMAL} (instead of raw you can also type ${BOLD}src${NORMAL})
${BOLD}raw-a${NORMAL}[nswer] e[pp]/[dict]  ${CYAN}# display raw answer${NORMAL}
"""))

    def epp_command(self, command):
        'Find EPP command in input.'
        cmd=None
        m=re.match('(\S+)',command)
        if m:
            if m.group(1) in self._available_commands:
                self.command_inside_session(m.group(1), command)
            else:
                self.append_note(_T("Unknown EPP command: %s.")%command)

    def command_inside_session(self, cmd, command):
        'Process EPP command inside session.'
        # Příkazy EPP
        # Pokud se příkaz našel, tak se provede pokračuje do stavu 2.
        if self._session[ONLINE] or cmd in ('hello','login'):
##        if 1: # Tady se vypíná kontrola zalogování:
            # když je klient zalogován, tak se volá EPP příkaz
            # výjimky pro příkazy hello a login
            fnc_name = "create_%s"%cmd
            if hasattr(self, fnc_name):
                # Příprava vstupních dat pro příkaz
                getattr(self, fnc_name)(command)
            else:
                # Když příprava vstupních dat pro příkaz chybí
                # To, že daná funkce existuje je již ověřeno
                # přes self._available_commands
                getattr(self._epp_cmd, "assemble_%s"%cmd)((self.__next_clTRID__(),))
            self.append_error(self._epp_cmd.get_errors())
        else:
            self.append_note(_T('You are not logged. You must login before working.\nType login'))

    def create_eppdoc(self, command, is_test=0):
        'Test client result answer.'
        xml_doc = ''
        self._notes = []
        self._epp_cmd.reset()
        cmd = command.strip()
        # Možnost zadání pomlčky místo podtržítka:
        m = re.match('(\S+)(.*)',cmd)
        if m: cmd = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if re.match('^(\?|h|help)$', cmd):
            # help
            self.help_command(cmd)
            # test help
            self.append_note(_T("Available test commands: (\n\t%s\n).")%"\n\t".join(client_eppdoc_test.get_test_help()),'WHITE')
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
                key = re.match('err[-_](.+)',command).group(1)
            xml_doc = self._epp_cmd.load_xml_doc(key,'epplib/testy')
            self.append_error(self._epp_cmd.get_errors())
        elif re.match('connect',cmd):
            self.connect() # připojení k serveru
            self.display()
        elif re.match('validate',cmd):
            self.set_validate(cmd) # set validation of created EPP document
        else:
            # příkazy pro EPP
            self.epp_command(cmd)
            xml_doc = self._epp_cmd.get_xml()
            if xml_doc: invalid_epp = self.is_epp_valid(xml_doc)
            if xml_doc and invalid_epp:
                # Pokud EPP dokument není validní, tak se výstup zruší
                self.append_error(_T('EPP document is not valid'),'BOLD')
                self.append_error(invalid_epp)
                xml_doc=''
        if xml_doc: self._raw_cmd = xml_doc # aby byl k dispozici raw, když se neodešle
        return xml_doc

    #==================================================
    #
    #    EPP commands
    #    funkce, které vytvářejí EPP dokumenty
    #
    #==================================================
    def create_check_contact(self, cmd):
        'Create EPP document check:contact'
        self.__create_param__('check_contact',cmd,(_T('contact-name'),'...'))
    def create_check_domain(self, cmd):
        'Create EPP document check:domain'
        self.__create_param__('check_domain',cmd,(_T('domain-name'),'...'))
    def create_check_nsset(self, cmd):
        'Create EPP document check:nsset'
        self.__create_param__('check_nsset',cmd,(_T('nsset-name'),'...'))
            
    def create_info_contact(self, cmd):
        'Create EPP document info:contact'
        self.__create_param__('info_contact',cmd,(_T('contact-name'),))
    def create_info_domain(self, cmd):
        'Create EPP document info:domain'
        self.__create_param__('info_domain',cmd,(_T('domain-name'),))
    def create_info_nsset(self, cmd):
        'Create EPP document info:nsset'
        self.__create_param__('info_nsset',cmd,(_T('nsset-name'),))

    def create_login(self, cmd):
        'Create EPP document login'
        if self._session[ONLINE]:
            # klient je už zalogován
            self.append_note(_T('You are logged allready.'))
        else:
            # klient se zaloguje
            # prefix 4 ASCII znaků pro clTRID (pro každé sezení nový)
            self.defs[PREFIX] = ''.join([chr(random.randint(97,122)) for n in range(4)])
            self.__create_param__('login', cmd
                ,(_T('login-name'),_T('password'),_T('[new password]'))
                ,(self.defs[VERSION],self.defs[objURI],self._session[LANG]))

def count_required_params(params):
    """Returns how many parameters from params list are required:
    IN: ('name','name','[name]','...')
    OUT: (minimum required, maximum allowed)
    Names in bracket are not required.
    If last name is '...', number of required is not known.
    """
    if params[-1]=='...': return (len(params)-1,None)
    return (len([n for n in params if n[0]!='[']), len(params))

