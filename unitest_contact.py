# -*- coding: utf8 -*-
#!/usr/bin/env python
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

class Test(unittest.TestCase):

    def test_2_00(self):
        '2.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, handle_contact, handle_nsset
        epp_cli = ccReg.Client()
        epp_cli._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = __find_available_handle__(epp_cli, 'contact','nexcon')
        # handle_nsset = __find_available_handle__(epp_cli, 'nsset','nexns')
        # Natvrdo definovany handle:
        handle_contact = 'neexist01'
        handle_nsset = 'neexist01'
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
    
    def test_2_01(self):
        '2.1 Check na seznam dvou neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Kontakt existuje: %s'%name)

    def test_2_02(self):
        '2.2 Pokus o Info na neexistujici kontakt'
        epp_cli.info_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_2_03(self):
        '2.3 Zalozeni neexistujiciho noveho kontaktu'
        # contact_id, name, email, city, cc
        epp_cli.create_contact(handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertEqual(epp_cli.is_val(), 1000)

    def test_2_04(self):
        '2.4 Pokus o zalozeni existujiciho kontaktu'
        # contact_id, name, email, city, cc
        epp_cli.create_contact(handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_2_05(self):
        '2.5 Check na seznam existujiciho a neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002')), 1)

    def test_2_06(self):
        '2.6 Info na existujici kontakt'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000)

    def test_2_07(self):
        '2.7 Update vsech parametru krome stavu'
        chg = {
            'postal_info': {
                'name': u'čuřil šížala',
                'org':'jina organizace',
                'addr':{
                    'street':('Ulice 1','Ulice 2','Ulice 3',),
                    'city': u'Město',
                    'sp':'123489',
                    'pc':'12000',
                    'cc':'CZ',
                },
            },
            'voice':'+123.156789',
            'fax':'+123.1264987',
            'email':'jiny@mail.cz',
            'disclose':{
                'flag':'1',
                'name':'nove jmeno',
                'org':'nova organizace',
                'addr': u'adresa a město',
                'voice':'+123.1234967',
                'fax':'+123.456734',
                'email':'jiny.disclose@mial.cz',
            },
            'vat':'45679',
            'ssn':'123486',
            'notifyEmail':'notifak@jojo.cz',
        }
        epp_cli.update_contact(handle_contact, None, None, chg)
        self.assertEqual(epp_cli.is_val(), 1000)
        
    def test_2_08(self):
        '2.8 Pokus o update vsech stavu server*'
        for status in ('serverDeleteProhibited', 'serverUpdateProhibited'):
            epp_cli.update_contact(handle_contact, status)
            self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
    def test_2_09(self):
        '2.9 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        epp_cli.update_contact(handle_contact, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o smazání
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_contact(handle_contact, None, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_2_10(self):
        '2.10 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        epp_cli.update_contact(handle_contact, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o změnu
        epp_cli.update_contact(handle_contact, None, None, {'notifyEmail':'notifak@jinak.cz'})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se aktualizoval, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_contact(handle_contact, None, status)
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)

    def test_2_11(self):
        '2.11 Vytvoreni nnsetu napojeneho na kontakt'
        epp_cli.create_nsset(handle_nsset, 'heslo', {'name':'ns1.test.cz'}, handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000)
        
    def test_2_12(self):
        '2.12 Smazani kontaktu na ktery existuji nejake vazby'
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_2_13(self):
        '2.13 Smazani nssetu'
        epp_cli.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000)

    def test_2_14(self):
        '2.14 Smazani kontaktu'
        epp_cli.delete_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000)

    def test_2_15(self):
        '2.15 Check na smazany kontakt'
        epp_cli.check_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 1)

def __find_available_handle__(epp_cli, type_object, prefix):
    'Find first available object.'
    available_handle = ''
    handles = []
    for n in range(10):
        handles.append('%s%02d'%(prefix,n))
    getattr(epp_cli,'check_%s'%type_object)(handles)
    for name in handles:
        if epp_cli.is_val(('data',name)) == 1:
            available_handle = name
            break
    return available_handle


epp_cli, handle_contact, handle_nsset = None,None,None

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
