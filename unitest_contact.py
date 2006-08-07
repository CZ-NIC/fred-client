#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import sys
import unittest
import ccReg

#----------------------------------------------
# Nastavení serveru, na kterém se bude testovat
# (Pokud je None, tak je to default)
#----------------------------------------------
HOST = None # 'curlew'

# CCREG_CONTACT[1] - create
# CCREG_CONTACT[2] - modify
# symbols: @ - attribute
CONTACT_HANDLE = 'test001'
CCREG_CONTACT = ( 
    {   # template
    'id': '', # (povinný) vaše kontaktní ID
    'name': '', # (povinný) vaše jméno
    'email': '', #(povinný) váš email
    'city': '', #(povinný) město
    'cc': '', #(povinný) kód země
    'org': '', #(nepovinný) název organizace
    'street': '', #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '', #(nepovinný) č.p.
    'pc': '', #(nepovinný) PSČ
    'voice': '', #(nepovinný) telefon
    'fax': '', #(nepovinný) fax
    'disclose': ('name','org','addr','voice','fax','email'),
    'vat': '', #(nepovinný) DPH
    'ssn': '', #(nepovinný) SSN
    'notify_email': '', #(nepovinný) oznámení na email
    },
    {   # create contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Řehoř Čížek', # (povinný) vaše jméno
    'email': 'rehor.cizek@mail.cz', #(povinný) váš email
    'city': u'Český Krumlov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'org': u'Čížková a spol', #(nepovinný) název organizace
    'street': (u'U práce',u'Za monitorem',u'Nad klávesnicí',), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '123', #(nepovinný) č.p.
    'pc': '12300', #(nepovinný) PSČ
    'voice': '+123.456789', #(nepovinný) telefon
    'fax': '+321.564987', #(nepovinný) fax
    'disclose_flag': '0',
    'disclose': ('name','org','addr','voice','fax','email'),
    'vat': '963', #(nepovinný) DPH
    'ssn': '852', #(nepovinný) SSN
    'notify_email': 'info@rehorovi.cz', #(nepovinný) oznámení na email
    },
    {   # modify contact
    'id': CONTACT_HANDLE, # (povinný) vaše kontaktní ID
    'name': u'Břéťa Žlučník', # (povinný) vaše jméno
    'email': 'breta.zlucnik@bricho.cz', #(povinný) váš email
    'city': u'Střevníkov', #(povinný) město
    'cc': 'CZ', #(povinný) kód země
    'org': u'Bolení s.r.o.', #(nepovinný) název organizace
    'street': (u'Na toaletách',u'U mísy'), #(nepovinný)  seznam o maximálně 3 položkách. ulice
    'sp': '321', #(nepovinný) č.p.
    'pc': '23101', #(nepovinný) PSČ
    'voice': '+321.987654', #(nepovinný) telefon
    'fax': '+321.987564', #(nepovinný) fax
    'disclose_flag': '0',
    'disclose': ('name','org','addr','voice','fax','email'),
    'vat': '753', #(nepovinný) DPH
    'ssn': '357', #(nepovinný) SSN
    'notify_email': 'info@zlucnikovi.cz', #(nepovinný) oznámení na email
    },
)

class Test(unittest.TestCase):

    def test_2_000(self):
        '2.0 Inicializace spojeni a definovani testovacich handlu'
        global epp_cli, handle_contact, handle_nsset
        # Natvrdo definovany handle:
        handle_contact = CCREG_CONTACT[1]['id'] # 'neexist01'
        handle_nsset = 'neexist01'
        # create client object
        epp_cli = ccReg.Client()
        if HOST: epp_cli._epp.set_host(HOST) # nastavení serveru
        epp_cli._epp.load_config()
        # login
        dct = epp_cli._epp.get_default_params_from_config('login')
        epp_cli.login(dct['username'], dct['password'])
        # Tady se da nalezt prazdny handle (misto pevne definovaneho):
        # handle_contact = __find_available_handle__(epp_cli, 'contact','nexcon')
        # handle_nsset = __find_available_handle__(epp_cli, 'nsset','nexns')
        # kontrola:
        self.assert_(epp_cli.is_logon(), 'Nepodarilo se zalogovat.')
        self.assert_(len(handle_contact), 'Nepodarilo se nalezt volny handle contact.')
        self.assert_(len(handle_nsset), 'Nepodarilo se nalezt volny handle nsset.')
    
    def test_2_010(self):
        '2.1 Check na seznam dvou neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        for name in handles:
            self.assertEqual(epp_cli.is_val(('data',name)), 1, 'Kontakt existuje: %s'%name)

    def test_2_020(self):
        '2.2 Pokus o Info na neexistujici kontakt'
        epp_cli.info_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_2_030(self):
        '2.3 Zalozeni neexistujiciho noveho kontaktu'
        d = CCREG_CONTACT[1]
        epp_cli.create_contact(handle_contact, 
            d['name'], d['email'], d['city'], d['cc'], d['org'], 
            d['street'], d['sp'], d['pc'], d['voice'], d['fax'], d['disclose'],
            d['vat'], d['ssn'], d['notify_email'])
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())

