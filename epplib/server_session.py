# -*- coding: utf8 -*-
# EPP Server module
#
# $Id$
#
# Tento modul je správce EPP dokumentů. Správce přijímá EPP dokumenty
# od klienta, které si nechá rozložit na hodnoty. Ty pak vyhodnotí a
# podle nich se dotazuje zdroje (corba rozhraní). Od zdroje přijme
# data odpovědi. Z těchto dat si nechá sestavit EPP odpověď, kterou předá
# klientovi.
#
# 1. Parsování XML (validace)
# 2. Validace EPP schemat
# 3. Validace EPP hodnot v kontextu
# 4. Provedení příkazu
# 5. Sestavení odpovědi
#
import re
from gettext import gettext as _T
import server_eppdoc
import server_socket

# enum
clTRID,svTRID = range(2)

class Manager:
    """EPP Server support. Mamage the instance of the client connection.
    """
    def __init__(self):
        self._session = [0, None, None] # session ID, user, password
        self._sd = [
             'ABC-12345' # clTRID TODO corba
            ,'54321-XYZ' # svTRID TODO corba
            ] 
        self._lang = 'en'
        self._epp_cmd = server_eppdoc.Message()
        self._epp_response = server_eppdoc.Message()
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._available_commands = self.get_server_commands()
        self._dock = None # class of server socket
        self._buffer = [] # incomming EPP messages
        self._end_anchor = '</epp>' # Indicator of the end EPP message
        self._keep_connection = ''  # ''-no keep, 'keep-connection'

    def fetch_errors(self, sep='\n'):
        if self._dock:
            self._errors.extend(self._dock._errors)
        msg = sep.join(self._errors)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        if self._dock:
            self._notes.extend(self._dock._notes)
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    def get_server_commands(self):
        'Return available server commands.'
        cmd = [name[8:] for name in dir(self.__class__) if name[:8]=='process_']
        cmd.append('command')
        return cmd

    def answer(self, epp_doc):
        "Server answer to user question."
        # Reset
        self._epp_cmd.reset()
        self._epp_response.reset()
        # 1. Parsování XML (validace)
        self._epp_cmd.parse_xml(epp_doc)
        # 1.1 Příprava odpovědi
        if self._epp_cmd.dom and self._epp_cmd.dom.encoding:
            # Nastavení výstupního kódování podle vstupu od klienta
            self._epp_response.encoding = self._epp_cmd.dom.encoding
        self._epp_response.create()
        self._epp_response.new_node_by_name('epp','response')
        if len(self._epp_cmd.errors):
            # 5.1 pokud se parsování nepodařilo, tak se jen sestaví chybové hlášení
            #for er in self._epp_cmd.errors:
            #    self._epp_response.create_node_error(er[0], '', er[1])
            self._epp_response.create_node_errors_from_EPP(self._epp_cmd)
        else:
            # 1.2 když se parsování povedlo, tak se provádějí jendotlivé příkazy
            self.read_commands()
        # 5.2 připojí se indetifikátory klienta
        self.__response_append_trID__()
        return self._epp_response.get_xml()

    def __response_append_trID__(self):
        'Append ID into response.'
        if self._sd[clTRID]:
            # ukložení jen v případě, že existuje ID transakce
            self._epp_response.new_node_by_name('response','trID')
            self._epp_response.new_node_by_name('trID','clTRID',self._sd[clTRID])
            self._epp_response.new_node_by_name('trID','svTRID',self._sd[svTRID])
    
    def read_commands(self):
        'Read and process all commands.'
        top = self._epp_cmd.dom.documentElement
        if top.nodeName.lower() != 'epp':
            # dokument není EPP
            self._epp_response.create_node_error(2000, node.nodeName, _T('Document is not EPP format'))
            return
        for node in top.childNodes:
            # pro všechny elementy hlavního EPP prvku
            if self._epp_cmd.is_element_node(node):
                # když je prvek typu Node.ELEMENT_NODE
                node_name = node.nodeName.lower()
                if node_name in self._available_commands:
                    # když se jméno elementu nachází v seznamu příkazů
                    # tak se může provést.
                    # Tady se můžou volat jen vybrané funkce:
                    # command a hello (a ještě něco?) ostatní funkce musí být
                    # v command elementu.
                    if node_name=='command':
                        # element <command> obsahuje jenden příkaz
                        # zjistíme jeho jméno
                        command_node = self._epp_cmd.get_command_node(node)
                        self._epp_response.create_node_errors_from_EPP(self._epp_cmd)
                        if command_node:
                            # 2. Validace EPP schemat
                            # Pokud jméno existuje, provede se kotrola platnosti
                            # tohoto příkazu
                            getattr(self._epp_cmd, "verify_%s"%command_node.nodeName)(command_node)
                            if len(self._epp_cmd.errors):
                                # validace neproběhla vpořádku, chyby se přesunou na výstup
                                self._epp_response.create_node_errors_from_EPP(self._epp_cmd)
                            else:
                                # EPP příkaz je validní
                                # 3. Validace EPP hodnot v kontextu
                                getattr(self,"process_%s"%command_node.nodeName)(command_node)
                    elif node_name=='hello':
                        # příkaz hello leží mimo <command>
                        self.process_hello(node)
                    else:
                        # Command syntax error, element, který na tomto místě nemá co dělat.
                        self._epp_response.create_node_error(2001, node.nodeName, _T('Element MUST be inside a command element'))
                else:
                    # Unknown command
                    # Jméno elementu se nenachází v seznamu příkazů
                    self._epp_response.create_node_error(2000, node.nodeName)
                
    #===========================================
    #
    # Process commands,
    # seznam dostupných EPP příkazů
    # každý příkaz musí provést validaci hodnot
    # 3. Validace EPP hodnot v kontextu
    #
    #===========================================
    
    #-------------------------------------------
    # Session management
    #-------------------------------------------
    def process_hello(self, node):
        self._epp_response.process_hello(node)
    def process_login(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_logout(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    
    #-------------------------------------------
    # Dotazovací (query)
    #-------------------------------------------
    def process_check(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_info(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_poll(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_transfer(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)

    #-------------------------------------------
    # Výkonné (transform)
    #-------------------------------------------
    def process_create(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_delete(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_renew(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)
    def process_update(self, node):
        self._epp_response.create_node_error(2101, node.nodeName)

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
            answer = self.answer(epp_message)
            self.send(answer) # send to client
            debug_label('CLIENT',epp_message)
            debug_label('ANSWER',answer)
            if not self._keep_connection:
                self.stop_listen() # po každé odpovědi se spojení přeruší
            # reset new message
            self._buffer=[]
            if part[1].strip()!='':
                self._buffer.append(part[1])

    def run_listen_loop(self):
        self._dock.run_listen_loop()


    def listen(self):
        return self._dock.listen()

    def close(self):
        if self._dock:
            self._dock.close()
            self._dock = None

    def send(self, message):
        return self._dock.send(message)

    def wait_to_listen(self):
        self._dock.join()

    def stop_listen(self):
        self._dock.stop_listening()

    def bind(self, HP):
        self._keep_connection = HP[2]
        if self._dock:
            self.disconnect()
        self._dock = server_socket.Dock()
        self._dock.handler_message = self.handler_message
        return self._dock.bind(HP[0], HP[1])

    #==================================================

def debug_label(text,message=''):
    print '\n'
    print '-'*60
    print '***',text.upper(),'***'
    print '-'*60
    if message: print message

if __name__ == '__main__':
    import client_session
    server = Manager()
    client = client_session.Manager()
    while 1:
        command = raw_input("CLIENT > (? help, q quit): ")
        if command in ('q','quit','exit','konec'): break
        notes, errors, epp_doc = client.get_TEST_result(command) # get_result
        if notes:
            debug_label('notes',notes)
        if errors:
            debug_label('errors',errors)
        if epp_doc:
            debug_label('client command',epp_doc)
            answer = server.answer(epp_doc)
            debug_label('server answer',answer)
    print '[END]'

