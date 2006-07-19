#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys
import getopt
import ccReg

def main(host, files):
    #-------------------------------------------------
    # Inicializace klienta
    #-------------------------------------------------
    if not len(files):
        print "No files defined to send."
        return
    epp = ccReg.ClientSession()
    if host:
        print "SET HOST:",host
        epp.set_host(host)
    if not epp.load_config(): return
    #=====================================================
    #
    # Pro každé jméno souboru ze zadaného seznamu
    #
    #=====================================================
    for filename in files:
        #-------------------------------------------------
        # načte XML
        #-------------------------------------------------
        command_name, epp_doc = epp.load_filename(filename)
        if not (command_name and epp_doc):
            # když se soubor nepodařilo načíst
            epp.display() # display errors or notes
            continue
        #-------------------------------------------------
        # pokud není zalogováno, tak zaloguje
        #-------------------------------------------------
        if not epp.is_connected():
            # automatický login
            print '_'*60
            print 'SEND AUTO-LOGIN:'
            try:
                # username a password musí být v config
                epp.api_command('login',epp.get_default_params_from_config('login'))
            except ccRegError, msg:
                print 'Error:',msg
                epp.display()
                break
            print '-'*60
            epp.display()
        #-------------------------------------------------
        # pokud je zalogováno, tak pošle soubor
        #-------------------------------------------------
        if epp.is_online(command_name) and epp.is_connected():
            print '_'*60
            print 'NOW SEND FILE "%s":'%filename
            # send document if only we are online
            epp.send(epp_doc)          # send to server
            xml_answer = epp.receive()     # receive answer
            epp.process_answer(xml_answer) # process answer
            epp.display() # display errors or notes
            epp.print_answer()
    #-------------------------------------------------
    # KONEC přenosu - automatický logout
    #-------------------------------------------------
    if epp.is_connected():
        try:
            epp.api_command('logout') # automatický logout
        except ccRegError, msg:
            print 'Error:',msg
        epp.print_answer()
    print '[END OF TRANSMIT]'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        optlist, args = getopt.getopt(args, 'h:')
        host = None
        for k,v in optlist:
            if k == '-h': host = v
        main(host, args)
    else:
        print """*** ccReg Sender ***

Send all files to the EPP server on the order of the list filenames.
If first file is NOT login - does login automaticly.

Usage: python ccreg_sender.py [-h host] file.xml [file.xml ...]
"""
