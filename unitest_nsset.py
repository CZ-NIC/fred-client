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
import ccReg
import unitest_ccreg_share

# CCREG_DATA[1] - create
# CCREG_DATA[2] - modify
# CCREG_DATA[3] - modified
CCREG_HANDLE = 'test001'
CCREG_CONTACT1 = 'CONTACT1'
CCREG_CONTACT2 = 'CONTACT2'
NSSET_PASSWORD = 'heslicko'
CCREG_DATA = ( 
    { # 0. template
    },
    #-------------------------------------------------------
    { # 1. create
    'id': CCREG_HANDLE, # (required)
    'pw': 'heslo', # (required)
    'dns': ( # (required)               list with max 9 items.
        {'name': 'ns.name1.cz', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') },
        {'name': 'ns.name2.cz', 'addr': ('217.31.206.130','217.31.206.129','217.31.206.128') },
        ),
    'tech': (CCREG_CONTACT1,)  # (optional)             unbounded list
    },
    #-------------------------------------------------------
    { # 2. modify
    'id': CCREG_HANDLE, # (required)
    'add': {
        'dns': (
            {'name':'ns.name3.cz','addr':('217.31.205.130','217.31.205.129','217.31.205.128')},
            {'name':'ns.name4.cz','addr':('217.31.204.130','217.31.204.129','217.31.204.128')},
        ),
        'tech':CCREG_CONTACT2,
        #'status':'clientDeleteProhibited',
    },
    'rem': {
        'name':('ns.name1.cz','ns.name2.cz'),
        'tech':CCREG_CONTACT1,
        #'status':'clientDeleteProhibited',
    },
    'chg': {
        'pw':NSSET_PASSWORD
    },
    },
    #-------------------------------------------------------
    { # 3. modified
    'id': CCREG_HANDLE,
    'pw': NSSET_PASSWORD,
    'dns': (
            {'name':'ns.name3.cz','addr':('217.31.205.130','217.31.205.129','217.31.205.128')},
            {'name':'ns.name4.cz','addr':('217.31.204.130','217.31.204.129','217.31.204.128')},
        ),
    'tech': (CCREG_CONTACT2,)
    },
    #-------------------------------------------------------
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
        # Natvrdo definovany handle:
        handle_nsset = CCREG_DATA[1]['id'] # 'neexist01'
        handle_contact = CCREG_CONTACT1
        # create client object
        epp_cli = ccReg.Client()
        epp_cli_TRANSF = ccReg.Client()
        if ccReg.translate.options['session']:
            # nastavení serveru
            epp_cli._epp.set_session_name(ccReg.translate.options['session'])
            epp_cli_TRANSF._epp.set_session_name(ccReg.translate.options['session'])
        epp_cli._epp.load_config()
        epp_cli_TRANSF._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = unitest_ccreg_share.find_available_handle(epp_cli, 'contact','nexcon')
        # handle_nsset = unitest_ccreg_share.find_available_handle(epp_cli, 'nsset','nexns')
        # self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        # self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')
        # logovací soubor
        if ccReg.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(ccReg.translate.options['log'],'w')
    
    def test_010(self):
        '3.1 Check na seznam dvou neexistujicich nssetu'
        handles = (handle_nsset,'neexist002')
        epp_cli.check_nsset(handles)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Nsset existuje: %s'%name)

    def test_020(self):
        '3.2 Pokus o Info na neexistujici nsset'
        epp_cli.info_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_031(self):
        '3.3.1 Zalozeni pomocnych kontaktu'
        epp_cli.create_contact(CCREG_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
    def test_032(self):
        '3.3.2 Zalozeni pomocnych kontaktu'
        epp_cli.create_contact(CCREG_CONTACT2,u'Miloš Pažout','milos@pazout.cz','Jevany','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_040(self):
        '3.4 Zalozeni neexistujiciho noveho nssetu'
        d = CCREG_DATA[1]
        epp_cli.create_nsset(d['id'], d['pw'], d['dns'], d['tech'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_050(self):
        '3.5 Pokus o zalozeni existujiciho nssetu'
        d = CCREG_DATA[1]
        epp_cli.create_nsset(d['id'], d['pw'], d['dns'], d['tech'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_060(self):
        '3.6 Check na seznam existujiciho a neexistujicich nssetu'
        handles = (handle_nsset,'neexist002')
        epp_cli.check_nsset(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_nsset)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002')), 1)

    def test_070(self):
        '3.7 Info na existujici nsset a kontrola hodnot'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __check_equality__(CCREG_DATA[1], epp_cli.is_val('data'))
        self.assert_(len(errors), '\n'.join(errors))

    def test_080(self):
        '3.8 Update vsech parametru krome stavu'
        d = CCREG_DATA[2]
        epp_cli.update_nsset(d['id'], d['add'], d['rem'], d['chg'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_081(self):
        '3.8.1 Overevni vsech hodnot zmeneneho nssetu'
        epp_cli.info_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __check_equality__(CCREG_DATA[3], epp_cli.is_val('data'))
        self.assert_(len(errors), '\n'.join(errors))
        
    def test_090(self):
        '3.9 Pokus o update vsech stavu server*[delete,update]'
        for status in ('serverDeleteProhibited', 'serverUpdateProhibited'):
            epp_cli.update_nsset(handle_nsset, {'status':status})
            self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
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
        epp_cli.update_nsset(handle_nsset, None, None, {'pw':'zmena hesla'})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Nsset se aktualizoval, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_nsset(handle_nsset, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_120(self):
        '3.12 Vytvoreni domeny napojene na nsset'
        epp_cli.create_domain('test-nsset.cz', 'heslo', handle_nsset, handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_130(self):
        '3.13 Smazani nssetu na ktery existuji nejake vazby'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_140(self):
        '3.14 Pokus o trasfer na vlastni nsset (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_nsset(handle_nsset, NSSET_PASSWORD)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_150(self):
        '3.15 Druhy registrator: Pokus o trasfer s neplatnym heslem (Chyba oprávnění)'
        epp_cli_TRANSF.transfer_nsset(handle_nsset, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))

    def test_160(self):
        '3.16 Druhy registrator: Trasfer nssetu'
        epp_cli_TRANSF.transfer_nsset(handle_nsset, NSSET_PASSWORD)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))

    def test_170(self):
        '3.17 Druhy registrator: Zmena hesla po prevodu nssetu'
        epp_cli_TRANSF.update_nsset(handle_nsset, None, None, {'pw':'nove-heslo'})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))

    def test_180(self):
        '3.18 Pokus o zmenu hesla nssetu, ktery registratorovi jiz nepatri'
        epp_cli.update_nsset(handle_nsset, None, None, {'pw':'moje-heslo'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_190(self):
        '3.19 Smazani domeny'
        epp_cli.delete_domain('test-nsset.cz')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_200(self):
        '3.20 Pokus o smazani nssetu, ktery registrator nevlastni'
        epp_cli.delete_nsset(handle_nsset)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_210(self):
        '3.21 Druhy registrator: Smazani nssetu'
        epp_cli_TRANSF.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli_TRANSF))

    def test_220(self):
        '3.22 Check na smazany nsset'
        epp_cli.check_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(('data',handle_nsset)), 1)

    def test_230(self):
        '3.23 Smazani pomocnych kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        epp_cli.delete_contact(CCREG_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))


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
    ##    'pw': 'heslo'}
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
    unitest_ccreg_share.err_not_equal(errors, data, 'nsset:clID', ref_value)
    unitest_ccreg_share.err_not_equal(errors, data, 'nsset:id', cols['id'])
    unitest_ccreg_share.err_not_equal(errors, data, 'nsset:tech', cols['tech'])
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

epp_cli, epp_cli_TRANSF, log_fp, log_step, handle_contact, handle_nsset = (None,)*6

if __name__ == '__main__':
##if 0:
    if ccReg.translate.option_errors:
        print ccReg.translate.option_errors
    elif ccReg.translate.options['help']:
        print unitest_ccreg_share.__doc__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()

if 0:
##if __name__ == '__main__':
    # TEST equals data
    epp_cli = ccReg.Client()
    if ccReg.translate.options['session']: epp_cli._epp.set_session_name(ccReg.translate.options['session']) # nastavení serveru
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
    errors = __check_equality__(CCREG_DATA[1], saved_data)
    if len(errors):
        print "ERRORS:"
        for e in errors:
            print e
    else:
        print "OK, NO ERRORS."

