#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
import sys
sys.path.insert(0, '..')
import re
import unittest
import fred
import unitest_share

# FRED_DATA[1] - create
# FRED_DATA[2] - modify
# FRED_DATA[3] - modified
FRED_NSSET1 = unitest_share.create_handle('NSSID:U1') ## 'NSSID:examp2134'
FRED_HANDLE = unitest_share.create_handle('NSSID:U2') ## 'NSSID:unittest2'
FRED_NSSET3 = unitest_share.create_handle('NSSID:U3')
FRED_DOMAIN = '%s.cz'%unitest_share.create_handle('nssetest')
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
    'tech': (FRED_CONTACT1,),  # (optional)             unbounded list
    'reportlevel':'0',
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
    'auth_info':NSSET_PASSWORD
    },
    #-------------------------------------------------------
    { # 3. modified
    'id': FRED_HANDLE,
    'auth_info': NSSET_PASSWORD,
    'dns': [
            {'name':'ns.name3.cz','addr':('217.31.205.130','217.31.205.129','217.31.205.128')},
            {'name':'ns.name4.cz','addr':('217.31.204.130','217.31.204.129','217.31.204.128')},
        ],
    'tech': (FRED_CONTACT2,),
    'reportlevel':'0',
    },
    #-------------------------------------------------------
    { # 4. invalid DNS
    'id': FRED_HANDLE, # (required)
    'auth_info': 'heslo', # (required)
    'dns': ( # (required)               list with max 9 items.
        {'name': 'ns.name1.cz', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') },
        {'name': 'ns.name2.cz', 'addr': ('217.31.206.130','217.31.206.129','217.31.206.128') },
        ),
    'tech': (FRED_CONTACT1,),  # (optional)             unbounded list
    'reportlevel':'0',
    },
    
)

# list of handles what hasn't been created and now must be deleted
HANDLES_TO_DELETE = [] # create
HANDLES_TO_REMOVE = [] # update add

def get_nssid_handle():
    'Must be always unique by cause of the protected time'
    return unitest_share.create_handle('NSSID:INV%02d' % len(HANDLES_TO_DELETE))

def append_created_handle(epp_cli, handle):
    global HANDLES_TO_DELETE
    if epp_cli.is_val() == 1000:
        HANDLES_TO_DELETE.append(handle)

