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
import sys
import unittest
import ccReg

#----------------------------------------------
# Nastavení serveru, na kterém se bude testovat
# (Pokud je None, tak je to default)
#----------------------------------------------
SESSION_NAME = None # 'curlew'

class Test(unittest.TestCase):

    def setUp(self):
        '1.0 vytvoreni klienta'
        self.epc = ccReg.Client()
        if SESSION_NAME: self.epc._epp.set_session_name(SESSION_NAME) # nastavení serveru
        self.epc._epp.load_config()

    def __login__(self, dct):
        'Login and logout.'
        code = 0
        error = ''
        for key in ('username','password'):
            if not dct.has_key(key): error += 'Chybi parametr: %s. '%key
        if not error:
            try:
                if dct.has_key('new_password'):
                    self.epc.login(dct['username'], dct['password'], dct['new_password'])
                else:
                    self.epc.login(dct['username'], dct['password'])
                code = self.epc.is_val()
            except ccReg.ccRegError, msg:
                error = 'ccRegError: %s'%msg
        return code, error

    def test_1_1(self):
        '1.1 Zalogovani s neexistujicim username'
        code, error = self.__login__({'username':'neexistuje', 'password':'123456789'})
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 2501)

        
    def test_1_2_a_4(self):
        '1.2 Zalogovani se spravnym heslem + 1.4 Zalogovani se spravnym otiskem certifikatu'
        dct = self.epc._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000)

    def test_1_3(self):
        '1.3 Zalogovani se spatnym heslem'
        self.epc.login('REG-LRR','chybne')
        self.assertEqual(self.epc.is_val(), 2501)

    def test_1_5(self):
        '1.5 Zalogovani se spatnym otiskem certifikatu'
        cert_name = None
        current_section = {False:'connect_%s'%SESSION_NAME, True:'connect'}[SESSION_NAME is None]
        valid_certificat = self.epc._epp.get_config_value(current_section,'ssl_cert')
        for section in self.epc._epp._conf.sections():
            if section[:7]=='connect' and section != current_section:
                # vybere se jiný certifikát než platný
                certificat = self.epc._epp.get_config_value(section,'ssl_cert')
                if certificat != valid_certificat:
                    cert_name = certificat
                    break
        self.assert_(cert_name, 'Nebyl nalezen vhodny certifikat. Nastavte v configu alespon jednu sekci connect_SESSION_NAME s jinym certifikatem, nez je ten platny.')
        if not cert_name: return
        # přiřazení neplatného certifikátu
        self.epc._epp._conf.set(current_section, 'ssl_cert', cert_name)
        dct = self.epc._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        self.assert_(len(error), error)
        self.assertNotEqual(code, 1000)

    def test_1_6(self):
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
        self.epc.logout()
        self.assertEqual(self.epc.is_val(), 1500,'Logout se nepodaril.')
        # zalogování pod novým heslem ........................
        dct['password'] = dct['new_password']
        dct.pop('new_password')
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, 'Nepodarilo se zadat nove heslo. Code: %d.\nDuvod: %s'%(code,self.epc.is_val('reason')))
        self.epc.logout()
        self.assertEqual(self.epc.is_val(), 1500,'Logout se nepodaril.')
        # vrácení původního hesla ............................
        dct['new_password'] = puvodni_heslo
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, 'Nepodarilo se zadat nove heslo. Code: %d.\nDuvod: %s'%(code,self.epc.is_val('reason')))


if __name__ == '__main__':
    if len(sys.argv) > 1: SESSION_NAME = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
