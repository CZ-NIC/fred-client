#!/usr/bin/env python
# -*- coding: utf8 -*-
from distutils.core import setup

setup(name = 'ccRegClient',
    description = 'ccReg EPP Client',
    author = 'CZ.NIC',
    author_email = 'info@nic.cz',
    url = 'http://www.nic.cz',
    version = '1.1',
    license = 'GNU GPL',
    packages = ['ccReg'],
    package_data={
        'ccReg':['INSTALL','LICENSE','CREDITS','*.txt','schemas/*.xsd',
        'lang/cz_nic_ccreg_client.po',
        'lang/cs/LC_MESSAGES/cz_nic_ccreg_client.mo',
        'certificates/*.pem',
        ],
    },
    scripts = ['ccreg_client.py','ccreg_console.py','ccreg_create.py','ccreg_sender.py'],
)
