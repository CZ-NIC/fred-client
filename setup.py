#!/usr/bin/env python
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
from distutils.core import setup
from fred.internal_variables import fred_version

APP_SCRIPTS = ['fred_client','fred_client_qt4.pyw']
if 'bdist_wininst' in sys.argv and '--install-script=setup_postinstall.py' in sys.argv:
    # join postinstall only for WIN distribution
    APP_SCRIPTS.append('setup_postinstall.py')

if __name__ == '__main__':

    setup(name = 'FredClient',
        description = 'Client FRED (Free Registry for enum and domain)',
        author = 'Zdenek Bohm, CZ.NIC',
        author_email = 'zdenek.bohm@nic.cz',
        url = 'http://www.nic.cz',
        version = fred_version,
        license = 'GNU GPL',
        packages = ['fred','guiqt4'],
        package_data={
            'fred': ['INSTALL','LICENSE','CREDITS','*.txt','schemas/*.xsd',
                'lang/fred_client_cs.po',
                'lang/cs/LC_MESSAGES/fred_client.mo'],
            'guiqt4': ['*.py','*.png','*.qm'],
        },
        scripts = APP_SCRIPTS, 
        data_files=[
            ('cznic_fred_docs',[
                'fred_client.conf.sample',
                'doc/fred_howto_cs.html',
            
                'doc/niccz_console.ico', 
                'doc/configure.ico',
                'doc/help.ico',
                
                'doc/README_CS.html',
                'doc/README_QT4_CS.pdf'])
            ]
        
        )

