#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
4.1  Check na seznam dvou neexistujicich domen
4.2  Pokus o Info na neexistujici domenu
4.3  Zalozeni pomocneho kontaktu
4.4  Zalozeni pomocneho nssetu
4.5  Pokus o zalozeni domeny s neexistujicim nssetem
4.6  Pokus o zalozeni domeny s neexistujicim kontaktem
...  Pokusy o zalozeni domeny s neplatnym nazvem
4.7  Zalozeni nove domeny
4.8  Zalozeni nove domeny enum
4.9  Pokus o zalozeni jiz existujici domeny
4.10 Check na seznam existujici a neexistujici domeny
4.11 Info na existujici domenu a kontrola hodnot
4.12 Update vsech parametru domeny
4.13 Pokus o update stavu Server*
4.14 Update stavu clientDeleteProhibited a pokus o smazani
4.15 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu
4.16 Pokus o Renew domain s nespravnym datumem
4.17 Renew domain
4.18 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)
4.19 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)
4.20 Druhy registrator: Trasfer domeny
4.21 Druhy registrator: Zmena hesla po prevodu domeny
4.22 Zmena hesla domeny, ktera registratorovi jiz nepatri
4.23 Pokus o smazani domeny, ktera registratorovi jiz nepatri
4.24 Druhy registrator: Smazani obou domen
4.25 Check na smazanou domenu
4.26 Smazani pomocnych kontaktu a nssetu
"""
import sys
import unittest
import ccReg

#----------------------------------------------
# Nastavení serveru, na kterém se bude testovat
# (Pokud je None, tak je to default)
#----------------------------------------------
SESSION_NAME = None # 'curlew'

#-----------------------
CCREG_CONTACT1 = 'CONT01'
CCREG_NSSET1 = 'NSSET01'
CCREG_DOMAIN1 = 'hokus-pokus.cz'
CCREG_DOMAIN2 = '0.1.1.7.4.5.2.2.2.0.2.4.e164.arpa'
CCREG_DOMAIN_PASSW = 'heslicko'
#-----------------------
CONTACT_1, NSSET_1, DOMAIN_1, DOMAIN_2  = range(4)
#-----------------------
CCREG_DATA = (
    # CONTACT_1
    (CCREG_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ'),
    # NSSET_1
    (CCREG_NSSET1, 'heslo', (('ns1.domain.cz', ('217.31.207.130', '217.31.207.129')),)),
    { # DOMAIN_1
       'name':CCREG_DOMAIN1,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': ('3','y'),
       'contact':(CCREG_CONTACT1,),
    }, 
    { # DOMAIN_2
       'name':CCREG_DOMAIN2,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': ('3','y'),
       'contact':(CCREG_CONTACT1,),
    }, 
    )

class Test(unittest.TestCase):

    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, handle_contact, handle_nsset
        # create client object
        epp_cli = ccReg.Client()
        epp_cli_TRANSF = ccReg.Client()
        if SESSION_NAME:
            # nastavení serveru
            epp_cli._epp.set_session_name(SESSION_NAME)
            epp_cli_TRANSF._epp.set_session_name(SESSION_NAME)
        epp_cli._epp.load_config()
        epp_cli_TRANSF._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')



def __get_reason__(client):
    'Returs reason a errors from client object'
    reason = get_local_text(client.is_val('reason'))
    er = []
    for error in client.is_val('errors'):
        er.append(get_local_text(error))
    return  '%s ERRORS:[%s]\nCOMMAND: %s'%(reason, '\n'.join(er), get_local_text(client._epp.get_command_line()))

epp_cli, epp_cli_TRANSF = None,None
get_local_text = ccReg.session_base.get_ltext

if __name__ == '__main__':
    print 'pracuji na tom...'
##    if len(sys.argv) > 1: SESSION_NAME = sys.argv[1]
##    suite = unittest.TestSuite()
##    suite.addTest(unittest.makeSuite(Test))
##    unittest.TextTestRunner(verbosity=2).run(suite)

