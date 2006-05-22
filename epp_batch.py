#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul bude zpracovávat příkazy ze souboru,
# nebo z příkazové řádky.
import epplib.client_session

def run_console(client):
    # zde se spustí naslouchací smyčka:
    client.run_listen_loop()
    print client.fetch_notes()
    print "[START LOOP prompt]"
    while 1:
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'):
            break
        notes, errors, epp_doc = client.get_TEST_result(command) # get_result
        if notes:
            print 'NOTES:\n',notes
            print "-"*60
        if errors:
            print 'ERRORS:\n',errors
            print "-"*60
        if epp_doc:
            print "CLIENT COMMAND:\n",epp_doc
            print "-"*60
            # odeslání dokumentu na server
            if not client.send(epp_doc): # send_to_server
                break
        client.run_listen_loop()
    client.close()
    print client.fetch_errors()
    print client.fetch_notes()
    print "[END CLIENT TEST]"


if __name__ == '__main__':
##    DATA=('localhost',700,'cli')
    DATA=('curlew',700,'ssl')
    client = epplib.client_session.Manager()
    if client.connect(DATA):
        run_console(client)
    else:
        print client.fetch_errors()
        print client.fetch_notes()

