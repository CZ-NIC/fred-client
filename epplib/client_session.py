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
import client_eppdoc, eppdoc
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
default_connecion = ('curlew',700)

# názvy sloupců pro data sestavené při spojení se serverem
ID,LANG = range(2)
# názvy sloupců pro defaultní hodnoty
DEFS_LENGTH = 4
VERSION,LANGS,objURI,PREFIX = range(DEFS_LENGTH)
SEPARATOR = '-'*60
TEST = 1

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
        self._session = [0, 'en'] # hodnoty vytvořené při sestavení session (ID, lang,...)
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
##        if msg:
##            # color output support
##            if type(color) in (list, tuple):
##                c = ''.join(['${%s}'%c for c in color])
##            else:
##                c = '${%s}'%(color or 'YELLOW') # default
##            self._notes.append('%s%s${NORMAL}'%(c,msg))

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
            sio = cStringIO.StringIO()
            pprint.pprint(data, sio)
            sio.reset()
            self.append_note(sio.read(),'GREEN')
        else:
            # XML EPP doc
            eppdoc = client_eppdoc.Message()
            eppdoc.parse_xml(data)
            if self._epp_response.is_error():
                # při parsování se vyskytly chyby
                self.append_note(eppdoc.get_errors(),'GREEN')
            else:
                self.append_note(eppdoc.get_xml(),'GREEN')
        
    #---------------------------------
    # funkce pro nastavení session
    #---------------------------------
    def __logout_session__(self):
        "Set internal session variables in the ID session."
        if self._session[ID]:
            # odlogování
            self._session[ID] = 0 # reset pořadí příkazů
            self._lorry.close() # zrušení konexe na server

    def __check_is_connected__(self):
        "Control if you are still connected."
        if self._lorry and self._lorry.is_error():
            # spojení spadlo
            if self._session[ID]: self.append_note('--- %s ---'%_T('Connection broken'))
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
        self._session[ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[ID],time.strftime('%y-%m-%dat%H:%M:%S')))
        
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
        if self._session[ID]:
            # klient je už zalogován
            self.append_note(_T('You are logged allready.'))
        else:
            # klient se zaloguje
            # prefix 4 ASCII znaků pro clTRID (pro každé sezení nový)
            self.defs[PREFIX] = ''.join([chr(random.randint(97,122)) for n in range(4)])
            self.__create_param__('login', cmd
                ,(_T('login-name'),_T('password'),_T('[new password]'))
                ,(self.defs[VERSION],self.defs[objURI],self._session[LANG]))
            self._session[ID] = 0 # číslo 1 bude přiřazeno až po úspěšném zalogování

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
${BOLD}traw-c${NORMAL}[ommand] e[pp]/[dict] ${CYAN}# display raw command${NORMAL}
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
        if self._session[ID] or cmd in ('hello','login'):
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
                getattr(self._epp_cmd, "assemble_%s"%cmd)((self.__next_clTRID__(),)) # self._session[ID](command)
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
        self._session[ID] = 0

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
        if not self._session[ID]: return # session zalogována nebyla
        self._epp_cmd.assemble_logout((self.__next_clTRID__(),)) # self._session[ID]
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
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
    def answer_greeting(self, dict_answer):
        "Part of process answer - parse greeting node."
        greeting = dict_answer['greeting']
        self.append_note(SEPARATOR)
        self.append_note(_T('Greeting message incomming'),('GREEN','BOLD'))
        self.defs[LANGS] = eppdoc.get_dict_data(greeting, ('svcMenu','lang'))
        if type(self.defs[LANGS]) in (str,unicode):
            self.defs[LANGS] = (self.defs[LANGS],)
        self.append_note('%s: %s'%(_T('Available language versions'),', '.join(self.defs[LANGS])))
        self.append_note('%s objURI:\n\t%s'%(_T('Available'),eppdoc.get_dict_data(greeting, ('svcs','objURI'),'\n\t')))

    def answer_response(self, dict_answer):
        "Part of process answer - parse response node."
        code, msg = ['']*2
        response = dict_answer.get('response',None)
##        print 'ANSWER_RESPONSE:',response #!!!
        if response:
            result = response.get('result',None)
            if result: code = eppdoc.get_dict_attr(response,'code')
##            print "RESULT:",result #!!!
##            print "CODE:",code #!!!
            if self._command_sent == 'login':
                if code == '1000':
                    self._session[ID] = 1 # první command byl login
                    self.append_note('*** %s ***'%_T('You are logged on!'),('GREEN','BOLD'))
                else:
                    self._session[ID] = 0 # počet příkazů zrušen, tím se indikuje i to, že session není zalogována
                    self.append_note('--- %s ---'%_T('Login failed'),('RED','BOLD'))
            elif self._command_sent == 'logout':
                self.append_note(_T('You are loged out of the private area.'))
                self.__logout_session__()
            else:
                # odpovědi na ostatní příkazy
                self.append_note(_T('server response:'),('GREEN','BOLD'))
                self.__put_raw_into_note__(dict_answer) #!!!

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
                invalid_epp = self.is_epp_valid(self._epp_response.get_xml())
                if invalid_epp:
                    # když se odpověd serveru neplatná...
                    self.append_error(_T('Server answer is not valid!'),'BOLD')
                    self.append_error(invalid_epp)
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
        elif re.match('raw[-_]',cmd):
            # Zobrazení 'surových' dat - zdrojová data
            # raw-cmd; raw-a[nswer] e[pp]; raw-answ [dict]
            m = re.match('raw[-_](\w+)(?:\s+(\w+))?',cmd)
            if m:
                self.append_note(SEPARATOR)
                if m.group(1)[0]=='c' and self._raw_cmd: # c cmd, command
                    # zobrazit EPP příkaz, který se poslal serveru
                    if m.group(2) and m.group(2)[0]=='d': # d dict
                        self.append_note(_T('Interpreted command'),('GREEN','BOLD'))
                        eppdoc = client_eppdoc.Message()
                        eppdoc.parse_xml(self._raw_cmd)
                        self.__put_raw_into_note__(eppdoc.create_data())
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
        eppdoc = client.create_eppdoc(command,TEST)
        client.display()
        if eppdoc:
            print 'EPP COMMAND:\n%s\n%s'%(eppdoc,'-'*60)
            if re.match('login',command):
                client._session[ID] = 1 # '***login***' # testovací zalogování
            if re.match('logout',command):
                client._session[ID] = 0 # testovací odlogování
            # client.process_answer(eppdoc)
            dict_answer = client._epp_cmd.create_data()
            if dict_answer:
                debug_label(u'dict:')
                pprint.pprint(dict_answer)
        print '='*60
    print '[END]'

