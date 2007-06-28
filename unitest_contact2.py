#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Testing process update one contact item and than check
changes.
"""
import time
import unittest
import fred
import unitest_share

get_ltext = fred.session_base.get_ltext

CONTACT_HANDLE = unitest_share.create_handle('CID:')
CONTACT_INFO = {   # create contact
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
    }



class TestContact(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        unitest_share.write_log(epp_cli_log, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli_log)

    def test_000(self):
        'Init connection'
        global epp_cli, epp_cli_log, log_fp
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
        logins = epp_cli._epp.get_logins_and_passwords(2) # 2 - num of login tuples: [('login','password'), ...]
        epp_cli.login(logins[0][0], logins[0][1])

        epp_cli_log = epp_cli
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')


    def test_010(self):
        'Hello - Check validity greeting'
        epp_cli.hello()
        self.assertTrue(len(epp_cli.is_val(('data','svID'))) > 0, unitest_share.get_reason(epp_cli))

    def test_020(self):
        'Create contact'
        d = CONTACT_INFO
        epp_cli.create_contact(d['id'], 
            d['name'], d['email'], d['city'], d['cc'], d['auth_info'],  d['org'], 
            d['street'], d['sp'], d['pc'], d['voice'], d['fax'], d['disclose'],
            d['vat'], d['ident'], d['notify_email'])
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))

    def test_030(self):
        'Check all values'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))


    def test_040(self):
        '01. Change email only'
        key = 'email'
        CONTACT_INFO[key] = 'pepa.zdepa@novy.mail.cz'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_045(self):
        '... Check all values after updating email'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_050(self):
        '02. Change notify email only'
        global CONTACT_INFO
        key = 'notify_email'
        CONTACT_INFO[key] = 'pepa.zdepa@novy.notify.mail.cz'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_055(self):
        '... Check all values after updating notify email'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

        
    def test_060(self):
        '03. Change name only'
        global CONTACT_INFO
        key = 'name'
        CONTACT_INFO[key] = u'Miloš Čuřil'
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info': {key: CONTACT_INFO[key]}, })
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_065(self):
        '... Check all values after updating name'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_070(self):
        '04. Change city and CC'
        global CONTACT_INFO
        CONTACT_INFO['city'] = u'Říčany u Prahy'
        CONTACT_INFO['cc'] = 'AU'
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info':{'addr':{'city': CONTACT_INFO['city'], 'cc': CONTACT_INFO['cc']}}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_075(self):
        '... Check all values after updating city and CC'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_090(self):
        '06. Change authInfo only'
        global CONTACT_INFO
        key = 'auth_info'
        CONTACT_INFO[key] = 'nove-heslo-pro-transfer'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_095(self):
        '... Check all values after updating authInfo'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_100(self):
        '07. Change organization only'
        global CONTACT_INFO
        key = 'org'
        CONTACT_INFO[key] = u'Žouželka a spol.'
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info':{key: CONTACT_INFO[key]}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_105(self):
        '... Check all values after updating organisation'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_110(self):
        '08. Change street only'
        global CONTACT_INFO
        key = 'street'
        CONTACT_INFO[key] = (u'Mřížová', u'Malušova', u'Hrušková')
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info':{'addr':{
            'city': CONTACT_INFO['city'], 
            'cc': CONTACT_INFO['cc'], 
            key: CONTACT_INFO[key]}}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_115(self):
        '... Check all values after updating street'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_120(self):
        '09. Change sp only'
        global CONTACT_INFO
        key = 'sp'
        CONTACT_INFO[key] = '0459'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info':{'addr':{
            'city': CONTACT_INFO['city'], 
            'cc': CONTACT_INFO['cc'], 
            key: CONTACT_INFO[key]}}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_125(self):
        '... Check all values after updating sp'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_130(self):
        '10. Change pc'
        global CONTACT_INFO
        key = 'pc'
        CONTACT_INFO[key] = '15800'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        epp_cli.update_contact(CONTACT_HANDLE, {'postal_info':{'addr':{
            'city': CONTACT_INFO['city'], 
            'cc': CONTACT_INFO['cc'], 
            key: CONTACT_INFO[key]}}})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_135(self):
        '... Check all values after updating pc'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_140(self):
        '11. Change voice only'
        global CONTACT_INFO
        key = 'voice'
        CONTACT_INFO[key] = '+245.468930'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_145(self):
        '... Check all values after updating voice'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_150(self):
        '12. Change fax only'
        global CONTACT_INFO
        key = 'fax'
        CONTACT_INFO[key] = '+420.888333'
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_155(self):
        '... Check all values after updating fax'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_160(self):
        '13. Change disclose only'
        global CONTACT_INFO
        key = 'disclose'
        CONTACT_INFO[key] = {'flag':'n', 'data':('voice','fax','email', 'vat')} # (name, )
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_165(self):
        '... Check all values after updating disclose'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_170(self):
        '14. Change VAT only'
        global CONTACT_INFO
        key = 'vat'
        CONTACT_INFO[key] = '567000567' # 963
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_175(self):
        '... Check all values after updating VAT'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_180(self):
        '15. Change Ident only'
        global CONTACT_INFO
        key = 'ident'
        CONTACT_INFO[key] = {'type':'birthday','number':'28.6.2007'} # {'type':'op','number':'12345679'}
        epp_cli.update_contact(CONTACT_HANDLE, {key: CONTACT_INFO[key]})
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))
    def test_185(self):
        '... Check all values after updating Ident'
        epp_cli.info_contact(CONTACT_HANDLE)
        errors = unitest_share.compare_contact_info('contact', CONTACT_INFO, epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))




    def test_999(self):
        'END: Smazání kontaktu'
        epp_cli.delete_contact(CONTACT_HANDLE)
        self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


# global variables of the client object and login file
epp_cli, epp_cli_log, log_fp, log_step = (None,)*4

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