def append_updated_handle(epp_cli, name):
    global HANDLES_TO_REMOVE
    if epp_cli.is_val() == 1000:
        HANDLES_TO_REMOVE.append(name)


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
        # validation is possible to switch off throught option -x --no_validate
        # tech level in schema - value of og range makes corruption
        epp_cli._epp.set_validate(0)
        epp_cli_TRANSF = fred.Client()
        epp_cli_TRANSF._epp.load_config()
        epp_cli_TRANSF._epp.set_validate(0)
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

        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = unitest_share.find_available_handle(epp_cli, 'contact','nexcon')
        # handle_nsset = unitest_share.find_available_handle(epp_cli, 'nsset','nexns')
        # self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        # self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-UNITTEST2" pro transfer.')
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
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Ulice','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_032(self):
        '3.3.2 Zalozeni pomocnych kontaktu'
        epp_cli.create_contact(FRED_CONTACT2,u'Miloš Pažout','milos@pazout.cz','U drahy','Jevany','20800','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '3.4.1 Pokus o zalozeni nssetu bez tech kontaktu'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], None, None, d['reportlevel'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_042(self):
        '3.4.2 Pokus o zalozeni nssetu s neznámým tech kontaktem'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], 'neznamycid', d['auth_info'], d['reportlevel'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_043(self):
        '3.4.3 Pokus o zalozeni nssetu jen s jednim dns'
        d = FRED_DATA[1]
        epp_cli.create_nsset(FRED_NSSET1, d['dns'][0], d['tech'], d['auth_info'], d['reportlevel'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_044(self):
        '3.4.4 Pokus o smazani nssetu, ktery by nemel existovat (vytvoril se chybne s jednim dns)'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_045(self):
        '3.4.5 Pokus o zalozeni nssetu s nepovolenym GLUE (Ticket #111)'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.name1.net', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_046(self):
        '3.4.6 Pokus o zalozeni nssetu s vyhrazenou IP: 127.0.0.1'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','127.0.0.1') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_047(self):
        '3.4.7 Pokus o zalozeni nssetu s neplatnou IP: 217.31.130.256'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','217.31.130.256') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    #def test_048(self):
        #'3.4.8 Pokus o zalozeni nssetu s vyhrazenou IP: 0.0.0.0'
        #d = FRED_DATA[1]
        #dns = list(d['dns'])
        #dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','0.0.0.0') })
        #epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'], d['reportlevel'])
        #self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    #def test_049(self):
        #'3.4.9 Pokus o zalozeni nssetu s vyhrazenou IP: 1.1.1.1'
        #d = FRED_DATA[1]
        #dns = list(d['dns'])
        #dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','1.1.1.1') })
        #epp_cli.create_nsset(d['id'], dns, d['tech'], d['auth_info'], d['reportlevel'])
        #self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_051(self):
        '3.5.1 Pokus o zalozeni nssetu s vyhrazenou IP: 10.0.0.0'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','10.0.0.0') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_052(self):
        '3.5.2 Pokus o zalozeni nssetu s neplatnou IP: 172.16.0.0'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','172.16.0.0') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_053(self):
        '3.5.3 Pokus o zalozeni nssetu s neplatnou IP: 192.168.0.0'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        dns = list(d['dns'])
        dns.append({'name': 'ns.myname1.cz', 'addr': ('217.31.207.130','192.168.0.0') })
        epp_cli.create_nsset(handle, dns, d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_060(self):
        '3.5.4.0 Pokus o zalozeni nssetu s neplatnym DNS: ...cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = '...cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_061(self):
        '3.5.4.1 Pokus o zalozeni nssetu s neplatnym DNS: .pokus.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = '.pokus.cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_062(self):
        '3.5.4.2 Pokus o zalozeni nssetu s neplatnym DNS: pokus..cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = 'pokus..cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_063(self):
        '3.5.4.3 Pokus o zalozeni nssetu s neplatnym DNS: pokus..test.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = 'pokus..test.cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_064(self):
        '3.5.4.4 Pokus o zalozeni nssetu s nepovolenymi znaky'
        global HANDLES_TO_DELETE
        errors = []
        d = FRED_DATA[4]
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
            handle = get_nssid_handle()
            name = 'ns.te%sbt.cz' % notallowed[position]
            d['dns'][1]['name'] = name
            epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
            # if nsset has been created append handle for delete it later
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been accepted.' % name)
                HANDLES_TO_DELETE.append(handle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' [%s] %s'%(handle, name), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_065(self):
        '3.5.4.5 Pokus o zalozeni nssetu s neplatnym DNS: -pokus.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = '-pokus.cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_066(self):
        '3.5.4.6 Pokus o zalozeni nssetu s neplatnym DNS: pokus-.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = 'pokus-.cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_067(self):
        '3.5.4.7 Pokus o zalozeni nssetu s neplatnym DNS: pok--us.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = 'pok--us.cz'
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_068(self):
        '3.5.4.8 Pokus o zalozeni nssetu s neplatnym DNS: a*64.cz'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        d['dns'][1]['name'] = '%s.cz' % ('a'*64, )
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_076(self):
        '3.5.6 Zalozeni neexistujiciho noveho nssetu'
        d = FRED_DATA[1]
        d['dns'][1]['name'] = 'ns.name2.cz' # obnoveni puvodniho stavu
        epp_cli.create_nsset(d['id'], d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_077(self):
        '3.5.7 Pokus o zalozeni existujiciho nssetu'
        d = FRED_DATA[4]
        handle = get_nssid_handle()
        epp_cli.create_nsset(handle, d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        # if nsset has been created append handle for delete it later
        append_created_handle(epp_cli, handle)
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
        errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_085(self):
        '3.7.9.1 Sendauthinfo na existujici nsset.'
        epp_cli.sendauthinfo_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))        
        
    def test_086(self):
        '3.7.9.2 Sendauthinfo na neexistujici nsset.'
        epp_cli.sendauthinfo_contact('NSSID:notexist007')
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Sendauthinfo na neexistujici nsset proslo')        

    def test_088(self):
	'3.7.9.3 Technical test na nsset.'
	epp_cli.technical_test(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))        

    def test_089(self):
	'3.7.9.4 Technical test na neexistujici nsset.'
	epp_cli.technical_test('NSSID:notexist008')
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))        

    def test_090(self):
        '3.8 Update vsech parametru krome stavu'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], d['add'], d['rem'], d['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_091(self):
        '3.8.1 Overevni vsech hodnot zmeneneho nssetu'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_092(self):
        '3.8.2 Pokus o odebrani neexistujici dns'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'name':'ns.namex.cz'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_093(self):
        '3.8.3 Pokus o odebnani dns tak, aby v nssetu zustal jen jeden'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'name':'ns.name3.cz'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_094(self):
        '3.9.1 Pokus o odstraneni tech-kontaktu'
        d = FRED_DATA[2]
        epp_cli.update_nsset(d['id'], None, {'tech':FRED_CONTACT2})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_100(self):
        '3.10.0 Zmena jen auth_info'
        FRED_DATA[3]['auth_info'] = 'zmena-jen-hesla'
        epp_cli.update_nsset(FRED_DATA[3]['id'], None, None, FRED_DATA[3]['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_101(self):
        '3.10.1 Kontrola zmenenych udaju po zmene pouze auth_info'
        epp_cli.info_nsset(FRED_DATA[3]['id'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_102(self):
        '3.10.2 Pokus o pridani neplatneho DNS: .cz'
        name = '.cz'
        newdns = {'name':name,'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_103(self):
        '3.10.3 Pokus o pridani neplatneho DNS: ...cz'
        name = '...cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_104(self):
        '3.10.4 Pokus o pridani neplatneho DNS: .pokus.cz'
        name = '.pokus.cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_105(self):
        '3.10.5 Pokus o pridani neplatneho DNS: pokus..cz'
        name = 'pokus..cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_106(self):
        '3.10.6 Pokus o pridani neplatneho DNS: pokus..test.cz'
        name = 'pokus..test.cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_107(self):
        '3.10.7 Pokus o pridani neplatneho DNS s nepovolenymi znaky'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
            name = 'ns.te%sbt.cz' % notallowed[position]
            newdns = {'name':name,'addr':('217.31.207.130','217.31.207.129')}
            epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been added.' % name)
                append_updated_handle(epp_cli, name)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%name, (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_108(self):
        '3.10.8 Pokus o odebrani dvou stejnych DNS'
        nsname = FRED_DATA[2]['rem']['name'][0]
        rem = {'name':(nsname, nsname)}
        epp_cli.update_nsset(FRED_HANDLE, None, rem)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_109(self):
        '3.10.9 Pokus o pridani neplatneho DNS: -pokus.cz'
        name = '-pokus.cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_110(self):
        '3.10.10 Pokus o pridani neplatneho DNS: pokus-.cz'
        name = 'pokus-.cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_111(self):
        '3.10.9 Pokus o pridani neplatneho DNS: po--kus.cz'
        name = 'po--kus.cz'
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_112(self):
        '3.11.2 Pridani IPv6 2001:200::fea5:3015'
        d = FRED_DATA[2]
        newdns = {'name':'ns.valid01.cz','addr':('2001:200::fea5:3015',)}
        FRED_DATA[3]['dns'].append(newdns)
        epp_cli.update_nsset(d['id'], {'dns':newdns})
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

    def test_125(self):
        '3.11.15 Pokus o pridani neplatneho DNS: a*64.cz'
        name = '%s.cz' % ('a'*64, )
        newdns = {'name':name, 'addr':('217.31.207.130','217.31.207.129')}
        epp_cli.update_nsset(FRED_HANDLE, {'dns':newdns})
        append_updated_handle(epp_cli, name)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_128(self):
        '3.11.16 Smazani dns, ktere nemely byt pridany'
        if len(HANDLES_TO_REMOVE):
            epp_cli.update_nsset(FRED_HANDLE, None, {'name':HANDLES_TO_REMOVE})
            self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_130(self):
        '3.12 Vytvoreni domeny napojene na nsset'
        epp_cli.create_domain(FRED_DOMAIN, handle_contact, 'heslo', handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_135(self):
        '3.13 Smazani nssetu na ktery existuji nejake vazby'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_140(self):
        '3.14.1 Pokus o trasfer na vlastni nsset (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_nsset(handle_nsset, FRED_DATA[3]['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_142(self):
        '3.14.2 Pokus o odebrani tech kontaktu'
        epp_cli.update_nsset(handle_nsset, None, {'tech': FRED_DATA[3]['tech']})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_144(self):
        '3.14.3 Pokus o update tech, ktery se jiz v nssetu nachazi'
        epp_cli.update_nsset(handle_nsset, {'tech': FRED_DATA[3]['tech']})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_150(self):
        '3.15.1 Pokus o nastaveni neplatneho tech levelu na -1 (mensi nez je rozsah)'
        invalid_answer = ''
        try:
            epp_cli.update_nsset(handle_nsset, None, None, None, "'-1'")
        except fred.FredError, e:
            invalid_answer = 'Server vratil neplatnou odpoved. Uz je opraven nsset:reportlevel?\n%s'%e
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        self.assert_(invalid_answer == '', invalid_answer)

    def test_151(self):
        '3.15.2 Pokus o nastaveni neplatneho tech levelu na 11 (vetsi nez je rozsah)'
        invalid_answer = ''
        try:
            epp_cli.update_nsset(handle_nsset, None, None, None, '11')
        except fred.FredError, e:
            invalid_answer = 'Server vratil neplatnou odpoved. Uz je opraven nsset:reportlevel?\n%s'%e
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        self.assert_(invalid_answer == '', invalid_answer)

    def test_152(self):
        '3.15.3 Nastaveni tech levelu na 5'
        FRED_DATA[3]['reportlevel'] = '5'
        epp_cli.update_nsset(handle_nsset, None, None, None, FRED_DATA[3]['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_153(self):
        '3.15.4 Kontrola tech levelu, ze je 5'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_154(self):
        '3.15.5 Nastaveni tech levelu na 8'
        FRED_DATA[3]['reportlevel'] = '8'
        epp_cli.update_nsset(handle_nsset, None, None, None, FRED_DATA[3]['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_155(self):
        '3.15.6 Kontrola tech levelu, ze je 8'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))


    def test_156(self):
        '3.16.1 Vymazani vsech poll zprav z fronty kvuli generovani poll zpravy z transferu'
        # disable settings autoack
        epp_cli._epp._session[fred.session_base.POLL_AUTOACK] = 0
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
        
    def test_160(self):
        '3.16.2 Druhy registrator: Pokus o trasfer s neplatnym heslem (Chyba oprávnění)'
        global epp_to_log
        epp_to_log = epp_cli_TRANSF
        epp_cli_TRANSF.transfer_nsset(handle_nsset, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_161(self):
        '3.16.3 Druhy registrator: Trasfer nssetu'
        epp_cli_TRANSF.transfer_nsset(handle_nsset, FRED_DATA[3]['auth_info'])
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_162(self):
        '3.16.4 Poll req - Kontrola, ze byla vygenerovana zprava o transferu.'
        global poll_msg_id
        # disable settings autoack
        epp_cli.poll('req')
        self.assertEqual(epp_cli.is_val(), 1301, 'Poll zprava chybi, prestoze mela existovat.')
        msg = epp_cli.is_val(('data','msg'))
        self.failIf(type(msg) not in (unicode, str), 'Poll zprava chybi')
        self.failIf(re.search(re.escape(handle_nsset), msg, re.I) is None, 'Zprava se nevztahuje k transferovane domene.')
        poll_msg_id = epp_cli.is_val(('data','msgQ.id'))
        self.failIf(type(poll_msg_id) is not int, 'Chybi ID poll zpravy')

    def test_163(self):
        '3.16.5 Poll ack - Vyrazeni zpravy o transferu z fronty.'
        self.failIf(type(poll_msg_id) is not int, 'Chybi ID poll zpravy')
        epp_cli.poll('ack', poll_msg_id)
        if epp_cli.is_val() not in (1000, 1300):
            self.assertEqual(0, 1, unitest_share.get_reason(epp_cli))
        
    def test_164(self):
        '3.16.6 Druhy registrator: Zjisteni noveho hesla'
        global NSSET_GENPSW
        epp_cli_TRANSF.info_nsset(handle_nsset)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        NSSET_GENPSW = epp_cli_TRANSF.is_val(('data','auth_info'))

    def test_170(self):
        '3.17 Druhy registrator: Zmena hesla po prevodu nssetu'
        epp_cli_TRANSF.update_nsset(handle_nsset, None, None, 'nove-heslo')
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_180(self):
        '3.18 Pokus o zmenu hesla nssetu, ktery registratorovi jiz nepatri'
        global epp_to_log
        epp_to_log = epp_cli
        epp_cli.update_nsset(handle_nsset, None, None, 'moje-heslo')
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_190(self):
        '3.19 Smazani domeny'
        epp_cli.delete_domain(FRED_DOMAIN )
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_200(self):
        '3.20 Pokus o smazani nssetu, ktery registrator nevlastni'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_210(self):
        '3.20.2 Druhy registrator: Smazani nssetu'
        global epp_to_log
        epp_to_log = epp_cli_TRANSF
        epp_cli_TRANSF.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_220(self):
        '3.20.3 Check na smazany nsset'
        global epp_to_log
        epp_to_log = epp_cli
        epp_cli.check_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(('data',handle_nsset)), 0)

    def test_300(self):
        '3.3 Pokus o zalozeni nssetu s vice stejnymi tech hodnotami'
        d = FRED_DATA[1]
        epp_cli.create_nsset(FRED_NSSET3, d['dns'], (FRED_CONTACT2, FRED_CONTACT2),  d['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_310(self):
        '3.4 Smazani nssetu, pokud se vytvoril'
        epp_cli.delete_nsset(FRED_NSSET3)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_312(self):
        '3.4.2 Smazani nssetu, ktere se nemely vytvorit, ale presto vznikly'
        errors = []
        max = len(HANDLES_TO_DELETE)
        for position in range(max):
            handle = HANDLES_TO_DELETE[position]
            epp_cli.delete_nsset(handle)
            if epp_cli.is_val() != 1000:
                errors.append('Handle %s se nepodarilo smazat.' % handle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),
                                    self.shortDescription()+' %s'%handle, (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_320(self):
        '3.5 Pokus o vytvoreni nssetu, ktery byl prave smazan a musi byt v ochranne zone'
        d = FRED_DATA[1]
        epp_cli.create_nsset(d['id'], d['dns'], d['tech'], d['auth_info'], d['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 2005, unitest_share.get_reason(epp_cli))
        

    def test_900(self):
        '3.END Smazani pomocnych kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_998(self):
        '98. logout'
        epp_cli_TRANSF.logout()
        self.assertEqual(epp_cli_TRANSF.is_val(), 1500, unitest_share.get_reason(epp_cli))

    def test_999(self):
        '99. logout'
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))


epp_cli, epp_cli_TRANSF, epp_to_log, log_fp, log_step, handle_contact, handle_nsset, poll_msg_id = (None,)*8

if __name__ == '__main__':
##if 0:
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
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
    saved_data = {'nsset:upID': u'REG-UNITTEST1', 
        'nsset:status.s': u'ok', 
        'nsset:id': u'test001', 
        'nsset:crDate': u'2006-08-03T09:38:05.0Z', 
        'nsset:ns': [
            [u'ns.name2.cz', [u'126.0.0.1', u'126.1.1.1', u'126.2.2.2']], 
            [u'ns.name1.cz', [u'127.0.0.1', u'127.1.1.1', u'127.2.2.2']],
           ],  
        'nsset:clID': u'REG-UNITTEST1', 
        'nsset:roid': u'N0000000027-CZ', 
        'nsset:tech': (u'CONTACT1',)}
    errors = unitest_share.compare_nsset_info(epp_cli, FRED_DATA[1], saved_data)
    if len(errors):
        print "ERRORS:"
        for e in errors:
            print e
    else:
        print "OK, NO ERRORS."

