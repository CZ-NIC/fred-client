#!/usr/bin/env python
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# EPP Console for registrant
#
# Your terminal should support unicode. Check locale to LANG=cs_CZ.UTF-8
#
"""
This is module with main loop of the client console.
At the beginning after check Python version and command line
options module creates fred.ClientSession object witch handles
whole manipulation with environment variables and communication
with server.

This module provide console loop, waits for user input,
hands on user input to the fred.Client object and display out
all messages or server answers.

For testing purpose is possible to display profiller to show
duration of the particular processes. For enable this part of code
you have to uncomment corresponding lines with PROFILER.
"""
import sys, re, time

import __init__
from session_base import colored_output, VERBOSE, RECONNECT
from translate import options, option_errors, script_name

help_option = _T("""
General options:
  -?, --help       Show this help and exit
  -V, --version    Display program version information and exit
  -l LANGUAGE, --lang=LANGUAGE
                   Set user interface language
  -v LEVEL, --verbose=LEVEL
                   Set verbose level
                   0 - print only XML answer from EPP server
                   1 - normal operation
                   2 - print more details
                   3 - print more details and display XML sources
  -x, --no_validate
                   Disable client-side XML validation

Connection options:
  -f CONFIG, --config=CONFIG
                   Load configuration from config file
  -s SESSION, --session=SESSION
                   Use session from config file

  -h HOSTNAME, --host=HOSTNAME
                   Fred server host 
  -p PORT, --port=PORT
                   Server port (default: 700)
  -u USERNAME, --user=USERNAME
                   Authenticate to server as user
  -w PASSWORD, --password=PASSWORD
                   Authenticate to server with password
  -c CERTIFICATE --cert=CERTIFICATE
                   Use SSL certificate to connect to server
  -k PRIVATEKEY --privkey=PRIVATEKEY
                   Use SSL private key to connect to server

  -n, --nologin    
                   Disable automatic connection to server at start
""")

def import_readline():
    'Returns readline if exists'
    try:
        import readline
    except ImportError:
        readline = None
    return readline


def display_profiler(label, indent, debug_time):
    'For test only.'
    # For enable time uncomment all lines with PROFILER (and display_profiler)
    # and in translate module option 'timer'.
    msg, prev_t = debug_time[0]
    print '='*60
    print indent,label
    print '='*60
    for msg,t in debug_time[1:]:
        print indent,('%s:'%msg).ljust(30),'%02.4f sec.'%(t - prev_t)
        prev_t = t
    print indent,'-'*43
    print indent,'Total:'.ljust(30),'%02.4f sec.'%(t - debug_time[0][1])

def make_validation(epp, xml_epp_doc, label):
    """Make validation and join error message according by verbose mode
    Returns True - valid, False - invalid
    """
    error_message = epp.is_epp_valid(xml_epp_doc) # make validation on the XML document
    if error_message:
        v = epp.get_session(VERBOSE)
        epp.append_error(label)
        if v < 2: epp.append_error(_T('More details in verbose 2 or higher.'))
        if v > 1: epp.append_error(error_message)
        if v > 2: epp.append_error(xml_epp_doc)
    return (len(error_message) == 0)
    