##    def test_2_031(self):
##        '2.3.1 Overevni vsech hodnot vznikleho kontaktu'
##        epp_cli.info_contact(handle_contact)
##        errors, disclose_names = __info_contact__('contact', CCREG_CONTACT[1], epp_cli.is_val('data'))
##        err = __check_disclosed_over__(disclose_names, epp_cli.is_val(('data','contact:disclose')))
##        if len(err): errors.extend(err)
##        self.assert_(len(errors), '\n'.join(errors))

    def test_2_040(self):
        '2.4 Pokus o zalozeni existujiciho kontaktu'
        # contact_id, name, email, city, cc
        epp_cli.create_contact(handle_contact,'Pepa Zdepa','pepa@zdepa.cz','Praha','CZ')
        self.assertNotEqual(epp_cli.is_val(), 1000)

    def test_2_050(self):
        '2.5 Check na seznam existujiciho a neexistujicich kontaktu'
        handles = (handle_contact,'neexist002')
        epp_cli.check_contact(handles)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 0)
        self.assertEqual(epp_cli.is_val(('data','neexist002')), 1)

    def test_2_060(self):
        '2.6 Info na existujici kontakt a overeni vsech hodnot'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())
        errors, disclose_names = __info_contact__('contact', CCREG_CONTACT[1], epp_cli.is_val('data'))
        err = __check_disclosed_over__(disclose_names, epp_cli.is_val(('data','contact:disclose')))
        if len(err): errors.extend(err)
        self.assert_(len(errors), '\n'.join(errors))

    def test_2_070(self):
        '2.7 Update vsech parametru krome stavu'
        d = CCREG_CONTACT[2]
        dd = d['disclose']
        chg = {
            'postal_info': {
                'name': d['name'],
                'org': d['org'],
                'addr':{
                    'street': d['street'],
                    'city':  d['city'],
                    'sp': d['sp'],
                    'pc': d['pc'],
                    'cc': d['cc'],
                },
            },
            'voice': d['voice'],
            'fax': d['fax'],
            'email': d['email'],
            'disclose_flag': '1',
            'disclose': ('name','org','addr','voice','fax','email'),
            'vat': d['vat'],
            'ssn': d['ssn'],
            'notify_email': d['notify_email'],
        }
        epp_cli.update_contact(handle_contact, None, None, chg)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())

    def test_2_071(self):
        '2.7.1 Overevni vsech hodnot zmeneneho kontaktu'
        epp_cli.info_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())
        errors, disclose_names = __info_contact__('contact', CCREG_CONTACT[2], epp_cli.is_val('data'))
        err = __check_disclosed_over__(disclose_names, epp_cli.is_val(('data','contact:disclose')))
        if len(err): errors.extend(err)
        self.assert_(len(errors), '\n'.join(errors))
        
    def test_2_080(self):
        '2.8 Pokus o update vsech stavu server*'
        for status in ('serverDeleteProhibited', 'serverUpdateProhibited'):
            epp_cli.update_contact(handle_contact, status)
            self.assertNotEqual(epp_cli.is_val(), 1000, 'Status "%s" prosel prestoze nemel.'%status)
        
    def test_2_090(self):
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
        
    def test_2_100(self):
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

    def test_2_110(self):
        '2.11 Vytvoreni nnsetu napojeneho na kontakt'
        epp_cli.create_nsset(handle_nsset, 'heslo', {'name':'ns1.test.cz'}, handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())
        
    def test_2_120(self):
        '2.12 Smazani kontaktu na ktery existuji nejake vazby'
        epp_cli.delete_contact(handle_contact)
        self.assertNotEqual(epp_cli.is_val(), 1000, __get_reason__())

    def test_2_130(self):
        '2.13 Smazani nssetu'
        epp_cli.delete_nsset(handle_nsset)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())

    def test_2_140(self):
        '2.14 Smazani kontaktu'
        epp_cli.delete_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(), 1000, __get_reason__())

    def test_2_150(self):
        '2.15 Check na smazany kontakt'
        epp_cli.check_contact(handle_contact)
        self.assertEqual(epp_cli.is_val(('data',handle_contact)), 1)

    def test_2_160(self):
        '2.16 Poll require'
        # 1000 OK (ack)
        # 1300 No messages
        # 1301 Any message
        epp_cli.poll('req')
        if epp_cli.is_val() not in (1000,1300,1301):
            self.assertEqual(0, 1, __get_reason__())

