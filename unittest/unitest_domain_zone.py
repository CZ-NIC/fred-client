#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
#263    unittesty na pravo na pristup do dane zony
Ticket #253 (defect)
    V tuto chvili se nikde netestuje zda ma prihlaseny registrator pravo na praci v dane zone. 
    V pripade ze nema je treba u opraci *_domain vyhodit chybovou hlasku.
"""
import sys
sys.path.insert(0, '..')
import time
import unittest
import fred
import unitest_share

#-----------------------
FRED_CONTACT1 = unitest_share.create_handle('CID:T1')
FRED_NSSET1 = unitest_share.create_handle('NSSID:T1')
FRED_DOMAIN1 = '%s.cz'%unitest_share.create_handle('tset')
FRED_DOMAIN2 = '0.1.1.7.4.5.6.2.2.0.2.4.e164.arpa'
FRED_DOMAIN3 =             '6.2.2.0.2.4.e164.arpa'
FRED_DOMAIN_PASSW = 'heslicko'
FRED_DOMAIN_PASSW_NEW = 'noveheslo'

FRED_ENUM_PREFIX  =           '5.7.2.2.0.2.4.e164.arpa'
FRED_ENUM_ENDUSER = '0.1.1.7.4.5.7.2.2.0.2.4.e164.arpa'

#-----------------------
DOMAIN_1, DOMAIN_2, CHANGE_DOMAIN, DOMAIN_3  = range(4)
#-----------------------
FRED_DATA = (
    { # DOMAIN_1
       'name':FRED_DOMAIN1,
       'auth_info':FRED_DOMAIN_PASSW,
       'nsset':FRED_NSSET1,
       'registrant':FRED_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(FRED_CONTACT1,),
    }, 
    { # DOMAIN_2
       'name':FRED_DOMAIN2,
       'auth_info':FRED_DOMAIN_PASSW,
       'nsset':FRED_NSSET1,
       'registrant':FRED_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(FRED_CONTACT1,),
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
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)

    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli_log, epp_cli, epp_cli_TRANSF, handle_contact, handle_nsset, log_fp
        # create client object
        epp_cli = fred.Client()
        epp_cli._epp.load_config()
        epp_cli_TRANSF = fred.Client()
        epp_cli_TRANSF._epp.load_config()
        # Validation MUST be disabled bycause we test commands with misssing required parameters
        epp_cli.set_validate(0)
        epp_cli_TRANSF.set_validate(0)
        if fred.translate.options['no_validate'] == '':
            # Set ON validation of the server answer. 
            # This behavor is possible switch off by option -x --no_validate
            epp_cli._epp.run_as_unittest = 1
            epp_cli_TRANSF._epp.run_as_unittest = 1

        # login:
        # prihlasovaci udaje si nastavte v config v sekci [connect_...]:
        #    [connect_curlew]
        #    username = REG-UNITTEST1
        #    password = 123456789
        #    username2 = REG-UNITTEST2
        #    password2 = 123456789
        logins = epp_cli._epp.get_logins_and_passwords(2) # 2 - num of login tuples: [('login','password'), ...]
        epp_cli.login(logins[0][0], logins[0][1])
        epp_cli_TRANSF.login(logins[1][0], logins[1][1])

        epp_cli_log = epp_cli
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-UNITTEST2" pro transfer.')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')

    def test_030(self):
        '1. Zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Ulice','Praha','12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_034(self):
        '1.1 Zalozeni pomocneho nssetu'
        epp_cli.create_nsset(FRED_NSSET1, NSSET_DNS, FRED_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    # -------------------------------------
    # start test
    # -------------------------------------

    def test_050(self):
        '4.5 (Ticket #119) Pokus o zalozeni domeny tretiho radu www.pokus.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('www.pokus.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_060(self):
        '4.6 (Ticket #122) Pokus o zalozeni neplatne domeny www..cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('www..cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_070(self):
        '4.7 (Ticket #126) Pokus o zalozeni neplatne domeny -w.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('-w.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_080(self):
        '4.8 (Ticket #126) Pokus o zalozeni neplatne domeny w-.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('w-', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_090(self):
        '4.9 (Ticket #126) Pokus o zalozeni neplatne domeny w--w.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('w--w.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_100(self):
        '4.10  Pokus o zalozeni neplatne domeny päpa.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('päpa.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_101(self):
        '4.10.1  Pokus o zalozeni neplatne domeny $$$$$.cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('$$$$$.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_110(self):
        '4.11  Pokus o zalozeni neplatne domeny .cz'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_120(self):
        '4.12  Pokus o zalozeni neplatne domeny nic.cx'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('nic.cx', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_130(self):
        '4.13  Pokus o zalozeni neplatne domeny nicnet'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('nicnet', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_140(self):
        '4.14  Pokus o zalozeni neplatne domeny test-nic.net'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('test-nic.net', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_150(self):
        '4.15  Pokus o zalozeni neplatne domeny "test nic.cz"'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain('test nic.cz', d['registrant'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_160(self):
        '4.16  Pokus o zalozeni neplatne domeny "abc"*256 + ".cz" (presahuje maximalni delku)'
        d = FRED_DATA[DOMAIN_1]
        try:
            epp_cli.create_domain('%s.cz'%('abc'*256), d['registrant'], d['auth_info'])
        except fred.FredError, msg:
            # hodnota neprojde přes validátor
            unitest_share.write_log_message(log_fp, '%s\n%s'%(self.test_160.__doc__,msg))
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_170(self):
        '4.17 (Ticket #250) Pokus o zalozeni domeny enum bez valExpDate'
        d = FRED_DATA[DOMAIN_2]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], None, d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_180(self):
        '4.18  Zalozeni ENUM domeny (enduser)'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], None, d['period'], d['contact'], val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_190(self):
        '4.19 Zalozeni ENUM domeny (prefix)'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(FRED_ENUM_PREFIX, d['registrant'], None, None, None, None, None, val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_200(self):
        '4.20 DRUHY REGISTRATOR: Pokus o zalozeni ENUM do jine zony (prefix je soucasti enduser)'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        # epp_cli_TRANSF.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'], val_ex_date)
        epp_cli_TRANSF.create_domain(FRED_DOMAIN3, d['registrant'], None, None, None, None, None, val_ex_date)
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, 'ENUM domena se vytvorila prestoze patri do jiz obsazene zony.')

    def test_210(self):
        '4.21 DRUHY REGISTRATOR: Pokus o zalozeni ENUM do jine zony (enduser je v rozsahu prefixu)'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli_TRANSF.create_domain(FRED_ENUM_ENDUSER, d['registrant'], None, None, None, None, None, val_ex_date)
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, 'ENUM domena se vytvorila prestoze patri do jiz obsazene zony.')

    def test_220(self):
        '4.22 Pokus o zalozeni ENUM ve vlastni zone (prefix je soucasti enduser)'
        global epp_cli_log
        epp_cli_log = epp_cli
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(FRED_DOMAIN3, d['registrant'], None, None, None, None, None, val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'ENUM FRED_DOMAIN3 se vytvorila prestoze patri do jiz obsazene zony.')

    def test_230(self):
        '4.21 Pokus o zalozeni ENUM ve vlastni zone (enduser je v rozsahu prefixu)'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(FRED_ENUM_ENDUSER, d['registrant'], None, None, None, None, None, val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'ENUM FRED_ENUM_ENDUSER se vytvorila prestoze patri do jiz obsazene zony.')
        
    # -------------------------------------
    # clean supported objects
    # -------------------------------------
##    def test_950(self):
##        '4.-6  Smazani domeny FRED_ENUM_ENDUSER'
##        epp_cli.delete_domain(FRED_ENUM_ENDUSER)
##        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
##
##    def test_960(self):
##        '4.-5  Smazani domeny FRED_DOMAIN3'
##        epp_cli.delete_domain(FRED_DOMAIN3)
##        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_970(self):
        '4.-4  Smazani domeny enum'
        epp_cli.delete_domain(FRED_ENUM_PREFIX)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_980(self):
        '4.-3  Smazani domeny enum'
        d = FRED_DATA[DOMAIN_2]
        epp_cli.delete_domain(d['name'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_990(self):
        '4.-2 Smazani pomocneho nssetu'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_992(self):
        '4.-1 Smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_998(self):
        '98. logout'
        epp_cli_TRANSF.logout()
        self.assertEqual(epp_cli_TRANSF.is_val(), 1500, unitest_share.get_reason(epp_cli))

    def test_999(self):
        '99. logout'
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))


epp_cli, epp_cli_TRANSF, epp_cli_log, log_fp, log_step = (None,)*5

if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()
