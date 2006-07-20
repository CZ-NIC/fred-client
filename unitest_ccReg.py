# -*- coding: utf8 -*-
#!/usr/bin/env python
import unittest
import ccReg

class BaseTest(unittest.TestCase):
    """Shared functions needed for testing.
    """

    def setUp(self):
        '1.0 vytvoreni klienta'
        try:
            type(self.epc)
        except AttributeError:
            self.epc = ccReg.Client()
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
            else:
                self.epc.logout()
        return code, error

    def __find_available_handle__(self, type_object, prefix):
        'Find first available object. (MUST be login)'
        available_handle = ''
        handles = []
        for n in range(10):
            handles.append('%s%02d'%(prefix,n))
##        print "!!! handles",handles
        getattr(self.epc,'check_%s'%type_object)(handles)
        for name in handles:
            if self.epc.is_val(('data',name)) == 1:
                available_handle = name
                break
        print "!!! available_handle:",available_handle
        return available_handle
