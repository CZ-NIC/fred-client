# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
# Tento modul je správce EPP dokumentu. Správce přijímá vstupní údaje,
# ověří je a pak si z nich nechá sestavit EPP dokument.
# Správce se stará o session data, která získal od serveru.
# Přijaté EPP odpovědi od serveru si správce nechá rozložit na hodnoty
# a ty pak zobrazí v nějakém vybraném formátu.
# Zobrazuje help. Přepíná jazykovou verzi.
#
import re
import time
import random
from gettext import gettext as _T
import eppdoc
import client_eppdoc
import client_eppdoc_test
import client_socket
import pprint, cStringIO
import os, commands, dircache # jen pro testování. v ostré verzi to nebude
import terminal_controler

"""Usage:

import epplib
client = epplib.client_session.Manager()
xml_epp_doc = client.create_eppdoc("hello")
print 'NOTES:',client.fetch_notes()
print 'ERRORS:',client.fetch_errors()
print 'XMLEPP:',xml_epp_doc
if xml_epp_doc:
    if client.connect():
        client.send(xml_epp_doc)
        answer = client.receive()
        client.process_answer(answer)
        client.close()
"""

#------------------------------------
# default connection to server
#------------------------------------
# host, port, (private key, certificate (public) key)
default_connecion = ('curlew',700,('client.key','client.crt'))

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE,CMD_ID,LANG = range(3)
# názvy sloupců pro defaultní hodnoty
DEFS_LENGTH = 4
VERSION,LANGS,objURI,PREFIX = range(DEFS_LENGTH)
SEPARATOR = '-'*60
TEST, COLOR = 1,1
ANSW_RESPONSE, ANSW_RESULT, ANSW_CODE, ANSW_MSG = range(4)

# Colored output
colored_output = terminal_controler.TerminalController()

class Manager:
    """EPP client support.
    Hold client ID, login, clTRID and other session variables.
    Parse command line and call EPP builder.
    """
    def __init__(self):
        self._epp_cmd = client_eppdoc.Message()
        self._epp_response = client_eppdoc.Message()
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        # Typ očekávané odpovědi serveru. Zde si Manager pamatuje jaký příkazy
        # odeslal a podle toho pak zařadí návratové hodnoty.
        self._command_sent = ''
        self._validate = 1 # automatické zapnutí validace EPP XML dokumentů
        #-----------------------------------------
        # Session data:
        #-----------------------------------------
        self._session = [0, 0, 'en'] # hodnoty vytvořené při sestavení session (ID, lang,...)
        # defaults
        self.defs = ['']*DEFS_LENGTH
        self.defs[VERSION] = '1.0'
        self.defs[LANGS] = ('en','cz') # seznam dostupných jazyků
        self.defs[objURI] = 'urn:ietf:params:xml:ns:obj1'
        self.defs[PREFIX] = '' # pro každé sezení nový prefix
        # buffer
        self._raw_cmd = None # XML EPP příkaz odeslaný serveru
        self._raw_answer = None # XML EPP odpověd serveru
        self._dict_answer = None # dict - slovník vytvořený z XML EPP odpovědi
        
    def get_errors(self, sep='\n'):
        return sep.join(self._errors)

    def append_error(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._errors, msg, color)

    def append_note(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._notes, msg, color)

    def fetch_errors(self, sep='\n'):
        msg = sep.join(self._errors)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        msg = sep.join(self._notes)
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
            print colored_output.render(self.fetch_notes())
        if self.is_error():
            # chybová hlášení
            print colored_output.render('${MAGENTA}')
            print colored_output.render(self.fetch_errors())
            print colored_output.render('${NORMAL}')

    def set_validate(self, cmd):
        "Set feature of the manager - it will or not validate EPP documents. cmd='validate on/off'"
        if re.match('validate$',cmd):
            # jen zobrazení stavu
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Status: Validation is'),('OFF','ON')[self._validate]))
        else:
            # změna stavu
            self._validate = (1,0)[re.match('validate\s+on',cmd, re.I)==None]
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Validation is set'),('OFF','ON')[self._validate]))

    def __put_raw_into_note__(self,data):
        "Use pprint for displaying structured data (dict, XML-EPP)."
        if data == None:
            self.append_note(_T('No data'),('RED','BOLD'))
        elif type(data) == dict:
            # Parsed data into dict
