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

FRED_CONTACT1 = unitest_share.create_handle('CID:U1')

DNSKEY = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo='}]
DNSKEY_BADFLAGS = [{
    'flags':    '1',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo='}]
DNSKEY_BADPROTOCOL = [{
    'flags':    '0',
    'protocol': '9',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo='}]
DNSKEY_BADALG = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '59',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo='}]
# key ma tri rovnitka na konci - nevalidni
DNSKEY_BADKEY1 = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgL==='}]
# key ma uvnitr nevalidni znak (@)
DNSKEY_BADKEY2 = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwY@AwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo='}]
# key ma uvnitr nevalidni znak (=)
DNSKEY_BADKEY3 = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2E=OWQxNGQ1NDNiYTU2OCAgLQo='}]
# klic ma spatnou delku
DNSKEY_BADKEY4 = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQoz='}]
# klic ma spatnou delku
DNSKEY_BADKEY5 = [{
    'flags':    '0',
    'protocol': '3',
    'alg':      '5',
    'pub_key':  'MmM4ZDBjNzhjODMwYjAwOTdjNjVmZWM3Y2EyOWQxNGQ1NDNiYTU2OCAgLQo'}]
DNSKEY_MANY = [
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q00='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q01='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q02='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q03='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q04='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q05='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q06='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q07='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q08='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q09='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q10='},
        {'alg': '5', 'flags': '0', 'protocol': '3', 'pub_key': 'q11='}]

DS = [{'key_tag': '1',  'alg': '3',  'digest_type': '1', 'digest': '7752dbd36b05b5e074c3fe94b2b3e977582b3cf2', 'max_sig_life': '1000'}]
DSREF = []
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

            
            
    def test_020(self):
        '2. Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Ulice','Praha', '12300','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_030(self):
        '3.0 Pokus o zalozeni nevalidniho keysetu - spatna polozka "flags"'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADFLAGS, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_031(self):
        '3.1 Pokus o zalozeni nevalidniho keysetu - spatna polozka "protocol"'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADPROTOCOL, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_032(self):
        '3.2 Pokus o zalozeni nevalidniho keysetu - spatna polozka "alg"'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADALG, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_033(self):
        '3.3 Pokus o zalozeni nevalidniho keysetu - spatny klic - vice vyplnovacich znaku nez je dovoleno'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADKEY1, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_034(self):
        '3.4 Pokus o zalozeni nevalidniho keysetu - spatny klic - obsahuje nevalidni znak'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADKEY2, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_035(self):
        '3.5 Pokus o zalozeni nevalidniho keysetu - spatny klic - obsahuje vyplnovaci znak ktery neni na konci klice'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADKEY3, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_036(self):
        '3.6 Pokus o zalozeni nevalidniho keysetu - spatny klic - spatna delka klice #1'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADKEY4, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_037(self):
        '3.7 Pokus o zalozeni nevalidniho keysetu - spatny klic - spatna delka klice #2'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_BADKEY5, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    
    def test_038(self):
        '3.8 Pokus o zalozeni nevalidniho keysetu - dvakrat je pouzit stejny dnskey zaznam'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY+DNSKEY, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_039(self):
        '3.9 Pokus o zalozeni nevalidniho keysetu - prilis mnoho dnskey zaznamu'
        epp_cli.create_keyset(FRED_KEYSET1, KEYSET['ds'], KEYSET['dsref'], DNSKEY_MANY, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4.0 Pridani Keysetu #1 s jednim DS zaznamem a jednim DNSKey zaznamem'
        epp_cli.create_keyset(FRED_KEYSET1, DS, KEYSET['dsref'], DNSKEY, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_041(self):
        '4.1 Odebrani DS zaznamu z Keysetu #1'
        epp_cli.update_keyset(FRED_KEYSET1, None, {'ds':DS})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_042(self):
        '4.2 Pokus o odebrani zbyvajiciho DNSKey zaznamu z Keysetu #1'
        epp_cli.update_keyset(FRED_KEYSET1, None, {'dnskey':DNSKEY})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '5.0 Pridani Keysetu #2 s jednim DS zaznamem a jednim DNSKey zaznamem'
        epp_cli.create_keyset(FRED_KEYSET2, DS, KEYSET['dsref'], DNSKEY, KEYSET['dnskeyref'], KEYSET['tech'], KEYSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_051(self):
        '5.1 Pokus o odebrani DNSKey zaznamu (je predan dvakrat) z Keysetu #1'
        epp_cli.update_keyset(FRED_KEYSET2, None, {'dnskey':DNSKEY+DNSKEY})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
 
    def test_052(self):
        '5.2 Odebrani DNSKey zaznamu z Keysetu #2'
        epp_cli.update_keyset(FRED_KEYSET2, None, {'dnskey':DNSKEY})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    # tohle vyhodi error jako ze 'Schemas validity error' takze asi tak...
    # def test_053(self):
        # '5.3 Pokus o odebrani zbyvajiciho DS zaznamu z Keysetu #2'
        # epp_cli.update_keyset(FRED_KEYSET2, None, {'ds':DS})
        # self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_054(self):
        '5.4 Pokus o odebrani neexistujiciho DNSKey zaznamu z Keysetu #2'
        epp_cli.update_keyset(FRED_KEYSET2, None, {'dnskey':DNSKEY})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_055(self):
        '5.5 Pokus o pridani existujiciho DS zaznamu do Keysetu #2'
        epp_cli.update_keyset(FRED_KEYSET2, {'ds':DS})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_060(self):
        '6.0 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "flags"'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADFLAGS})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_061(self):
        '6.1 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "protocol"'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADPROTOCOL})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_062(self):
        '6.2 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "alg"'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADALG})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_063(self):
        '6.3 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "key" - vice vyplnovacich znaku nez je dovoleno'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADKEY1})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_064(self):
        '6.4 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "key" - obsahuje nevalidni znak'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADKEY2})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_065(self):
        '6.5 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "key" - obsahuje vyplnovaci znak ktery neni na konci klice'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADKEY3})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_066(self):
        '6.6 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "key" - spatna delka klice #1'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADKEY4})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_067(self):
        '6.7 Pokus o pridani nevalidniho DNSKey zaznamu - spatna polozka "key" - spatna delka klice #2'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_BADKEY5})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_068(self):
        '6.8 Pokus o pridani prilis mnoha DNSKey zaznamu'
        epp_cli.update_keyset(FRED_KEYSET1, {'dnskey':DNSKEY_MANY})
        self.assertNotEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_910(self):
        '13.0 Smazani keysetu #2'
        epp_cli.delete_keyset(FRED_KEYSET2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_911(self):
        '13.1 Smazani keysetu #1'
        epp_cli.delete_keyset(FRED_KEYSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_920(self):
        '14.0 Smazani 1. pomocneho kontaktu'
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
