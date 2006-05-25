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
"""Usage:

import epplib
client = epplib.client_session.Manager()
notes, errors, epp_doc = client.get_result("hello")
print 'NOTES:',notes
print 'ERRORS:',error
print 'XMLEPP:',epp_doc
if epp_doc:
    client.send_to_server(epp_doc)
"""

class Manager:
    """EPP client support.
    Hold client ID, login, password and server answers.
    Parse command line and call EPP builder.
    """
    def __init__(self):
        self._session = [0, None, None] # session ID, user, password
        self._lang = 'en'
        self._epp_cmd = client_eppdoc.Message()
        self._epp_response = client_eppdoc.Message()
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        self._buffer = [] # incomming EPP messages
        self._end_anchor = '</epp>' # Indicator of the end EPP message

    def get_errors(self, sep='\n'):
        return sep.join(self._errors)

    def fetch_errors(self, sep='\n'):
        if self._lorry:
            self._errors.extend(self._lorry._errors)
        msg = sep.join(self._errors)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        if self._lorry:
            self._notes.extend(self._lorry._notes)
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    #==================================================
    #
    #    EPP commands
    #
    #==================================================
    def create_login(self, cmd):
        if self._session[0]:
            # klient je už zalogován
            self._notes.append(_T('You are logged allready.'))
        else:
            # klient se zaloguje
            m = re.match(r'login\s+(\S+)\s+(\S+)\s*(\S*)',cmd)
            if m:
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
##        if self._session[0] or cmd in ('hello','login'):
        if 1: # Tady se vypíná kontrola zalogování:
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
                getattr(self._epp_cmd, "assemble_%s"%cmd)(command)
        else:
            self._notes.append(_T('You are not logged. You must login before working.\nPut command: login your_urename, your_password'))


    def get_result(self, command):
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
        return self._sep.join(self._notes), self._epp_cmd.get_errors(self._sep), self._epp_cmd.get_xml()

    #==================================================
    #
    #    Transfer functions
    #
    #==================================================
    def handler_message(self, msg):
        'Handler of incomming message'
        # funkce pro přijetí zprávy
        part = re.split(self._end_anchor,msg,re.I) # </epp>
        self._buffer.append(part[0])
        if len(part)>1:
            # end of EPP document occured
            self._buffer.append(self._end_anchor)
            epp_message = '\n'.join(self._buffer)
            self.process_answer(epp_message)
            # reset new message
            self._buffer=[]
            if part[1].strip()!='':
                self._buffer.append(part[1])

    def run_listen_loop(self):
        self._lorry.run_listen_loop()

    def start_lorry_loading(self, noblocking=None):
        'Start receiving loop.'
        if self._lorry.start_listen_loop(self.receive_from_server) and not noblocking:
            self._lorry.join()

    def connect(self, data):
        "Connect transfer socket. data=('host',port,'client-type')"
        if self._lorry: self.disconnect()
        self._lorry = client_socket.Lorry()
        self._lorry.handler_message = self.handler_message
        return self._lorry.connect(data[0], data[1], data[2])
        
    def close(self):
        if self._lorry:
            self._lorry.close()
            self._lorry = None

    def send(self, message):
        return self._lorry.send(message)

    #==================================================
    def process_answer(self, epp_server_answer):
        'This funcion is called by listen socket.'
        debug_label(u'zdrojový epp:') #!!!
        # print epp_server_answer #!!!
        # create XML DOM tree:
        self._epp_response.reset()
        self._epp_response.parse_xml(epp_server_answer)
        print self._epp_response.get_xml()
        debug_label(u'dict:') #!!!
        pprint.pprint(self._epp_response.make_dict())

    def get_TEST_result(self, command):
        'Test client result answer.'
        self._notes = []
        self._epp_cmd.reset()
        cmd = command.strip().lower()
        if re.match('^(\?|h|help)$', cmd):
            # help
            self.help_command(cmd)
            # test help
            self._notes.append(_T("Available test commands: (\n\t%s\n).")%"\n\t".join(client_eppdoc_test.get_test_help()))
        elif re.match('err-',cmd):
            # Testovací příkazy
            m = re.match('(\S+)',command)
            key = client_eppdoc_test.get_test_key(m.group(1))
            if not key:
                key = re.match('err-(.+)',command).group(1)
            xml_doc = self._epp_cmd.load_xml_doc(key,'epplib/testy')
            return 'ERROR TEST', self._epp_cmd.get_errors(self._sep), xml_doc
        else:
            # příkazy pro EPP
            self.epp_command(cmd)
        return self._sep.join(self._notes), self._epp_cmd.get_errors(self._sep), self._epp_cmd.get_xml()


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
        notes, errors, epp_doc = client.get_result(command)
        if notes:
            print 'NOTES:\n',notes
        if errors:
            print 'ERRORS:\n',errors
        if epp_doc:
            print 'EPP COMMAND:\n',epp_doc
        print '-'*60
    print '[END]'