def __get_reason__():
    'Returs reason a errors from client object'
    reason = get_local_text(epp_cli.is_val('reason'))
    er = []
    for error in epp_cli.is_val('errors'):
        er.append(get_local_text(error))
    return  '%s ERRORS:[%s]\nCOMMAND: %s'%(reason, '\n'.join(er), get_local_text(epp_cli._epp.get_command_line()))

def __find_available_handle__(epp_cli, type_object, prefix):
    'Find first available object.'
    available_handle = ''
    handles = []
    for n in range(30):
        handles.append('%s%02d'%(prefix,n))
    getattr(epp_cli,'check_%s'%type_object)(handles)
    for name in handles:
        if epp_cli.is_val(('data',name)) == 1:
            available_handle = name
            break
    return available_handle

def __info_contact__(prefix, cols, scope, key=None, pkeys=[]):
    'Check info-[object] against selected set.'
    disclose_names = []
    prevkeys = ':'.join(pkeys)
    if key:
        data = scope[key]
    else:
        data = scope
    # print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    if type(data) is list:
        # Special mode for disclose.
        flag = scope.get('%s.%s'%(prevkeys,'flag'),None)
        for k in cols:
            if k == 'flag': # Exception for "flag" name.
                key = '%s.%s'%(prevkeys,k)
                refval = cols[k]
                if scope.has_key(key):
                    value = scope[key]
                    if value != refval:
                        errors.append('Data nesouhlasi. %s JSOU:%s MELY BYT:%s'%(key,str(value),str(refval)))
                else:
                    errors.append('Atribut %s chybi'%key)
                continue
            key = '%s:%s'%(prefix,k)
            # print "!!! key:",key,'flag:',flag #!!!
            # TODO: dodelat kontrolu na 0/1
            if key in data:
                disclose_names.append(key)
            else:
                errors.append('Hodnota %s.%s chybi'%(prevkeys,key))
        return errors, disclose_names
    #--------------------------------
    for k,v in cols.items():
        key = '%s:%s'%(prefix,k)
        if data.has_key(key):
            if type(v) is dict:
                pkeys.append(key)
                err, disnam = __info_contact__(prefix, v, data, key, pkeys)
                pkeys.pop()
                if len(err): errors.extend(err)
                if len(disnam): disclose_names.extend(disnam)
            else:
                if type(data[key]) is list:
                    vals = tuple(data[key])
                else:
                    vals = data[key]
                if vals != v:
                    errors.append('Data nesouhlasi. %s.%s JSOU:%s MELY BYT:%s'%(prevkeys,key,str(vals),str(v)))
        else:
            errors.append('Chybi klic %s'%key)
    return errors, disclose_names

def __check_disclosed_over__(disclose_names, saved_data):
    'Check disclosed names if they are over.'
    errors = []
    if saved_data is None: # NoneType
        errors.append('Neplatna disclosed data')
    else:
        data = saved_data[:]
        for name in disclose_names:
            if name in data:
                data.pop(data.index(name))
        if len(data): errors.append('Disclose hodnoty navic: (%s)'%', '.join(data))
    return errors
    
epp_cli, handle_contact, handle_nsset = None,None,None
get_local_text = ccReg.session_base.get_ltext

if __name__ == '__main__':
##if 0:
    if len(sys.argv) > 1: HOST = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    unittest.TextTestRunner(verbosity=2).run(suite)

if 0:
##if __name__ == '__main__':
    # TEST equals data
    saved_data = {'contact:voice': u'+123.456789', 'contact:org': u'\u010c\xed\u017ekov\xe1 a spol', 
    'contact:fax': u'+321.564987', 'contact:status.s': u'ok', 
    'contact:disclose': ['contact:voice', 'contact:org', 'contact:fax', 'contact:email', 'contact:name','contact:addr'], 
    'contact:email': u'rehor.cizek@mail.cz', 'contact:city': u'\u010cesk\xfd Krumlov', 
    'contact:disclose.flag': u'1', 
    'contact:pc': u'12300', 'contact:crDate': u'2006-08-02T09:19:48.0Z', 
    'contact:street': [u'U pr\xe1ce', u'Za monitorem', u'Nad kl\xe1vesnic\xed'], 
    'contact:crID': u'REG-LRR', 'contact:sp': u'123', 'contact:roid': u'C0000001153-CZ', 
    'contact:cc': u'CZ', 'contact:name': u'\u0158eho\u0159 \u010c\xed\u017eek', 
    'contact:id': u'test001',
    'contact:ssn':'852',
    'contact:notify_email':'info@rehorovi.cz',
    'contact:vat':'963',
    }
    errors, disclose_names = __info_contact__('contact', CCREG_CONTACT[1], saved_data)
    err = __check_disclosed_over__(disclose_names, saved_data['contact:disclose'])
    if len(err): errors.extend(err)
    if len(errors):
        print "ERRORS:"
        for e in errors:
            print e
    else:
        print "OK, NO ERRORS."

