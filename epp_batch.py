#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul bude zpracovávat příkazy ze souboru,
# nebo z příkazové řádky.
# getopt -- Parser for command line options
import sys, re
import pprint # TEST ONLY
import epplib.client_session

# Kontrola na Unicode
try:
    u'žščřřťňě'.encode(sys.stdout.encoding)
except UnicodeEncodeError, msg:
    print msg
    print 'Nelze pouzit Python teto verze, protoze nepodporuje Unicode znaky.'
    print 'Unpossible use this Python version cause of not support Unicode chars.'
    print '[END]'
    sys.exit()
# kontrola na readline
try:
    import readline
except ImportError:
    print u'readline modul chybí - historie příkazů je vypnuta'
    print 'readline module missing - cmd history is diabled'
    readline = None

class Completer:
    def __init__(self, words):
        self.words = words
        self.prefix = None
    def complete(self, prefix, index):
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [w for w in self.words if w.startswith(prefix)]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

def main():
    # readline
    words = "check_contact", "check_domain", "check_nsset", "create", "delete", "hello", "info_contact", "info_domain", "info_nsset", "login", "logout", "poll", "renew", "transfer", "update"
    if readline:
        completer = Completer(words)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)

    client = epplib.client_session.Manager()
    #---------------------------------------------------
    if 0:
        # automatické připojení k serveru
        if not client.connect():
            # když se spojení nepodařilo navázat
            print '[batch] NOTES:\n',client.fetch_notes()
            print '[batch] ERRORS:\n',client.fetch_errors()
            return
        print client.fetch_notes() # zobrazit poznámky
    else:
        print u"Pro spojení se serverem zadeje: connect nebo rovnou login"
    #---------------------------------------------------
    print "[BATCH: START LOOP prompt]"
    while 1:
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'):
            client.send_logout()
            break
        epp_doc = client.create_eppdoc(command, epplib.client_session.TEST)
        if epp_doc:
            if re.match('login ',command): client.connect() # automatické připojení, pokud nebylo navázáno
            if client.is_connected():
                client.send(epp_doc)          # odeslání dokumentu na server
                answer = client.receive()     # příjem odpovědi
                client.process_answer(answer) # zpracování odpovědi
            else:
                print "You are not connected! For connection type command: connect and then login"
        client.display() # display errors or notes
    print "[BATCH: END LOOP prompt]"
    client.close()
    print "[END BATCH]"


if __name__ == '__main__':
    main()
