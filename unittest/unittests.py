#!/usr/bin/env python

import sys
import unittest

import unitest_contact
import unitest_contact2
import unitest_domain
import unitest_domain_zone
import unitest_domain2
import unitest_keyset
import unitest_keyset2
import unitest_keyset3
import unitest_keyset4
import unitest_keyset5
import unitest_login
import unitest_nsset
import unitest_nsset2

tests = [
    unitest_contact, 
    unitest_contact2,
    unitest_domain,
    unitest_domain_zone,
    unitest_domain2,
    unitest_keyset,
    unitest_keyset2,
    unitest_keyset3,
    unitest_keyset4,
    unitest_keyset5,
    unitest_login,
    unitest_nsset,
    unitest_nsset2
]

if __name__ == '__main__':
    tests_list = []
    for test in tests:
        foo = unittest.TestLoader().loadTestsFromModule(test)
        tests_list.append(foo)

    alltests = unittest.TestSuite(tests_list)
    unittest.TextTestRunner(verbosity=2).run(alltests)
