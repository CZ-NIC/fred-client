# -*- coding: utf8 -*-
#!/usr/bin/env python
"""
1.1 Zalogovani s neexistujicim username
1.2 Zalogovani se spravnym heslem
1.3 Zalogovani se spatnym heslem
1.4 Zalogovani se spravnym otiskem certifikatu
1.5 Zalogovani se spatnym otiskem certifikatu
1.6 Zmena hesla tam a zpatky s kontrolnim zalogovanim
"""
import unittest
import unitest_ccReg

class Test(unitest_ccReg.BaseTest):

    def test_login_neexistujici_username(self):
        '1.1 Zalogovani s neexistujicim username'
        code, error = self.__login__({'username':'neexistuje', 'password':'123456789'})
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 2501)

        
    def test_login_platny_login(self):
        '1.2 Zalogovani se spravnym heslem + 1.4 Zalogovani se spravnym otiskem certifikatu'
        dct = self.epc._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000)

    def test_login_chybne_heslo(self):
        '1.3 Zalogovani se spatnym heslem'
        self.epc.login('REG-LRR','chybne')
        self.assertEqual(self.epc.is_val(), 2501)

    def test_login_nespravny_certifikat(self):
        '1.5 Zalogovani se spatnym otiskem certifikatu'
        cert_name = None
        for section in self.epc._epp._conf.sections():
            if section[:7] == 'conect_':
                cert_name = self.epc._epp.get_config_value(section,'ssl_cert')
                break
        self.assert_(cert_name, 'Nebyl nalezen jiny certifikat')
        if not cert_name: return
        # přiřazení neplatného certifikátu
        self.epc._epp._conf.set('conect','ssl_cert', cert_name)
        dct = self.epc._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        self.assert_(len(error), error)
        self.assertNotEqual(code, 1000)

    def test_login_platny_login(self):
        '1.6 Zmena hesla tam a zpatky s kontrolnim zalogovanim'
        dct = self.epc._epp.get_default_params_from_config('login')
        for key in ('username','password'):
            self.assert_(dct.has_key(key))
        puvodni_heslo = dct['password']
        # změna hesla ........................................
        dct['new_password'] = 'nove-heslo'
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, 'Nepodarilo se zadat nove heslo. Code: %d.\nDuvod: %s'%(code,self.epc.is_val('reason')))
        # zalogování pod novým heslem ........................
        dct['password'] = dct['new_password']
        dct.pop('new_password')
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, 'Nepodarilo se zadat nove heslo. Code: %d.\nDuvod: %s'%(code,self.epc.is_val('reason')))
        # vrácení původního hesla ............................
        dct['new_password'] = puvodni_heslo
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, 'Nepodarilo se zadat nove heslo. Code: %d.\nDuvod: %s'%(code,self.epc.is_val('reason')))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
