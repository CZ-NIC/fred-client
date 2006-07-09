#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# EPP Console for registrant
#
# Your terminal should support unicode. Check locale to LANG=cs_CZ.UTF-8
#
import sys, re
from gettext import gettext as _T
#import cmd_history
import ccReg
from ccReg.session_base import colored_output

# Kontrola na Unicode
try:
    u'žščřťňě'.encode(sys.stdout.encoding)
except UnicodeEncodeError, msg:
    from ccReg.terminal_controler import TerminalController
    term = TerminalController()
    print term.BOLD+term.RED+_T('WARNING! Your terminal does not support UTF-8 encoding. Set locale to LANG=cs_CZ.UTF-8.')+term.NORMAL

def main(host):
    epp = ccReg.ClientSession()
    ccReg.cmd_history.set_history(epp.get_command_names())
    print epp.welcome()
    if not epp.load_config(): return
    epp.display() # display errors or notes
    if host: epp.set_host(host)
    print _T('For connection to the EPP server type "connect" or directly "login".')
    status = ('${BOLD}${YELLOW}OFF${NORMAL}','${BOLD}${GREEN}ON${NORMAL}')
    online = status[0]
    while 1:
        try:
            command = raw_input(colored_output.render("> (?-help, q-quit) %s: "%online))
        except (KeyboardInterrupt, EOFError):
            break
        if command in ('q','quit','exit','konec'):
            epp.send_logout()
            break
        command_name, epp_doc = epp.create_eppdoc(command)
        invalid_epp = epp.is_epp_valid(epp_doc)
        if invalid_epp:
            epp.append_error(_T('EPP document is not valid'),'BOLD')
            epp.append_error(invalid_epp)
        else:
            if command_name and epp_doc: # if only command is EPP command
                if epp.is_online(command_name) and epp.is_connected(): # only if we are online
                    if epp.is_confirm_cmd_name(command_name):
                        confirmation = raw_input('%s (y/n): '%_T('Do you want send this command to the server?'))
                        if confirmation not in ('y','Y'): continue
                    epp.send(epp_doc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    epp.process_answer(xml_answer) # process answer
                    epp.display() # display errors or notes
                    epp.print_answer()
                else:
                    epp.append_note(_T('You are not connected! Type login before working on the server.'),('BOLD','RED'))
        epp.display() # display errors or notes
        online = status[epp.is_logon()]
    epp.close()
    epp.display() # display logout messages
    print "[END]"


if __name__ == '__main__':
    host = None
    if len(sys.argv) > 1: host = sys.argv[1]
    main(host)
