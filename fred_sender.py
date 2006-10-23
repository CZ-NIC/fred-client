#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys, os, re, time
import ccReg
from ccReg.session_receiver import ccRegError
from ccReg.session_transfer import BEGIN, END
from ccReg.translate import options, option_errors, option_args

def __auto_login__(epp, verbose):
    'Do login'
    if verbose > 1: print 'SEND AUTO-LOGIN:'
    try:
        # username a password musí být v config
        dansw = epp.api_command('login',epp.get_default_params_from_config('login'))
        ok = 1
    except ccRegError, msg:
        print 'Error:',msg
        ok = 0
        dansw={}
    if dansw.get('code',0) != 1000: epp.append_error(ccReg.session_base.get_ltext(dansw.get('reason',_T('Login failed'))))
    epp.display()
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
    
def send_docs(display_bar, docs=[]):
    names = ()
    #-------------------------------------------------
    # Inicializace klienta
    #-------------------------------------------------
    epp = ccReg.ClientSession()
    if not epp.load_config(): return
    
    if len(options['verbose']):
        verbose = epp.set_verbose(options['verbose'])
    else:
        verbose = '1'

    #-------------------------------------------------
    # Apped docs from argv params
    #-------------------------------------------------
    for filepath in option_args:
        if os.path.isfile(filepath):
            docs.extend(split_docs(open(filepath).read()))
        else:
            docs.append((0,'File not found: %s'%filepath))
    #-------------------------------------------------
    # For every loaded document
    #-------------------------------------------------
    if display_bar:
        verbose = epp.set_verbose(0)
        sart_at = time.time()
        bar = None
        bar_pos = 0
        max = len(docs)
        bar_step = (100.0/max)*0.01
        bar_header = '%s: %d'%(_T('Send files'),max)
    epp.print_tag(BEGIN)
    for code, xmldoc in docs:
        epp.reset_round()
        if code:
            command_name = epp.grab_command_name_from_xml(xmldoc)
            if len(command_name):
                if not epp.is_connected():
                    if command_name == 'login':
                        epp.connect()
                    else:
                        if not __auto_login__(epp, verbose): break
                if command_name == 'logout':
                    verbose = epp.set_verbose(0) # silent logout
                #-------------------------------------------------
                # pokud je zalogováno, tak pošle soubor
                #-------------------------------------------------
                if epp.is_online(command_name) and epp.is_connected():
                    # send document if only we are online
                    epp.send(xmldoc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    epp.process_answer(xml_answer) # process answer
                    epp.print_tag(END)
                    epp.print_answer()
                    epp.print_tag(BEGIN)
            epp.display() # display errors or notes
        else:
            if not display_bar: print "ERRORS:",xmldoc
        if display_bar:
            if bar is None: bar = ccReg.terminal_controler.ProgressBar(ccReg.session_base.colored_output,bar_header)
            bar.clear()
            bar.update(bar_pos, _T('sending...'))
            bar_pos += bar_step
    epp.print_tag(END)
    if display_bar:
        # print final 100%
        note = "Ran test in %.3f sec"%(time.time() - sart_at)
        bar.clear()
        bar.update(1.0, note)

    #-------------------------------------------------
    # KONEC přenosu - automatický logout
    #-------------------------------------------------
    if epp.is_connected():
        epp.set_verbose(0)
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
        if not sys.stdin.isatty():
            send_docs(options['bar'], split_docs(sys.stdin.read())) # commands from pipe
        else:
            if not options['help'] and len(sys.argv) > 1:
                send_docs(options['bar']) # commands from argv
            else:
                from ccreg_console import help_option
                print '%s: %s [OPTIONS...]\n\n%s\n\n%s\n\n%s:\n%s\n\n  %s\n'%(_T('Usage'), 'ccreg_sender.py',
                _T('Module for sending files to the EPP server.'),
                help_option,
                _T('EXAMPLES'),
"""
  ./ccreg_create.py info_domain nic.cz > cmd1.xml
  ./ccreg_create.py info_contact reg-id pokus > cmd2.xml
  ./ccreg_sender.py cmd1.xml cmd2.xml
  ./ccreg_sender.py -s epp_host -l cs cmd1.xml cmd2.xml
    
  echo -en "check_domain nic.cz\\ninfo_domain nic.cz" | ./ccreg_create.py | ./ccreg_sender.py""",
   _T('For more information, see README.'))
