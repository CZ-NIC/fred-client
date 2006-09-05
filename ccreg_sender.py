#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys, os, re, time
import ccReg
from ccReg.session_receiver import ccRegError
from ccReg.translate import _T, options, option_errors, option_args

def __auto_login__(epp, verbose):
    'Do login'
    if verbose: print 'SEND AUTO-LOGIN:'
    try:
        # username a password musí být v config
        epp.api_command('login',epp.get_default_params_from_config('login'))
        ok = 1
    except ccRegError, msg:
        print 'Error:',msg
        ok = 0
    epp.display()
    if verbose: print '_'*60
    return ok

def split_docs(docset):
    docs = []
    patt_error = re.compile('<errors>(.+?)</errors>', re.S)
    for doc in re.split('<\\?xml', docset):
        doc = doc.strip()
        if not len(doc): continue
        m_err = patt_error.search(doc)
        if m_err:
            docs.append((0,m_err.group(1)))
        else:
            docs.append((1,'<?xml %s'%doc))
    return docs

def load_docs(names):
    docs=[]
    for filepath in names:
        if os.path.isfile(filepath):
            docs.extend(split_docs(open(filepath).read()))
        else:
            docs.append((0,'File not found: %s'%filepath))
    return docs

def send_docs_in_threads(epp, docs=[]):
    max = len(docs)
    bar_step = bar_pos = 0
    bar = None
    if options['bar']:
        bar_header = '%s: %d'%(_T('Send files'),max)
        bar = ccReg.terminal_controler.ProgressBar(ccReg.session_base.colored_output,bar_header)
        verbose = epp.set_verbose(0)
        sart_at = time.time()
        bar_pos = 0
        bar_step = (100.0/max)*0.01
    if max > 100:
        part = max/4.0
##        t1 = docs[:]
##        t2 = docs[:]
##        t3 = docs[:]
    send_docs(epp, bar, bar_pos, bar_step, docs)
    # final bar
    if bar:
        # print final 100%
        note = "Ran test in %.3f sec"%(time.time() - sart_at)
        bar.clear()
        bar.update(1.0, note)

    
def send_docs(epp, bar, bar_pos, bar_step, docs=[]):
    names = ()
    
    if len(options['verbose']):
        verbose = epp.set_verbose(options['verbose'])
    else:
        verbose = '1'

    #-------------------------------------------------
    # For every loaded document
    #-------------------------------------------------
    if display_bar:
        verbose = epp.set_verbose(0)
        sart_at = time.time()
        bar_pos = 0
        max = len(docs)
        bar_step = (100.0/max)*0.01
        bar_header = '%s: %d'%(_T('Send files'),max)
    for code, xmldoc in docs:
        if code:
            command_name = epp.grab_command_name_from_xml(xmldoc)
            if len(command_name):
                if not epp.is_connected():
                    if command_name == 'login':
                        epp.connect()
                    else:
                        if not __auto_login__(epp, verbose): break
                #-------------------------------------------------
                # pokud je zalogováno, tak pošle soubor
                #-------------------------------------------------
                if epp.is_online(command_name) and epp.is_connected():
                    if not display_bar and verbose: print 'SEND COMMAND:',command_name
                    # send document if only we are online
                    epp.send(xmldoc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    epp.process_answer(xml_answer) # process answer
                    epp.print_answer()
            epp.display() # display errors or notes
        else:
            if not display_bar: print "ERRORS:",xmldoc
        if not display_bar:
            if verbose: print '_'*60
        else:
##            if bar is None: bar = ccReg.terminal_controler.ProgressBar(ccReg.session_base.colored_output,bar_header)
            bar.clear()
            bar.update(bar_pos, _T('sending...'))
            bar_pos += bar_step
##    if display_bar:
##        # print final 100%
##        note = "Ran test in %.3f sec"%(time.time() - sart_at)
##        bar.clear()
##        bar.update(1.0, note)

    #-------------------------------------------------
    # KONEC přenosu - automatický logout
    #-------------------------------------------------
    if epp.is_connected():
        try:
            epp.api_command('logout') # automatický logout
        except ccRegError, msg:
            print 'Error:',msg
        epp.print_answer()

if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        epp = ccReg.ClientSession()
        epp.load_config(options['session'])
##        if options['bar']:
##            bar = ccReg.terminal_controler.ProgressBar(ccReg.session_base.colored_output,bar_header)
##        else:
##            bar = None
        if not sys.stdin.isatty():
            send_docs_in_threads(epp, split_docs(sys.stdin.read())) # commands from pipe
        else:
            if not options['help'] and len(sys.argv) > 1:
                send_docs_in_threads(epp, load_docs(option_args)) # commands from argv
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
                   session values are read from config file
  -c CONFIG, --config=CONFIG
                   load config from filename"""),
    _T('EXAMPLES'),
"""
  ./ccreg_create.py info_domain nic.cz > cmd1.xml
  ./ccreg_create.py info_contact reg-id pokus > cmd2.xml
  ./ccreg_sender.py cmd1.xml cmd2.xml
  ./ccreg_sender.py -s epp_host -l cs cmd1.xml cmd2.xml
    
  ./ccreg_create.py info_domain nic.cz | ./ccreg_create.py info_contact reg-id pokus | ./ccreg_create.py check_domain hokus pokus cosi | ./ccreg_sender.py""",
   _T('For more information, see README.'))
