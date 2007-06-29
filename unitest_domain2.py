#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import unittest
import fred
import unitest_share


#-----------------------
FRED_CONTACT1 = unitest_share.create_handle('CID:D1')
FRED_CONTACT2 = unitest_share.create_handle('CID:D2')
FRED_NSSET1 = unitest_share.create_handle('NSSID:D1')
FRED_NSSET2 = unitest_share.create_handle('NSSID:D2')
FRED_DOMAIN1 = '%s.cz'%unitest_share.create_handle('test')
FRED_DOMAIN2 = unitest_share.create_enumdomain(); 
FRED_DOMAIN3 = '%s.cz'%unitest_share.create_handle('tmp')
FRED_DOMAIN_PASSW = 'heslicko'
FRED_DOMAIN_PASSW_NEW = 'noveheslo'
INVALID_DOMAIN_NAME = 'myname.net'
#-----------------------

NSSET_DNS = (
            {'name': u'ns.pokus1.cz', 'addr': ('217.31.204.130','217.31.204.129')},
            {'name': u'ns.pokus2.cz', 'addr': ('217.31.204.131','217.31.204.127')},
        )

DOMAIN = {
       'name':FRED_DOMAIN1,
       'auth_info':FRED_DOMAIN_PASSW,
       'nsset':FRED_NSSET1,
       'registrant':FRED_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(FRED_CONTACT1,),
          }        


class TestDomain(unittest.TestCase):

    def __get_results__(self, needle, label):
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
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)

    def test_000(self):
        '1.0 Inicializace spojeni a definovani testovacich handlu'
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
        '4.3.1 Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
            
    def test_031(self):
        '4.3.2 Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(FRED_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Praha','CZ','heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_040(self):
        '4.4.1 Zalozeni 1. pomocneho nssetu'
        epp_cli.create_nsset(FRED_NSSET1, NSSET_DNS, FRED_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_041(self):
        '4.4.2 Zalozeni 2. pomocneho nssetu'
        epp_cli.create_nsset(FRED_NSSET2, NSSET_DNS, FRED_CONTACT1, 'heslo')
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))



    def test_080(self):
        '4.8  Zalozeni nove domeny'
        d = DOMAIN
        epp_cli.create_domain(d['name'], d['registrant'], d['auth_info'], d['nsset'], d['period'], d['contact'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
        

        
    def test_310(self):
        '4.25.1 Smazani domeny'
        d = DOMAIN
        epp_cli.delete_domain(d['name'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
        
    def test_350(self):
        '4.27.0 Smazani 2. pomocneho nssetu'
        epp_cli.delete_nsset(FRED_NSSET2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_360(self):
        '4.27.1 Smazani 1. pomocneho nssetu'
        epp_cli.delete_nsset(FRED_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_370(self):
        '4.27.2 Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(FRED_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_380(self):
        '4.27.3 Smazani 1. pomocneho kontaktu'
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
        suite.addTest(unittest.makeSuite(TestDomain))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()
