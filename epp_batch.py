#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul bude zpracovávat příkazy ze souboru,
# nebo z příkazové řádky.
import epplib.client_session
from epplib.client_session import debug_label

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
            debug_label('notes',notes)
        if errors:
            debug_label('errors',errors)
        if epp_doc:
            debug_label('client command',epp_doc)
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

