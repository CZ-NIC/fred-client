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
import ccReg
import unitest_ccreg_share

class Test(unittest.TestCase):

    def __login__(self, dct):
        'Login and logout.'
        code = 0
        error = ''
        for key in ('username','password'):
            if not dct.has_key(key): error += 'Chybi parametr: %s. '%key
        if not error:
            try:
                if dct.has_key('new_password'):
                    epp_cli.login(dct['username'], dct['password'], dct['new_password'])
                else:
                    epp_cli.login(dct['username'], dct['password'])
                code = epp_cli.is_val()
            except ccReg.ccRegError, msg:
                error = 'ccRegError: %s'%msg
        return code, error

    def setUp(self):
        '1.0 vytvoreni klienta'
        if epp_cli:
            if epp_cli._epp.is_online('') and epp_cli._epp.is_connected(): # only if we are online
                epp_cli.logout()
                self.assertEqual(epp_cli.is_val(), 1500, unitest_ccreg_share.get_reason(epp_cli))
            else:
                epp_cli.close()

    def tearDown(self):
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription())
        unitest_ccreg_share.reset_client(epp_cli)

    def test_000(self):
        '1.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, log_fp
        epp_cli = ccReg.Client()
        if ccReg.translate.options['session']:
            # nastavení serveru
            epp_cli._epp.set_session_name(ccReg.translate.options['session'])
        epp_cli._epp.load_config()
        # logovací soubor
        if ccReg.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(ccReg.translate.options['log'],'w')
            unitest_ccreg_share.write_log_header(log_fp)

    def test_010(self):
        '1.1 Zalogovani s neexistujicim username'
        code, error = self.__login__({'username':'neexistuje', 'password':'123456789'})
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 2501, unitest_ccreg_share.get_reason(epp_cli))

        
    def test_020(self):
        '1.2 Zalogovani se spravnym heslem a spravnym otiskem certifikatu'
        dct = epp_cli._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_ccreg_share.get_reason(epp_cli))

    def test_030(self):
        '1.3 Zalogovani se spatnym heslem'
        epp_cli.login('REG-LRR','chybne')
        self.assertEqual(epp_cli.is_val(), 2501, unitest_ccreg_share.get_reason(epp_cli))

    def test_040(self):
        '1.4 Zalogovani se spatnym otiskem certifikatu'
        cert_name = None
        current_section = epp_cli._epp.config_get_section_connect()
        valid_certificat = epp_cli._epp.get_config_value(current_section,'ssl_cert')
        for section in epp_cli._epp._conf.sections():
            if section[:7]=='connect' and section != current_section:
                # vybere se jiný certifikát než platný
                certificat = epp_cli._epp.get_config_value(section,'ssl_cert')
                if certificat != valid_certificat:
                    cert_name = certificat
                    break
        self.assert_(cert_name, 'Nebyl nalezen vhodny certifikat. Nastavte v configu alespon jednu sekci connect_SESSION_NAME s jinym certifikatem, nez je ten platny.')
        if not cert_name: return
        # přiřazení neplatného certifikátu
        epp_cli._epp._conf.set(current_section, 'ssl_cert', cert_name)
        dct = epp_cli._epp.get_default_params_from_config('login')
        code, error = self.__login__(dct)
        # navrácení platného certifikátu
        epp_cli._epp._conf.set(current_section, 'ssl_cert', valid_certificat)
        self.assert_(len(error), error)
        self.assertNotEqual(code, 1000, 'Zalogovani proslo s neplatnym certifikatem:\n%s (section: %s)\nplatny je:\n%s.'%(cert_name,current_section,valid_certificat))

    def test_050(self):
        '1.5 Zmena hesla tam a zpatky s kontrolnim zalogovanim'
        dct = epp_cli._epp.get_default_params_from_config('login')
        for key in ('username','password'):
            self.assert_(dct.has_key(key))
        puvodni_heslo = dct['password']
        # změna hesla ........................................
        dct['new_password'] = 'nove-heslo'
        code, error = self.__login__(dct)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_ccreg_share.get_reason(epp_cli))
        unitest_ccreg_share.reset_client(epp_cli)
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_ccreg_share.get_reason(epp_cli))
        # zalogování pod novým heslem ........................
        dct['password'] = dct['new_password']
        dct.pop('new_password')
        code, error = self.__login__(dct)
        unitest_ccreg_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_ccreg_share.get_reason(epp_cli))
        unitest_ccreg_share.reset_client(epp_cli)
        epp_cli.logout()
        self.assertEqual(epp_cli.is_val(), 1500, unitest_ccreg_share.get_reason(epp_cli))
        # vrácení původního hesla ............................
        dct['new_password'] = puvodni_heslo
        code, error = self.__login__(dct)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_ccreg_share.get_reason(epp_cli))

epp_cli, log_fp, log_step = (None,)*3

if __name__ == '__main__':
    if ccReg.translate.option_errors:
        print ccReg.translate.option_errors
    elif ccReg.translate.options['help']:
        print unitest_ccreg_share.__doc__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()

