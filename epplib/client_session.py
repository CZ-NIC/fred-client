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
from gettext import gettext as _T
import client_eppdoc
import client_eppdoc_test
import client_socket
import pprint
import os, commands, dircache # jen pro testování. v ostré verzi to nebude

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

ID,LANG = range(2)

class Manager:
    """EPP client support.
    Hold client ID, login, password and server answers.
    Parse command line and call EPP builder.
    """
    def __init__(self):
        self._session = ['', 'en'] # session ID, lang
        self._epp_cmd = client_eppdoc.Message()
        self._epp_response = client_eppdoc.Message()
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        # Typ očekávané odpovědi serveru. Zde si Manager pamatuje jaký příaz
        # odeslal a podlat toho pak zařadí návratové hodnoty.
        self._expected_answer_type = ''

    def get_errors(self, sep='\n'):
        return sep.join(self._errors)

    def fetch_errors(self, sep='\n'):
        msg = sep.join(self._errors)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    #==================================================
    #
    #    EPP commands
    #    funkce, které vytvářejí EPP dokumenty
    #
    #==================================================
    def __create_info__(self,name,cmd):
        'Supprot for create_info_...() functions.'
        m = re.match(r'%s\s+(\S+)'%name,cmd)
        if m:
            getattr(self._epp_cmd,'assemble_%s'%name)((m.group(1), self._session[ID]))
        else:
            self._notes.append(_T('Error: Parametres missing. Type: %s name')%name)

    def create_info_contact(self, cmd):
        'Create EPP document info:contact'
        self.__create_info__('info_contact',cmd)

    def create_info_domain(self, cmd):
        'Create EPP document info:domain'
        self.__create_info__('info_domain',cmd)

    def create_info_nsset(self, cmd):
        'Create EPP document info:domain'
        self.__create_info__('info_nsset',cmd)

    def create_login(self, cmd):
        if self._session[ID]:
            # klient je už zalogován
            self._notes.append(_T('You are logged allready.'))
        else:
            # klient se zaloguje
            m = re.match(r'login\s+(\S+)\s+(\S+)\s*(\S*)',cmd)
            if m:
                self._expected_answer_type = 'login'
                self._epp_cmd.assemble_login(m.groups())
            else:
                self._notes.append(_T('Error: Parametres missing. Type:\nlogin username password [newpassword]\n(Values in the brackets are optional.)'))
    #==================================================
    def help_command(self, command):
        # Když je dotaz na help
        self._notes.append(_T("Available EPP commands: (%s).")%", ".join(self._available_commands))

    def epp_command(self, command):
        'Find EPP command in input.'
        cmd=None
        m=re.match('(\S+)',command)
        if m:
            if m.group(1) in self._available_commands:
                self.command_inside_session(m.group(1), command)
            else:
                self._notes.append(_T("Unknown EPP command: %s.")%command)

    def command_inside_session(self, cmd, command):
        'Process EPP command inside session.'
        # Příkazy EPP
        # Pokud se příkaz našel, tak se provede pokračuje do stavu 2.
        if self._session[ID] or cmd in ('hello','login'):