##            sio = cStringIO.StringIO()
##            pprint.pprint(data, sio)
##            sio.reset()
##            self.append_note(sio.read(),'GREEN')
            self.append_note(eppdoc.prepare_for_display(data,COLOR))
        else:
            # XML EPP doc
            edoc = client_eppdoc.Message()
            edoc.parse_xml(data)
            if self._epp_response.is_error():
                # při parsování se vyskytly chyby
                self.append_note(edoc.get_errors(),'GREEN')
            else:
                self.append_note(edoc.get_xml(),'GREEN')
        
    #---------------------------------
    # funkce pro nastavení session
    #---------------------------------
    def __logout_session__(self):
        "Set internal session variables in the ID session."
        if self._session[ONLINE]:
            # odlogování
            self._session[ONLINE] = 0 # reset pořadí příkazů
            self._lorry.close() # zrušení konexe na server

    def __check_is_connected__(self):
        "Control if you are still connected."
        if self._lorry and not self._lorry.is_connected():
            # spojení spadlo
            if self._session[ONLINE]: self.append_note('--- %s ---'%_T('Connection broken'))
            self.__logout_session__()

            
    def __command_sent__(self, message):
        "Save EPP command type for recognize server answer."
        # manager si zapamatuje jakého typu příkaz byl a podle toho 
        # pak pracuje s hodnotami, které mu server vrátí
        # Tady se typ musí vytáhnout přímo z XML, jiná možnost není. 
        # Protože lze posílat i XML již vytvořené dříve nebo z jiného programu.
        epp_xml = client_eppdoc.Message()
        epp_xml.parse_xml(message)
        self._command_sent = epp_xml.get_epp_command_name()

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
${BOLD}traw-c${NORMAL}[ommand] e[pp]/[dict] ${CYAN}# display raw command${NORMAL} instead of raw you can also type ${BOLD}src{NORMAL}
${BOLD}raw-a${NORMAL}[nswer] e[pp]/[dict]   ${CYAN}# display raw answer${NORMAL}
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

    #==================================================
    #
    #    Transfer functions
    #    funkce pro komunikaci se socketem
    #
    #==================================================
    def connect(self, data=None):
        "Connect transfer socket. data=('host',port,'client-type')"
        if self.is_connected(): return 1 # spojení je již navázáno
        self._lorry = client_socket.Lorry()
        self._lorry._notes = self._notes
        self._lorry._errors = self._errors
        self._lorry.handler_message = self.process_answer
        if not data: data = default_connecion # default connection
        if self._lorry.connect(data):
            epp_greeting = self._lorry.receive() # receive greeting
            self.__check_is_connected__()
            if epp_greeting:
                self.process_answer(epp_greeting)
                return 1
        return 0
        
    def close(self):
        "Close connection with server."
        if self._lorry:
            self._lorry.close()
            self._lorry = None
        # když se spojení zrušilo, tak o zalogování nemůže být ani řeči
        self._session[ONLINE] = 0

    def is_connected(self):
        "Check if the manager is connected."
        return self._lorry and self._lorry.is_connected()
        
    def send(self, message):
        "Send message to server."
        ret = 0
        self._raw_cmd = message
        if self._lorry:
            ret = self._lorry.send(message)
            if ret:
                # pokud se podařilo dokument odeslat, tak si manager zapamatuje
                # jakého typu příkaz byl a podle toho pak pracuje s hodnotami,
                # které mu server vrátí
                self.__command_sent__(message)
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    def send_logout(self):
        'Send EPP logout message.'
        if not self._session[ONLINE]: return # session zalogována nebyla
        self._epp_cmd.assemble_logout((self.__next_clTRID__(),))
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            self.append_note(_T('Send logout'))
            self.send(epp_doc)          # odeslání dokumentu na server
            answer = self.receive()     # příjem odpovědi
            self.process_answer(answer) # zpracování odpovědi
        else:
            self.append_error(self._epp_cmd.get_errors())
            
    def receive(self):
        "Receive message from server."
        ret = ''
        if self._lorry:
            ret = self._lorry.receive()
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    #==================================================
    #
    # funkce pro uložení hodnot z odpovědi od serveru
    # process_answer() -> answer_response() -> answer_response_result()
    #                  -> answer_greeting()
    #
    #==================================================
    def __append_note_from_dct__(self,dict,cols):
        """Append columns values from dict to note stack.
        cols = ('column-name','column-name','column-name attr-name attr-name','node')
        """
        for column_name in cols:
            lcol = column_name.split(' ')
            if len(lcol)>1:
                value = eppdoc.get_dct_value(dict, lcol[0])
                attr = []
                for a in lcol[1:]:
                    attr.append('\t${BOLD}%s${NORMAL}\t%s'%(a,eppdoc.get_dct_attr(dict, lcol[0], a)))
                self.append_note('${BOLD}%s${NORMAL}\t%s\n%s'%(lcol[0],value,','.join(attr)))
            else:
                self.append_note('${BOLD}%s${NORMAL}\t%s'%(column_name,eppdoc.get_dct_value(dict, column_name)))

    def __response_msg__(self, data, label):
        "Shared for many answers. data=(response,result,code,msg)"
        self.append_note('${BOLD}%s${NORMAL} ${%s}%s${NORMAL}'%(label, ('RED','GREEN')[data[ANSW_CODE] == '1000'], data[ANSW_MSG]))

    def __code_isnot_1000__(self, data, label):
        """Append standard message if answer code is not 1000.
        Returns FALSE - code is 1000; TRUE - code is NOT 1000;
        """
        if data[ANSW_CODE] != '1000':
            self.__response_msg__(data, label)
        return data[ANSW_CODE] != '1000'
        
    def answer_greeting(self, dict_answer):
        "Part of process answer - parse greeting node."
        greeting = dict_answer['greeting']
        self.append_note(SEPARATOR)
        self.append_note(_T('Greeting message incomming'),('GREEN','BOLD'))
        self.defs[LANGS] = eppdoc.get_dct_value(greeting, ('svcMenu','lang'))
        if type(self.defs[LANGS]) in (str,unicode):
            self.defs[LANGS] = (self.defs[LANGS],)
        self.append_note('%s: %s'%(_T('Available language versions'),', '.join(self.defs[LANGS])))
        self.append_note('%s objURI:\n\t%s'%(_T('Available'),eppdoc.get_dct_value(greeting, ('svcMenu','objURI'),'\n\t')))

    def answer_response_logout(self, data):
        "data=(response,result,code,msg)"
        self.append_note(data[ANSW_MSG])
        self.append_note(_T('You are loged out of the private area.'))
        self.__logout_session__()

    def answer_response_login(self, data):
        "data=(response,result,code,msg)"
        self.append_note(data[ANSW_MSG])
        if data[ANSW_CODE] == '1000':
            self._session[ONLINE] = 1 # indikátor zalogování
            self._session[CMD_ID] = 1 # reset - první command byl login
            self.append_note('*** %s ***'%_T('You are logged on!'),('GREEN','BOLD'))
            self.append_note('${BOLD}${GREEN}%s${NORMAL}\n%s'%(_T("Available EPP commands:"),", ".join(self._available_commands)))
        else:
            self.append_note('--- %s ---'%_T('Login failed'),('RED','BOLD'))

    def answer_response_contact_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:contact'): return
        try:
            resData = data[ANSW_RESPONSE]['response']['resData']
            contact_infData = resData['contact:infData']
            contact_postalInfo = contact_infData['contact:postalInfo']
            contact_disclose = contact_infData['contact:disclose']
        except KeyError, msg:
            self.append_error('answer_response_contact_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(contact_infData,
                ('contact:id','contact:roid','contact:status s'))
            self.append_note('${BOLD}contact:postalInfo${NORMAL} %s'%('-'*20))
            self.__append_note_from_dct__(contact_postalInfo,('contact:name','contact:org'))
            contact_addr = contact_postalInfo.get('contact:addr',None)
            if contact_addr:
                self.__append_note_from_dct__(contact_addr,('contact:street','contact:city','contact:cc'))
            self.append_note('-'*40)
            self.__append_note_from_dct__(contact_infData,('contact:email','contact:crID','contact:crDate','contact:upID','contact:upDate'))
            contact_disclose = contact_infData.get('contact:disclose',None)
            if contact_disclose:
                self.__append_note_from_dct__(contact_disclose,('contact:name','contact:org','contact:addr','contact:voice','contact:fax','contact:email'))

    def answer_response_domain_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:domain'): return
        try:
            resData = data[ANSW_RESPONSE]['response']['resData']
            domain_infData = resData['domain:infData']
        except KeyError, msg:
            self.append_error('answer_response_domain_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(domain_infData,
                ('domain:name','domain:roid','domain:status s','domain:registrant'
                ,'domain:contact type','domain:nsset','domain:clID','domain:crID'
                ,'domain:crDate','domain:exDate','domain:upID'))

    def answer_response_nsset_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:nsset'): return
        try:
            resData = data[ANSW_RESPONSE]['response']['resData']
            nsset_infData = resData['nsset:infData']
            nsset_ns = nsset_infData['nsset:ns']
        except KeyError, msg:
            self.append_error('answer_response_nsset_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(nsset_infData,('nsset:id','nsset:roid','nsset:clID','nsset:crID'
                ,'nsset:crDate','nsset:upID','nsset:trDate','nsset:authInfo'))
            self.append_note('${BOLD}nsset:ns${NORMAL} %s'%('-'*20))
            if type(nsset_ns) == list:
                for item in nsset_ns:
                    self.__append_note_from_dct__(item,('nsset:name','nsset:addr'))
            else:
                self.__append_note_from_dct__(nsset_ns,('nsset:name','nsset:addr'))

    def answer_response(self, dict_answer):
        "Part of process answer - parse response node."
        display_src = 1 # Má se odpověd zobrazit celá? 1-ano, 0-ne
        response = dict_answer.get('response',None)
        if response:
            result = response.get('result',None)
            if result:
                fnc_name = 'answer_response_%s'%self._command_sent.replace(':','_')
                if hasattr(self,fnc_name):
                    getattr(self,fnc_name)((dict_answer, result, eppdoc.get_dct_attr(result,(),'code'), eppdoc.get_dct_value(result,'msg')))
                    display_src = 0 # Odpověd byla odchycena, není potřeba ji zobrazovat celou.
                else:
                    # odpovědi na ostatní příkazy
                    self.append_note('%s: %s'%(_T('Server response'),self._command_sent),('GREEN','BOLD'))
            else:
                self.append_note(_T('Missing result in the response message.'),('RED','BOLD'))
        else:
            self.append_note(_T('Unknown server response:'),('RED','BOLD'))
        if display_src:
            # Pokud odpověd neodchytila žádná funkce, tak se odpověd zobrazí celá.
            self.__put_raw_into_note__(dict_answer)

    def process_answer(self, epp_server_answer):
        'Main function. Process incomming EPP messages. This funcion is called by listen socket.'
        if epp_server_answer:
            self._raw_answer = epp_server_answer
            # create XML DOM tree:
            self._epp_response.reset()
            self._epp_response.parse_xml(epp_server_answer)
            if self._epp_response.is_error():
                # při parsování se vyskytly chyby
                self.append_error(self._epp_response.get_errors())
            else:
                # validace
                #FIXME: Někde se to odlogovává, když neprojde validace :-(
                invalid_epp = self.is_epp_valid(self._epp_response.get_xml())
                if invalid_epp:
                    # když se odpověd serveru neplatná...
                    self.append_note(_T('Server answer is not valid!'),('RED','BOLD'))
                    self.append_note(invalid_epp)
            if not self._epp_response.is_error():
                # když přišla nějaká odpověd a podařilo se jí zparsovat:
                self._dict_answer = self._epp_response.create_data()
                if self._dict_answer.get('greeting',None):
                    self.answer_greeting(self._dict_answer)
                elif self._dict_answer.get('response',None):
                    self.answer_response(self._dict_answer)
                else:
                    self.append_note(_T('Unknown response type:'),('RED','BOLD'))
                    self.__put_raw_into_note__(self._dict_answer)
        else:
            self.append_note(_T("No response. EPP Server doesn't answer."))
            self.__logout_session__()
        self.display() # zobrazení všech hlášení vygenerovaných během zpracování

    #==================================================
    def is_epp_valid(self, message):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._validate: return '' # validace je vypnutá
        tmpname='tmp.xml'
        open(tmpname,'w').write(message)
        # kontrola validity XML
        valid = commands.getoutput('xmllint --schema ../mod_eppd/schemas/all-1.0.xsd %s'%tmpname)
        os.unlink(tmpname)
        if valid[-9:]=='validates':
            valid='' # '' = žádné chybové hlášení. Když se vrátí prázdný řetězec, tak je XML validní.
        else:
            if re.search('command not found',valid) \
                or re.search(u'není názvem vnitřního ani vnějšího příkazu'.encode('cp852'),valid): # když příkaz chybí ve Windows XP
                # sh: xmllint: command not found
                self.append_note('%s: %s'%(_T('XML validator is not available'),valid))
                self._validate = 0 # automatické vypnutí validace
                # pokud není validátor k dispozici, tak se to nepovažuje za chybu, 
                # na serveru se data stejně ověřují
                valid=''
            else:
                # odstraní se kopie zdrojového souboru, která je před popisem chyby
                m = re.search('</epp>\s*(.+)',valid,re.I)
                if m: valid = m.group(1)
        return valid

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
        elif re.match('lang\s+\w+',cmd):
            # nastavení zazykové verze
            lang = re.match('lang\s+(\w+)',cmd).group(1)
            if lang in self.defs[LANGS]:
                self._session[LANG] = lang
                self.append_note('%s: "${BOLD}%s${NORMAL}"'%(_T('Session language was set to'),lang))
            else:
                self.append_error('%s: "${BOLD}%s${NORMAL}"'%(_T('Unknown language code'),lang))
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

    def welcome(self):
        msg = u"""
+----------------------------+
|    Vítejte v EPP clientu   |
+----------------------------+
Revision: $Id$
"""
        return msg
        
