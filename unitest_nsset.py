#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
3.1 Check na seznam dvou neexistujicich nssetu
3.2 Pokus o Info na neexistujici nsset
3.3 Zalozeni pomocneho kontaktu
3.4 Zalozeni neexistujiciho noveho nssetu
3.5 Pokus o zalozeni existujiciho nssetu
3.6 Check na seznam existujiciho a neexistujicich nssetu
3.7 Info na existujici nsset a kontrola hodnot
3.8 Update vsech parametru nssetu
3.9 Pokus o update stavu Server*

Pokus o odstraneni tech-kontaktu
Pokus o odstraneni predposledniho dns
Ticket #113 Update adresy 2001:200::fea5:3015

3.10 Update stavu clientDeleteProhibited a pokus o smazani
3.11 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu
3.12 Vytvoreni domeny napojene na nsset
3.13 Smazani nssetu na ktery existuji nejake vazby
3.14 Trasfer na vlastni nsset (Objekt je nezpůsobilý pro transfer)
3.15 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)
3.16 Druhy registrator: Trasfer nssetu
3.17 Druhy registrator: Zmena hesla po prevodu nssetu
3.18 Zmena hesla na nssetu, ktery registratorovi jiz nepatri
3.19 Smazani domeny
3.20 Smazani nssetu
3.21 Druhy registrator: Smazani nssetu
3.22 Check na smazany nsset
3.23 Smazani pomocnych kontaktu
"""
import unittest
import fred
import unitest_share

# FRED_DATA[1] - create
# FRED_DATA[2] - modify
# FRED_DATA[3] - modified
FRED_NSSET1 = unitest_share.create_handle('NSSID:U1') ## 'NSSID:examp2134'
FRED_HANDLE = unitest_share.create_handle('NSSID:U2') ## 'NSSID:unittest2'
FRED_NOTEXIST = unitest_share.create_handle('NSSID:NE')
FRED_CONTACT1 = unitest_share.create_handle('CID:U1') ## 'CID:UNITTEST1'
FRED_CONTACT2 = unitest_share.create_handle('CID:U2') ## 'CID:UNITTEST2'
NSSET_PASSWORD = 'heslicko'
NSSET_GENPSW = ''
FRED_DATA = ( 
    { # 0. template
    },
    #-------------------------------------------------------
    { # 1. create
    'id': FRED_HANDLE, # (required)
    'auth_info': 'heslo', # (required)
    'dns': ( # (required)               list with max 9 items.
        {'name': 'ns.name1.cz', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') },
        {'name': 'ns.name2.cz', 'addr': ('217.31.206.130','217.31.206.129','217.31.206.128') },
        ),
    'tech': (FRED_CONTACT1,)  # (optional)             unbounded list
    },
    #-------------------------------------------------------
    { # 2. modify
    'id': FRED_HANDLE, # (required)
    'add': {
        'dns': (
            {'name':'ns.name3.cz','addr':('217.31.205.130','217.31.205.129','217.31.205.128')},
            {'name':'ns.name4.cz','addr':('217.31.204.130','217.31.204.129','217.31.204.128')},
        ),
        'tech':FRED_CONTACT2,
        #'status':'clientDeleteProhibited',
    },
    'rem': {
        'name':('ns.name1.cz','ns.name2.cz'),
        'tech':FRED_CONTACT1,
        #'status':'clientDeleteProhibited',
    },
    'chg': {
        'auth_info':NSSET_PASSWORD
    },
    },
    #-------------------------------------------------------
    { # 3. modified
    'id': FRED_HANDLE,
    'auth_info': NSSET_PASSWORD,
    'dns': (
            {'name':'ns.name3.cz','addr':('217.31.205.130','217.31.205.129','217.31.205.128')},
            {'name':'ns.name4.cz','addr':('217.31.204.130','217.31.204.129','217.31.204.128')},
        ),
    'tech': (FRED_CONTACT2,)
    },
    #-------------------------------------------------------
)

class Test(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_to_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_to_log)
        
    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, epp_to_log, handle_contact, handle_nsset, log_fp
        # Natvrdo definovany handle:
        handle_nsset = FRED_DATA[1]['id'] # 'neexist01'
        handle_contact = FRED_CONTACT1
        # create client object
        epp_cli = fred.Client()
        epp_cli._epp.load_config()
        #epp_cli._epp.set_validate(0)
        epp_cli_TRANSF = fred.Client()
        epp_cli_TRANSF._epp.load_config()
        
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = unitest_share.find_available_handle(epp_cli, 'contact','nexcon')
        # handle_nsset = unitest_share.find_available_handle(epp_cli, 'nsset','nexns')
        # self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        # self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')
        epp_to_log = epp_cli
    
    def test_010(self):
        '3.1 Check na seznam dvou neexistujicich nssetu'
        handles = (handle_nsset, FRED_NOTEXIST)
        epp_cli.check_nsset(handles)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Nsset existuje: %s'%name)

    def test_020(self):
        '3.2 Pokus o Info na neexistujici nsset'
        epp_cli.info_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_031(self):
        '3.3.1 Zalozeni pomocnych kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_032(self):
        '3.3.2 Zalozeni pomocnych kontaktu'
        epp_cli.create_contact(FRED_CONTACT2,u'Miloš Pažout','milos@pazout.cz','Jevany','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '3.4.1 Pokus o zalozeni nssetu bez tech kontaktu'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], None)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_042(self):
        '3.4.2 Pokus o zalozeni nssetu s neznámým tech kontaktem'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], 'neznamycid', d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_043(self):
        '3.4.3 Pokus o zalozeni nssetu jen s jednim dns'
        d = FRED_DATA[1]
        epp_cli.create_nsset(FRED_NSSET1, d['dns'][0], d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_044(self):
        '3.4.4 Pokus o smazani nssetu, ktery by nemel existovat (vytvoril se chybne s jednim dns)'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_045(self):
        '3.4.5 Pokus o zalozeni nssetu s nepovolenym GLUE (Ticket #111)'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.name1.net', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_046(self):
        '3.4.6 Pokus o zalozeni nssetu s vyhrazenou IP: 127.0.0.1'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','127.0.0.1') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_047(self):
        '3.4.7 Pokus o zalozeni nssetu s neplatnou IP: 217.31.130.256'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','217.31.130.256') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    #def test_048(self):
        #'3.4.8 Pokus o zalozeni nssetu s vyhrazenou IP: 0.0.0.0'
        #d = FRED_DATA[1]
        #dns = list(d['dns'])
        #dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','0.0.0.0') })
        #epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        #self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    #def test_049(self):
        #'3.4.9 Pokus o zalozeni nssetu s vyhrazenou IP: 1.1.1.1'
        #d = FRED_DATA[1]
        #dns = list(d['dns'])
        #dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','1.1.1.1') })
        #epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        #self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_051(self):
        '3.5.1 Pokus o zalozeni nssetu s vyhrazenou IP: 10.0.0.0'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','10.0.0.0') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_052(self):
        '3.5.2 Pokus o zalozeni nssetu s neplatnou IP: 172.16.0.0'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','172.16.0.0') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_053(self):
        '3.5.3 Pokus o zalozeni nssetu s neplatnou IP: 192.168.0.0'
        d = FRED_DATA[1]
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','192.168.0.0') })
        epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_076(self):
        '3.5.6 Zalozeni neexistujiciho noveho nssetu'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], d['tech'], d['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_077(self):
        '3.5.7 Pokus o zalozeni existujiciho nssetu'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], d['tech'], d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_078(self):
        '3.7.8 Check na seznam existujiciho a neexistujicich nssetu'
        handles = (handle_nsset, FRED_NOTEXIST)
        epp_cli.check_nsset(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_nsset)), 0)
        self.assertEqual(epp_cli.is_val(('data',FRED_NOTEXIST)), 1)

    def test_079(self):
        '3.7.9 Info na existujici nsset a kontrola hodnot'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[1], epp_cli.is_val('data'))
        self.assert_(len(errors), '\n'.join(errors))

    def test_080(self):
        '3.8 Update vsech parametru krome stavu'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], d['add'], d['rem'], d['chg'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_081(self):
        '3.8.1 Overevni vsech hodnot zmeneneho nssetu'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = __check_equality__(FRED_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors), '\n'.join(errors))
        
    def test_082(self):
        '3.8.2 Pokus o odebrani neexistujici dns'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'name':'ns.namex.cz'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_084(self):
        '3.8.3 Pokus o odebnani dns tak, aby v nssetu zustal jen jeden'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'name':'ns.name3.cz'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_090(self):
        '3.9 Pokus o update vsech stavu server*[delete,update]'
        for status in ('serverDeleteProhibited', 'serverUpdateProhibited'):
            epp_cli.update_nsset(handle_nsset, {'status':status})
            self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
    def test_094(self):
        '3.9.1 Pokus o odstraneni tech-kontaktu'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'tech':FRED_CONTACT2})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_100(self):
        '3.10 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        epp_cli.update_nsset(handle_nsset, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o smazání
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_nsset(handle_nsset, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_110(self):
        '3.11 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        epp_cli.update_nsset(handle_nsset, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o změnu
        epp_cli.update_nsset(handle_nsset, None, None, {'auth_info':'zmena hesla'})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Nsset se aktualizoval, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_nsset(handle_nsset, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_112(self):
        '3.11.2 Pridani IPv6 2001:200::fea5:3015'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.valid01.cz','addr':('2001:200::fea5:3015',)}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_113(self):
        '3.11.3 Pokus o pridani neplatne IPv6 ::'
        d = FRED_DATA[2]
        try:
            epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail01.cz','addr':('::',)}})
        except fred.FredError, msg:
            # hodnota '::' neprojde přes validátor
            unitest_share.write_log_message(log_fp, '%s\n%s'%(self.test_113.__doc__,msg))
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_114(self):
        '3.11.4 Pokus o pridani neplatne IPv6 ::1'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail01.cz','addr':('::1',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_115(self):
        '3.11.5 Pokus o pridani neplatne IPv6 2001:718:1c01:16:214:22ff:fec9:xca5 (to "x" na konci)'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail02.cz','addr':('2001:718:1c01:16:214:22ff:fec9:xca5',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_116(self):
        '3.11.6 Pokus o pridani vyhrazene IP: 0.0.0.0'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail03.cz','addr':('0.0.0.0',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_117(self):
        '3.11.7 Pokus o pridani vyhrazene IP: 1.1.1.1'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail04.cz','addr':('1.1.1.1',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_118(self):
        '3.11.8 Pokus o pridani vyhrazene IP: 127.0.0.1'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail05.cz','addr':('127.0.0.1',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_119(self):
        '3.11.9 Pokus o pridani vyhrazene IP (trida A): 10.0.0.0'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail06.cz','addr':('10.0.0.0',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_120(self):
        '3.11.10 Pokus o pridani vyhrazene IP (trida A): 10.255.255.255'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail07.cz','addr':('10.255.255.255',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_121(self):
        '3.11.11 Pokus o pridani vyhrazene IP (trida B): 172.16.0.0'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail08.cz','addr':('172.16.0.0',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_122(self):
        '3.11.12 Pokus o pridani vyhrazene IP (trida B): 172.31.255.255'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail09.cz','addr':('172.31.255.255',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_123(self):
        '3.11.13 Pokus o pridani vyhrazene IP (trida C): 192.168.0.0'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail10.cz','addr':('192.168.0.0',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_124(self):
        '3.11.14 Pokus o pridani vyhrazene IP (trida C): 192.168.255.255'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], {'dns':{'name':'ns.fail11.cz','addr':('192.168.255.255',)}})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_130(self):
        '3.12 Vytvoreni domeny napojene na nsset'
        epp_cli.create_domain('test-nsset.cz', handle_contact, 'heslo', handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_135(self):
        '3.13 Smazani nssetu na ktery existuji nejake vazby'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_140(self):
        '3.14 Pokus o trasfer na vlastni nsset (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_nsset(handle_nsset, NSSET_PASSWORD)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_150(self):
        '3.15 Druhy registrator: Pokus o trasfer s neplatnym heslem (Chyba oprávnění)'
        global epp_to_log
        epp_to_log = epp_cli_TRANSF
        epp_cli_TRANSF.transfer_nsset(handle_nsset, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_161(self):
        '3.16.1 Druhy registrator: Trasfer nssetu'
        epp_cli_TRANSF.transfer_nsset(handle_nsset, NSSET_PASSWORD)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_162(self):
        '3.16.2 Druhy registrator: Zjisteni noveho hesla'
        global NSSET_GENPSW
        epp_cli_TRANSF.info_nsset(handle_nsset)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        NSSET_GENPSW = epp_cli_TRANSF.is_val(('data','auth_info'))

    def test_170(self):
        '3.17 Druhy registrator: Zmena hesla po prevodu nssetu'
        epp_cli_TRANSF.update_nsset(handle_nsset, None, None, {'auth_info':'nove-heslo'})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_180(self):
        '3.18 Pokus o zmenu hesla nssetu, ktery registratorovi jiz nepatri'
        global epp_to_log
        epp_to_log = epp_cli
        epp_cli.update_nsset(handle_nsset, None, None, {'auth_info':'moje-heslo'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_190(self):
        '3.19 Smazani domeny'
        epp_cli.delete_domain('test-nsset.cz')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_200(self):
        '3.20 Pokus o smazani nssetu, ktery registrator nevlastni'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_210(self):
        '3.21 Druhy registrator: Smazani nssetu'
        global epp_to_log
        epp_to_log = epp_cli_TRANSF
        epp_cli_TRANSF.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_220(self):
        '3.22 Check na smazany nsset'
        global epp_to_log
        epp_to_log = epp_cli
        epp_cli.check_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(('data',handle_nsset)), 1)

    def test_230(self):
        '3.23 Smazani pomocnych kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


def __check_equality__(cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    ##============================================================
    ##COLS:
    ##{'tech': ('contact1',), 
    ##'id': 'test001', 
    ##'dns': (
    ##    {'name': 'ns.name1.cz', 'addr': ('127.0.0.1', '127.1.1.1', '127.2.2.2')}, 
    ##    {'name': 'ns.name2.cz', 'addr': ('126.0.0.1', '126.1.1.1', '126.2.2.2')}
    ##    ), 
    ##    'auth_info': 'heslo'}
    ##------------------------------------------------------------
    ##DATA:
    ##    saved_data = {'nsset:upID': u'REG-LRR', 
    ##        'nsset:status.s': u'ok', 
    ##        'nsset:id': u'test001', 
    ##        'nsset:crDate': u'2006-08-03T09:38:05.0Z', 
    ##        'nsset:ns': [
    ##            [u'ns.name2.cz', [u'126.0.0.1', u'126.1.1.1', u'126.2.2.2']], 
    ##            [u'ns.name1.cz', [u'127.0.0.1', u'127.1.1.1', u'127.2.2.2']]], 
    ##        'nsset:clID': u'REG-LRR', 
    ##        'nsset:roid': u'N0000000027-CZ', 
    ##        'nsset:tech': u'CONTACT1'}
    ##____________________________________________________________
    # not checked: 
    #   nsset:upID          u'REG-LRR'
    #   nsset:status.s      u'ok'
    #   nsset:crDate        u'2006-08-03T09:38:05.0Z'
    #   nsset:roid          u'N0000000027-CZ'
    key = 'nsset:upID'
    ref_value = epp_cli._epp.get_config_value('connect','username')
    unitest_share.err_not_equal(errors, data, 'nsset:clID', ref_value)
    unitest_share.err_not_equal(errors, data, 'nsset:id', cols['id'])
    unitest_share.err_not_equal(errors, data, 'nsset:tech', cols['tech'])
    ns = data.get('nsset:ns',[])
    dns = cols['dns']
    if len(ns) == len(dns):
        for name,addr in ns:
            ref_addr = None
            for d in dns:
                if d['name'] == name:
                    ref_addr = list(d['addr'])
                    break
            if ref_addr is None:
                errors.append('DNS name "%s" nebyl nalezen'%name)
            else:
                if addr != ref_addr:
                    errors.append('DNS "%s" addr nejsou shodne: jsou: %s maji byt: %s'%(name, str(addr), str(ref_addr)))
    else:
        errors.append('Seznam DNS nema pozadovany pocet. Ma %d a mel by mit %d.'%(len(ns),len(dns)))
    return errors

epp_cli, epp_cli_TRANSF, epp_to_log, log_fp, log_step, handle_contact, handle_nsset = (None,)*7

if __name__ == '__main__':
##if 0:
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()

if 0:
##if __name__ == '__main__':
    # TEST equals data
    epp_cli = fred.Client()
    if fred.translate.options['session']: epp_cli._epp.set_session_name(fred.translate.options['session']) # nastavení serveru
    epp_cli._epp.load_config()
    saved_data = {'nsset:upID': u'REG-LRR', 
        'nsset:status.s': u'ok', 
        'nsset:id': u'test001', 
        'nsset:crDate': u'2006-08-03T09:38:05.0Z', 
        'nsset:ns': [
            [u'ns.name2.cz', [u'126.0.0.1', u'126.1.1.1', u'126.2.2.2']], 
            [u'ns.name1.cz', [u'127.0.0.1', u'127.1.1.1', u'127.2.2.2']],
           ],  
        'nsset:clID': u'REG-LRR', 
        'nsset:roid': u'N0000000027-CZ', 
        'nsset:tech': (u'CONTACT1',)}
    errors = __check_equality__(FRED_DATA[1], saved_data)
    if len(errors):
        print "ERRORS:"
        for e in errors:
            print e
    else:
        print "OK, NO ERRORS."

