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
import ConfigParser
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

    def __save_conf__(self):
        'Save conf file.'
        try:
            fp = open(os.path.expanduser('~/%s'%self._name_conf),'w')
            self._conf.write(fp)
            fp.close()
            self.append_note(_T('Default config file saved. For more see help.'))
        except IOError, (no, msg):
            self.append_error('%s: [%d] %s'%(_T('Impossible saving conf file. Reason'),no,msg))

    def __get_config__(self,section,option,is_int=None):
        'Get value from config and catch exceptions.'
        value=None
        try:
            value = self._conf.get(section,option)
        except ConfigParser.NoSectionError, msg:
            self.append_error('ConfigError: %s'%msg)
        except ConfigParser.NoOptionError, msg:
            self.append_error('ConfigError: %s'%msg)
        if is_int:
            try:
                value = int(value)
            except ValueError, msg:
                self.append_error('Config ${BOLD}%s:${NORMAL} %s.'%(option,msg))
                value = 0
        return value

    def load_config(self):
        "Load config file and init internal variables."
        self._name_conf = '.epp_client.conf'
        self._conf = ConfigParser.SafeConfigParser()
        glob_conf = '/etc/%s'%self._name_conf
        self._conf.read([glob_conf, os.path.expanduser('~/%s'%self._name_conf)])
        if not self._conf.has_section('session'):
            self.__create_default_conf__()
            self.__save_conf__()
        # set session variables
        section = 'session'
        lang = self.__get_config__(section,'lang')
        if lang in self.defs[LANGS]:
            self._session[LANG] = lang
        else:
            self.append_note('%s: ${BOLD}%s${NORMAL} %s'%(_T('This language code is not allowed'),lang,str(self.defs[LANGS])))
##        #!!!
##        for section in self._conf.sections():
##            print "SECTION:",section
##            for name in self._conf.options(section):
##                print name,":",self.__get_config__(section,name)
##        self.display() #!!!
            
        
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

