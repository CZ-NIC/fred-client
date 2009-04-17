#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
sys.path.insert(0, '..')
import re
import unittest
import fred
import unitest_share

FRED_KEYSET1 = unitest_share.create_handle('KEYSID:U1')
FRED_CONTACT1 = unitest_share.create_handle('CID:U1')
FRED_CONTACT2 = unitest_share.create_handle('CID:U2')

DS = [{'key_tag': '1', 'alg': '1', 'digest_type': '1', 'digest': '0123456789012345678901234567890123456789'}, 
      {'key_tag': '1', 'alg': '5', 'digest_type': '1', 'digest': '9876543210987654321098765432109876543210', 'max_sig_life': '1'}]
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
        if epp_cli_TRANSF: self.assert_(epp_cli_TRANSF.is_logon(),'the second client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_to_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_to_log)
        
    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, epp_to_log, log_fp
        # create client object
        epp_cli = fred.Client()
        epp_cli._epp.load_config()
        # validation is possible to switch off through option -x --no_validate
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
    

    def test_001(self):
        '0.0.1 Create a contact to use with the keyset'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Ulice','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_002(self):
        '0.0.2 Second registrar: Create a contact to use with the keyset'
	global epp_to_log
	epp_to_log = epp_cli_TRANSF
        epp_cli_TRANSF.create_contact(FRED_CONTACT2,'Honza Zdepa','pepa@zdepa.cz','Ulice','Praha', '12300','CZ')
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_005(self):
        '0.1 Create keyset'
	global epp_to_log
	epp_to_log = epp_cli
        n = KEYSET
        epp_cli.create_keyset(n['id'], n['ds'], n['dsref'], n['dnskey'], n['dnskeyref'], n['tech'], n['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

	# new
    def test_020(self):
        '10.1.1 Sendauthinfo na existujici keyset.'
        epp_cli.sendauthinfo_keyset(FRED_KEYSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_025(self):
        '10.1.2 Sendauthinfo na neexistujici keyset.'
        epp_cli.sendauthinfo_keyset('KEYSID:notexist007')
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Sendauthinfo na neexistujici keyset proslo.')




    def test_040(self):
        '10.2.1 Check na existujici keyset.'
        epp_cli.check_keyset(FRED_KEYSET1);
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_045(self):
        '10.2.2 Check na neexistujici keyset.'
        epp_cli.check_keyset('KEYSID:notexist007')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '10.2.3 Check na seznam existujiciho a neexistujiciho keysetu'
        handles = (FRED_KEYSET1,'KEYSID:notexist008')
        epp_cli.check_keyset(handles)
        self.assertEqual(epp_cli.is_val(('data',FRED_KEYSET1)), 0)
        self.assertEqual(epp_cli.is_val(('data','KEYSID:notexist008')), 1)


	# -----------------


# TODO poll command (2 testcases to improve so far)
    def test_070(self):
        '11.1 Poll request'
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

    def test_075(self):
        '11.2 Poll ack'
        if id_message:
            epp_cli.poll('ack', id_message)
            if epp_cli.is_val() not in (1000, 1300):
                self.assertEqual(0, 1, unitest_share.get_reason(epp_cli))
       # TODO
        # else:
            # self.__testMethodDoc += ' skip test (no message ID)'


    def test_080(self):
       '11.5 Check na smazany keyset'
       epp_cli.check_keyset(FRED_KEYSET1)
       self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


	# end new 


    def test_100(self):
	'1.0 Try to transfer own keyset (Object not suitable for transfer)'
	epp_cli.transfer_keyset(KEYSET['id'], KEYSET['auth_info'])
	self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
	
    def test_105(self):
	'1.1 Druhy registrator: Pokus o trasfer s neplatnym heslem (Chyba oprávnění)'
	global epp_to_log
	epp_to_log = epp_cli_TRANSF
	epp_cli_TRANSF.transfer_keyset(KEYSET['id'], 'wrong password')
	self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))
	
    def test_110(self):
	'1.2 Druhy registrator: Trasfer nssetu'
	epp_cli_TRANSF.transfer_keyset(KEYSET['id'], KEYSET['auth_info'])
	self.assertEqual(epp_cli_TRANSF.is_val(), 1000, unitest_share.get_reason(epp_cli_TRANSF))

    def test_999(self):
        '99. logout'
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))

epp_cli, epp_cli_TRANSF, epp_to_log, log_fp, handle_contact, handle_nsset,  log_step, id_message, poll_msg_id = (None,)*9

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


