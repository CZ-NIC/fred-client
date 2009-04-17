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
FRED_CONTACT1 = unitest_share.create_handle('CID:U1')
FRED_CONTACT2 = unitest_share.create_handle('CID:U2')

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
            
    def test_031(self):
        '3. Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Dolni','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4. Zalozeni keysetu'
        n = KEYSET
        epp_cli.create_keyset(n['id'], n['ds'], n['dsref'], n['dnskey'], n['dnskeyref'], n['tech'], n['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '5. Pridani kontaktu ke keysetu'
        KEYSET['tech'].append(FRED_CONTACT2)
        epp_cli.update_keyset(KEYSET['id'], {'tech':FRED_CONTACT2})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_060(self):
        '.. Kontrola vsech hodnot keysetu po pridani kontaktu'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_070(self):
        '6. Odebrani kontaktu'
        con = KEYSET['tech'].pop(0)
        epp_cli.update_keyset(FRED_KEYSET1, None, {'tech':con})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_080(self):
        '.. Kontrola vsech hodnot keysetu po odebrani kontaktu'
        epp_cli.info_keyset(FRED_KEYSET1)
        errors = unitest_share.compare_keyset_info(epp_cli, KEYSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_900(self):
        '11. Smazani keysetu'
        epp_cli.delete_keyset(FRED_KEYSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_910(self):
        '12. Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_920(self):
        '13. Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT1)
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
        if log_fp: log_fp.close()
