#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# EPP Console for registrant
#
# Your terminal should support unicode. Check locale to LANG=cs_CZ.UTF-8
#
import sys, re, time
import ccReg
from ccReg.session_base import colored_output, VERBOSE
from ccReg.translate import _T, options, option_errors

def display_profiler(label, indent, debug_time):
    'For test only.'
    msg, prev_t = debug_time[0]
    print '='*60
    print indent,label
    print '='*60
    for msg,t in debug_time[1:]:
        print indent,('%s:'%msg).ljust(30),'%02.4f sec.'%(t - prev_t)
        prev_t = t
    print indent,'-'*43
    print indent,'Total:'.ljust(30),'%02.4f sec.'%(t - debug_time[0][1])
    
def main(options):
    'Main console loop.'
    if ccReg.translate.warning:
        print colored_output.render("${BOLD}${RED}%s${NORMAL}"%ccReg.translate.warning)
    epp = ccReg.ClientSession()
    ccReg.cmd_history.set_history(epp.get_command_names())
    if not epp.load_config(options): return
    print epp.welcome()
    epp.display() # display errors or notes
    is_online = 0
    prompt = '> '
    online = prompt
    epp.automatic_login()
    epp.restore_history()
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
            epp.remove_from_history()
            epp.send_logout()
            break
        debug_time = [('START',time.time())] # PROFILER
        command_name, epp_doc, stop_interactive_mode = epp.create_eppdoc(command)
        debug_time.append(('Command created',time.time())) # PROFILER
        if command_name == 'q': # User press Ctrl+C or Ctrl+D in interactive mode.
            epp.send_logout()
            break
        if stop_interactive_mode:
            epp.display() # display errors or notes
            continue
        if command_name and epp_doc: # if only command is EPP command
            invalid_epp = epp.is_epp_valid(epp_doc) # make validation on the XML document
            debug_time.append(('Validation',time.time())) # PROFILER
            if invalid_epp:
                epp.append_error(_T('EPP document is not valid'),'BOLD')
                v = epp.get_session(VERBOSE)
                epp.append_error(invalid_epp)
                if v > 2: epp.append_error(epp_doc)
            else:
                if epp.is_online(command_name) and epp.is_connected(): # only if we are online
                    epp.display() # display errors or notes
                    if epp.is_confirm_cmd_name(command_name):
                        confirmation = raw_input('%s (y/N): '%_T('Do you really want to send this command to the server?'))
                        epp.remove_from_history()
                        if confirmation not in ('y','Y'): continue
                    debug_time.append(('Save and restore history',time.time())) # PROFILER
                    epp.send(epp_doc)          # send to server
                    debug_time.append(('SEND to server',time.time())) # PROFILER
                    xml_answer = epp.receive()     # receive answer
                    debug_time.append(('RECEIVE from server',time.time())) # PROFILER
                    try:
                        debug_time_answer = epp.process_answer(xml_answer) # process answer
                        debug_time.append(('Parse answer',time.time())) # PROFILER
                    except (KeyboardInterrupt, EOFError):
                        debug_time_answer = []
                        break # handle Ctrl+C or Ctrl+D from testy user
                    epp.display() # display errors or notes
                    debug_time.append(('Prepare answer for display',time.time())) # PROFILER
                    epp.print_answer()
                    debug_time.append(('Display answer',time.time())) # PROFILER
                    if options['timer']:
                        display_profiler('Main LOOP time profiler','',debug_time)
                        display_profiler('From Main LOOP only "Parse answer"','\t',debug_time_answer)
                else:
                    epp.append_note(_T('You are not connected.'),('BOLD','RED'))
        if command_name == 'connect': epp.print_answer()
        epp.display() # display errors or notes
    epp.close()
    epp.save_history()
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
