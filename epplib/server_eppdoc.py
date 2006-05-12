# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
# Tento modul obsahuje funkce a data, která jsou potřebná
# na sestavení EPP dokumentu pro server.
#
# Funkce s prefixem "verify_" jsou jednotlivé EPP příkazy, které třída
# Message() umí sestavit. Seznam dostupných příkazů vrací funkce get_server_commands().
#
import re
from gettext import gettext as _T
import eppdoc
import responses

class Message(eppdoc.Message):
    "Client EPP commands."

    def get_server_commands(self):
        'Return available server commands.'
        cmd = [name[7:] for name in dir(self.__class__) if name[:7]=='verify_']
        cmd.append('command')
        return cmd

    def create_node_error(self, code, value='', reason=''):
        'Create EPP node <result>'
        # TODO doplnit element msQ
        if code:
            # Standardní chybové hlášení
            node_result = self.new_node_by_name('response', 'result', None, (('code','%d'%code),))
            msg = responses.msg.get(code,'')
            if msg:
                self.new_node(node_result, 'msg', msg)
        else:
            node_result = self.new_node_by_name('response', 'result')
        if value:
            self.new_node(node_result, 'value', value)
        if reason:
            self.new_node(node_result, 'reason', reason)

    def create_node_errors_from_EPP(self, epp):
        for er in epp.errors:
            #self.create_node_error(2001, node_cmd.nodeName, _T('This element is not allowed here'))
            self.create_node_error(er[0], None, er[1])
        epp.errors=[]

    #===========================================
    #
    # Call top nodes
    #
    #===========================================
    #def call_hello(self, node):
    #    self.process_hello(node)

    def get_command_node(self, node):
        'Find command name inside <command> element.'
        command_node = None
        if node.hasChildNodes():
            node_cmd = self.get_element_node(node)
            if node_cmd:
                fnc_name = 'verify_%s'%node_cmd.nodeName
                if re.match('command',node_cmd.nodeName,re.I):
                    # vnořený command - nelze! To by se zacyklilo!
                    #self.create_node_error(2001, node_cmd.nodeName, _T('This element is not allowed here'))
                    self.errors.append((2001,_T('This element is not allowed here')))
                elif fnc_name in dir(self.__class__):
                    # OK, uzel je nalezen, předá se správci
                    command_node = node_cmd
                else:
                    # Unknown command , "Inside element: %s"%node.nodeName
                    #self.create_node_error(2000, node_cmd.nodeName)
                    self.errors.append((2000, node_cmd.nodeName))
            else:
                # prázdný <command>, Command syntax error
                #self.create_node_error(2001, node.nodeName, _T('Node has no data'))
                self.errors.append((2001, _T('Node has no data')))
        else:
            # prázdný <command>, Command syntax error
            #self.create_node_error(2001, node.nodeName, _T('Node is empty'))
            self.errors.append((2001, _T('Node is empty')))
        return command_node


    #===========================================
    #
    # Process commands,
    # seznam dostupných EPP příkazů
    # Každý příkaz musí mít část verify a může mít část process
    #   verify_[cmd]  - ověřuje platnost EPP příkazu
    #   process_[cmd] - sestavuje EPP odpověd z dodaných hodnot
    #
    #===========================================
    
    #-------------------------------------------
    # Session management
    #-------------------------------------------
    def verify_hello(self, node):
        pass
    def process_hello(self, node, data=None):
        # TODO: Dočasný kód
        if hasattr(node, 'nodeName'):
            self.create_node_error(2101, node.nodeName)
        else:
            self.load_EPP_template('greeting')
        # Tohle tady nemůže být aby to nepřepsalo již připravenou strukturu response
        #self.load_EPP_template('greeting')
        #TODO Co má být tady? Může být greeting v <epp><response> ?
        pass
    def verify_login(self, node):
        pass
    def verify_logout(self, node):
        pass

    #-------------------------------------------
    # Dotazovací (query)
    #-------------------------------------------
    def verify_check(self, node):
        pass

    def verify_info(self, node):
        pass

    def verify_poll(self, node):
        pass

    def verify_transfer(self, node):
        pass

    #-------------------------------------------
    # Výkonné (transform)
    #-------------------------------------------
    def verify_create(self, node):
        pass

    def verify_delete(self, node):
        pass

    def verify_renew(self, node):
        pass

    def verify_update(self, node):
        pass



def test_command(command, label):
    "Test if template si valid."
    epp = Message()
    cmd = command.split()
    fnc_name = "process_%s"%cmd[0]
    if hasattr(epp, fnc_name):
        getattr(epp, fnc_name)(cmd[1:])
    else:
        print "Error: Command not found."
    errors,xml_epp = epp.get_results()
    print '%s:'%label
    if errors: print 'ERRORS:',errors
    if xml_epp: print xml_epp
    print '-'*60

if __name__ == '__main__':
    # Test na jednotlivé příkazy
    test_command('hello', 'TEST hello -> greeting')

