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
import unitest_ccReg

class Test(unitest_ccReg.BaseTest):
    
    def setUp(self):
        try:
            type(self._lock)
        except AttributeError:
            unitest_ccReg.BaseTest.setUp(self)
            self.handle_contact = self.__find_available_handle__('contact','nexcon')
            self.handle_nsset = self.__find_available_handle__('nsset','nexns')
            self.assert_(len(self.handle_contact), 'Nepodarilo se nalezt volny contact')
            self.assert_(len(self.handle_nsset), 'Nepodarilo se nalezt volny nsset')
    ##        if len(self.handle_contact) and len(self.handle_nsset):
            if 0:
                code, error = self.__login__(self.epc._epp.get_default_params_from_config('login'))
                self.assert_(len(error), error)
                self.assertNotEqual(code, 1000)
        self._lock = 1

    def test_2_1(self):
        '2.1 Check na seznam dvou neexistujicich kontaktu'
        handles = (self.handle_contact,'neexist02')
        self.epc.check_contact(handles)
        for name in handles:
            self.assertEqual(self.epc.is_val(('data',name)), 1, 'Kontakt existuje: %s'%name)

    def test_2_2(self):
        '2.2 Pokus o Info na neexistujici kontakt'
        self.epc.info_contact(self.handle_contact)
        self.assertNotEqual(self.epc.is_val(), 1000)

    def test_2_3(self):
        '2.3 Zalozeni neexistujiciho noveho kontaktu'
        # contact_id, name, email, city, cc
        self.epc.create_contact(self.handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertEqual(self.epc.is_val(), 1000)

    def test_2_4(self):
        '2.4 Pokus o zalozeni existujiciho kontaktu'
        # contact_id, name, email, city, cc
        self.epc.create_contact(self.handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertNotEqual(self.epc.is_val(), 1000)

    def test_2_5(self):
        '2.5 Check na seznam existujiciho a neexistujicich kontaktu'
        handles = (self.handle_contact,'neexist02')
        self.epc.check_contact(handles)
        self.assertEqual(self.epc.is_val(('data',self.handle_contact)), 1)
        self.assertEqual(self.epc.is_val(('data','neexist02')), 0)

    def test_2_6(self):
        '2.6 Info na existujici kontakt'
        self.epc.info_contact(self.handle_contact)
        self.assertEqual(self.epc.is_val(), 1000)

    def test_2_7(self):
        '2.7 Update vsech parametru krome stavu'
##    contact-id (required)
##    add (optional)              list with max 5 items.
##    rem (optional)              list with max 5 items.
##    chg (optional)
##        postalInfo (optional)
##            name (optional)
##            org (optional)
##            addr (optional)
##                street (optional)  list with max 3 items.
##                city (required)
##                sp (optional)
##                pc (optional)
##                cc (required)
##        voice (optional)
##        fax (optional)
##        email (optional)
##        disclose (optional)
##            flag (required) accept only values: (0,1)
##            name (optional)
##            org (optional)
##            addr (optional)
##            voice (optional)
##            fax (optional)
##            email (optional)
##        vat (optional)
##        ssn (optional)
##        notifyEmail (optional)
##        (self, contact_id, add=None, rem=None, chg=None)
        add = ('ok', 'clientTransferProhibited')
        rem = None
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
        self.epc.update_contact(self.handle_contact, add, rem, chg)
        self.assertEqual(self.epc.is_val(), 1000)
        
    def test_2_8(self):
        '2.8 Pokus o update stavu Server*'
        self.epc.update_contact(self.handle_contact, 'serverDeleteProhibited')
        self.assertNotEqual(self.epc.is_val(), 1000)
        
    def test_2_9(self):
        '2.9 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        self.epc.update_contact(self.handle_contact, status)
        self.assertEqual(self.epc.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        if self.epc.is_val() == 1000: return
        # pokus o smazání
        self.epc.delete_contact(self.handle_contact)
        self.assertNotEqual(self.epc.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        # zrušení stavu
        self.epc.update_contact(self.handle_contact, None, status)
        self.assertEqual(self.epc.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_2_10(self):
        '2.10 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        self.epc.update_contact(self.handle_contact, status)
        self.assertEqual(self.epc.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        if self.epc.is_val() == 1000: return
        # pokus o změnu
        self.epc.update_contact(self.handle_contact, None, None, {'notifyEmail':'notifak@jinak.cz'})
        self.assertNotEqual(self.epc.is_val(), 1000, 'Kontakt se aktualizoval, prestoze mel nastaven %s'%status)
        # zrušení stavu
        self.epc.update_contact(self.handle_contact, None, status)
        self.assertEqual(self.epc.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_2_11(self):
        '2.11 Vytvoreni nnsetu napojeneho na kontakt'
##(self, nsset_id, pw, dns, tech=None):
##    dns (required)               list with max 9 items.
##        name (required)
##        addr (optional)         unbounded list
##        dns = {'name':'ns1.test.cz'}
        self.epc.create_nsset(self.handle_nsset, 'heslo', {'name':'ns1.test.cz'})
        self.assertEqual(self.epc.is_val(), 1000)
        
    def test_2_12(self):
        '2.12 Smazani kontaktu na ktery existuji nejake vazby'
        self.epc.delete_contact(self.handle_contact)
        self.assertNotEqual(self.epc.is_val(), 1000)

    def test_2_13(self):
        '2.13 Smazani nssetu'
        self.epc.delete_nsset(self.handle_nsset)
        self.assertEqual(self.epc.is_val(), 1000)

    def test_2_14(self):
        '2.14 Smazani kontaktu'
        self.epc.delete_contact(self.handle_contact)
        self.assertEqual(self.epc.is_val(), 1000)

    def test_2_15(self):
        '2.15 Check na smazany kontakt'
        self.epc.check_contact(self.handle_contact)
        self.assertEqual(self.epc.is_val(('data',self.handle_contact)), 1)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
