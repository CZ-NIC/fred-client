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
    while 1:
        try:
            command = raw_input("> (?-help, q-quit): ")
        except (KeyboardInterrupt, EOFError):
            break
        if command in ('q','quit','exit','konec'):
            epp.send_logout()
            break
        epp_doc = epp.create_eppdoc(command)
        if epp_doc:
            if epp.is_connected():
                epp.send(epp_doc)          # send to server
                answer = epp.receive()     # receive answer
                epp.process_answer(answer) # process answer
            else:
                print _T("You are not connected! For connection type command: connect and then login")
        epp.display() # display errors or notes
    epp.close()
    print "[END]"


if __name__ == '__main__':
    host = None
    if len(sys.argv) > 1: host = sys.argv[1]
    main(host)
