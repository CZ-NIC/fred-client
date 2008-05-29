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
from distutils import log
from freddist.core import setup
from freddist.command.install import install
from freddist.command.install_scripts import install_scripts
from freddist.command.install_lib import install_lib
from freddist.command.install_data import install_data
from freddist import file_util

from fred.internal_variables import fred_version, config_name
from fred.session_config import get_etc_config_name

# datarootdir/prog_name/ssl => /usr/local/share/fred-client/ssl (default)
DEFAULT_SSL_PATH = 'ssl'
# datarootdir/prog_name/schemas/all-1.4.xsd =>
# /usr/local/share/fred-client/schemas/all-1.4.xsd
DEFAULT_SCHEMAS_FILEMANE = 'schemas/all-1.4.xsd'

APP_SCRIPTS = ['fred-client','fred-client-qt4.pyw']
#if 'bdist_wininst' in sys.argv and '--install-script=setup_postinstall.py'
#in sys.argv:
if 'bdist_wininst' in sys.argv:
    # join postinstall only for WIN distribution
    APP_SCRIPTS.append('setup_postinstall.py')

g_install_unittest = None
    
class EPPClientInstall(install):

    user_options = install.user_options
    user_options.append(('keeppatt', None,
        'not change patterns in config file.'))
    user_options.append(('host=', None,
        'fred server host [localhost]'))
    user_options.append(('port=', None,
        'fred server port [700]'))
    user_options.append(('install-unittest', None,
        'setup will install unittest scripts into PREFIX/lib/fred-client/unittest '
        'directory'))


    boolean_options = install.boolean_options
    boolean_options.append('install-unittest')

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
        self.install_unittest = None

    def finalize_options(self):
        install.finalize_options(self)
        if not self.host:
            self.host = 'localhost'
        if not self.port:
            self.port = '700'

        if self.install_unittest:
            self.distribution.data_files.append(
                    ('LIBDIR/%s/unittest' % self.distribution.get_name(), 
                        file_util.all_files_in_2('unittest')))
        global g_install_unittest
        g_install_unittest = self.install_unittest

    def update_fred_config(self):
        '''Update fred config'''
        if not self.keeppatt:
            root = self.get_actual_root()
            if not os.path.exists('build'):
                os.makedirs('build')
            values = []
            values.append(('FRED_CLIENT_SSL_PATH', root + os.path.join(
                self.datarootdir, 
                self.distribution.metadata.name, 
                DEFAULT_SSL_PATH)))
            values.append(('FRED_CLIENT_SCHEMAS_FILEMANE', root + os.path.join(
                self.datarootdir, 
                self.distribution.metadata.name, 
                DEFAULT_SCHEMAS_FILEMANE)))
            values.append(('FRED_CLIENT_HOST', self.host))
            values.append(('FRED_CLIENT_PORT', self.port))
            self.replace_pattern(
                os.path.join(self.srcdir, 'conf', config_name+'.install'),
                os.path.join('build', config_name),
                values)
        print 'File %s was created.' % config_name

    def run(self):
        self.update_fred_config()
        install.run(self)

class EPPClientInstall_scripts(install_scripts):

    def update_fred_client(self):
        values = [((r"(sys\.path\.insert\(0, )\'\'\)",
            r"\1'%s')" % self.getDir('purelibdir')))]
        self.replace_pattern(os.path.join(self.build_dir, 'fred-client'),
                None, values)
        print "fred-client file has been updated"

    def update_fred_client_qt4(self):
        values = [((r"(sys\.path\.insert\(0, )\'\'\)",
            r"\1'%s')" % self.getDir('purelibdir')))]
        self.replace_pattern(os.path.join(self.build_dir, 'fred-client-qt4.pyw'),
                None, values)
        print "fred-client-qt4.pyw file has been updated"

    def run(self):
        self.update_fred_client()
        self.update_fred_client_qt4()
        install_scripts.run(self)

class Install_lib(install_lib):
    def update_session_config(self):
        filename = os.path.join(self.build_dir, 'fred', 'session_config.py')
        values = [((
            r"(glob_conf = )\'\'",
            r"\1'%s'" % os.path.join(
                self.getDir('sysconfdir'), 'fred', config_name)))]
        self.replace_pattern(filename, None, values)
        print "session_config.py file has been updated"

    def update_session_base(self):
        filename = os.path.join(self.build_dir, 'fred', 'session_base.py')
        values = [((
            r"(self\._config_name = )\'\'",
            r"\1'%s'" % os.path.join(
                self.getDir('sysconfdir'), 'fred', config_name)))]
        self.replace_pattern(filename, None, values)
        print "session_base.py file has been updated"

    def run(self):
        self.update_session_config()
        self.update_session_base()
        install_lib.run(self)

class Install_data(install_data):
    def update_file(self, filename):
        values = []
        values.append((r'(sys\.path\.insert\(0,\ )\'\'\)',
            r"\1'%s')" % self.getDir('purelibdir')))
        self.replace_pattern(os.path.join(self.getDir('libdir'),
            self.distribution.get_name(), 'unittest', filename),
            None, values)
        print "%s file has been updated" %filename

    def run(self):
        install_data.run(self)
        # TODO unittest cannot be added into rpm package - because of
        # update_file method don't know proper path
        if g_install_unittest or self.is_bdist_mode:
            files = file_util.all_files_in_2('unittest', onlyFilenames=True)
            for file in files:
                self.update_file(file)

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
                ('DATADIR/fred-client/schemas', file_util.all_files_in_2('fred/schemas')),
                # on posix: '/etc/fred/' 
                # on windows:  ALLUSERSPROFILE = C:\Documents and Settings\All Users
                # on windows if ALL... missing:  C:\Python25\ 
                #get_etc_config_name()
                ('SYSCONFDIR/fred', [os.path.join('build', config_name)]) 
                ], 
                
            cmdclass = {
                    'install': EPPClientInstall, 
                    'install_scripts': EPPClientInstall_scripts,
                    'install_lib':Install_lib,
                    'install_data':Install_data,
                }, 
            )
        return True
    except Exception, e:
        log.error("Error: %s", e)
        return False
if __name__ == '__main__':
    if main():
        print "All done!"
