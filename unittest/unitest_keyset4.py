#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Check KEYSET for changes after updating.
"""
import sys
sys.path.insert(0, '..')
import unittest
import fred
import unitest_share

FRED_KEYSET1 = unitest_share.create_handle('KEYSID:U1')
FRED_KEYSET2 = unitest_share.create_handle('KEYSID:U2')
FRED_KEYSET3 = unitest_share.create_handle('KEYSID:U3')
FRED_KEYSET4 = unitest_share.create_handle('KEYSID:U4')

FRED_CONTACT1 = unitest_share.create_handle('CID:U1')
FRED_CONTACT2 = unitest_share.create_handle('CID:U2')

DS = [{'key_tag': '1',  'alg': '1',  'digest_type': '1', 'digest': 'dbccddaa768e340e0dfb2e7b39aa2b88d9069236', 'max_sig_life': '1000'}]
DSREF = []
DS_DUP = [
        {'key_tag': '1','alg': '5', 'digest_type': '1', 'digest': '1e99515b6bef7bc9aa1211fc062bb923c85b6e50'},
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': 'dbccddaa768e340e0dfb2e7b39aa2b88d9069236', 'max_sig_life': '1000'}]

DS_BAD_TYPE = [
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': 'cbf67919c3108df24e92a5f386ac5dd1eefb5bbc'},
        {'key_tag': '1','alg': '1', 'digest_type': '8', 'digest': '124c4d0ca58776ba0f69d914360bc655d0e4baf6', 'max_sig_life': '100'}]

DS_BAD_DIGEST_1 = [
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': '339e28818f74d58c99f6684a72a5df05108e0cf1'},
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': '8fe20821f9f92544a6b91a9364c2592d', 'max_sig_life': '100'}]

DS_BAD_DIGEST_2 = [
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': '19838413b23fb9e848b0e75c57c2c20b624bd765'},
        {'key_tag': '1','alg': '1', 'digest_type': '1', 'digest': 'd382bf19eb86f79427f619895620d72f0c91bece235426dd0a4dc0b5100f254f', 'max_sig_life': '100'}]

DNSKEY = [
    {'flags': '257', 'protocol': '3', 'alg': '5', 
        'pub_key': 'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8'
        'TSoH4+jPNwiWmT3+PQVbL5TD90KVw6S09Ae9cYU8A7xnZWkfzq8q2pX6'
        '7yVvshlQqJnuSV6uMBEMziIGu3NZEJb9eTl1T5q1cli7Fk+xTt5GVvZR' 
        '3BJhtRAf'}, 
    ]
DNSKEYREF = []

KEYSET = {
    'id': FRED_KEYSET1, # (required)
    'auth_info': 'heslo', # (required)
    'ds': DS, 
    'dsref': DSREF, 
    'dnskey': DNSKEY, 
    'dnskeyref': DNSKEYREF, 
    'tech': [FRED_CONTACT1],   # (optional)             unbounded list
    }

    
class Test(unittest.TestCase):


    def setUp(self):
        'Check if cilent is online.'
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
            
    # def test_031(self):
        # '3. Zalozeni 2. pomocneho kontaktu'
        # epp_cli.create_contact(FRED_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Dolni','Praha', '12300','CZ')
        # self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4. Zalozeni validniho keysetu'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET1, DS, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_041(self):
        '4.1 zalozeni validniho keysetu (1.ds-zaznam v poradku, 2.ds-zaznam jiz existuje v databazi)'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET3, DS_DUP, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_042(self):
        '4.2 Pokus o zalozeni nevalidniho keysetu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: spatny typ digest-u)'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, DS_BAD_TYPE, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_043(self):
        '4.3 Pokus o zalozeni nevalidniho keysetu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: digest prilis kratky (md5))'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, DS_BAD_DIGEST_1, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_044(self):
        '4.4 Pokus o zalozeni nevalidniho keysetu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: digest prilis dlouhy (sha256))'
        n = KEYSET
        epp_cli.create_keyset(FRED_KEYSET2, DS_BAD_DIGEST_2, n['dsref'], n['dnskey'], n['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_051(self):
        '5.1 Pokus o pridani neplatneho ds-zaznamu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: jiz existuje v databazi)'
        epp_cli.update_keyset(FRED_KEYSET1, {'ds':DS_DUP})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_052(self):
        '5.2 Pokus o pridani neplatneho ds-zaznamu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: spatny typ digest-u)'
        epp_cli.update_keyset(FRED_KEYSET1, {'ds':DS_BAD_TYPE})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_053(self):
        '5.3 Pokus o pridani neplatneho ds-zaznamu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: digest prilis kratky (md5))'
        epp_cli.update_keyset(FRED_KEYSET1, {'ds':DS_BAD_DIGEST_1})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_054(self):
        '5.4 Pokus o pridani neplatneho ds-zaznamu (1.ds-zaznam v poradku, 2.ds-zaznam spatny: digest prilis dlouhy (sha256))'
        epp_cli.update_keyset(FRED_KEYSET1, {'ds':DS_BAD_DIGEST_2})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_900(self):
        '11. Smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_901(self):
        '11.1 Smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET3)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    # def test_910(self):
        # '12. Smazani 2. pomocneho kontaktu'
        # epp_cli.delete_contact(FRED_CONTACT2)
        # self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_920(self):
        '13. Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

        
        
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
        if log_fp: log_fp.close()
