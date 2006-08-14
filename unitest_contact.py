#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import unittest
import ccReg
from ccReg.eppdoc_assemble import contact_disclose
import unitest_ccreg_share


# CCREG_CONTACT[1] - create
# CCREG_CONTACT[2] - modify
# CCREG_CONTACT[3] - chg (changes)
CONTACT_HANDLE = 'test001'
CCREG_CONTACT = [
    {   # template
    'id': '', # (povinný) vaše kontaktní ID
    'name': '', # (povinný) vaše jméno
    'email': '', #(povinný) váš email
    'city': '', #(povinný) město
    'cc': '', #(povinný) kód země
    'org': '', #(nepovinný) název organizace
    'street': '', #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '', #(nepovinný) č.p.
    'pc': '', #(nepovinný) PSČ
    'voice': '', #(nepovinný) telefon
    'fax': '', #(nepovinný) fax
    'disclose_flag':'n',
    'disclose': ('name','org','addr','voice','fax','email'),
    'vat': '', #(nepovinný) DPH
    'ssn': '', #(nepovinný) SSN
    'notify_email': '', #(nepovinný) oznámení na email
    },
    {   # create contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Řehoř Čížek', # (povinný) vaše jméno
    'email': 'rehor.cizek@mail.cz', #(povinný) váš email
    'city': u'Český Krumlov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'org': u'Čížková a spol', #(nepovinný) název organizace
    'street': (u'U práce',u'Za monitorem',u'Nad klávesnicí',), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '123', #(nepovinný) č.p.
    'pc': '12300', #(nepovinný) PSČ
    'voice': '+123.456789', #(nepovinný) telefon
    'fax': '+321.564987', #(nepovinný) fax
    'disclose_flag': 'n',
    'disclose': ('name',), # ,'org','addr','voice','fax','email'
    'vat': '963', #(nepovinný) DPH
    'ssn': '852', #(nepovinný) SSN
    'notify_email': 'info@rehorovi.cz', #(nepovinný) oznámení na email
    },
    {   # modify contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Břéťa Žlučník', # (povinný) vaše jméno
    'email': 'breta.zlucnik@bricho.cz', #(povinný) váš email
    'city': u'Střevníkov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'org': u'Bolení s.r.o.', #(nepovinný) název organizace
    'street': (u'Na toaletách',u'U mísy'), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '321', #(nepovinný) č.p.
    'pc': '23101', #(nepovinný) PSČ
    'voice': '+321.987654', #(nepovinný) telefon
    'fax': '+321.987564', #(nepovinný) fax
    'disclose_flag': 'y',
    'disclose': ('voice','fax','email'), # 'name','org','addr',
    'vat': '753', #(nepovinný) DPH
    'ssn': '357', #(nepovinný) SSN
    'notify_email': 'info@zlucnikovi.cz', #(nepovinný) oznámení na email
    },
]

d = CCREG_CONTACT[2]
CCREG_CONTACT.append({ # chg part to modify contact
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
            'disclose_flag': d['disclose_flag'],
            'disclose': d['disclose'],
            'vat': d['vat'],
            'ssn': d['ssn'],
            'notify_email': d['notify_email'],
    })

