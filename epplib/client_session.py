# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id: client_session.py 482 2006-06-15 14:49:10Z zbohm $
#
# Tento modul je správce EPP dokumentu. Správce přijímá vstupní údaje,
# ověří je a pak si z nich nechá sestavit EPP dokument.
# Správce se stará o session data, která získal od serveru.
# Přijaté EPP odpovědi od serveru si správce nechá rozložit na hodnoty
# a ty pak zobrazí v nějakém vybraném formátu.
# Zobrazuje help. Přepíná jazykovou verzi.
#
"""Usage:
import epplib.client_session
mngr = epplib.client_session.Manager()
epp_doc = mngr.create_eppdoc("hello") # vytvoření příkazu v XML EPP
mngr.connect()                        # připojení k serveru
mngr.send(epp_doc)                    # odeslání dokumentu na server
answer = mngr.receive()               # příjem odpovědi
mngr.process_answer(answer)           # zpracování odpovědi
mngr.close()                          # uzavření spojení
"""
import os
from gettext import gettext as _T
from client_session_base import *
from client_session_receiver import ManagerReceiver
# kontrola na readline
try:
    import readline
except ImportError:
    print u'readline modul chybí - historie příkazů je vypnuta'
    print 'readline module missing - cmd history is diabled'
    readline = None

TEST = 1

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

def set_history(words):
    if readline:
        completer = Completer(words)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)

class Manager(ManagerReceiver):
    """EPP client support.
    Hold client ID, login, clTRID and other session variables.
    Parse command line and call EPP builder.
    """

    def welcome(self):
        "Welcome message"
        welcome = '|   %s   |'%_T('Welcome to the EPP client')
        sep = '+%s+'%('-'*(len(welcome)-2))
        return '%s\n%s\n%s\n%s'%(sep,welcome,sep,_T('For help type "help" (or "h", "?")'))

    def __create_default_conf__(self):
        'Create default config file.'
        conf = """
[session]
lang     cs
validate on
schema   ../mod_eppd/schemas/all-1.0.xsd
poll_ack off

[conect]
host     curlew
port     700
ssl_key  client.key
ssl_cert client.crt

[epp_login]
username REG-LRR
password 123456789
        """
        patt = re.compile('(\w+)\s*=?\s*(.*)')
        patt_sec = re.compile('\[(\w+)\]')
        section=''
        for raw in conf.split('\n'):
            m = patt_sec.match(raw)
            if m:
                section = m.group(1)
                self._conf.add_section(section)
                continue
            if not section: continue
            m = patt.match(raw)
            if not m: continue
            self._conf.set(section, m.group(1), m.group(2))
        
if __name__ == '__main__':
    client = Manager()
    set_history(client.get_command_names())
##    print "TEST ONLY: Session set internal login (not on server)."
##    client._session[ONLINE] = 1
    while 1:
        command = raw_input("> (? help, q quit): ")
        if command in ('q','quit','exit','konec'): break
        edoc = client.create_eppdoc(command,TEST)
        client.display()
        if edoc:
            print 'EPP COMMAND:\n%s\n%s'%(edoc,'-'*60)
            if re.match('login',command):
                client._session[ONLINE] = 1 # '***login***' # testovací zalogování
            if re.match('logout',command):
                client._session[ONLINE] = 0 # testovací odlogování
            client.process_answer(edoc)
        print '='*60
    print '[END]'