##        if 1: # Tady se vypíná kontrola zalogování:
            # když je klient zalogován, tak se volá EPP příkaz
            # výjimky pro příkazy hello a login
            fnc_name = "create_%s"%cmd
            self._expected_answer_type = cmd
            if hasattr(self, fnc_name):
                # Příprava vstupních dat pro příkaz
                getattr(self, fnc_name)(command)
            else:
                # Když příprava vstupních dat pro příkaz chybí
                # To, že daná funkce existuje je již ověřeno
                # přes self._available_commands
                getattr(self._epp_cmd, "assemble_%s"%cmd)(command)
            errors = self._epp_cmd.get_errors()
            if errors: self._errors.append(errors)
        else:
            self._notes.append(_T('You are not logged. You must login before working.\nPut command: login your_urename, your_password'))

    def create_eppdoc(self, command):
        "Build EPP question form user query. IN: command; OUT: note, errors, epp_xml"
        self._notes = []
        self._epp_cmd.reset()
        cmd = command.strip().lower()
        if re.match('^(\?|h|help)$', cmd):
            # help
            self.help_command(cmd)
        else:
            # příkazy pro EPP
            self.epp_command(cmd)
        return self._epp_cmd.get_xml()

    #==================================================
    #
    #    Transfer functions
    #    funkce pro komunikaci se socketem
    #
    #==================================================
    def connect(self, data=None):
        "Connect transfer socket. data=('host',port,'client-type')"
        if self._lorry: self.disconnect()
        self._lorry = client_socket.Lorry()
        self._lorry._notes = self._notes
        self._lorry._errors = self._errors
        self._lorry.handler_message = self.process_answer
        if not data: data = default_connecion # default connection
        if self._lorry.connect(data):
            self._expected_answer_type = 'greeting'
            epp_greeting = self._lorry.receive() # receive greeting
            if epp_greeting:
                self.process_answer(epp_greeting)
                return 1
        return 0
        
    def close(self):
        if self._lorry:
            self._lorry.close()
            self._lorry = None
        # když se spojení zrušilo, tak o zalogování nemůže být ani řeči
        self._session[ID] = 0

    def send(self, message):
        if self._lorry:
            return self._lorry.send(message)
        else:
            self._errors.append(_T('You are not connected.'))
            return 0

    def send_logout(self):
        'Send EPP logoff message.'
        if not self._session[ID]: return # session zalogována nebyla
        self._epp_cmd.assemble_logout()
        xmlepp = self._epp_cmd.get_xml()
        if xmlepp:
            if self.send(xmlepp): self._session[ID] = '' # odlogování se podařilo
        else:
            self._errors.append(self._epp_cmd.get_errors())
        
        
    def receive(self):
        if self._lorry:
            return self._lorry.receive()
        else:
            self._errors.append(_T('You are not connected.'))
            return ''

    def is_error(self):
        return len(self._errors)
        
    #==================================================
    #
    # funkce pro uložení hodnot z odpovědi od serveru
    #
    #==================================================
    def answer_greeting(self, node):
        print "answer_greeting((node)%s)"%node.nodeName #!!!

    def answer_response_result(self, node, parent_node):
        print "answer_response_result((node)%s)"%node.nodeName #!!!
        if self._expected_answer_type == 'login':
            if node.getAttribute('code') == '1000':
                # zalogování se podařilo
                self._session[ID] = self._epp_response.get_node_values(parent_node,('trID','clTRID'))
                self._notes.append('*** %s ***'%_T('You are logged on!'))
            else:
                self._notes.append('--- %s ---'%_T('Wrong login'))
        else:
            #TODO: ostatní příkazy
            pass

    def answer_response(self, node):
        print "answer_response((node)%s)"%node.nodeName #!!!
        for e in node.childNodes:
            if not self._epp_response.is_element_node(e): continue
            # pro všechny uzly
            fnc = getattr(self, 'answer_response_%s'%e.nodeName, None)
            if fnc: fnc(e, node) # Zpracuje se část odpovědi.

    def process_answer(self, epp_server_answer):
        'This funcion is called by listen socket.'
        # create XML DOM tree:
        self._epp_response.reset()
        self._epp_response.parse_xml(epp_server_answer)
        if self._epp_response.dom:
            # když přišla nějaká odpověd:
            print 'EXPECTED_ANSWER_TYPE:',self._expected_answer_type #!!!
            top_node = self._epp_response.get_element_node(self._epp_response.dom.documentElement)
            fnc = getattr(self, 'answer_%s'%top_node.nodeName, None)
            if fnc:
                fnc(top_node) # Odpověd se zpracuje.
            else:
                self._notes.append('%s: %s'%(_T('Missing answer function on the node name'),top_node.nodeName))
        else:
            # při parsování se vyskytly chyby
            self._errors.append(self._epp_response.get_errors())
        if 1: #!!! TEST !!!
            dict_answer = self._epp_response.create_data()
            if dict_answer:
                debug_label(u'dict:')
                pprint.pprint(dict_answer)
            else:
                print '[client_session:process_answer] no data (answer)' #!!!
    #==================================================

    def create_eppdoc_TEST(self, command):
        'Test client result answer.'
        xml_doc = ''
        self._notes = []
        self._epp_cmd.reset()
        cmd = command.strip() #.lower()
        m = re.match('([\S_]+)(.*)',cmd)
        # Možnost zadání pomlčky místo podtržítka:
        if m: cmd = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if re.match('^(\?|h|help)$', cmd):
            # help
            self.help_command(cmd)
            # test help
            self._notes.append(_T("Available test commands: (\n\t%s\n).")%"\n\t".join(client_eppdoc_test.get_test_help()))
        elif re.match('ex-',cmd):
            # Poslání souboru z adresáře examples
            m = re.match('ex-(.+)',command)
            if m:
                # odeslat zkušební soubor
                filename = m.group(1)
                try:
                    xml_doc = open('epplib/examples/%s'%filename,'rb').read()
                except IOError, (no, msg):
                    self._errors.append('IOError: [%d] %s'%(no, msg))
                self._errors.append(self._epp_cmd.get_errors(self._sep))
            else:
                # vypsat seznam dostupných souborů
                print 'List of examples:'
                print dircache.listdir('epplib/examples/')
        elif re.match('err-',cmd):
            # Testovací příkazy
            m = re.match('(\S+)',command)
            key = client_eppdoc_test.get_test_key(m.group(1))
            if not key:
                key = re.match('err-(.+)',command).group(1)
            xml_doc = self._epp_cmd.load_xml_doc(key,'epplib/testy')
            self._errors.append(self._epp_cmd.get_errors(self._sep))
        else:
            # příkazy pro EPP
            self.epp_command(cmd)
            xml_doc = self._epp_cmd.get_xml()
        return xml_doc

def is_epp_valid(message):
    "Check XML EPP by xmllint."
    tmpname='tmp.xml'
    open(tmpname,'w').write(message)
    # jen dočasný test
    body = commands.getoutput('xmllint --schema ../mod_eppd/schemas/all-1.0.xsd %s'%tmpname)
    os.unlink(tmpname)
    if body[-9:]=='validates':
        valid=1
    else:
        valid=0
        print "Internal: EPP DOC is not valid:"
        print body
        print '-'*60
    return valid

def debug_label(text,message=''):
    print '\n'
    print '-'*60
    print '***',text.upper(),'***'
    print '-'*60
    if message: print message

if __name__ == '__main__':
    client = Manager()
    client._session[ID] = 'logování vypnuto!'
    while 1:
        command = raw_input("> (? help, q quit): ")
        if command in ('q','quit','exit','konec'): break
        eppdoc = client.create_eppdoc_TEST(command)
        print 'ERRORS:',client.fetch_errors()
        print 'NOTES:',client.fetch_notes()
        if eppdoc:
            if is_epp_valid(eppdoc):
                print 'EPP COMMAND:\n%s\n%s'%(eppdoc,'-'*60)
            client.process_answer(eppdoc)
        print '='*60
    print '[END]'

