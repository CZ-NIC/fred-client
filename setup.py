#!/usr/bin/env python
# -*- coding: utf8 -*-
from distutils.core import setup

setup(name = 'FredClient',
    description = 'Client FRED (Free Registry for enum and domain)',
    author = 'Zdenek Bohm, CZ.NIC',
    author_email = 'zdenek.bohm@nic.cz',
    url = 'http://www.nic.cz',
    version = '1.0.0',
    license = 'GNU GPL',
    packages = ['fred'], ## ,'guiqt' temporary disabled
    package_data={
        'fred': ['INSTALL','LICENSE','CREDITS','*.txt','schemas/*.xsd',
            'lang/fred_client_cs.po',
            'lang/cs/LC_MESSAGES/fred_client.mo'],
## temporary disabled
##        'guiqt': ['*.py','*.ui','*.ts','*.qm','*.png','qt_client.project'],

    },
    scripts = ['fred_client.py','fred_console.py','fred_create.py','fred_sender.py'],
)
