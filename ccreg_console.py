#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# EPP Console for registrant
#
# Your terminal should support unicode. Check locale to LANG=cs_CZ.UTF-8
#
import sys, re
import ccReg
from ccReg.session_base import colored_output
from ccReg import _T

def main(host):
    epp = ccReg.ClientSession()
    ccReg.cmd_history.set_history(epp.get_command_names())
    if host: epp.set_host(host)
    if not epp.load_config(): return
    print epp.welcome()
    epp.display() # display errors or notes
    print _T('For connection to the EPP server type "connect" or directly "login".')
    is_online = 0
    status = ('OFF','ON')
    online = status[is_online]
    while 1:
        try:
            command = raw_input("> (?-help, q-quit) %s: "%online)
        except (KeyboardInterrupt, EOFError):
            break
        if command in ('q','quit','exit','konec'):
            epp.send_logout()
            break
        command_name, epp_doc = epp.create_eppdoc(command)
        if len(epp_doc):
            invalid_epp = epp.is_epp_valid(epp_doc)
            if invalid_epp:
                epp.append_error(_T('EPP document is not valid'),'BOLD')
                epp.append_error(invalid_epp)
                epp_doc = '' # not send invalid document
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
                epp.append_note(_T('You are not connected! Type login for connection to the server.'),('BOLD','RED'))
        if command_name == 'connect': epp.print_answer()
        epp.display() # display errors or notes
        # change prompt status:
        if is_online:
            if not epp.is_logon():
                is_online = 0
                online = status[is_online]
        else:
            online = status[0]
            if epp.is_logon():
                is_online = 1
                online = '%s@%s'%epp.get_username_and_host()
    epp.close()
    epp.display() # display logout messages
    print "[END]"


if __name__ == '__main__':
    if sys.version_info[:2] < (2,4):
        print _T('This program needs Python 2.4 or higher. Your version is'),sys.version
    else:
        host = None
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg in ('en','cs'): continue
                host = arg
                break
        else:
            print _T("Usage: python ccreg_console.py [host] [lang] # (lang is only cs/en and it can be also set befor host)")
        if ccReg.translate.warning:
            print colored_output.render("${BOLD}${RED}%s${NORMAL}"%ccReg.translate.warning)
        print colored_output.render('Unicode encodings to ${BOLD}%s${NORMAL}.'%ccReg.translate.encoding)
        main(host)
