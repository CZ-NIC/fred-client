#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
#263    unittesty na pravo na pristup do dane zony
Ticket #253 (defect)
    V tuto chvili se nikde netestuje zda ma prihlaseny registrator pravo na praci v dane zone. 
    V pripade ze nema je treba u opraci *_domain vyhodit chybovou hlasku.
"""
import time
import unittest
import ccReg
import unitest_ccreg_share

#-----------------------
CCREG_CONTACT1 = 'CID:TDOMCONT01'
CCREG_NSSET1 = 'NSSID:TDOMNSSET01'
CCREG_DOMAIN1 = 'hokus-pokus.cz'
CCREG_DOMAIN2 = '0.1.1.7.4.5.6.2.2.0.2.4.e164.arpa'
CCREG_DOMAIN3 = '6.2.2.0.2.4.e164.arpa'
CCREG_DOMAIN_PASSW = 'heslicko'
CCREG_DOMAIN_PASSW_NEW = 'noveheslo'
#-----------------------
DOMAIN_1, DOMAIN_2, CHANGE_DOMAIN, DOMAIN_3  = range(4)
#-----------------------
CCREG_DATA = (
    { # DOMAIN_1
       'name':CCREG_DOMAIN1,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(CCREG_CONTACT1,),
    }, 
    { # DOMAIN_2
       'name':CCREG_DOMAIN2,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(CCREG_CONTACT1,),
    }, 
    )

NSSET_DNS = (
            {'name': u'ns.pokus1.cz', 'addr': ('217.31.204.130','217.31.204.129')},
            {'name': u'ns.pokus2.cz', 'addr': ('217.31.204.131','217.31.204.127')},
        )
    
class Test(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription())
        unitest_ccreg_share.reset_client(epp_cli)

    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, handle_contact, handle_nsset, log_fp
        # create client object
        epp_cli = ccReg.Client()
        epp_cli._epp.load_config()
        #epp_cli_TRANSF = ccReg.Client()
        #epp_cli_TRANSF._epp.load_config()
        # vypnutí validátoru
        epp_cli._epp.set_validate(0)
        #epp_cli_TRANSF.set_validate(0)
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        #epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        #self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')
        # logovací soubor
        if ccReg.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(ccReg.translate.options['log'],'w')

    def test_030(self):
        '1. Zalozeni pomocneho kontaktu'
        epp_cli.create_contact(CCREG_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_034(self):
        '1.1 Zalozeni pomocneho nssetu'
        epp_cli.create_nsset(CCREG_NSSET1, NSSET_DNS, CCREG_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    # -------------------------------------
    # start test
    # -------------------------------------

    def test_050(self):
        '4.5 (Ticket #119) Pokus o zalozeni domeny tretiho radu www.pokus.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('www.pokus.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_060(self):
        '4.6 (Ticket #122) Pokus o zalozeni neplatne domeny www..cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('www..cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_070(self):
        '4.7 (Ticket #126) Pokus o zalozeni neplatne domeny -w.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('-w.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_080(self):
        '4.8 (Ticket #126) Pokus o zalozeni neplatne domeny w-.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('w-', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_090(self):
        '4.9 (Ticket #126) Pokus o zalozeni neplatne domeny w--w.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('w--w.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_100(self):
        '4.10  Pokus o zalozeni neplatne domeny päpa.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('päpa.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_101(self):
        '4.10.1  Pokus o zalozeni neplatne domeny $$$$$.cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('$$$$$.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_110(self):
        '4.11  Pokus o zalozeni neplatne domeny .cz'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_120(self):
        '4.12  Pokus o zalozeni neplatne domeny nic.cx'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('nic.cx', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_130(self):
        '4.13  Pokus o zalozeni neplatne domeny nicnet'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('nicnet', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_140(self):
        '4.14  Pokus o zalozeni neplatne domeny test-nic.net'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('test-nic.net', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_150(self):
        '4.15  Pokus o zalozeni neplatne domeny "test nic.cz"'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('test nic.cz', d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_160(self):
        '4.16  Pokus o zalozeni neplatne domeny "abc"*256 + ".cz" (presahuje maximalni delku)'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain('%s.cz'%('abc'*256), d['registrant'], d['pw'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_170(self):
        '4.17 (Ticket #250) Pokus o zalozeni domeny enum bez valExpDate'
        d = CCREG_DATA[DOMAIN_2]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_180(self):
        '4.18  Zalozeni nove domeny enum'
        d = CCREG_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_190(self):
        '4.19  Smazani domeny enum'
        d = CCREG_DATA[DOMAIN_2]
        epp_cli.delete_domain(d['name'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
##    def test_130(self):
##        '4.13 Update vsech parametru domeny'
##        epp_cli.update_domain(CCREG_DOMAIN1, None, None, CCREG_DATA[CHANGE_DOMAIN])
##        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    # -------------------------------------
    # clean supported objects
    # -------------------------------------
    def test_990(self):
        '4.LAST.1 Smazani pomocneho nssetu'
        epp_cli.delete_nsset(CCREG_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
    
    def test_992(self):
        '4.LAST.2 Smazani pomocneho kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))


epp_cli, epp_cli_TRANSF, epp_cli_log, log_fp, log_step = (None,)*5

if __name__ == '__main__':
    if ccReg.translate.option_errors:
        print ccReg.translate.option_errors
    elif ccReg.translate.options['help']:
        print unitest_ccreg_share.__doc__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()
