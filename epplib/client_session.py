# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
# Tento modul je správce EPP dokumentu. Správce přijímá vstupní údaje,
# ověří je a pak si z nich nechá sestavit EPP dokument.
# Správce se stará o session data, která získal od serveru.
# Přijaté EPP odpovědi od serveru si správce nechá rozložit na hodnoty
# a ty pak zobrazí v nějakém vybraném formátu.
# Zobrazuje help. Přepíná jazykovou verzi.
#
##from client_session_transfer import ManagerTransfer
from client_session_command import ManagerCommand
from client_session_receiver import ManagerReceiver

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

TEST = 1

class Manager(ManagerCommand, ManagerReceiver):
    """EPP client support.
    Hold client ID, login, clTRID and other session variables.
    Parse command line and call EPP builder.
    """
    def __init__(self):
##        ManagerTransfer.__init__(self)
        ManagerCommand.__init__(self)
        ManagerReceiver.__init__(self)

    def welcome(self):
        msg = u"""
+----------------------------+
|    Vítejte v EPP clientu   |
+----------------------------+
Revision: $Id$
"""
        return msg
        
def debug_label(text,message=''):
    print '\n'
    print '-'*60
    print '***',text.upper(),'***'
    print '-'*60
    if message: print message

if __name__ == '__main__':
    client = Manager()
    while 1:
        command = raw_input("> (? help, q quit): ")
        if command in ('q','quit','exit','konec'): break
        edoc = client.create_eppdoc(command,TEST)
        client.display()
        if edoc:
            print 'EPP COMMAND:\n%s\n%s'%(edoc,'-'*60)
            if re.match('login',command):
                client._session[ID] = 1 # '***login***' # testovací zalogování
            if re.match('logout',command):
                client._session[ID] = 0 # testovací odlogování
            # client.process_answer(edoc)
            dict_answer = client._epp_cmd.create_data()
            if dict_answer:
                debug_label(u'dict:')
                pprint.pprint(dict_answer)
        print '='*60
    print '[END]'

