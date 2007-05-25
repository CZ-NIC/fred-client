#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
4.0 Inicializace spojeni a definovani testovacich handlu
4.1  Check na seznam dvou neexistujicich domen
4.2  Pokus o Info na neexistujici domenu
4.3.1 Zalozeni 1. pomocneho kontaktu
4.3.2 Zalozeni 2. pomocneho kontaktu
4.4.1 Zalozeni 1. pomocneho nssetu
4.4.2 Zalozeni 2. pomocneho nssetu
4.5  Pokus o zalozeni domeny s neexistujicim nssetem
4.6.1  Pokus o zalozeni domeny s neexistujicim registratorem
4.6.2  Pokus o zalozeni domeny s neexistujicim kontaktem
4.7  Pokusy o zalozeni domeny s neplatnym nazvem
4.7.1  Smazani domeny s neplatnym jmenem (pokud byla vytvorena)
4.7.2  Pokus o zalozeni domeny se dvema stejnymi admin kontakty
4.8  Zalozeni nove domeny
4.8.1  Zalozeni nove domeny s povinnymi parametry - jen s registrantem
4.9.1 Pokus o zalozeni domeny enum bez valExpDate
4.9.2 Pokus o zalozeni domeny enum s valExDate = 6 mes + 1 den
4.9.3 Pokus o zalozeni domeny enum s valExDate = aktualni datum
4.9.3  Zalozeni nove domeny enum valExDate = dnes + 6 mes
4.10  Pokus o zalozeni jiz existujici domeny
4.11 Check na seznam existujici a neexistujici domeny
4.12.1 Info na existujici domenu a kontrola hodnot
4.12.2 Pokus o update domeny s dvema shodnymi admin kontakty
4.12.3 Pokus o odebrani neexistujiciho admin kontaktu domeny
4.13.1 Update vsech parametru domeny
4.13.2 Kontrola zmenenych udaju
4.13.3 Resetovani nssetu
4.13.4 Kontrola zmenenych udaju po resetovani nssetu
4.14.1 Zmena jen auth_info
4.14.2 Kontrola zmenenych udaju po zmene pouze auth_info
4.17 Pokus o Renew domain s nespravnym datumem
4.17.1 Ziskani hodnoty domain_renew pro prikazy renew
4.17.2 Pokus o nastaveni valExDate na 7 mesicu v Renew enum domain
4.17.3 Nastaveni valExDate na dva mesice v Renew enum domain
4.17.4 Pokus o update enum domeny na neplatny valExDate
4.17.5 Pokus update domeny, ktera neni ENUM, s valExDate.
4.17.6 Update enum domeny s valExDate na 5 mesicu.
4.18.0 Nastaveni valExDate na dnes+15dni (neni v ochranne lhute)
4.18.1 Pokus o prodlouzeni validace o 6 mesicu ode dne valExDate s prekrocenim 14 denni lhuty
4.18.2 Nastaveni valExDate na dnes+14dni (je v ochranne lhute)
4.18.3 Pokus o prodlouzeni validace o 6 mesicu + 15 dni v ochranne lhute
4.18.4 Prodlouzeni validace o 6 mesicu + 14 dni v ochranne lhute
4.19 Renew domain o tri roky
4.19.5 Trasfer na vlastni domenu (Objekt je nezp\u016fsobil\u00fd pro transfer)
4.19.6 Vymazani vsech poll zprav z fronty kvuli generovani poll zpravy z transferu
4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba opr\u00e1vn\u011bn\u00ed)
4.21 Druhy registrator: Trasfer domeny
4.22 Druhy registrator: Zmena hesla po prevodu domeny
4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri
4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri
4.24.2 Poll req - Kontrola, ze byla vygenerovana zprava o transferu.
4.24.3 Poll ack - Vyrazeni zpravy o transferu z fronty.
4.25.1 Druhy registrator: Smazani domeny
4.25.2 Druhy registrator: Smazani domeny enum
4.25.3 Druhy registrator: Smazani domeny
4.26 Check na smazanou domenu
4.27.0 Smazani 2. pomocneho nssetu
4.27.1 Smazani 1. pomocneho nssetu
4.27.2 Smazani 2. pomocneho kontaktu
4.27.3 Smazani 1. pomocneho kontaktu
"""
import re
import time
import unittest
import fred
import unitest_share

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
FRED_CONTACT1 = unitest_share.create_handle('CID:D1')
FRED_CONTACT2 = unitest_share.create_handle('CID:D2')
FRED_NSSET1 = unitest_share.create_handle('NSSID:D1')
FRED_NSSET2 = unitest_share.create_handle('NSSID:D2')
FRED_DOMAIN1 = '%s.cz'%unitest_share.create_handle('test')
FRED_DOMAIN2 = unitest_share.create_enumdomain(); 
# old  '0.1.1.7.4.5.1.2.2.0.2.4.e164.arpa'
FRED_DOMAIN3 = '%s.cz'%unitest_share.create_handle('tmp')
FRED_DOMAIN_PASSW = 'heslicko'
FRED_DOMAIN_PASSW_NEW = 'noveheslo'
INVALID_DOMAIN_NAME = 'myname.net'
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
    { # modify CHANGE_DOMAIN
      'nsset': FRED_NSSET2,
      'registrant': FRED_CONTACT2,
      'auth_info': FRED_DOMAIN_PASSW_NEW,
    },
    { # DOMAIN_3 - modified
       'name':FRED_DOMAIN1,
       'auth_info':FRED_DOMAIN_PASSW_NEW,
       'nsset':FRED_NSSET2, # tato hodnota se pak zresetuje
       'registrant':FRED_CONTACT2,
       'period': {'num':'3','unit':'y'},
       'contact':(FRED_CONTACT1,),
    }, 
    )

NSSET_DNS = (
            {'name': u'ns.pokus1.cz', 'addr': ('217.31.204.130','217.31.204.129')},
            {'name': u'ns.pokus2.cz', 'addr': ('217.31.204.131','217.31.204.127')},
        )


class TestDomain(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)

    def test_000(self):
        '4.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, epp_cli_log, handle_contact, handle_nsset, log_fp
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

    def test_010(self):
        '4.1  Check na seznam dvou neexistujicich domen'
        handles = (FRED_DOMAIN1,'neexist002.cz')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Domena existuje: %s'%name)

    def test_020(self):
        '4.2  Pokus o Info na neexistujici domenu'
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_030(self):
        '4.3.1 Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_031(self):
        '4.3.2 Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4.4.1 Zalozeni 1. pomocneho nssetu'
        epp_cli.create_nsset(FRED_NSSET1, NSSET_DNS, FRED_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_041(self):
        '4.4.2 Zalozeni 2. pomocneho nssetu'
        epp_cli.create_nsset(FRED_NSSET2, NSSET_DNS, FRED_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '4.5  Pokus o zalozeni domeny s neexistujicim nssetem'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], 'nsset-not-exists', d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)


    def test_060(self):
        '4.6.1  Pokus o zalozeni domeny s neexistujicim registratorem'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], 'reg-not-exists', d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_062(self):
        '4.6.2  Pokus o zalozeni domeny s neexistujicim kontaktem'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], 'CXXX0X')
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_070(self):
        '4.7  Pokusy o zalozeni domeny s neplatnym nazvem'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(INVALID_DOMAIN_NAME, d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena %s se vytvorila prestoze nemela.'%INVALID_DOMAIN_NAME)

    def test_071(self):
        '4.7.1  Smazani domeny s neplatnym jmenem (pokud byla vytvorena)'
        epp_cli.check_domain(INVALID_DOMAIN_NAME)
        if epp_cli.is_val(('data',INVALID_DOMAIN_NAME)) == 0:
            epp_cli.delete_domain(INVALID_DOMAIN_NAME)

    def test_072(self):
        '4.7.2  Pokus o zalozeni domeny se dvema stejnymi admin kontakty'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], (FRED_CONTACT1, FRED_CONTACT1))
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

        
    def test_080(self):
        '4.8  Zalozeni nove domeny'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_082(self):
        '4.8.1  Zalozeni nove domeny s povinnymi parametry - jen s registrantem'
        epp_cli.create_domain(FRED_DOMAIN3, FRED_DATA[DOMAIN_2]['registrant'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_090(self):
        '4.9.1 Pokus o zalozeni domeny enum bez valExpDate'
        d = FRED_DATA[DOMAIN_2]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_092(self):
        '4.9.2 Pokus o zalozeni domeny enum s valExDate = 6 mes + 1 den'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = unitest_share.datedelta_from_now(0, 6, 1) # sest mesicu a jeden den
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena enum se vytvorila i kdyz valExDate byl neplatny')

    def test_093(self):
        '4.9.3 Pokus o zalozeni domeny enum s valExDate = aktualni datum'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = unitest_share.datedelta_from_now(0, 0, 0)
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena enum se vytvorila i kdyz valExDate byl neplatny')

        
    def test_096(self):
        '4.9.3  Zalozeni nove domeny enum valExDate = dnes + 6 mes'
        d = FRED_DATA[DOMAIN_2]
        val_ex_date = unitest_share.datedelta_from_now(0, 6) # sest mesicu
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'], val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_100(self):
        '4.10  Pokus o zalozeni jiz existujici domeny'
        d = FRED_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se vytvorila prestoze jiz existuje')

    def test_110(self):
        '4.11 Check na seznam existujici a neexistujici domeny'
        handles = (FRED_DOMAIN1,'neexist002.cz')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(('data',FRED_DOMAIN1)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002.cz')), 1)

    def test_120(self):
        '4.12.1 Info na existujici domenu a kontrola hodnot'
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[DOMAIN_1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_125(self):
        '4.12.2 Pokus o update domeny s dvema shodnymi admin kontakty'
        epp_cli.update_domain(FRED_DOMAIN1, (FRED_CONTACT1, FRED_CONTACT1))
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_126(self):
        '4.12.3 Pokus o odebrani neexistujiciho admin kontaktu domeny'
        epp_cli.update_domain(FRED_DOMAIN1, None, 'cid:tento-neexistuje')
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


    def test_130(self):
        '4.13.1 Update vsech parametru domeny'
        # update_domain(name, add_admin, rem_admin, rem_tempc, chg, val_ex_date, cltrid)
        epp_cli.update_domain(FRED_DOMAIN1, chg = FRED_DATA[CHANGE_DOMAIN])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_131(self):
        '4.13.2 Kontrola zmenenych udaju'
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[DOMAIN_3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_135(self):
        '4.13.3 Resetovani nssetu'
        FRED_DATA[DOMAIN_3]['nsset'] = '' # zresetovani nssetu
        epp_cli.update_domain(FRED_DOMAIN1, chg = {'nsset':''})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


    def test_137(self):
        '4.13.4 Kontrola zmenenych udaju po resetovani nssetu'
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[DOMAIN_3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))


    def test_140(self):
        '4.14.1 Zmena jen auth_info'
        FRED_DATA[DOMAIN_3]['auth_info'] = 'zmena-jen-hesla'
        epp_cli.update_domain(FRED_DOMAIN1, chg = {'auth_info':'zmena-jen-hesla'})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_142(self):
        '4.14.2 Kontrola zmenenych udaju po zmene pouze auth_info'
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[DOMAIN_3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))


    def test_170(self):
        '4.17 Pokus o Renew domain s nespravnym datumem'
        epp_cli.renew_domain(FRED_DOMAIN1, '2000-01-01') # cur_exp_date
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze byl zadan chybny datum cur_exp_date.')

    def test_171(self):
        '4.17.1 Ziskani hodnoty domain_renew pro prikazy renew'
        global domain_renew
        # ziskani hodnoty cur_exp_date
        epp_cli.info_domain(FRED_DOMAIN2)
        domain_renew = epp_cli.is_val(('data','domain:renew')) # cur_exp_date
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_172(self):
        '4.17.2 Pokus o nastaveni valExDate na 7 mesicu v Renew enum domain'
        period = {'num':'2','unit':'y'}
        val_ex_date = unitest_share.datedelta_from_now(0, 7) # sedm měsíců
        epp_cli.renew_domain(FRED_DOMAIN2, domain_renew, period, val_ex_date)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze bylo valExDate zadano na 7 mesicu.')
        
    def test_173(self):
        '4.17.3 Nastaveni valExDate na dva mesice v Renew enum domain'
        period = {'num':'2','unit':'y'}
        val_ex_date = unitest_share.datedelta_from_now(0, 2) # dva měsíce
        epp_cli.renew_domain(FRED_DOMAIN2, domain_renew, period, val_ex_date)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_174(self):
        '4.17.4 Pokus o update enum domeny na neplatny valExDate'
        # update_domain(name, add_admin, rem_admin, rem_tempc, chg, val_ex_date, cltrid)
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 7))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Proslo renew-domain prestoze bylo valExDate zadano na 7 mesicu.')

    def test_175(self):
        '4.17.5 Pokus update domeny, ktera neni ENUM, s valExDate.'
        # unitest_share.datedelta_from_now(0,6,13) # maximální povolené datum
        epp_cli.update_domain(FRED_DOMAIN1, val_ex_date = unitest_share.datedelta_from_now(0, 5))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Probehlo update_domain s valExDate prestoze domena neni ENUM.')

    def test_176(self):
        '4.17.6 Update enum domeny s valExDate na 5 mesicu.'
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 5))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_180(self):
        '4.18.0 Nastaveni valExDate na dnes+15dni (neni v ochranne lhute)'
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 0, 15))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_181(self):
        '4.18.1 Pokus o prodlouzeni validace o 6 mesicu + 1 den (mimo ochrannou lhutu)'
        # val_ex_date je now + 15
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 6, 1))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'update_domain proslo s val_ex_date o jeden den vetsim nez je povoleno.')

    def test_182(self):
        '4.18.2 Nastaveni valExDate na dnes+14dni (je v ochranne lhute)'
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 0, 14))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_183(self):
        '4.18.3 Pokus o prodlouzeni validace o 6 mesicu + 15 dni v ochranne lhute'
        # val_ex_date je now + 14
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 6, 15))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Pokus o prodlouzeni validace o 6 mesicu + 15 dni v ochranne lhute prosel.')

    def test_184(self):
        '4.18.4 Prodlouzeni validace o 6 mesicu + 14 dni v ochranne lhute'
        # val_ex_date je now + 14
        epp_cli.update_domain(FRED_DOMAIN2, val_ex_date = unitest_share.datedelta_from_now(0, 6, 14))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


    def test_190(self):
        '4.19 Renew domain o tri roky'
        # ziskani hodnoty cur_exp_date
        epp_cli.info_domain(FRED_DOMAIN1)
        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        # prodlozeni o nastavenou periodu
        period = {'num':'3','unit':'y'}
        renew = epp_cli.is_val(('data','domain:renew')) # cur_exp_date
        unitest_share.reset_client(epp_cli)
        epp_cli.renew_domain(FRED_DOMAIN1, renew, period)
        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        unitest_share.reset_client(epp_cli)
        # kontrola nastaveni
        epp_cli.info_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        is_equal, expiration = unitest_share.check_date(renew, period, renew)
        exDate = epp_cli.is_val(('data','domain:exDate'))[:10]
        self.assert_(expiration == exDate, 'Expirace neprosla. Data domain:exDate nesouhlasi: je: %s ma byt: %s'%(exDate, expiration))
        
    def test_195(self):
        '4.19.5 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_domain(FRED_DOMAIN1, FRED_DATA[DOMAIN_3]['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_196(self):
        '4.19.6 Vymazani vsech poll zprav z fronty kvuli generovani poll zpravy z transferu'
        epp_cli.poll('req')
        self.failIf(epp_cli.is_val() not in (1000, 1300, 1301), unitest_share.get_reason(epp_cli))
        poll_msg_count = epp_cli.is_val(('data','msgQ.count'))
        if type(poll_msg_count) is int:
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(0, poll_msg_count))
            errors = []
            for n in range(poll_msg_count):
                epp_cli.poll('ack', epp_cli.is_val(('data','msgQ.id')))
                if epp_cli.is_val() != 1000:
                    errors.extend(epp_cli.is_val('errors'))
                unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(n+1, poll_msg_count))
                epp_cli.poll('req')
                if epp_cli.is_val() not in (1000, 1301):
                    errors.extend(epp_cli.is_val('errors'))
                unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(n+1, poll_msg_count))
            self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_200(self):
        '4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.transfer_domain(FRED_DOMAIN1, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_210(self):
        '4.21 Druhy registrator: Trasfer domeny'
        epp_cli_TRANSF.transfer_domain(FRED_DOMAIN1, FRED_DATA[DOMAIN_3]['auth_info'])
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        
    def test_220(self):
        '4.22 Druhy registrator: Zmena hesla po prevodu domeny'
        epp_cli_TRANSF.update_domain(FRED_DOMAIN1, chg = {'auth_info': FRED_DOMAIN_PASSW})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        
    def test_230(self):
        '4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.update_domain(FRED_DOMAIN1, chg = {'auth_info': FRED_DATA[DOMAIN_3]['auth_info']})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_240(self):
        '4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri'
        epp_cli.delete_domain(FRED_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se smazala prestoze nemela')

    def test_242(self):
        '4.24.2 Poll req - Kontrola, ze byla vygenerovana zprava o transferu.'
        global poll_msg_id
        epp_cli.poll('req')
        self.assertEqual(epp_cli.is_val(), 1301, 'Poll zprava chybi, prestoze mela existovat.')
        msg = epp_cli.is_val(('data','msg'))
        self.failIf(type(msg) not in (unicode, str), 'Poll zprava chybi')
        self.failIf(re.search('<domain:id>\s*%s\s*</domain:id>'%re.escape(FRED_DOMAIN1), msg, re.I) is None, 'Zprava se nevztahuje k transferovane domene.')
        poll_msg_id = epp_cli.is_val(('data','msgQ.id'))
        self.failIf(type(poll_msg_id) is not int, 'Chybi ID poll zpravy')


    def test_243(self):
        '4.24.3 Poll ack - Vyrazeni zpravy o transferu z fronty.'
        self.failIf(type(poll_msg_id) is not int, 'Chybi ID poll zpravy')
        epp_cli.poll('ack', poll_msg_id)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


    def test_250(self):
        '4.25.1 Druhy registrator: Smazani domeny'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.delete_domain(FRED_DOMAIN1)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_251(self):
        '4.25.2 Druhy registrator: Smazani domeny enum'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.delete_domain(FRED_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_252(self):
        '4.25.3 Druhy registrator: Smazani domeny'
        epp_cli.delete_domain(FRED_DOMAIN3)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_260(self):
        '4.26 Check na smazanou domenu'
        epp_cli.check_domain(FRED_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        self.assertEqual(epp_cli.is_val(('data',FRED_DOMAIN2)), 1, 'Domena existuje: %s'%FRED_DOMAIN2)
        
    def test_270(self):
        '4.27.0 Smazani 2. pomocneho nssetu'
        epp_cli.delete_nsset(FRED_NSSET2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_271(self):
        '4.27.1 Smazani 1. pomocneho nssetu'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_272(self):
        '4.27.2 Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_273(self):
        '4.27.3 Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))



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
    ##    'auth_info': 'heslicko'}
    ##------------------------------------------------------------
    ##DATA:
    ##{   'domain:contact': u'TDOMCONT01', 
    ##    'domain:crID': u'REG-UNITTEST1', 
    ##    'domain:clID': u'REG-UNITTEST1', 
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
    username, password = epp_cli._epp.get_actual_username_and_password()
    unitest_share.err_not_equal(errors, data, 'domain:clID', username)
    unitest_share.err_not_equal(errors, data, 'domain:name', cols['name'])
    unitest_share.err_not_equal(errors, data, 'domain:nsset', cols['nsset'])
    unitest_share.err_not_equal(errors, data, 'domain:authInfo', cols['auth_info'])
    if not unitest_share.are_equal(data['domain:registrant'], cols['registrant']):
        errors.append('Data domain:registrant nesouhlasi. JSOU:%s MELY BYT:%s'%(unitest_share.make_str(data['domain:registrant']), unitest_share.make_str(cols['registrant'])))
    is_equal, exdate = unitest_share.check_date(data['domain:exDate'], cols['period'])
    if not is_equal:
        errors.append('Data domain:exDate nesouhlasi: jsou: %s a mely byt: %s'%(data['domain:exDate'], exdate))
    actual_time = time.strftime('%Y-%m-%d',time.gmtime())
    if data['domain:crDate'][:10] != actual_time:
        errors.append('Data domain:crDate nesouhlasi: jsou: %s a mely by byt: %s'%(data['domain:crDate'],actual_time))
    return errors

epp_cli, epp_cli_TRANSF, epp_cli_log, log_fp, log_step, poll_msg_id = (None,)*6
domain_renew = ''

if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDomain))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()