def main(options):
    'Main console loop.'
    if __init__.translate.warning:
        print colored_output.render("${BOLD}${RED}%s${NORMAL}"%__init__.translate.warning)
    epp = __init__.ClientSession()
    if not check_options(epp): return # any option error occurs
    
    readline = None
    if not options['command']:
        # import readline if only not command mode
        readline = import_readline()
        # join welcome message only in console mode
        epp.append_note(epp.welcome())
        
    if not epp.load_config():
        epp.display() # display errors or notes
        return

    epp.init_readline(readline) # readline behavior for Unix line OS
    is_online = 0
    prompt = '> '
    online = prompt
    
    # options['command']
    # choke down the login message output in non-interactive (command) mode
    if not epp.automatic_login(options['command']):
        epp.join_missing_config_messages()
        epp.display() # display errors or notes
        return

    epp.restore_history(readline)
    epp.display() # display errors or notes
    
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
                online = '%s@%s> '%epp.get_username_and_host()
        
        if options['command']:
            # non-interactive mode (command from command line options)
            command = options['command']
            # disable confirm mode
            epp.set_confirm('OFF')
        else:
            # interactive mode
            try:
                command = raw_input(online).strip()
            except KeyboardInterrupt: # Ctrl+C
                break
            except EOFError: # Ctrl+D
                epp.send_logout()
                break
            if command == '': continue
            if command in ('q','quit','exit'):
                epp.remove_from_history(readline)
                epp.send_logout()
                break
            
        #debug_time = [('START',time.time())] # PROFILER
        command_name, epp_doc, stop_interactive_mode = epp.create_eppdoc(command)
        #debug_time.append(('Command created',time.time())) # PROFILER
        if command_name == 'q': # User press Ctrl+C or Ctrl+D in interactive mode.
            epp.send_logout()
            break
        if stop_interactive_mode:
            epp.display() # display errors or notes
            continue
        if command_name and epp_doc: # if only command is EPP command
            is_valid = make_validation(epp, epp_doc, _T('Command data XML document failed to validate.'))
            #debug_time.append(('Validation',time.time())) # PROFILER
            if not (epp.is_online(command_name) and epp.is_connected()):
                epp.append_note(_T('You are not connected.'),('BOLD','RED'))
            elif is_valid: # only if we are online and command XML document is valid
                epp.display() # display errors or notes
                if epp.is_confirm_cmd_name(command_name):
                    try:
                        confirmation = raw_input('%s (y/N): '%_T('Do you really want to send this command to the server?'))
                    except (KeyboardInterrupt, EOFError), msg:
                        # user breaks sending command
                        epp.append_note(_T('skipped'))
                        epp.display() # display errors or notes
                        continue
                    epp.remove_from_history(readline)
                    if confirmation not in ('y','Y'): continue
                #debug_time.append(('Save and restore history',time.time())) # PROFILER
                epp.send(epp_doc)          # send to server
                #debug_time.append(('SEND to server',time.time())) # PROFILER
                xml_answer = epp.receive()     # receive answer
                #debug_time.append(('RECEIVE from server',time.time())) # PROFILER
                
                # try ro reconnect
                #   if connection was interrupted 
                #   and console is not in --command mode
                #   and config doesn't disable reconnection
                #   and answer is not code 2502 (Session limit exceeded; server closing connection)
                if not epp.is_connected() \
                    and not options['command'] \
                    and epp.get_session(RECONNECT):
                    
                    epp.display() # display errors or notes
                    # try reconnect and send command again
                    epp.append_note(_T('Try to automaticly reconnect - send login.'))
                    if not epp.automatic_login():
                        epp.display() # display errors or notes
                        break
                    if epp.is_connected():
                        # if login has been succefull send command again to the server
                        epp.send(epp_doc)
                        xml_answer = epp.receive() # receive answer
                
                if epp.is_connected():
                    is_valid = make_validation(epp, xml_answer, _T('Server answer XML document failed to validate.'))
                    #debug_time.append(('Validation',time.time())) # PROFILER
                    try:
                        debug_time_answer = epp.process_answer(xml_answer) # process answer
                        #debug_time.append(('Parse answer',time.time())) # PROFILER
                    except (KeyboardInterrupt, EOFError):
                        debug_time_answer = []
                        break # handle Ctrl+C or Ctrl+D from testy user
                    epp.display() # display errors or notes
                    #debug_time.append(('Prepare answer for display',time.time())) # PROFILER
                    epp.print_answer()
                    #debug_time.append(('Display answer',time.time())) # PROFILER
                    #if options['timer']:
                    #    display_profiler('Main LOOP time profiler','',debug_time)
                    #    display_profiler('From Main LOOP only "Parse answer"','\t',debug_time_answer)

            if is_valid and command_name == 'logout':
                # only if we are online and command XML document is valid
                epp.close() # close connection but not client
                
        epp.display() # display errors or notes
        
        if options['command']:
            # non-interactive mode (command from command line options)
            # It does only one EPP command and stops.
            epp.send_logout('not-display-output')
            break
    
    epp.close()
    epp.save_history(readline)
    epp.display() # display logout messages

def check_options(epp):
    'Check options what needs epp object for validate.'
    retval=1
    if options['verbose']:
        if epp.parse_verbose_value(options['verbose']) is None:
            retval=0
            print epp.fetch_errors()
            print _T("""Usage: %s [OPTIONS...]
Try '%s --help' for more information.""")%(script_name, script_name)
    return retval

if __name__ == '__main__':
    msg_invalid = __init__.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if options['help']:
            print '%s: %s [OPTIONS...]\n%s\n%s\n'%(_T('Usage'), 'fred_console',
            help_option,
            _T('See README for more information.'))
        elif options['version']:
            epp = fred.ClientSession()
            print epp.version()
        else:
            if option_errors:
                print option_errors
            else:
                main(options)
