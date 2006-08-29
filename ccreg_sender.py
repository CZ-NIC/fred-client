#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys
import os
import re
import ccReg
from ccReg.session_receiver import ccRegError
from ccReg.translate import _T, options, option_errors, option_args

def __auto_login__(epp):
    'Do login'
    print 'SEND AUTO-LOGIN:'
    try:
        # username a password musí být v config
        epp.api_command('login',epp.get_default_params_from_config('login'))
        ok = 1
    except ccRegError, msg:
        print 'Error:',msg
        ok = 0
    epp.display()
    print '_'*60
    return ok

def send_docs(docs=[]):
    names = ()
    #-------------------------------------------------
    # Inicializace klienta
    #-------------------------------------------------
    epp = ccReg.ClientSession()
    if not epp.load_config(options['session']): return

    #-------------------------------------------------
    # Apped docs from argv params
    #-------------------------------------------------
    for filepath in option_args:
        if os.path.isfile(filepath):
            docs.append((1,open(filepath).read()))
        else:
            docs.append((0,'File not found: %s'%filepath))
    #-------------------------------------------------
    # For every loaded document
    #-------------------------------------------------
    for code, xmldoc in docs:
        if code:
            command_name = epp.grab_command_name_from_xml(xmldoc)
            if len(command_name):
                if not epp.is_connected():
                    if command_name == 'login':
                        epp.connect()
                    else:
                        if not __auto_login__(epp): break
                #-------------------------------------------------
                # pokud je zalogováno, tak pošle soubor
                #-------------------------------------------------
                if epp.is_online(command_name) and epp.is_connected():
                    print 'SEND COMMAND:',command_name
                    # send document if only we are online
                    epp.send(xmldoc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    epp.process_answer(xml_answer) # process answer
                    epp.print_answer()
            epp.display() # display errors or notes
        else:
            print "ERRORS:",xmldoc
        print '_'*60
    #-------------------------------------------------
    # KONEC přenosu - automatický logout
    #-------------------------------------------------
    if epp.is_connected():
        try:
            epp.api_command('logout') # automatický logout
        except ccRegError, msg:
            print 'Error:',msg
        epp.print_answer()

def run_pipe():
    docs = []
    patt_error = re.compile('<errors>(.+?)</errors>', re.S)
    for doc in re.split('<\\?xml', sys.stdin.read()):
        doc = doc.strip()
        if not len(doc): continue
        m_err = patt_error.search(doc)
        if m_err:
            docs.append((0,m_err.group(1)))
        else:
            docs.append((1,'<?xml %s'%doc))
    send_docs(docs)


if __name__ == '__main__':
    if sys.version_info[:2] < (2,4):
        print _T('This program requires Python 2.4 or higher. Your version is'),sys.version
    else:
        if not sys.stdin.isatty():
            run_pipe() # commands from pipe
        else:
            if not options['help'] and len(sys.argv) > 1:
                send_docs() # commands from argv
            else:
                print '%s: %s [OPTIONS...]\n\n%s\n\n%s\n\n%s:\n%s\n\n  %s\n'%(_T('Usage'), 'ccreg_sender.py',
_T('Module for sending files to the EPP server.'),
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
                   session values are read from config file"""),
    _T('EXAMPLES'),
"""
  ./ccreg_create.py info_domain nic.cz > cmd1.xml
  ./ccreg_create.py info_contact reg-id pokus > cmd2.xml
  ./ccreg_sender.py cmd1.xml cmd2.xml
  ./ccreg_sender.py -s epp_host -l cs cmd1.xml cmd2.xml
    
  ./ccreg_create.py info_domain nic.cz | ./ccreg_create.py info_contact reg-id pokus | ./ccreg_create.py check_domain hokus pokus cosi | ./ccreg_sender.py""",
   _T('For more information, see README.'))
