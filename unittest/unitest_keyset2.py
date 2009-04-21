#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Check KEYSET for changes after updating.
"""
import sys, copy
sys.path.insert(0, '..')
import unittest
import fred
import unitest_share

FRED_KEYSET1 = unitest_share.create_handle('KEYSID:U1')
FRED_KEYSET2 = unitest_share.create_handle('KEYSID:U2')
FRED_KEYSET3 = unitest_share.create_handle('KEYSID:U3')
FRED_KEYSET4 = unitest_share.create_handle('KEYSID:U4')
FRED_KEYSET5 = unitest_share.create_handle('KEYSID:U5')
FRED_CONTACT1 = unitest_share.create_handle('CID:U1')
FRED_CONTACT2 = unitest_share.create_handle('CID:U2')
FRED_CONTACT3 = unitest_share.create_handle('CID:U3')

FRED_CONTACT10 = unitest_share.create_handle('CID:U10')
FRED_CONTACT11 = unitest_share.create_handle('CID:U11')
FRED_CONTACT12 = unitest_share.create_handle('CID:U12')
FRED_CONTACT13 = unitest_share.create_handle('CID:U13')
FRED_CONTACT14 = unitest_share.create_handle('CID:U14')
FRED_CONTACT15 = unitest_share.create_handle('CID:U15')

A_LOT_OF_CONTACTS = [FRED_CONTACT10, FRED_CONTACT11, FRED_CONTACT12, FRED_CONTACT13, FRED_CONTACT14, FRED_CONTACT15]

DS = [{'key_tag': '1',  'alg': '1',  'digest_type': '1', 'digest': '0123456789012345678901234567890123456789'}, 
      {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': '9876543210987654321098765432109876543210', 'max_sig_life': '1'}]
DSREF = []

DNSKEY = [
    {'flags': '257', 'protocol': '3', 'alg': '5', 
        'pub_key': 'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8'
        'TSoH4+jPNwiWmT3+PQVbL5TD90KVw6S09Ae9cYU8A7xnZWkfzq8q2pX6'
        '7yVvshlQqJnuSV6uMBEMziIGu3NZEJb9eTl1T5q1cli7Fk+xTt5GVvZR' 
        '3BJhtRAf'}, 
    ]
DNSKEYREF = []

DS_OK = {'key_tag': '1',  'alg': '1',  'digest_type': '1', 'digest': 'bac69ce188c234ae02142d554c015c20f656aa4a'}
DS_OK2 = {'key_tag': '1',  'alg': '1',  'digest_type': '1', 'digest': '716a4d6a847887b0f03a3cda8a9319e2f65a22b4'}
BAD_DS_DIGEST_TYPE = {'key_tag': '1','alg': '5', 'digest_type': '3', 'digest': '55823e6fcde38c08f6f09917ae804b44d406808b'}
BAD_DS_DIGEST_LEN_1 = {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': 'eeba3a3a61fd3020d65477671e61797a'}
BAD_DS_DIGEST_LEN_2 = {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': '476d2f4171631aa63fd18501769d419eb446246eca6c6a909db44f9a'}
BAD_DS_SAME = [
        {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': '1e99515b6bef7bc9aa1211fc062bb923c85b6e50'},
        {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': '1e99515b6bef7bc9aa1211fc062bb923c85b6e50'}
        ]


KEYSET = {
    'id': FRED_KEYSET1, # (required)
    'auth_info': 'heslo', # (required)
    'ds': DS, 
    'dsref': DSREF, 
    'dnskey': DNSKEY, 
    'dnskeyref': DNSKEYREF, 
    'tech': [FRED_CONTACT1],   # (optional)             unbounded list
    }

newds = {'alg': '1', 'digest_type': '1', 'digest': 'ABCDE12345BBBBBB2345ABCDE12345ABCDE12345', 'key_tag': '3'}

class Test(unittest.TestCase):

    def __verify_results__(self, needle, label):
        'Pomocna funkce'
        haystack = ['']
        not_found = 1
        while haystack:
            if needle in haystack:
                not_found = 0
                break
            epp_cli.get_results()
            self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
            haystack = epp_cli.is_val(('data','list'))
        self.failIf(not_found, '%s %s se v seznamu nenachazi.'%(label, needle))



    def setUp(self):
        'Check if client is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)
        

    def test_000(self):
        '1. Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_log, handle_contact, handle_keyset, log_fp
        # create client object
        epp_cli = fred.Client()
        epp_cli._epp.load_config()
        # Validation MUST be disabled bycause we test commands with misssing required parameters
        epp_cli.set_validate(0)
        if fred.translate.options['no_validate'] == '':
            # Set ON validation of the server answer. 
            # This behavor is possible switch off by option -x --no_validate
            epp_cli._epp.run_as_unittest = 1

        # login:
        # prihlasovaci udaje si nastavte v config v sekci [connect_...]:
        logins = epp_cli._epp.get_logins_and_passwords(2) # 2 - num of login tuples: [('login','password'), ...]
        epp_cli.login(logins[0][0], logins[0][1])

        epp_cli_log = epp_cli
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')

            
            
    def test_030(self):
        '2. Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Ulice','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
            
    def test_031(self):
        '3.1 Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Dolni','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_032(self):
        '3.2 Zalozeni 3. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT3, u'Jujo Pajo', 'jujo@cokoliv.cz', 'Horni', 'Ostrava, pico', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_033(self):
        '3.3 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT10, u'Jujo Pajo 1', 'jujo1@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_034(self):
        '3.4 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT11, u'Jujo Pajo 2', 'jujo2@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_035(self):
        '3.5 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT12, u'Jujo Pajo 3', 'jujo3@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_036(self):
        '3.6 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT13, u'Jujo Pajo 4', 'jujo4@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_037(self):
        '3.7 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT14, u'Jujo Pajo 5', 'jujo5@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_038(self):
        '3.8 zalozeni pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT15, u'Jujo Pajo 6', 'jujo6@cokoliv.cz', 'Horni', 'Ostrava', '12345', 'CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4. Zalozeni keysetu'
        n = KEYSET
        epp_cli.create_keyset(n['id'], n['ds'], n['dsref'], n['dnskey'], n['dnskeyref'], n['tech'], n['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_041(self):
        '4.1 pokus o zalozeni keysetu s neplatnym ds-zaznamem (spatna hodnota digest typu)'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, BAD_DS_DIGEST_TYPE, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_042(self):
        '4.2 pokus o zalozeni keysetu s neplatnym ds-zaznamem (digest prilis kratky - md5)'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, BAD_DS_DIGEST_LEN_1, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_043(self):
        '4.3 pokus o zalozeni keysetu s neplatnym ds-zaznamem (digest prilis dlouhy - sha256)'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, BAD_DS_DIGEST_LEN_2, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_044(self):
        '4.4 zalozeni noveho keysetu s ds-zaznamem, ktery jiz v databazi existuje'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET3, KEYSET['ds'], n['dsref'], n['dnskey'], n['dnskeyref'], [FRED_CONTACT3], KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_045(self):
        '4.5 pokus zalozeni noveho keysetu se dvema stejnyma ds-zaznamama'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, BAD_DS_SAME, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_046(self):
        '4.6 pokus zalozeni keysetu bez administratorskeho kontaktu'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET4, DS_OK, n['dsref'], n['dnskey'], n['dnskeyref'], [""], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_047(self):
        '4.7 pokus o zalozeni keysetu s neexistujicim administratorskym kontaktem'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET4, DS_OK, n['dsref'], n['dnskey'], n['dnskeyref'], ["CID:1234"], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_048(self):
        '4.8 pokus o zalozeni keysetu se dvama stejnymi administratorskymi kontakty'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET3, DS_OK2, n['dsref'], n['dnskey'], n['dnskeyref'], [FRED_CONTACT11, FRED_CONTACT11], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_049(self):
        '4.9 zalozeni keyset s mnoha adminiatratorskymi kontakty'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET5, DS_OK2, n['dsref'], n['dnskey'], n['dnskeyref'], A_LOT_OF_CONTACTS, KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '5. Pridani DS'
        newds = {'alg': '1', 'digest_type': '1', 'digest': 'ABCDE12345ABCDE12345ABCDE12345ABCDE12345', 'key_tag': '3'}
        KEYSET['ds'].append(newds)
        epp_cli.update_keyset(KEYSET['id'], {'ds':newds})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_051(self):
        '5.1 pokus o pridani neplatneho DS zaznamu (spatny digest typ)'
        epp_cli.update_keyset(KEYSET['id'], {'ds':BAD_DS_DIGEST_TYPE})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_052(self):
        '5.2 pokus o pridani neplatneho DS zaznamu (digest prilis kratky - md5)'
        epp_cli.update_keyset(KEYSET['id'], {'ds':BAD_DS_DIGEST_LEN_1})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_053(self):
        '5.3 pokus o pridani neplatneho DS zaznamu (digest prilis dlouhy - sha256)'
        epp_cli.update_keyset(KEYSET['id'], {'ds':BAD_DS_DIGEST_LEN_2})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_054(self):
        '5.4 pridani DS zaznamu ktery jiz v databazi existuje'
        epp_cli.update_keyset(KEYSET['id'], {'ds':newds})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_055(self):
        '.. Kontrola vsech hodnot keysetu po pridani DS'
        epp_cli.info_keyset(FRED_KEYSET1)
        DS.append(newds)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_060(self):
        '6. Odebrani DS'
        ds = KEYSET['ds'].pop(0)
        # rem: name, tech
        epp_cli.update_keyset(FRED_KEYSET1, None, {'ds':ds})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_065(self):
        '.. Kontrola vsech hodnot keysetu po odebrani DS'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_070(self):
        '7. Pridani tech. kontaktu'
        KEYSET['tech'].append(FRED_CONTACT2)
        epp_cli.update_keyset(FRED_KEYSET1, {'tech':FRED_CONTACT2})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_075(self):
        '.. Kontrola vsech hodnot keysetu po pridani tech. kontaktu'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_080(self):
        '8. Odebrani tech. kontaktu'
        tech = KEYSET['tech'].pop(0)
        epp_cli.update_keyset(FRED_KEYSET1, None, {'tech':tech})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_085(self):
        '.. Kontrola vsech hodnot keysetu po odebrani tech. kontaktu'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_090(self):
        '9. Zmena auth info'
        KEYSET['auth_info'] = 'nove heslo'
        epp_cli.update_keyset(FRED_KEYSET1, None, None, KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_095(self):
        '.. Kontrola vsech hodnot keysetu po zmene auth info'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_098(self):
        '10.0 zalozeni keysetu'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET4, DS_OK, n['dsref'], n['dnskey'], n['dnskeyref'], FRED_CONTACT3, KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_099(self):
        '10.1 pokus o odebrani jedineho zbyvajiciho administratorskeho kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, None, {'tech':FRED_CONTACT3})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_100(self):
        '10.1.1 pokus o pridani kontaktu ktery je jiz keyset-u prirazen'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':FRED_CONTACT3}, None)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_102(self):
        '10.2 pokus o odebrani administratorskeho kontaktu a okamzite pridani tehoz'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':FRED_CONTACT3}, {'tech':FRED_CONTACT3})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_103(self):
        '10.3 odebrani kontaktu a okamzite pridani noveho jineho'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':FRED_CONTACT1}, {'tech':FRED_CONTACT3})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_104(self):
        '10.4 pridani spousta kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':A_LOT_OF_CONTACTS}, None)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_105(self):
        '10.5 pokus o pridani neexistujici kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':'CID:1234'}, None)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_106(self):
        '10.6 odebrani spousta kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, None, {'tech':A_LOT_OF_CONTACTS})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_107(self):
        '10.7 pokus o odebrani neexistujiciho kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, None, {'tech':'CID:0987'})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_108(self):
        '10.8 pokus o pridani dvou stejnych kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':[FRED_CONTACT3, FRED_CONTACT3]}, None)
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_109(self):
        '10.9 pridani dvou ruznym kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, {'tech':[FRED_CONTACT3, FRED_CONTACT2]}, None)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_110(self):
        '10.10 pokus o odebrani dvou stejnych kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, None, {'tech':[FRED_CONTACT3, FRED_CONTACT3]})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_111(self):
        '10.11 odebrani dvou ruznych kontaktu'
        epp_cli.update_keyset(FRED_KEYSET4, None, {'tech':[FRED_CONTACT2, FRED_CONTACT3]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_112(self):
        '10.12 odebrani dvou ruznych kontaktu z mnoha'
        epp_cli.update_keyset(FRED_KEYSET5, None, {'tech':[FRED_CONTACT11, FRED_CONTACT15, FRED_CONTACT12]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


    def test_200(self):
	'10.50 prep_keysets: Seznam keysetu'
	epp_cli.prep_keysets()
	self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
	self.failIf(int(epp_cli.is_val(('data','count'))) == 0, 'Seznam je prazdny prestoze by tam mela byt alespon jedna polozka.')

    def test_201(self):
	'10.51 prep_keysets_by_contact: Seznam keysetu podle kontaktu'
	epp_cli.prep_keysets_by_contact(FRED_CONTACT13)
	self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

	print 'Number of keysets found: ', int(epp_cli.is_val(('data','count')))

	self.failIf(int(epp_cli.is_val(('data','count'))) == 0, 'Seznam je prazdny prestoze by tam mela byt alespon jedna polozka.')

    def test_202(self):
	'10.51.1 get_results: (prep_keyset_by_contact): Overeni zda je v seznamu spravny keyset'
	self.__verify_results__(FRED_KEYSET5, 'Keyset')
	
    def test_205(self):
	'10.52 prep_keysets_by_contact: Seznam keysetu podle kontaktu'
	epp_cli.prep_keysets_by_contact(FRED_CONTACT1)
	self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

	print 'Number of keysets found: ', int(epp_cli.is_val(('data','count')))

	self.failIf(int(epp_cli.is_val(('data','count'))) == 0, 'Seznam je prazdny prestoze by tam mela byt alespon jedna polozka.')

    def test_206(self):
	'10.52.1 get_results: (prep_keyset_by_contact): Overeni zda je v seznamu spravny keyset'
	self.__verify_results__(FRED_KEYSET4, 'Keyset')

    def test_897(self):
        '10.97 smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET5)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_898(self):
        '10.98 smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET3)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_899(self):
        '10.99 smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET4)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_900(self):
        '11. Smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_905(self):
        '11.1 Smazani 3.pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT3)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_910(self):
        '12. Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_920(self):
        '13. Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_930(self):
        '14.0 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT10)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_931(self):
        '14.1 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT11)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_932(self):
        '14.2 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT12)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_933(self):
        '14.3 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT13)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_934(self):
        '14.4 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT14)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_935(self):
        '14.5 smazani pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT15)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_999(self):
        '99. logout'
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))

epp_cli, epp_cli_log, log_fp, log_step, poll_msg_id = (None,)*5

if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
