#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
2.1 Check na seznam dvou neexistujicich kontaktu
2.2 Pokus o Info na neexistujici kontakt
2.3 Zalozeni neexistujiciho noveho kontaktu
2.4 Pokus o zalozeni existujiciho kontaktu
2.5 Check na seznam existujiciho a neexistujicich kontaktu
2.6 Info na existujici kontakt
2.7 Update vsech parametru krome stavu
2.8 Pokus o update stavu Server*
2.9 Update stavu clientDeleteProhibited a pokus o smazani
2.10 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu
2.11 Vytvoreni nnsetu napojeneho na kontakt
2.12 Smazani kontaktu na ktery existuji nejake vazby
2.13 Smazani nssetu
2.14 Smazani kontaktu 
2.15 Check na smazany kontakt
"""
import sys
sys.path.insert(0, '..')
import time
import unittest
import fred
import unitest_share


# FRED_CONTACT[1] - create
# FRED_CONTACT[2] - modify
# FRED_CONTACT[3] - chg (changes)
#CONTACT_HANDLE = 'CID:test002'
CONTACT_HANDLE = unitest_share.create_handle('CID:')
NSSET_HANDLE = unitest_share.create_handle('NSSID:')
#print "CREATE CONTACT_HANDLE: ",CONTACT_HANDLE
#print "CREATE NSSET_HANDLE: ",NSSET_HANDLE
FRED_CONTACT = [
    {   # template
    'id': '', # (povinný) vaše kontaktní ID
    'name': '', # (povinný) vaše jméno
    'email': '', #(povinný) váš email
    'city': '', #(povinný) město
    'cc': '', #(povinný) kód země
    'auth_info': '', #(povinný) heslo
    'org': '', #(nepovinný) název organizace
    'street': '', #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '', #(nepovinný) č.p.
    'pc': '', #(nepovinný) PSČ
    'voice': '', #(nepovinný) telefon
    'fax': '', #(nepovinný) fax
    'disclose': {'flag':'n', 'data':('voice','fax','email', 'vat', 'ident', 'notify_email')},
    'vat': '', #(nepovinný) DPH
    'ident': '', #(nepovinný) Ident
    'ident': {'type':'','number':''}, #(nepovinný) Ident
    'notify_email': '', #(nepovinný) oznámení na email
    },
    {   # create contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Řehoř Čížek', # (povinný) vaše jméno
    'email': 'rehor.cizek@mail.cz', #(povinný) váš email
    'city': u'Český Krumlov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'auth_info': 'mojeheslo', #(povinný) heslo
    'org': u'Čížková a spol', #(nepovinný) název organizace
    'street': (u'U práce',u'Za monitorem',u'Nad klávesnicí',), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '123', #(nepovinný) č.p.
    'pc': '12300', #(nepovinný) PSČ
    'voice': '+123.456789', #(nepovinný) telefon
    'fax': '+321.564987', #(nepovinný) fax
    'disclose': {'flag':'n', 'data':('name',)},
    'vat': '963', #(nepovinný) DPH
    'ident': {'type':'op','number':'12345679'}, #(nepovinný) ident
    'notify_email': 'info@rehorovi.cz', #(nepovinný) oznámení na email
    },
    {   # modify contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Břéťa Žlučník', # (povinný) vaše jméno
    'email': 'breta.zlucnik@bricho.cz', #(povinný) váš email
    'city': u'Střevníkov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'auth_info': 'nove-heslo', #(povinný) heslo
    'org': u'Bolení s.r.o.', #(nepovinný) název organizace
    'street': (u'Na toaletách',u'U mísy'), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '321', #(nepovinný) č.p.
    'pc': '23101', #(nepovinný) PSČ
    'voice': '+321.987654', #(nepovinný) telefon
    'fax': '+321.987564', #(nepovinný) fax
    'disclose': {'flag':'y', 'data':('voice','fax','email')},
    'vat': '753', #(nepovinný) DPH
    'ident': {'type':'birthday','number':'28.6.2007'}, #(nepovinný) ident
    'notify_email': 'info@zlucnikovi.cz', #(nepovin.ý. oznámení na email
    },
]

d = FRED_CONTACT[2]
FRED_CONTACT.append({ # chg part to modify contact
            'postal_info': {
                'name': d['name'],
                'org': d['org'],
                'addr':{
                    'street': d['street'],
                    'city':  d['city'],
                    'sp': d['sp'],
                    'pc': d['pc'],
                    'cc': d['cc'],
                },
            },
            'voice': d['voice'],
            'fax': d['fax'],
            'email': d['email'],
            'auth_info': d['auth_info'],
            'disclose': d['disclose'],
            'vat': d['vat'],
            'ident': d['ident'],
            'notify_email': d['notify_email'],
    })

class TestContact(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)

    def test_000(self):
        '2.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, epp_cli_log, handle_contact, log_fp
        # Natvrdo definovany handle:
        handle_contact = FRED_CONTACT[1]['id'] # 'neexist01'
        # create client object
        epp_cli = fred.Client()
        epp_cli_TRANSF = fred.Client()
        epp_cli._epp.load_config()
        epp_cli_TRANSF.load_config()
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
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = __find_available_handle__(epp_cli, 'contact','nexcon')
        # handle_nsset = __find_available_handle__(epp_cli, 'nsset','nexns')
        # self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        # self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-UNITTEST2" pro transfer.')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')

    def test_005(self):
        '2.0 Hello - Kontrola validity greeting'
        epp_cli.hello()
        self.assertTrue(len(epp_cli.is_val(('data','svID'))) > 0, unitest_share.get_reason(epp_cli))

    
    def test_010(self):
        '2.1 Check na seznam dvou neexistujicich kontaktu'
        handles = (handle_contact,'CID:neexist002')
        epp_cli.check_contact(handles)
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Kontakt existuje: %s'%name)

    def test_020(self):
        '2.2 Pokus o Info na neexistujici kontakt'
        epp_cli.info_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'handle_contact %s existuje'%handle_contact)

    def test_030(self):
        '2.3 Zalozeni neexistujiciho noveho kontaktu'
        d = FRED_CONTACT[1]
        epp_cli.create_contact(handle_contact, 
            d['name'], d['email'], d['street'], d['city'], d['pc'], d['cc'], d['sp'], 
            d['org'], d['auth_info'],
            d['voice'], d['fax'], d['disclose'],
            d['vat'], d['ident'], d['notify_email'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_031(self):
        '2.3.1 Overevni vsech hodnot vznikleho kontaktu'
        epp_cli.info_contact(handle_contact)
        errors = unitest_share.compare_contact_info('contact', FRED_CONTACT[1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_040(self):
        '2.4 Pokus o zalozeni existujiciho kontaktu'
        # contact_id, name, email, city, cc
        epp_cli.create_contact(handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Ulice', 'Praha', '12300', 'CZ')
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Contakt se vytvoril prestoze jiz existuje.')

    def test_050(self):
        '2.5 Check na seznam existujiciho a neexistujicich kontaktu'
        handles = (handle_contact,'CID:neexist002')
        epp_cli.check_contact(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 0)
        self.assertEqual(epp_cli.is_val(('data','CID:neexist002')), 1)

    def test_060(self):
        '2.6 Info na existujici kontakt a overeni vsech hodnot'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_contact_info('contact', FRED_CONTACT[1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_070(self):
        '2.7 Update vsech parametru krome stavu'
        epp_cli.update_contact(handle_contact, FRED_CONTACT[3])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_071(self):
        '2.7.1 Overevni vsech hodnot zmeneneho kontaktu'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_contact_info('contact', FRED_CONTACT[2], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_080(self):
        '2.8.1 Zmena jen auth_info'
        FRED_CONTACT[2]['auth_info'] = 'zmena-jen-hesla'
        epp_cli.update_contact(handle_contact, {'auth_info':'zmena-jen-hesla'})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_085(self):
        '2.8.2 Kontrola zmenenych udaju po zmene pouze auth_info'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        errors = unitest_share.compare_contact_info('contact', FRED_CONTACT[2], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

        
##    def test_080(self):
##        '2.8.1 Pokus o update stavu serverDeleteProhibited'
##        status = 'serverDeleteProhibited'
##        epp_cli.update_contact(handle_contact, status)
##        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
##
##    def test_081(self):
##        '2.8.2 Pokus o update stavu serverUpdateProhibited'
##        status = 'serverUpdateProhibited'
##        epp_cli.update_contact(handle_contact, status)
##        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
##
##    def test_090(self):
##        '2.9 Update stavu clientDeleteProhibited a pokus o smazani'
##        status = 'clientDeleteProhibited'
##        epp_cli.update_contact(handle_contact, status)
##        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
##        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
##        unitest_share.reset_client(epp_cli)
##        # pokus o smazání
##        epp_cli.delete_contact(handle_contact)
##        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
##        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
##        unitest_share.reset_client(epp_cli)
##        # zrušení stavu
##        epp_cli.update_contact(handle_contact, None, status)
##        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
##
##    def test_100(self):
##        '2.10 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
##        status = 'clientUpdateProhibited'
##        epp_cli.update_contact(handle_contact, status)
##        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
##        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
##        unitest_share.reset_client(epp_cli)
##        # pokus o změnu
##        epp_cli.update_contact(handle_contact, None, None, {'notifyEmail':'notifak@jinak.cz'})
##        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
##        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se aktualizoval, prestoze mel nastaven %s'%status)
##        unitest_share.reset_client(epp_cli)
##        # zrušení stavu
##        epp_cli.update_contact(handle_contact, None, status)
##        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_110(self):
        '2.11 Vytvoreni nnsetu napojeneho na kontakt'
        epp_cli.create_nsset(NSSET_HANDLE, ({'name':'ns1.test.cz'},{'name':'ns2.test.cz'}), handle_contact, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_120(self):
        '2.12 Smazani kontaktu na ktery existuji nejake vazby'
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_130(self):
        '2.13 Smazani nssetu'
        epp_cli.delete_nsset(NSSET_HANDLE)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_140(self):
        '2.14 Trasfer na vlastni contact (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_contact(handle_contact, FRED_CONTACT[2]['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_150(self):
        '2.15 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.transfer_contact(handle_contact, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        
    def test_160(self):
        '2.16 Druhy registrator: Trasfer kontaktu'
        epp_cli_TRANSF.transfer_contact(handle_contact, FRED_CONTACT[2]['auth_info'])
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_161(self):
        '2.16.1 Kontrola, ze se po stransferu automaticky zmenilo heslo.'
        epp_cli_TRANSF.info_contact(handle_contact)
        self.assertNotEqual(epp_cli_TRANSF.is_val(('data','contact:auth_info')), FRED_CONTACT[2]['auth_info'], 'Heslo po transferu zustalo puvodni.')
        
    def test_170(self):
        '2.17 Druhy registrator: Zmena hesla po prevodu domeny'
        epp_cli_TRANSF.update_contact(handle_contact, {'auth_info':FRED_CONTACT[1]['auth_info']})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
        
    def test_180(self):
        '2.18 Zmena hesla kontaktu, ktery registratorovi jiz nepatri'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.update_contact(handle_contact, {'auth_info':'moje-heslo2'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_190(self):
        '2.19 Pokus o smazani kontaktu, ktery jiz registratorovi nepatri'
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Contact se smazal prestoze nemel')
        
    def test_200(self):
        '2.20 Smazani kontaktu'
        global epp_cli_log
        epp_cli_log = epp_cli_TRANSF
        epp_cli_TRANSF.delete_contact(handle_contact)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_210(self):
        '2.21 Check na smazany kontakt'
        global epp_cli_log
        epp_cli_log = epp_cli
        epp_cli.check_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 0, '%s nelze smazat'%handle_contact)

    def test_220(self):
        '2.22 Poll request'
        global id_message
        # 1000 OK (ack)
        # 1300 No messages
        # 1301 Any message
        
        # disable settings autoack
        epp_cli._epp._session[fred.session_base.POLL_AUTOACK] = 0
        
        epp_cli.poll('req')
        if epp_cli.is_val() not in (1000,1300,1301):
            self.assertEqual(0, 1, unitest_share.get_reason(epp_cli))
        id_message = epp_cli.is_val(('data','msgQ.id'))

    def test_223(self):
        '2.23 Poll ack'
        if id_message:
            epp_cli.poll('ack', id_message)
            if epp_cli.is_val() not in (1000, 1300):
                self.assertEqual(0, 1, unitest_share.get_reason(epp_cli))
        else:
            self.__testMethodDoc += ' skip test (no message ID)'



epp_cli, epp_cli_TRANSF, epp_cli_log, log_fp, log_step, handle_contact = (None,)*6

if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestContact))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()

