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
    client.start_lorry_loading('interactive')
    lorry = client.get_lorry()
    # start command line:
    while lorry.isAlive():
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'): break
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
            client.send_to_server(epp_doc)
    client.disconnect()
    print "[END CLIENT TEST]"


if __name__ == '__main__':
    client = epplib.client_session.Manager()
    if client.connect('localhost',700):
        run_console(client)
    else:
        print client.get_transfer_errors()

