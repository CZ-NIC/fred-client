#!/usr/bin/env python
# -*- coding: utf8 -*-
from distutils.core import setup

setup(name = 'FredClient',
    description = 'Client FRED (Free Registry for enum and domain)',
    author = 'Zdenek Bohm, CZ.NIC',
    author_email = 'zdenek.bohm@nic.cz',
    url = 'http://www.nic.cz',
    version = '1.3.0',
    license = 'GNU GPL',
    packages = ['fred','guiqt4'],
    package_data={
        'fred': ['INSTALL','LICENSE','CREDITS','*.txt','schemas/*.xsd',
            'lang/fred_client_cs.po',
            'lang/cs/LC_MESSAGES/fred_client.mo'],
        'guiqt4': ['*.py','*.png','*.qm'],
    },
    scripts = ['fred_client.py'],
)

