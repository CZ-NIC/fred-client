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

import sys, os, re
import re
# from distutils.core import setup
# from distutils.command.install import install
from distutils import log
from freddist.core import setup
from freddist.command.install import install
from freddist.command.install_scripts import install_scripts

from fred.internal_variables import fred_version, config_name
from fred.session_config import get_etc_config_name


# datarootdir/prog_name/ssl => /usr/local/share/fred-client/ssl (default)
FRED_CLIENT_SSL_PATH = 'ssl/'
# datarootdir/prog_name/schemas/all-1.4.xsd =>
# /usr/local/share/fred-client/schemas/all-1.4.xsd
FRED_CLIENT_SCHEMAS_FILEMANE = 'schemas/all-1.4.xsd'

APP_SCRIPTS = ['fred-client','fred-client-qt4.pyw']
#if 'bdist_wininst' in sys.argv and '--install-script=setup_postinstall.py'
#in sys.argv:
if 'bdist_wininst' in sys.argv:
    # join postinstall only for WIN distribution
    APP_SCRIPTS.append('setup_postinstall.py')

g_srcdir = None
    
def all_files_in(dirname):
    'Returns all fullnames'
    return map(lambda s:os.path.join(g_srcdir, dirname, s),
            [n for n in os.listdir(os.path.join(g_srcdir, dirname)) if 
                os.path.isfile(os.path.join(g_srcdir, dirname,n))])

class EPPClientInstall(install):

    user_options = install.user_options
    user_options.append(('keeppatt', None,
        'not change patterns in config file.'))
    user_options.append(('host=', None,
        'fred server host [localhost]'))
    user_options.append(('port=', None,
        'fred server port [700]'))

    def __init__(self, *attrs):
        install.__init__(self, *attrs)
        # keep valid paths during package creation
        self.is_bdist_mode = None 
        self.keeppatt = None
        # check if object runs in bdist mode
        for dist in attrs:
            for name in dist.commands:
                if name == 'bdist':
                    # it is bdist mode - we are on creating the package
                    self.is_bdist_mode = 1 
                elif name == 'bdist_wininst':
                    # if we create package for windows, we change patterns
                    # as late in postinstall process
                    self.keeppatt = 1

    def initialize_options(self):
        install.initialize_options(self)
        self.host = None
        self.port = None

    def finalize_options(self):
        install.finalize_options(self)
        if not self.host:
            self.host = 'localhost'
        if not self.port:
            self.port = '700'

    def replace_patterns(self, body, names):
        """Replace patterns in config file by real values.
        Join paths with root and prefix values if they has been given.
        """
        root = self.get_actual_root()
        for varname in names:
            body = re.sub(varname, root+os.path.join(
                self.datarootdir, self.distribution.metadata.name, globals().get(varname)), body)
            # body = re.sub(varname, root+os.path.join(self.prefix, globals().get(varname)), body, 1)
        return body

    def update_fred_config(self):
        'Update fred config'
        body = open(os.path.join(self.srcdir, 'conf', config_name+'.install')).read()

        if not self.keeppatt:
            body = self.replace_patterns(body, ('FRED_CLIENT_SSL_PATH',
                'FRED_CLIENT_SCHEMAS_FILEMANE'))
            body = re.sub('FRED_CLIENT_HOST', self.host, body)
            body = re.sub('FRED_CLIENT_PORT', self.port, body)

        if not os.path.exists('build'):
            os.makedirs('build')

        open(os.path.join('build', config_name), 'w').write(body)
        print 'File %s was created.'%config_name

    def run(self):
        self.update_fred_config()
        install.run(self)

class EPPClientInstall_scripts(install_scripts):
    def update_session_config(self):
        filename = os.path.join(os.path.split(self.build_dir)[0], 'lib', 'fred', 'session_config.py')
        body = open(filename).read()

        body = re.sub(r"glob_conf = '/etc/fred/' \+ name",
                "glob_conf = os.path.join('%s/fred/',  name)" % self.sysconfdir, body)

        open(filename, 'w').write(body)
        print "session_config.py file has been updated"

    def update_fred_client(self):
        #create path where python modules are located
        pythonLibPath = os.path.join('lib', 'python' +
                str(sys.version_info[0]) + '.' + 
                str(sys.version_info[1]), 'site-packages')
        print os.path.join(self.build_dir, 'fred-client')

        body = open(os.path.join(self.build_dir, 'fred-client')).read()

        if self.get_actual_root():
            body = re.sub(r'(sys\.path\.append)\(\'[\w/_\- \.]*\'\)', r'\1' +
                    "('" + os.path.join(self.root, self.prefix.lstrip(os.path.sep),
                        pythonLibPath) + "')", body)
        else:
            body = re.sub(r'(sys\.path\.append)\(\'[\w/_\- \.]*\'\)', r'\1' +
                    "('" + os.path.join(self.prefix, pythonLibPath) + "')", body)

        open(os.path.join(self.build_dir, 'fred-client'), 'w').write(body)
        print "fred-client file has been updated"

    def run(self):
        self.update_session_config()
        self.update_fred_client()
        install_scripts.run(self)
    
def main():
    try:
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
                ('DATADIR/fred-client',[
                    'doc/fred_howto_cs.html',
                
                    'doc/niccz_console.ico', 
                    'doc/niccz_gui.ico', 
                    'doc/configure.ico',
                    'doc/help.ico',
                    
                    'doc/README_EN.txt',
                    'doc/README_CS.txt',
                    'doc/README_CS.html',
                    'doc/README_QT4_CS.pdf']),
                ('DATADIR/fred-client/ssl', [
                    'fred/certificates/test-cert.pem',
                    'fred/certificates/test-key.pem']),
                ('DATADIR/fred-client/schemas', all_files_in('fred/schemas')),
                # on posix: '/etc/fred/' 
                # on windows:  ALLUSERSPROFILE = C:\Documents and Settings\All Users
                # on windows if ALL... missing:  C:\Python25\ 
                #get_etc_config_name()
                ('SYSCONFDIR/fred', [os.path.join('build', config_name)]) 
                ], 
                
            cmdclass = {
                    'install': EPPClientInstall, 
                    'install_scripts': EPPClientInstall_scripts,
                }, 
            srcdir = g_srcdir
            )
        return True
    except Exception, e:
        log.error("Error: %s", e)
        return False
if __name__ == '__main__':
    g_srcdir = os.path.dirname(sys.argv[0])
    if not g_srcdir:
        g_srcdir = os.curdir
    if main():
        print "All done!"
