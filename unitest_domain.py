#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
4.1  Check na seznam dvou neexistujicich domen
4.2  Pokus o Info na neexistujici domenu
4.3  Zalozeni pomocneho kontaktu
4.4  Zalozeni pomocneho nssetu
4.5  Pokus o zalozeni domeny s neexistujicim nssetem
4.6  Pokus o zalozeni domeny s neexistujicim kontaktem
4.7  Pokusy o zalozeni domeny s neplatnym nazvem
4.8  Zalozeni nove domeny
4.9  Zalozeni nove domeny enum
4.10  Pokus o zalozeni jiz existujici domeny
4.11 Check na seznam existujici a neexistujici domeny
4.12 Info na existujici domenu a kontrola hodnot
4.13 Update vsech parametru domeny
4.14 Pokus o update stavu Server*
4.15 Update stavu clientDeleteProhibited a pokus o smazani
4.16 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu
4.17 Pokus o Renew domain s nespravnym datumem
4.18 Renew domain
4.19 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)
4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)
4.21 Druhy registrator: Trasfer domeny
4.22 Druhy registrator: Zmena hesla po prevodu domeny
4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri
4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri
4.25 Druhy registrator: Smazani obou domen
4.26 Check na smazanou domenu
4.27 Smazani pomocnych kontaktu a nssetu
"""
import time
import unittest
import ccReg
import unitest_ccreg_share

##    1 |   222 | D0000000222-CZ | 1.1.1.7.7.7.0.2.4.e164.arpa
##    1 |   340 | D0000000340-CZ | 9.1.7.4.5.2.2.2.0.2.4.e164.arpa
##    1 |   223 | D0000000223-CZ | 1.2.2.7.7.7.0.2.4.e164.arpa
##    1 |   341 | D0000000341-CZ | 1.8.1.7.4.5.2.2.2.0.2.4.e164.arpa
##    1 |   184 | D0000000184-CZ | 1.1.1.1.1.1.1.1.1.0.2.4.e164.arpa
##    1 |   194 | D0000000194-CZ | 1.2.1.1.1.1.1.1.1.0.2.4.e164.arpa
##    1 |   195 | D0000000195-CZ | 1.3.1.1.1.1.1.1.1.0.2.4.e164.arpa
##    1 |   196 | D0000000196-CZ | 1.4.1.1.1.1.1.1.1.0.2.4.e164.arpa
##    1 | 12637 | D0000012637-CZ | 2.2.2.0.2.4.e164.arpa
##    1 | 12642 | D0000012642-CZ | 4.4.4.0.2.4.e164.arpa

#-----------------------
CCREG_CONTACT1 = 'CID:TDOMCONT01'
CCREG_CONTACT2 = 'CID:TDOMCONT02'
CCREG_NSSET1 = 'NSSID:TDOMNSSET01'
CCREG_NSSET2 = 'NSSID:TDOMNSSET02'
CCREG_DOMAIN1 = 'hokus-pokus.cz' # hokus-pokus.cz sakra.cz
CCREG_DOMAIN2 = '0.1.1.7.4.5.1.2.2.0.2.4.e164.arpa'
##VAL_EX_DATE = '2007-02-02'
CCREG_DOMAIN_PASSW = 'heslicko'
CCREG_DOMAIN_PASSW_NEW = 'noveheslo'
INVALID_DOMAIN_NAME = 'myname.net'
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
    { # modify CHANGE_DOMAIN
      'nsset': CCREG_NSSET2,
      'registrant': CCREG_CONTACT2,
##      'auth_info': {'pw': CCREG_DOMAIN_PASSW_NEW,},
      'pw': CCREG_DOMAIN_PASSW_NEW,
    },
    { # DOMAIN_3 - modified
       'name':CCREG_DOMAIN1,
       'pw':CCREG_DOMAIN_PASSW_NEW,
       'nsset':CCREG_NSSET2,
       'registrant':CCREG_CONTACT2,
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
        unitest_ccreg_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_ccreg_share.reset_client(epp_cli_log)

    def test_000(self):
        '4.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, epp_cli_log, handle_contact, handle_nsset, log_fp
        # create client object
        epp_cli = ccReg.Client()
        epp_cli._epp.load_config(ccReg.translate.options['session'])
        epp_cli_TRANSF = ccReg.Client()
        epp_cli_TRANSF._epp.load_config(ccReg.translate.options['session'])
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        epp_cli_log = epp_cli
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')
        # logovací soubor
        if ccReg.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(ccReg.translate.options['log'],'w')

    def test_010(self):
        '4.1  Check na seznam dvou neexistujicich domen'
        handles = (CCREG_DOMAIN1,'neexist002.cz')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Domena existuje: %s'%name)

    def test_020(self):
        '4.2  Pokus o Info na neexistujici domenu'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_030(self):
        '4.3.1 Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(CCREG_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_031(self):
        '4.3.2 Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(CCREG_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_040(self):
        '4.4.1 Zalozeni 1. pomocneho nssetu'
        epp_cli.create_nsset(CCREG_NSSET1, NSSET_DNS, CCREG_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_041(self):
        '4.4.2 Zalozeni 2. pomocneho nssetu'
        epp_cli.create_nsset(CCREG_NSSET2, NSSET_DNS, CCREG_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_050(self):
        '4.5  Pokus o zalozeni domeny s neexistujicim nssetem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], 'nsset-not-exists', d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_060(self):
        '4.6.1  Pokus o zalozeni domeny s neexistujicim registratorem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], 'reg-not-exists', d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_062(self):
        '4.6.2  Pokus o zalozeni domeny s neexistujicim kontaktem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], 'CXXX0X')
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_070(self):
        '4.7  Pokusy o zalozeni domeny s neplatnym nazvem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(INVALID_DOMAIN_NAME, d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena %s se vytvorila prestoze nemela.'%INVALID_DOMAIN_NAME)

    def test_071(self):
        '4.7.1  Smazani domeny s neplatnym jmenem (pokud byla vytvorena)'
        epp_cli.check_domain(INVALID_DOMAIN_NAME)
        if epp_cli.is_val(('data',INVALID_DOMAIN_NAME)) == 0:
            epp_cli.delete_domain(INVALID_DOMAIN_NAME)
        
    def test_080(self):
        '4.8  Zalozeni nove domeny'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_090(self):
        '4.9.1 Pokus o zalozeni domeny enum bez valExpDate'
        d = CCREG_DATA[DOMAIN_2]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_092(self):
        '4.9.2 Pokus o zalozeni domeny enum s nespravnym valExDate'
        d = CCREG_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*7)) # sedm měsíců
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena enum se vytvorila i kdyz valExDate byl neplatny')
        
    def test_096(self):
        '4.9.3  Zalozeni nove domeny enum'
        d = CCREG_DATA[DOMAIN_2]
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_100(self):
        '4.10  Pokus o zalozeni jiz existujici domeny'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['pw'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se vytvorila prestoze jiz existuje')

    def test_110(self):
        '4.11 Check na seznam existujici a neexistujici domeny'
        handles = (CCREG_DOMAIN1,'neexist002.cz')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(('data',CCREG_DOMAIN1)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002.cz')), 1)

    def test_120(self):
        '4.12 Info na existujici domenu a kontrola hodnot'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __check_equality__(CCREG_DATA[DOMAIN_1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_130(self):
        '4.13 Update vsech parametru domeny'
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, CCREG_DATA[CHANGE_DOMAIN])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_131(self):
        '4.13.2 Kontrola zmenenych udaju'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __check_equality__(CCREG_DATA[DOMAIN_3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_140(self):
        '4.14.1 Pokus o update stavu serverDeleteProhibited'
        status = 'serverDeleteProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)

    def test_141(self):
        '4.14.2 Pokus o update stavu serverUpdateProhibited'
        status = 'serverUpdateProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
    def test_150(self):
        '4.15 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # pokus o smazání
        epp_cli.delete_domain(CCREG_DOMAIN1)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # zrušení stavu
        epp_cli.update_domain(CCREG_DOMAIN1, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_160(self):
        '4.16 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # pokus o změnu
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':'zmena hesla'}})
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se aktualizovala, prestoze mela nastaven status %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # zrušení stavu
        epp_cli.update_domain(CCREG_DOMAIN1, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_170(self):
        '4.17 Pokus o Renew domain s nespravnym datumem'
        epp_cli.renew_domain(CCREG_DOMAIN1, '2000-01-01') # cur_exp_date
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze byl zadan chybny datum cur_exp_date.')

    def test_171(self):
        '4.17.1 Ziskani hodnoty domain_renew pro prikazy renew'
        global domain_renew
        # ziskani hodnoty cur_exp_date
        epp_cli.info_domain(CCREG_DOMAIN2)
        domain_renew = epp_cli.is_val(('data','domain:renew')) # cur_exp_date
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_172(self):
        '4.17.2 Pokus o nastaveni valExDate na 7 mesicu v Renew enum domain'
        period = {'num':'2','unit':'y'}
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*7)) # sedm měsíců
        epp_cli.renew_domain(CCREG_DOMAIN2, domain_renew, period, val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze bylo valExDate zadano na 7 mesicu.')
        
    def test_173(self):
        '4.17.3 Nastaveni valExDate na dva mesice v Renew enum domain'
        period = {'num':'2','unit':'y'}
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*2)) # dva měsíce
        epp_cli.renew_domain(CCREG_DOMAIN2, domain_renew, period, val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_174(self):
        '4.17.4 Pokus o update enum domeny na neplatny valExDate'
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*7)) # sedm měsíců
        epp_cli.update_domain(CCREG_DOMAIN2, None, None, None, val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze bylo valExDate zadano na 7 mesicu.')

    def test_175(self):
        '4.17.5 Update enum domeny s valExDate na 5 mesicu.'
        val_ex_date = time.strftime("%Y-%m-%d",time.localtime(time.time()+60*60*24*30*5)) # pět měsíců
        epp_cli.update_domain(CCREG_DOMAIN2, None, None, None, val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_180(self):
        '4.18 Renew domain o tri roky'
        # ziskani hodnoty cur_exp_date
        epp_cli.info_domain(CCREG_DOMAIN1)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        # prodlozeni o nastavenou periodu
        period = {'num':'3','unit':'y'}
        renew = epp_cli.is_val(('data','domain:renew')) # cur_exp_date
        unitest_ccreg_share.reset_client(epp_cli)
        epp_cli.renew_domain(CCREG_DOMAIN1, renew, period)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        unitest_ccreg_share.reset_client(epp_cli)
        # kontrola nastaveni
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        is_equal, expiration = unitest_ccreg_share.check_date(renew, period, renew)
        exDate = epp_cli.is_val(('data','domain:exDate'))[:10]
        self.assert_(expiration == exDate, 'Expirace neprosla. Data domain:exDate nesouhlasi: je: %s ma byt: %s'%(exDate, expiration))
        
    def test_190(self):
        '4.19 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_domain(CCREG_DOMAIN1, CCREG_DOMAIN_PASSW_NEW)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_200(self):
        '4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.transfer_domain(CCREG_DOMAIN1, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))
        
    def test_210(self):
        '4.21 Druhy registrator: Trasfer domeny'
        epp_cli_TRANSF.transfer_domain(CCREG_DOMAIN1, CCREG_DOMAIN_PASSW_NEW)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))
        
    def test_220(self):
        '4.22 Druhy registrator: Zmena hesla po prevodu domeny'
        epp_cli_TRANSF.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':CCREG_DOMAIN_PASSW}})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))
        
    def test_230(self):
        '4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':'moje-heslo'}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_240(self):
        '4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri'
        epp_cli.delete_domain(CCREG_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se smazala prestoze nemela')
        
    def test_250(self):
        '4.25.1 Druhy registrator: Smazani domeny'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.delete_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))

    def test_251(self):
        '4.25.2 Druhy registrator: Smazani domeny enum'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.delete_domain(CCREG_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_260(self):
        '4.26 Check na smazanou domenu'
        epp_cli.check_domain(CCREG_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        self.assertEqual(epp_cli.is_val(('data',CCREG_DOMAIN2)), 1, 'Domena existuje: %s'%CCREG_DOMAIN2)
        
    def test_270(self):
        '4.27.0 Smazani 2. pomocneho nssetu'
        epp_cli.delete_nsset(CCREG_NSSET2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_271(self):
        '4.27.1 Smazani 1. pomocneho nssetu'
        epp_cli.delete_nsset(CCREG_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_272(self):
        '4.27.2 Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_273(self):
        '4.27.3 Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))


def __check_equality__(cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    ##============================================================
    ##COLS:
    ##{   'name': 'hokus-pokus.cz', 
    ##    'period': {'num': u'3', 'unit': u'y'}, 
    ##    'contact': ('TDOMCONT01',), 
    ##    'nsset': 'TDOMNSSET01', 
    ##    'registrant': 'TDOMCONT01', 
    ##    'pw': 'heslicko'}
    ##------------------------------------------------------------
    ##DATA:
    ##{   'domain:contact': u'TDOMCONT01', 
    ##    'domain:crID': u'REG-LRR', 
    ##    'domain:clID': u'REG-LRR', 
    ##    'domain:name': u'hokus-pokus.cz', 
    ##    'domain:status.s': u'ok', 
    ##    'domain:exDate': u'2009-08-10T00:00:00.0Z', 
    ##    'domain:nsset': u'TDOMNSSET01', 
    ##    'domain:pw': u'heslicko', 
    ##    'domain:crDate': u'2006-08-10T09:58:16.0Z', 
    ##    'domain:roid': u'D0000000219-CZ', 
    ##    'domain:registrant': u'TDOMCONT01', 
    ##    'domain:renew': u'2009-08-10', 
    ##    'domain:contact.type': u'admin'}
    ##____________________________________________________________
    ref_value = epp_cli._epp.get_config_value('connect','username')
    unitest_ccreg_share.err_not_equal(errors, data, 'domain:clID', ref_value)
    unitest_ccreg_share.err_not_equal(errors, data, 'domain:name', cols['name'])
    unitest_ccreg_share.err_not_equal(errors, data, 'domain:nsset', cols['nsset'])
    unitest_ccreg_share.err_not_equal(errors, data, 'domain:pw', cols['pw'])
    if not unitest_ccreg_share.are_equal(data['domain:registrant'], cols['registrant']):
        errors.append('Data domain:registrant nesouhlasi. JSOU:%s MELY BYT:%s'%(unitest_ccreg_share.make_str(data['domain:registrant']), unitest_ccreg_share.make_str(cols['registrant'])))
    is_equal, exdate = unitest_ccreg_share.check_date(data['domain:exDate'], cols['period'])
    if not is_equal:
        errors.append('Data domain:exDate nesouhlasi: jsou: %s a mely byt: %s'%(data['domain:exDate'], exdate))
    actual_time = time.strftime('%Y-%m-%d',time.gmtime())
    if data['domain:crDate'][:10] != actual_time:
        errors.append('Data domain:crDate nesouhlasi: jsou: %s a mely by byt: %s'%(data['domain:crDate'],actual_time))
    return errors

epp_cli, epp_cli_TRANSF, epp_cli_log, log_fp, log_step = (None,)*5
domain_renew = ''

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
