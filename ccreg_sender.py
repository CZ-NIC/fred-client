#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys
import os
import re
import getopt
import ccReg

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

def __get_host_and_filenames__():
    args = sys.argv[1:]
    optlist, args = getopt.getopt(args, 'h:')
    host = None
    for k,v in optlist:
        if k == '-h': host = v
    return host, args
            
def send_docs(docs=[]):
    host, names = __get_host_and_filenames__()
    #-------------------------------------------------
    # Inicializace klienta
    #-------------------------------------------------
    epp = ccReg.ClientSession()
    if host:
        print "SET HOST:",host
        epp.set_host(host)
    if not epp.load_config(): return
    #-------------------------------------------------
    # Apped docs from argv params
    #-------------------------------------------------
    for filepath in names:
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
    if sys.stdin.isatty():
        if len(sys.argv) > 1:
            send_docs() # commands from argv
        else:
            print """*** ccReg Sender ***

Send all files to the EPP server on the order of the list filenames.
If first file is NOT login - does login automaticly.

Usage: 

python ccreg_sender.py [-h host] file.xml [file.xml ...]

Examples:
./ccreg_create.py info-domain nic.cz > cmd1.xml
./ccreg_create.py info-contact reg-id pokus > cmd2.xml
./ccreg_sender.py cmd1.xml cmd2.xml

or

./ccreg_create.py info-domain nic.cz | ./ccreg_create.py info-contact reg-id pokus | ./ccreg_create.py check-domain hokus pokus cosi | ./ccreg_sender.py
"""
    else:
        run_pipe() # commands from pipe

