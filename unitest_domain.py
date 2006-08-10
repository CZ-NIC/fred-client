#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
4.1  Check na seznam dvou neexistujicich domen
4.2  Pokus o Info na neexistujici domenu
4.3  Zalozeni pomocneho kontaktu
4.4  Zalozeni pomocneho nssetu
4.5  Pokus o zalozeni domeny s neexistujicim nssetem
4.6  Pokus o zalozeni domeny s neexistujicim kontaktem
4.7  Pokusy o zalozeni domeny s neplatnym nazvem
4.8  Zalozeni nove domeny
4.9  Zalozeni nove domeny enum
4.10  Pokus o zalozeni jiz existujici domeny
4.11 Check na seznam existujici a neexistujici domeny
4.12 Info na existujici domenu a kontrola hodnot
4.13 Update vsech parametru domeny
4.14 Pokus o update stavu Server*
4.15 Update stavu clientDeleteProhibited a pokus o smazani
4.16 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu
4.17 Pokus o Renew domain s nespravnym datumem
4.18 Renew domain
4.19 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)
4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)
4.21 Druhy registrator: Trasfer domeny
4.22 Druhy registrator: Zmena hesla po prevodu domeny
4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri
4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri
4.25 Druhy registrator: Smazani obou domen
4.26 Check na smazanou domenu
4.27 Smazani pomocnych kontaktu a nssetu
"""
import sys, os, re, time
import unittest
import ccReg

#----------------------------------------------
# Nastavení serveru, na kterém se bude testovat
# (Pokud je None, tak je to default)
#----------------------------------------------
SESSION_NAME = None # 'curlew'

#-----------------------
CCREG_CONTACT1 = 'TDOMCONT01'
CCREG_CONTACT2 = 'TDOMCONT02'
CCREG_NSSET1 = 'TDOMNSSET01'
CCREG_NSSET2 = 'TDOMNSSET02'
CCREG_DOMAIN1 = 'hokus-pokus.cz'
CCREG_DOMAIN2 = '0.1.1.7.4.5.2.2.2.0.2.4.e164.arpa'
CCREG_DOMAIN_PASSW = 'heslicko'
CCREG_DOMAIN_PASSW_NEW = 'noveheslo'
INVALID_DOMAIN_NAME = 'myname.net'
#-----------------------
DOMAIN_1, DOMAIN_2, CHANGE_DOMAIN, DOMAIN_3  = range(4)
#-----------------------
CCREG_DATA = (
    { # DOMAIN_1
       'name':CCREG_DOMAIN1,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(CCREG_CONTACT1,),
    }, 
    { # DOMAIN_2
       'name':CCREG_DOMAIN2,
       'pw':CCREG_DOMAIN_PASSW,
       'nsset':CCREG_NSSET1,
       'registrant':CCREG_CONTACT1,
       'period': {'num':'3','unit':'y'},
       'contact':(CCREG_CONTACT1,),
    }, 
    { # modify
      'nsset': CCREG_NSSET2,
      'registrant': CCREG_CONTACT2,
      'auth_info': {'pw': CCREG_DOMAIN_PASSW_NEW,},
    },
    { # DOMAIN_3 - modified
       'name':CCREG_DOMAIN1,
       'pw':CCREG_DOMAIN_PASSW_NEW,
       'nsset':CCREG_NSSET2,
       'registrant':CCREG_CONTACT2,
       'period': {'num':'3','unit':'y'},
       'contact':(CCREG_CONTACT1,),
    }, 
    )

class Test(unittest.TestCase):

    def setUp(self):
        'Check if cilent is online.'
        if epp_cli: self.assert_(epp_cli.is_logon(),'client is offline')

    def tearDown(self):
        __write_log__()

    def test_000(self):
        '3.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, epp_cli_TRANSF, handle_contact, handle_nsset, log_fp
        # create client object
        epp_cli = ccReg.Client()
        epp_cli_TRANSF = ccReg.Client()
        if SESSION_NAME:
            # nastavení serveru
            epp_cli._epp.set_session_name(SESSION_NAME)
            epp_cli_TRANSF._epp.set_session_name(SESSION_NAME)
        epp_cli._epp.load_config()
        epp_cli_TRANSF._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        epp_cli_TRANSF.login('REG-LRR2', dct['password'])
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(epp_cli_TRANSF.is_logon(), 'Nepodarilo se zalogovat uzivatele "REG-LRR2" pro transfer.')
        # logovací soubor
        if 0: # zapnuti/vypuni ukladani prikazu do logu
            filepath = os.path.join(os.path.expanduser('~'),'unittest_domain_log.txt')
            try:
                log_fp = open(filepath,'w')
            except IOError, (no, msg):
                pass # ignore if log file doenst created

    def test_010(self):
        '4.1  Check na seznam dvou neexistujicich domen'
        handles = (CCREG_DOMAIN1,'neexist002')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Domena existuje: %s'%name)

    def test_020(self):
        '4.2  Pokus o Info na neexistujici domenu'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_030(self):
        '4.3.1 Zalozeni 1. pomocneho kontaktu'
        epp_cli.create_contact(CCREG_CONTACT1,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_031(self):
        '4.3.2 Zalozeni 2. pomocneho kontaktu'
        epp_cli.create_contact(CCREG_CONTACT2, u'řehoř čuřil','rehor@curil.cz','Praha','CZ')
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_040(self):
        '4.4.1 Zalozeni 1. pomocneho nssetu'
        epp_cli.create_nsset(CCREG_NSSET1, 'heslo', {'name': u'ns.pokus1.cz', 'addr': ('127.0.0.1', '127.0.1.1')})
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_041(self):
        '4.4.2 Zalozeni 2. pomocneho nssetu'
        epp_cli.create_nsset(CCREG_NSSET2, 'heslo', {'name': u'ns.pokus2.cz', 'addr': ('127.0.0.1', '127.0.1.1')})
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_050(self):
        '4.5  Pokus o zalozeni domeny s neexistujicim nssetem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['pw'], 'nsset-not-exists', d['registrant'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_060(self):
        '4.6.1  Pokus o zalozeni domeny s neexistujicim registratorem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['pw'], d['nsset'], 'reg-not-exists', d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_062(self):
        '4.6.2  Pokus o zalozeni domeny s neexistujicim kontaktem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['pw'], d['nsset'], d['registrant'], d['period'], 'CXXX0X')
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_070(self):
        '4.7  Pokusy o zalozeni domeny s neplatnym nazvem'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(INVALID_DOMAIN_NAME, d['pw'], d['nsset'], d['registrant'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena %s se vytvorila prestoze nemela.'%INVALID_DOMAIN_NAME)

    def test_071(self):
        '4.7.1  Smazani domeny s neplatnym jmenem (pokud byla vytvorena)'
        epp_cli.check_domain(INVALID_DOMAIN_NAME)
        if epp_cli.is_val(('data',INVALID_DOMAIN_NAME)) == 0:
            epp_cli.delete_domain(INVALID_DOMAIN_NAME)
        
    def test_080(self):
        '4.8  Zalozeni nove domeny'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['pw'], d['nsset'], d['registrant'], d['period'], d['contact'])
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_090(self):
        '4.9  Zalozeni nove domeny enum'
        d = CCREG_DATA[DOMAIN_2]
        epp_cli.create_domain(d['name'], d['pw'], d['nsset'], d['registrant'], d['period'], d['contact'])
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_100(self):
        '4.10  Pokus o zalozeni jiz existujici domeny'
        d = CCREG_DATA[DOMAIN_1]
        epp_cli.create_domain(d['name'], d['pw'], d['nsset'], d['registrant'], d['period'], d['contact'])
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se vytvorila prestoze jiz existuje')

    def test_110(self):
        '4.11 Check na seznam existujici a neexistujici domeny'
        handles = (CCREG_DOMAIN1,'neexist002')
        epp_cli.check_domain(handles)
        self.assertEqual(epp_cli.is_val(('data',CCREG_DOMAIN1)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002')), 1)

    def test_120(self):
        '4.12 Info na existujici domenu a kontrola hodnot'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        errors = __check_equality__(CCREG_DATA[DOMAIN_1], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))

    def test_130(self):
        '4.13 Update vsech parametru domeny'
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, CCREG_DATA[CHANGE_DOMAIN])
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_131(self):
        '4.13.2 Kontrola zmenenych udaju'
        epp_cli.info_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        errors = __check_equality__(CCREG_DATA[DOMAIN_3], epp_cli.is_val('data'))
        self.assert_(len(errors)==0, '\n'.join(errors))
        
    def test_140(self):
        '4.14.1 Pokus o update stavu serverDeleteProhibited'
        status = 'serverDeleteProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)

    def test_141(self):
        '4.14.2 Pokus o update stavu serverUpdateProhibited'
        status = 'serverUpdateProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
    def test_150(self):
        '4.15 Update stavu clientDeleteProhibited a pokus o smazani'
        status = 'clientDeleteProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o smazání
        epp_cli.delete_domain(CCREG_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Kontakt se smazal, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_domain(CCREG_DOMAIN1, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_160(self):
        '4.16 Update stavu clientUpdateProhibited a pokus o zmenu objektu, smazani stavu'
        status = 'clientUpdateProhibited'
        epp_cli.update_domain(CCREG_DOMAIN1, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se nastavit status: %s'%status)
        # pokus o změnu
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':'zmena hesla'}})
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Nsset se aktualizoval, prestoze mel nastaven %s'%status)
        # zrušení stavu
        epp_cli.update_domain(CCREG_DOMAIN1, None, {'status':status})
        self.assertEqual(epp_cli.is_val(), 1000, 'Nepodarilo se odstranit status: %s'%status)
        
    def test_170(self):
        '4.17 Pokus o Renew domain s nespravnym datumem'
        
    def test_180(self):
        '4.18 Renew domain'
        
    def test_190(self):
        '4.19 Trasfer na vlastni domenu (Objekt je nezpůsobilý pro transfer)'
        epp_cli.transfer_domain(CCREG_DOMAIN1, CCREG_DOMAIN_PASSW_NEW)
        self.assertNotEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        
    def test_200(self):
        '4.20 Druhy registrator: Trasfer s neplatnym heslem (Chyba oprávnění)'
        epp_cli_TRANSF.transfer_domain(CCREG_DOMAIN1, 'heslo neznam')
        self.assertNotEqual(epp_cli_TRANSF.is_val(), 1000, __get_reason__(epp_cli_TRANSF))
        
    def test_210(self):
        '4.21 Druhy registrator: Trasfer domeny'
        epp_cli_TRANSF.transfer_domain(CCREG_DOMAIN1, CCREG_DOMAIN_PASSW_NEW)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, __get_reason__(epp_cli_TRANSF))
        
    def test_220(self):
        '4.22 Druhy registrator: Zmena hesla po prevodu domeny'
        epp_cli_TRANSF.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':CCREG_DOMAIN_PASSW}})
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, __get_reason__(epp_cli_TRANSF))
        
    def test_230(self):
        '4.23 Zmena hesla domeny, ktera registratorovi jiz nepatri'
        epp_cli.update_domain(CCREG_DOMAIN1, None, None, {'auth_info':{'pw':'moje-heslo'}})
        self.assertNotEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        
    def test_240(self):
        '4.24 Pokus o smazani domeny, ktera registratorovi jiz nepatri'
        epp_cli.delete_domain(CCREG_DOMAIN1)
        self.assertNotEqual(epp_cli.is_val(), 1000, 'Domena se smazala prestoze nemela')
        
    def test_250(self):
        '4.25.1 Druhy registrator: Smazani domeny'
        epp_cli_TRANSF.delete_domain(CCREG_DOMAIN1)
        self.assertEqual(epp_cli_TRANSF.is_val(), 1000, __get_reason__(epp_cli_TRANSF))

    def test_251(self):
        '4.25.2 Druhy registrator: Smazani domeny enum'
        epp_cli.delete_domain(CCREG_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        
    def test_260(self):
        '4.26 Check na smazanou domenu'
        epp_cli.check_domain(CCREG_DOMAIN2)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))
        self.assertEqual(epp_cli.is_val(('data',CCREG_DOMAIN2)), 1, 'Domena existuje: %s'%CCREG_DOMAIN2)
        
    def test_270(self):
        '4.27.0 Smazani 2. pomocneho nssetu'
        epp_cli.delete_nsset(CCREG_NSSET2)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_271(self):
        '4.27.1 Smazani 1. pomocneho nssetu'
        epp_cli.delete_nsset(CCREG_NSSET1)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_272(self):
        '4.27.2 Smazani 2. pomocneho kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT2)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))

    def test_273(self):
        '4.27.3 Smazani 1. pomocneho kontaktu'
        epp_cli.delete_contact(CCREG_CONTACT1)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__(epp_cli))


def __get_reason__(client):
    'Returs reason a errors from client object'
    reason = get_local_text(client.is_val('reason'))
    er = []
    for error in client.is_val('errors'):
        er.append(get_local_text(error))
    return  '%s ERRORS:[%s]\nCOMMAND: %s'%(reason, '\n'.join(er), get_local_text(client._epp.get_command_line()))

def __write_log__():
    if log_fp and epp_cli._epp._raw_cmd:
        log_fp.write('COMMAND: %s\n%s\n'%(epp_cli._epp._command_sent,'.'*60))
        log_fp.write(epp_cli._epp._raw_cmd)
        log_fp.write('%s\nANSWER:\n'%('-'*60))
        answer = epp_cli.get_answer()
        if answer:
            log_fp.write('%s\n'%re.sub('\x1b(\\[|\\()\d*(m|B)','',answer))
        edoc = ccReg.eppdoc.Message()
        edoc.parse_xml(epp_cli._epp._raw_answer)
        log_fp.write(edoc.get_xml())
        log_fp.write('\n%s\n'%('='*60))
        epp_cli._epp._raw_cmd = '' # reset

def make_str(value):
    if type(value) in (tuple,list):
        arr=[]
        for item in value:
            arr.append(item.encode(encoding))
        value = '(%s)'%', '.join(arr)
    elif type(value) == unicode:
        value = value.encode(encoding)
    return value

def __are_equal__(val1,val2):
    'Compare values or lists. True - equal, False - not equal.'
    if type(val1) in (list, tuple):
        if type(val2) not in (list, tuple): return False
        lst2 = list(val2)
        if len(val1) == len(lst2):
            for v in val1:
                if v in lst2: lst2.pop(lst2.index(v))
            retv = len(lst2) == 0
        else:
            retv = False
    else:
        retv = val1 == val2
    return retv

def __err_not_equal__(errors, data, key, refval):
    if data[key] != refval:
        errors.append('Neplatny klic "%s" je "%s" (ma byt: "%s")'%(key,data[key],refval))

def __check_date__(date, nu):
    'Check expected date.'
    ts = list(time.gmtime())
    num = int(nu['num'])
    if nu['unit'] == 'y':
        ts[0] += num
    else:
        ts[0] += num/12
        ts[1] += num%12
        if ts[1] > 12:
            ts[0] += 1
            ts[1] = ts[1]%12
    return time.strftime('%Y-%m-%d',ts) == date[:10]

def __check_equality__(cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
##============================================================
##COLS:
##{   'name': 'hokus-pokus.cz', 
##    'period': {'num': u'3', 'unit': u'y'}, 
##    'contact': ('TDOMCONT01',), 
##    'nsset': 'TDOMNSSET01', 
##    'registrant': 'TDOMCONT01', 
##    'pw': 'heslicko'}
##------------------------------------------------------------
##DATA:
##{   'domain:contact': u'TDOMCONT01', 
##    'domain:crID': u'REG-LRR', 
##    'domain:clID': u'REG-LRR', 
##    'domain:name': u'hokus-pokus.cz', 
##    'domain:status.s': u'ok', 
##    'domain:exDate': u'2009-08-10T00:00:00.0Z', 
##    'domain:nsset': u'TDOMNSSET01', 
##    'domain:pw': u'heslicko', 
##    'domain:crDate': u'2006-08-10T09:58:16.0Z', 
##    'domain:roid': u'D0000000219-CZ', 
##    'domain:registrant': u'TDOMCONT01', 
##    'domain:renew': u'2009-08-10', 
##    'domain:contact.type': u'admin'}
##____________________________________________________________
    ref_value = epp_cli._epp.get_config_value('connect','username')
    __err_not_equal__(errors, data, 'domain:clID', ref_value)
    __err_not_equal__(errors, data, 'domain:name', cols['name'])
    __err_not_equal__(errors, data, 'domain:nsset', cols['nsset'])
    __err_not_equal__(errors, data, 'domain:pw', cols['pw'])
    if not __are_equal__(data['domain:registrant'], cols['registrant']):
        errors.append('Data domain:registrant nesouhlasi. JSOU:%s MELY BYT:%s'%(make_str(data['domain:registrant']), make_str(cols['registrant'])))
    if not __check_date__(data['domain:exDate'], cols['period']):
        errors.append('Data domain:exDate nesouhlasi: %s'%data['domain:exDate'])
    if data['domain:crDate'][:10] != time.strftime('%Y-%m-%d',time.gmtime()):
        errors.append('Data domain:crDate nesouhlasi: %s'%data['domain:crDate'])
    return errors

epp_cli, epp_cli_TRANSF, log_fp = None,None,None
get_local_text = ccReg.session_base.get_ltext

if __name__ == '__main__':
    if len(sys.argv) > 1: SESSION_NAME = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
    if log_fp: log_fp.close()