def append_with_colors(list_of_messages, msg, color):
    "Used by Manager::append_error() and Manager::append_note() functions"
    if type(color) in (list, tuple):
        c = ''.join(['${%s}'%c for c in color])
    else:
        c = '${%s}'%(color or 'YELLOW') # default
    list_of_messages.append('%s%s${NORMAL}'%(c,msg))
        
def count_required_params(params):
    """Returns how many parameters from params list are required:
    IN: ('name','name','[name]','...')
    OUT: (minimum required, maximum allowed)
    Names in bracket are not required.
    If last name is '...', number of required is not known.
    """
    if params[-1]=='...': return (len(params)-1,None)
    return (len([n for n in params if n[0]!='[']), len(params))

def debug_label(text,message=''):
    print '\n'
    print '-'*60
    print '***',text.upper(),'***'
    print '-'*60
    if message: print message

if __name__ == '__main__':
    client = Manager()
    while 1:
        command = raw_input("> (? help, q quit): ")
        if command in ('q','quit','exit','konec'): break
        edoc = client.create_eppdoc(command,TEST)
        client.display()
        if edoc:
            print 'EPP COMMAND:\n%s\n%s'%(edoc,'-'*60)
            if re.match('login',command):
                client._session[ID] = 1 # '***login***' # testovací zalogování
            if re.match('logout',command):
                client._session[ID] = 0 # testovací odlogování
            # client.process_answer(edoc)
            dict_answer = client._epp_cmd.create_data()
            if dict_answer:
                debug_label(u'dict:')
                pprint.pprint(dict_answer)
        print '='*60
    print '[END]'

