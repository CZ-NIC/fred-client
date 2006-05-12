#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul bude zpracovávat příkazy ze souboru,
# nebo z příkazové řádky.
import epplib.client_session

def run_console(client):
    while 1:
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
            client.send_to_server(epp_doc)
            if not client.receive_from_server():
                print client.get_transfer_errors()
                break
            response = client.get_response()
            print "SERVER ANSWSER:\n",response
            print "-"*60
            result = client.process_answer(response)
            print "SERVER RESULT:\n",result
            print "-"*60
        print "="*60


if __name__ == '__main__':
    client = epplib.client_session.Manager()
    if client.connect('localhost',700):
        run_console(client)
    else:
        print client.get_transfer_errors()

