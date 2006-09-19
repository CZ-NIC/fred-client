#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# EPP Console for registrant
#
# Your terminal should support unicode. Check locale to LANG=cs_CZ.UTF-8
#
import sys, re
import ccReg
from ccReg.session_base import colored_output, VERBOSE
from ccReg.translate import _T, options, option_errors

def main(session_name):
    if ccReg.translate.warning:
        print colored_output.render("${BOLD}${RED}%s${NORMAL}"%ccReg.translate.warning)
    epp = ccReg.ClientSession()
    ccReg.cmd_history.set_history(epp.get_command_names())
    if not epp.load_config(options['session']): return
    print epp.welcome()
    epp.display() # display errors or notes
    is_online = 0
    prompt = '> '
    online = prompt
    epp.automatic_login()
    while 1:
        # change prompt status:
        if is_online:
            if not epp.is_logon():
                is_online = 0
                online = prompt
        else:
            online = prompt
            if epp.is_logon():
                is_online = 1
                online = '%s@%s: '%epp.get_username_and_host()
        try:
            command = raw_input(online).strip()
        except (KeyboardInterrupt, EOFError):
            break
        if command == '': continue
        if command in ('q','quit','exit'):
            epp.send_logout()
            break
        command_name, epp_doc = epp.create_eppdoc(command)
        if command_name == 'q': # User press Ctrl+C or Ctrl+D in interactive mode.
            epp.send_logout()
            break
        if command_name and epp_doc: # if only command is EPP command
            invalid_epp = epp.is_epp_valid(epp_doc)
            if invalid_epp:
                epp.append_error(_T('EPP document is not valid'),'BOLD')
                v = epp.get_session(VERBOSE)
                epp.append_error(invalid_epp)
                if v > 2: epp.append_error(epp_doc)
            else:
                if epp.is_online(command_name) and epp.is_connected(): # only if we are online
                    if epp.is_confirm_cmd_name(command_name):
                        epp.save_history()
                        confirmation = raw_input('%s (y/n): '%_T('Do you want send this command to the server?'))
                        epp.restore_history()
                        if confirmation not in ('y','Y'): continue
                    epp.send(epp_doc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    try:
                        epp.process_answer(xml_answer) # process answer
                    except (KeyboardInterrupt, EOFError):
                        break # handle Ctrl+C or Ctrl+D from testy user
                    epp.display() # display errors or notes
                    epp.print_answer()
                else:
                    epp.append_note(_T('You are not connected! Type login for connection to the server.'),('BOLD','RED'))
        if command_name == 'connect': epp.print_answer()
        epp.display() # display errors or notes
    epp.close()
    epp.display() # display logout messages
    print "[END]"


if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if options['help']:
            print '%s: %s [OPTIONS...]\n\n%s\n\n%s\n\n  %s\n'%(_T('Usage'), 'ccreg_console.py',
_T('Console for communication with EPP server.'),
_T("""Connection options:
  -?, --help       show this help and exit
  -V, --version    Display program version information

  -l LANGUAGE, --lang=LANGUAGE
                   set user interface language
  -r, --colors     turn on colored output
  -v LEVEL, --verbose=LEVEL
                   set verbose level
                   1 - normal operation
                   2 - print more details
                   3 - print more details and display XML sources
  -h HOSTNAME, --host=HOSTNAME
                   ccReg server to connect 
  -u USERNAME, --user=USERNAME
                   authenticate to server as user
  -p PASSWORD, --password=PASSWORD
                   authenticate to server with password
  -s SESSION, --session=SESSION
                   read session name  used for connect to the EPP server
                   session values are read from config file
  -c CONFIG, --config=CONFIG
                   load config from filename"""),
   _T('For more information, see README.'))
        elif options['version']:
            epp = ccReg.ClientSession()
            print epp.version()
        else:
            if option_errors:
                print option_errors
            else:
                main(options['session'])
