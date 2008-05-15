#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Check NSSET for changes after updating.
"""
import sys
sys.path.insert(0, '')
import unittest
import fred
import unitest_share

FRED_NSSET1 = unitest_share.create_handle('NSSID:U1') ## 'NSSID:examp2134'
##FRED_DOMAIN = '%s.cz'%unitest_share.create_handle('nssetest')
FRED_CONTACT1 = unitest_share.create_handle('CID:U1') ## 'CID:UNITTEST1'
FRED_CONTACT2 = unitest_share.create_handle('CID:U2') ## 'CID:UNITTEST2'

NSSET = {
    'id': FRED_NSSET1, # (required)
    'auth_info': 'heslo', # (required)
    'dns': [ # (required)               list with max 9 items.
        {'name': 'ns.name1.cz', 'addr': ('217.31.207.130','217.31.207.129','217.31.207.128') },
        {'name': 'ns.name2.cz', 'addr': ('217.31.206.130','217.31.206.129','217.31.206.128') },
        ],
    'tech': [FRED_CONTACT1],   # (optional)             unbounded list
    'reportlevel':'0',
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
        global epp_cli, epp_cli_log, handle_contact, handle_nsset, log_fp
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
        '4. Zalozeni nssetu'
        n = NSSET
        epp_cli.create_nsset(n['id'], n['dns'], n['tech'], n['auth_info'], n['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_050(self):
        '5. Pridani NS'
        newdns = {'name':'ns.valid01.cz','addr':('2001:200::fea5:3015',)}
        NSSET['dns'].append(newdns)
        #update_nsset(nsset_id, add, rem, auth_info, reportlevel):
        epp_cli.update_nsset(NSSET['id'], {'dns':newdns})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_055(self):
        '.. Kontrola vsech hodnot nssetu po pridani NS'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_060(self):
        '6. Odebrani NS'
        ns = NSSET['dns'].pop(0)
        # rem: name, tech
        epp_cli.update_nsset(FRED_NSSET1, None, {'name':ns['name']})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_065(self):
        '.. Kontrola vsech hodnot nssetu po odebrani NS'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))


    def test_070(self):
        '7. Pridani tech. kontaktu'
        NSSET['tech'].append(FRED_CONTACT2)
        #update_nsset(nsset_id, add, rem, auth_info, reportlevel):
        epp_cli.update_nsset(FRED_NSSET1, {'tech':FRED_CONTACT2})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_075(self):
        '.. Kontrola vsech hodnot nssetu po pridani tech. kontaktu'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_080(self):
        '8. Odebrani tech. kontaktu'
        tech = NSSET['tech'].pop(0)
        #update_nsset(nsset_id, add, rem, auth_info, reportlevel):
        epp_cli.update_nsset(FRED_NSSET1, None, {'tech':tech})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_085(self):
        '.. Kontrola vsech hodnot nssetu po odebrani tech. kontaktu'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_090(self):
        '9. Zmena auth info'
        NSSET['auth_info'] = 'nove heslo'
        epp_cli.update_nsset(FRED_NSSET1, None, None, NSSET['auth_info'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_095(self):
        '.. Kontrola vsech hodnot nssetu po zmene auth info'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_100(self):
        '10. Zmena reportlevelu'
        NSSET['reportlevel'] = '6'
        epp_cli.update_nsset(FRED_NSSET1, None, None, None, NSSET['reportlevel'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_105(self):
        '... Kontrola vsech hodnot nssetu po zmene reportlevelu'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        

    def test_110(self):
        '11. Zmena adresy u posledniho NS (soucasne odebrani a pridani)'
        ns = NSSET['dns'].pop()
        newdns = {'name':ns['name'],'addr':('2001:200::fea5:3015','217.31.206.118')}
        NSSET['dns'].append(newdns)
        epp_cli.update_nsset(FRED_NSSET1, {'dns':newdns}, {'name':ns['name']})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_115(self):
        '... Kontrola vsech hodnot nssetu po zmene adresy u posledniho NS'
        epp_cli.info_nsset(FRED_NSSET1)
        errors = unitest_share.compare_nsset_info(epp_cli, NSSET, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))



    def test_900(self):
        '11. Smazani nssetu'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_910(self):
        '12. Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

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
