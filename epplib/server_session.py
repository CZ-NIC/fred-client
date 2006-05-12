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
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._available_commands = self.get_server_commands()
        self._dock = None # class of server socket
    
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
    def listen(self, host, port):
        if self._dock: self.disconnect()
        self._dock = server_socket.Dock()
        return self._dock.listen(host, port)
        
    def disconnect(self):
        if self._dock:
            self._dock.close()
            self._dock = None

    def send_to_client(self, message):
        self._dock.send(message)

    def receive_from_client(self):
        return self._dock.receive()

    def get_transfer_errors(self):
        return self._dock.fetch_errors()

    def get_received_command(self):
        return self._dock.get_cargo()
        
    #==================================================

def test(host, port):
    server = Manager()
    if not server.listen(host, port):
        return
    while 1:
        if not server.receive_from_client():
            print server.get_transfer_errors()
            break
        command = server.get_received_command()
        answer = server.answer(command)
        server.send_to_client(command)
        print '-'*60,'\nCLIENT COMMAND:\n',command
        print '-'*60,'\nSERVER ANSWER:\n',answer
    server.disconnect()
    print "[END SERVER TEST]"

        
if __name__ == '__main__':
    test('', 700)