class Test(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription())
        unitest_ccreg_share.reset_client(epp_cli)

    def test_2_000(self):
        '2.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, handle_contact, handle_nsset, log_fp
        # Natvrdo definovany handle:
        handle_contact = CCREG_CONTACT[1]['id'] # 'neexist01'
        handle_nsset = 'neexist01'
        # create client object
        epp_cli = ccReg.Client()
        if ccReg.translate.options['session']:
            epp_cli._epp.set_session_name(ccReg.translate.options['session']) # nastavení serveru
        epp_cli._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = __find_available_handle__(epp_cli, 'contact','nexcon')
        # handle_nsset = __find_available_handle__(epp_cli, 'nsset','nexns')
        # self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        # self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        # logovací soubor
        if ccReg.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(ccReg.translate.options['log'],'w')
    
    def test_2_010(self):
        '2.1 Check na seznam dvou neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Kontakt existuje: %s'%name)

    def test_2_020(self):
        '2.2 Pokus o Info na neexistujici kontakt'
        epp_cli.info_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'handle_contact %s existuje'%handle_contact)

    def test_2_030(self):
        '2.3 Zalozeni neexistujiciho noveho kontaktu'
        d = CCREG_CONTACT[1]
        epp_cli.create_contact(handle_contact, 
            d['name'], d['email'], d['city'], d['cc'], d['org'], 
            d['street'], d['sp'], d['pc'], d['voice'], d['fax'], d['disclose_flag'], d['disclose'],
            d['vat'], d['ssn'], d['notify_email'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_2_031(self):
        '2.3.1 Overevni vsech hodnot vznikleho kontaktu'
        epp_cli.info_contact(handle_contact)
        errors = __info_contact__('contact', CCREG_CONTACT[1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_2_040(self):
        '2.4 Pokus o zalozeni existujiciho kontaktu'
        # contact_id, name, email, city, cc
        epp_cli.create_contact(handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Contakt se vytvoril prestoze jiz existuje.')

    def test_2_050(self):
        '2.5 Check na seznam existujiciho a neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002')), 1)

    def test_2_060(self):
        '2.6 Info na existujici kontakt a overeni vsech hodnot'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __info_contact__('contact', CCREG_CONTACT[1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_2_070(self):
        '2.7 Update vsech parametru krome stavu'
        epp_cli.update_contact(handle_contact, None, None, CCREG_CONTACT[3])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_2_071(self):
        '2.7.1 Overevni vsech hodnot zmeneneho kontaktu'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        errors = __info_contact__('contact', CCREG_CONTACT[2], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_2_080(self):
        '2.8.1 Pokus o update stavu serverDeleteProhibited'
        status = 'serverDeleteProhibited'
        epp_cli.update_contact(handle_contact, status)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)

    def test_2_081(self):
        '2.8.2 Pokus o update stavu serverUpdateProhibited'
        status = 'serverUpdateProhibited'
        epp_cli.update_contact(handle_contact, status)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)

    def test_2_090(self):
        '2.9 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        epp_cli.update_contact(handle_contact, status)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # pokus o smazání
        epp_cli.delete_contact(handle_contact)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # zrušení stavu
        epp_cli.update_contact(handle_contact, None, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_2_100(self):
        '2.10 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        epp_cli.update_contact(handle_contact, status)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # pokus o změnu
        epp_cli.update_contact(handle_contact, None, None, {'notifyEmail':'notifak@jinak.cz'})
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se aktualizoval, prestoze mel nastaven %s'%status)
        unitest_ccreg_share.reset_client(epp_cli)
        # zrušení stavu
        epp_cli.update_contact(handle_contact, None, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_2_110(self):
        '2.11 Vytvoreni nnsetu napojeneho na kontakt'
        epp_cli.create_nsset(handle_nsset, 'heslo', {'name':'ns1.test.cz'}, handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))
        
    def test_2_120(self):
        '2.12 Smazani kontaktu na ktery existuji nejake vazby'
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_2_130(self):
        '2.13 Smazani nssetu'
        epp_cli.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_2_140(self):
        '2.14 Smazani kontaktu'
        epp_cli.delete_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_2_150(self):
        '2.15 Check na smazany kontakt'
        epp_cli.check_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 1, '%s nelze smazat'%handle_contact)

    def test_2_160(self):
        '2.16 Poll require'
        # 1000 OK (ack)
        # 1300 No messages
        # 1301 Any message
        epp_cli.poll('req')
        if epp_cli.is_val() not in (1000,1300,1301):
            self.assertEqual(0, 1, unitest_ccreg_share.get_reason(epp_cli))

    
def __info_contact__(prefix, cols, scope, key=None, pkeys=[]):
    'Check info-[object] against selected set.'
    prevkeys = ':'.join(pkeys)
    if key:
        data = scope[key]
    else:
        data = scope
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    # prepare list disclose, hide: if disclose_flag is 0, names must be moved into hide
    keep_disclose = cols['disclose']
    cols['hide'] = []
    if cols['disclose_flag'] == 'n':
        cols['hide'] = cols['disclose']
        cols['disclose'] = []
    if len(cols['hide']):
        cols['disclose'] = tuple([n for n in contact_disclose if n not in cols['hide']])
    else:
        cols['hide'] = tuple([n for n in contact_disclose if n not in cols['disclose']])
    #--------------------------------
    for k,v in cols.items():
        key = '%s:%s'%(prefix,k)
        if data.has_key(key):
            if type(v) is dict:
                pkeys.append(key)
                err = __info_contact__(prefix, v, data, key, pkeys)
                pkeys.pop()
                if len(err): errors.extend(err)
            else:
                if type(data[key]) is list:
                    vals = tuple(data[key])
                else:
                    vals = data[key]
                if not unitest_ccreg_share.are_equal(vals,v):
                    errors.append('Data nesouhlasi:\n%s.%s JSOU:%s MELY BYT:%s'%(prevkeys, key, unitest_ccreg_share.make_str(vals), unitest_ccreg_share.make_str(v)))
        else:
            if key != '%s:disclose_flag'%prefix: # except disclose_flag - it not shown
                errors.append('Chybi klic %s'%key)
    cols['disclose'] = keep_disclose # restore values
    return errors

epp_cli, log_fp, log_step, handle_contact, handle_nsset = (None,)*5

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
    DATA = (
    #'2.3.1 Overevni vsech hodnot vznikleho kontaktu'
    (CCREG_CONTACT[1], {'contact:voice': u'+123.456789', 'contact:org': u'\u010c\xed\u017ekov\xe1 a spol', 'contact:fax': u'+321.564987', 'contact:status.s': u'ok', 'contact:disclose': ['name', 'org', 'addr', 'email', 'fax', 'voice'], 'contact:hide': [], 'contact:email': u'rehor.cizek@mail.cz', 'contact:city': u'\u010cesk\xfd Krumlov', 'contact:pc': u'12300', 'contact:crDate': u'2006-08-08T07:59:03.0Z', 'contact:street': [u'U pr\xe1ce', u'Za monitorem', u'Nad kl\xe1vesnic\xed'], 'contact:crID': u'REG-LRR', 'contact:sp': u'123', 'contact:roid': u'C0000426646-CZ', 'contact:cc': u'CZ', 'contact:name': u'\u0158eho\u0159 \u010c\xed\u017eek', 'contact:id': u'test001'}),
    #'2.6 Info na existujici kontakt a overeni vsech hodnot'
    (CCREG_CONTACT[1], {'contact:voice': u'+123.456789', 'contact:org': u'\u010c\xed\u017ekov\xe1 a spol', 'contact:fax': u'+321.564987', 'contact:status.s': u'ok', 'contact:disclose': ['name', 'org', 'addr', 'voice', 'fax', 'email'], 'contact:hide': [], 'contact:email': u'rehor.cizek@mail.cz', 'contact:city': u'\u010cesk\xfd Krumlov', 'contact:pc': u'12300', 'contact:crDate': u'2006-08-08T07:59:03.0Z', 'contact:street': [u'U pr\xe1ce', u'Za monitorem', u'Nad kl\xe1vesnic\xed'], 'contact:crID': u'REG-LRR', 'contact:sp': u'123', 'contact:roid': u'C0000426646-CZ', 'contact:cc': u'CZ', 'contact:name': u'\u0158eho\u0159 \u010c\xed\u017eek', 'contact:id': u'test001'}),
    #'2.7.1 Overevni vsech hodnot zmeneneho kontaktu'
    (CCREG_CONTACT[2], {'contact:voice': u'+321.987654', 'contact:org': u'Bolen\xed s.r.o.', 'contact:fax': u'+321.987564', 'contact:status.s': u'ok', 'contact:disclose': ['name', 'org', 'addr', 'voice', 'fax', 'email'], 'contact:hide': [], 'contact:email': u'breta.zlucnik@bricho.cz', 'contact:city': u'St\u0159evn\xedkov', 'contact:pc': u'23101', 'contact:crDate': u'2006-08-08T07:59:03.0Z', 'contact:street': (u'Na toaletách',u'U mísy'), 'contact:crID': u'REG-LRR', 'contact:sp': u'321', 'contact:roid': u'C0000426646-CZ', 'contact:cc': u'CZ', 'contact:name': u'B\u0159\xe9\u0165a \u017dlu\u010dn\xedk', 'contact:id': u'test001','contact:ssn':'357','contact:notify_email':'info@zlucnikovi.cz','contact:vat':'753'}),
    )
    print '-'*60
    for cols,vals in DATA:
        errors = __info_contact__('contact', cols, vals)
        if len(errors):
            print "ERRORS:"
            for e in errors:
                print e
        else:
            print "OK, NO ERRORS."
        print '_'*60
