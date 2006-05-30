#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul bude zpracovávat příkazy ze souboru,
# nebo z příkazové řádky.
import epplib.client_session

def main():
    client = epplib.client_session.Manager()
    if not client.connect():
        # když se spojení nepodařilo navázat
        print 'NOTES:',client.fetch_notes()
        print 'ERRORS:',client.fetch_errors()
        return
    # zde se spustí naslouchací smyčka:
    print client.fetch_notes()
    print "[START LOOP prompt]"
    while 1:
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'):
            client.send_logout()
            break
        epp_doc = client.create_eppdoc_TEST(command)
        if epp_doc and epplib.client_session.is_epp_valid(epp_doc):
            epplib.client_session.debug_label('client command',epp_doc)
            # odeslání dokumentu na server
            if not client.send(epp_doc):
                print "když se odeslání nepodařilo..."#!!!
                break # když se odeslání nepodařilo
            # příjem odpovědi
            answer = client.receive()
            if not answer:
                # odpověď od serveru nepřišla
                print "No response. EPP Server doesn't answer."
##                break
            # zpracování odpovědi
            client.process_answer(answer)
        else:
            print 'ERRORS:',client.fetch_errors()
            print 'NOTES:',client.fetch_notes()
        if client.is_error():
            print "vyskytly se nějaké chyby...?"#!!!
            break # vyskytly se nějaké chyby
    print "[END LOOP prompt]"
    print 'ERRORS:',client.fetch_errors()
    print 'NOTES:',client.fetch_notes()
    client.close()
    print "[END CLIENT]"


if __name__ == '__main__':
    main()
