#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
sys.path.insert(0, '..')
import re
import unittest
import fred
import unitest_share


class Test(unittest.TestCase):

    def setUp(self):
        'Check if client is online.'
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


    def test_060(self):
        '1.0 Test info contact with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.info_contact(invhandle)

            # if nsset has been created append handle for delete it later
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been accepted.' % invhandle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))


    def test_061(self):
        '1.1 Test info keyset with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.info_keyset(invhandle)

            # if nsset has been created append handle for delete it later
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been accepted.' % invhandle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_062(self):
        '1.2 Test info nsset with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.info_nsset(invhandle)

            # if nsset has been created append handle for delete it later
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been accepted.' % invhandle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_063(self):
        '1.3 Test info domain with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.info_domain(invhandle)

            # if nsset has been created append handle for delete it later
            if epp_cli.is_val() == 1000:
                errors.append('Name %s has been accepted.' % invhandle)
            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))


    def test_070(self):
        '2.0 Test check contact with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/;<=>?@[\]^`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]

	    epp_cli.check_contact(invhandle)

            if epp_cli.is_val() != 1000:
                errors.append('Check contact did not return code 1000 for handle %s ' % invhandle)

	    if epp_cli.is_val(('data', invhandle + ':reason')) != 'Not available. invalid format':
		errors.append('Name %s has been accepted by check contact.' % invhandle)

            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))


    def test_071(self):

        '2.1 Test check keyset with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/;<=>?@[\]^`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.check_keyset(invhandle)

	    if epp_cli.is_val() != 1000:
		errors.append('Check keyset did not return code 1000 for handle %s ' % invhandle)
	    if epp_cli.is_val(('data', invhandle + ':reason')) != 'Not available. invalid format':
		errors.append('Name %s has been accepted by check keyset.' % invhandle)


            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_072(self):
        '2.2 Test check nsset with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/;<=>?@[\]^`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.check_nsset(invhandle)

	    if epp_cli.is_val() != 1000:
		errors.append('Check nsset did not return code 1000 for handle %s ' % invhandle)
	    if epp_cli.is_val(('data', invhandle + ':reason')) != 'Not available. invalid format':
		errors.append('Name %s has been accepted by check nsset.' % invhandle)

            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))

    def test_073(self):
        '2.3 Test check domain with some invalid handles'
        errors = []
        notallowed = '!"#$%&\'()*+,/:;<=>?@[\]^_`{|}~'
        max = len(notallowed)
        for position in range(max):
	    invhandle = 'han%sdle' % notallowed[position]
	    epp_cli.check_domain(invhandle)

	    if epp_cli.is_val() != 1000:
		errors.append('Check domain did not return code 1000 for handle %s ' % invhandle)
	    if epp_cli.is_val(('data', invhandle + ':reason')) != 'Not available. invalid format':
	    	errors.append('Name %s has been accepted by check domain.' % invhandle)

            unitest_share.write_log(epp_cli, log_fp, log_step, self.id(), 
                                    self.shortDescription()+' %s'%(invhandle), (position, max))
        self.failIf(len(errors) > 0, '\n'.join(errors))


# global variables of the client object and login file
epp_cli, epp_cli_log, log_fp, log_step = (None,)*4


if __name__ == '__main__':
    if fred.translate.option_errors:
        print fred.translate.option_errors
    elif fred.translate.options['help']:
        print unitest_share.__doc__%__file__
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        unittest.TextTestRunner(verbosity=2).run(suite)
        if log_fp: log_fp.close()


