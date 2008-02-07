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

import sys, os
import re
from distutils.core import setup
from distutils.command.install import install

from fred.internal_variables import fred_version
from fred.session_config import get_etc_config_name

config_name = 'fred-client.conf'

FRED_CLIENT_SSL_PATH = 'share/fred-client/ssl/'
FRED_CLIENT_SCHEMAS_FILEMANE = 'share/fred-client/schemas/all-1.4.xsd'
APP_SCRIPTS = ['fred-client','fred-client-qt4.pyw']
if 'bdist_wininst' in sys.argv and '--install-script=setup_postinstall.py' in sys.argv:
    # join postinstall only for WIN distribution
    APP_SCRIPTS.append('setup_postinstall.py')

    
def all_files_in(dir):
    'Returns all fullnames'
    return map(lambda s:os.path.join(dir, s), [n for n in os.listdir(dir) if os.path.isfile(os.path.join(dir,n))])

class EPPClientInstall(install):

    user_options = install.user_options
    user_options.extend([
            ('preservepath', None, 'Preserve path in configuration file.'), 
            ])

    def __init__(self, *attrs):
        install.__init__(self, *attrs)
        # keep valid paths during package creation
        self.preservepath = None
        self.is_bdist_mode = None 
        # check if object runs in bdist mode
        for dist in attrs:
            for name in dist.commands:
                if name == 'bdist':
                    self.is_bdist_mode = 1 # it is bdist mode - we are on creating the package
                    break
            if self.is_bdist_mode:
                break

    def get_actual_root(self):
        'Return actual root only in case if the process is not in creation of the package'
        return ((self.is_bdist_mode or self.preservepath) and [''] or [type(self.root) is not None and self.root or ''])[0]
    
    def replace_patterns(self, body, names):
        """Replace patterns in config file by real values.
        Join paths with root and prefix values if they has been given.
        """
        root = self.get_actual_root()
        for varname in names:
            body = re.sub(varname, root+os.path.join(self.prefix, globals().get(varname)), body, 1)
        return body

    def update_fred_config(self):
        'Update cherry config'
        body = open(config_name+'.install').read()
        body = self.replace_patterns(body, ('FRED_CLIENT_SSL_PATH', 'FRED_CLIENT_SCHEMAS_FILEMANE'))
        open(config_name, 'w').write(body)
        print 'File %s was created.'%config_name

    def run(self):
        self.update_fred_config()
        install.run(self)

    
if __name__ == '__main__':

    setup(name = 'fred-client',
        description = 'Client FRED (Free Registry for enum and domain)',
        author = 'Zdenek Bohm, CZ.NIC',
        author_email = 'zdenek.bohm@nic.cz',
        url = 'http://www.nic.cz',
        version = fred_version,
        license = 'GNU GPL',
        packages = ['fred','guiqt4'],
        package_data={
            'fred': ['INSTALL','LICENSE','CREDITS','*.txt',
                'lang/fred_client_cs.po',
                'lang/cs/LC_MESSAGES/fred_client.mo'],
            'guiqt4': ['*.py','*.png','*.qm'],
        },
        scripts = APP_SCRIPTS, 
        data_files=[
            ('share/fred-client',[
                'doc/fred_howto_cs.html',
            
                'doc/niccz_console.ico', 
                'doc/configure.ico',
                'doc/help.ico',
                
                'doc/README_CS.html',
                'doc/README_QT4_CS.pdf']),
            ('share/fred-client/ssl', [
                'fred/certificates/test-cert.pem',
                'fred/certificates/test-key.pem']),
            ('share/fred-client/schemas', all_files_in('fred/schemas')),
            (get_etc_config_name(),[config_name]) # '/etc/fred/' |  ALLUSERSPROFILE = C:\Documents and Settings\All Users
            ], 
            
        cmdclass = {
                'install': EPPClientInstall, 
            }, 
        
        )

