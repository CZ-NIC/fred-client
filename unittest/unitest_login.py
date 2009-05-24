#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
1.1 Zalogovani s neexistujicim username
1.2 Zalogovani se spravnym heslem
1.3 Zalogovani se spatnym heslem
1.4 Zalogovani se spravnym otiskem certifikatu
1.5 Zalogovani se spatnym otiskem certifikatu
1.6 Zmena hesla tam a zpatky s kontrolnim zalogovanim
"""
import sys
sys.path.insert(0, '..')
import unittest
import fred
import unitest_share

INVALID_LOGIN = 1
USERNAME = '' # 'REG-LRR'
PASSWORD = '' # '123456789'

class TestLogin(unittest.TestCase):

    def __login__(self, dct, invalid_login=0):
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
            except fred.FredError, msg:
                if not invalid_login:
                    # we need error message in case of valid login
                    # when we try invalid, we havent reseive errors otherwice
                    error = 'FredError: %s'%msg
        return code, error

    def setUp(self):
        '1.0 vytvoreni klienta'
        if epp_cli:
            if epp_cli._epp.is_online('') and epp_cli._epp.is_connected(): # only if we are online
                try:
                    epp_cli.logout()
                except fred.FredError, msg:
                    pass
#                    print '\nsetUp() epp_cli.logout()',msg
#                self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))
            else:
                epp_cli.close()

    def tearDown(self):
        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription())
        unitest_share.reset_client(epp_cli)

    def test_001(self):
        '1.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, log_fp, USERNAME, PASSWORD

        epp_cli = fred.Client()
        epp_cli._epp.load_config()
        USERNAME, PASSWORD = epp_cli._epp.get_actual_username_and_password()
        self.assert_(USERNAME, 'USERNAME missing')
        self.assert_(PASSWORD, 'PASSWORD missing')
        # logovací soubor
        if fred.translate.options['log']: # zapnuti/vypuni ukladani prikazu do logu
            log_fp = open(fred.translate.options['log'],'w')
            unitest_share.write_log_header(log_fp)

    def test_010(self):
        '1.1 Zalogovani s neexistujicim username'
        try:
            epp_cli.login('neplatne_usernam',PASSWORD) # maximum 16 chars to username
        except fred.FredError, msg:
            pass
        self.assertEqual(epp_cli.is_val(), 2501, unitest_share.get_reason(epp_cli))

        
    def test_020(self):
        '1.2 Zalogovani se spatnym heslem'
        try:
            epp_cli.login(USERNAME,'chybne_heslo')
        except fred.FredError, msg:
            pass
        self.assertEqual(epp_cli.is_val(), 2501, unitest_share.get_reason(epp_cli))
        
#    def test_030(self):
#        '1.3 Zalogovani se spatnym otiskem certifikatu'
#        global dct_login
#        cert_name = None
#        current_section = epp_cli._epp.config_get_section_connect()
#        valid_certificat = epp_cli._epp.get_config_value(current_section,'ssl_cert')
#        for section in epp_cli._epp._conf.sections():
#            if section[:7]=='connect' and section != current_section:
#                # vybere se jiný certifikát než platný
#                certificat = epp_cli._epp.get_config_value(section,'ssl_cert')
#                if certificat != valid_certificat:
#                    cert_name = certificat
#                    break
#        self.assert_(cert_name, 'Nebyl nalezen vhodny certifikat. Nastavte v configu alespon jednu sekci connect_SESSION_NAME s jinym certifikatem, nez je ten platny.')
#        if not cert_name: return
#        # přiřazení neplatného certifikátu
#        epp_cli._epp._conf.set(current_section, 'ssl_cert', cert_name)
#        login = epp_cli._epp.get_logins_and_passwords()[0]
#        # dct_login - create global login values:
#        dct_login['username'] = login[0]
#        dct_login['password'] = login[1]
#        code, error = self.__login__(dct_login)
#        # navrácení platného certifikátu
#        epp_cli._epp._conf.set(current_section, 'ssl_cert', valid_certificat)
#        self.assert_(len(error), error)
#        self.assertNotEqual(code, 1000, 'Zalogovani proslo s neplatnym certifikatem:\n%s (section: %s)\nplatny je:\n%s.'%(cert_name,current_section,valid_certificat))

    def test_040(self):
        '1.4 Zalogovani se spravnym heslem a spravnym otiskem certifikatu'

        login = epp_cli._epp.get_logins_and_passwords()[0]
	global dct_login
        dct_login['username'] = login[0]
        dct_login['password'] = login[1]

        code, error = self.__login__(dct_login)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_share.get_reason(epp_cli))

    def test_045(self):
        '1.4.1 Odlogovani'
        unitest_share.reset_client(epp_cli)
	epp_cli.login(USERNAME, PASSWORD);

        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')
        try:
            epp_cli.logout()
        except fred.FredError, msg:
            pass
            print '\n1.5.2 Odlogovani:',msg

        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))


    def test_050(self):
        '1.5.1 Zmena hesla tam a zpatky s kontrolnim zalogovanim: Zmena hesla'
        global dct_login
        for key in ('username','password'):
            self.assert_(dct_login.has_key(key))
        dct_login['old_password'] = dct_login['password']
        # změna hesla ........................................
        dct_login['new_password'] = 'nove-heslo'
        code, error = self.__login__(dct_login)
        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(1,3))
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_share.get_reason(epp_cli))

    
    def test_070(self):
        '1.5.3 Zalogovani s novym heslem'
        # zalogování pod novým heslem ........................
        dct_login['password'] = dct_login.pop('new_password')
        code, error = self.__login__(dct_login)
        unitest_share.write_log(epp_cli, log_fp, log_step, self.id(),self.shortDescription(),(2,3))
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_share.get_reason(epp_cli))

#    def test_080(self):
#        '1.5.4 Odlogovani'
#        unitest_share.reset_client(epp_cli)
#        try:
#            epp_cli.logout()
#        except fred.FredError, msg:
#            pass
#            print '\n1.5.4 Odlogovani:',msg
#        self.assertEqual(epp_cli.is_val(), 1500, unitest_share.get_reason(epp_cli))
#

    def test_090(self):
        '1.5.5 Navraceni puvodniho hesla'
        global dct_login
        # vrácení původního hesla ............................
        dct_login['new_password'] = dct_login['old_password']
        code, error = self.__login__(dct_login)
        self.assert_(len(error)==0, error)
        self.assertEqual(code, 1000, unitest_share.get_reason(epp_cli))

    def test_100(self):
	'1.6 Credit info'
	# global epp_cli, epp_cli_log, handle_contact, handle_keyset, log_fp
	epp_cli.login(USERNAME, PASSWORD);

        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')
	epp_cli.credit_info()
	self.assertEqual(epp_cli.is_val(), 1000, unitest_share.get_reason(epp_cli))


epp_cli, log_fp, log_step = (None,)*3
dct_login = {} # global login values - login, password

if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestLogin))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()

