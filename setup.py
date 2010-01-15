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

import sys, os, shutil
from distutils import log
from freddist.core import setup
from freddist.command.sdist import sdist
from freddist.command.install import install
from freddist.command.install_scripts import install_scripts
from freddist.command.install_lib import install_lib
from freddist.command.install_data import install_data
from freddist import file_util
from freddist.file_util import *

from fred.internal_variables import fred_version, config_name
from fred.session_config import get_etc_config_name

g_directory = ''

# datarootdir/prog_name/ssl => /usr/local/share/fred-client/ssl (default)
DEFAULT_SSL_PATH = 'ssl'
# datarootdir/prog_name/schemas/all.xsd =>
# /usr/local/share/fred-client/schemas/all.xsd
DEFAULT_SCHEMAS_FILEMANE = 'schemas/all.xsd'

APP_SCRIPTS = ['fred-client', 'fred-client-qt4.pyw']
#if 'bdist_wininst' in sys.argv and '--install-script=setup_postinstall.py'
#in sys.argv:
if 'bdist_wininst' in sys.argv:
    # join postinstall only for WIN distribution
    APP_SCRIPTS.append('setup_postinstall.py')


class EPPClientSDist(sdist):
    "sdist check required"
    
    def run(self):
        "run main process"
        if not os.path.exists(os.path.join(self.srcdir, 'freddist')):
            raise IOError(2, 'Folder freddist missing. Make symlink or copy '
                             'from enum/distutils.')
        sdist.run(self)
    

class EPPClientInstall(install):

    user_options = install.user_options
    user_options.append(('keeppatt', None,
        'not change patterns in config file.'))
    user_options.append(('host=', None,
        'fred server host [localhost]'))
    user_options.append(('port=', None,
        'fred server port [700]'))


    boolean_options = install.boolean_options

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
        self.include_scripts = True

    def finalize_options(self):
        install.finalize_options(self)
        if not self.host:
            self.host = 'localhost'
        if not self.port:
            self.port = '700'


    def update_fred_config(self):
        '''Update fred config'''
        if not self.keeppatt:
            root = self.get_actual_root()
            if not os.path.exists('build'):
                os.makedirs('build')
            values = []
            values.append(('FRED_CLIENT_SSL_PATH',
                os.path.join(
                    self.getDir_std('appdir'),
                    DEFAULT_SSL_PATH))
                )
            values.append(('FRED_CLIENT_SCHEMAS_FILEMANE',
                os.path.join(
                    self.getDir_std('appdir'),
                    DEFAULT_SCHEMAS_FILEMANE))
                )
            values.append(('FRED_CLIENT_HOST', self.host))
            values.append(('FRED_CLIENT_PORT', self.port))
            self.replace_pattern(
                os.path.join(self.srcdir, 'conf', config_name+'.install'),
                os.path.join('build', config_name),
                values)
        else:
            shutil.copyfile(
                    os.path.join(self.srcdir, 'conf', config_name + '.install'),
                    os.path.join('build', config_name))
        print 'File %s was created.' % config_name


    def run(self):
        self.update_fred_config()
        install.run(self)

class EPPClientInstall_scripts(install_scripts):

    def update_fred_client(self):
        values = [((r"(sys\.path\.insert\(0, )\'[\w/_ \-\.]*\'\)",
            r"\1'%s')" % self.getDir_std('purelibdir')))]
        self.replace_pattern(os.path.join(self.build_dir, 'fred-client'),
                None, values)
        if os.environ.has_key('BDIST_SIMPLE'):
            self.replace_pattern(os.path.join(self.build_dir, 'fred-client.py'),
                    None, values)
        print "fred-client file has been updated"

    def update_fred_client_qt4(self):
        values = [((r"(sys\.path\.insert\(0, )\'[\w/_ \-\.]*\'\)",
            r"\1'%s')" % self.getDir_std('purelibdir')))]
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
        # when simple package creation is in progress this enviroment variable is set to 'True'
        if os.environ.has_key('BDIST_SIMPLE'):
            # simple package must use as a first configuration file its own
            # file from ``data_files'' directory, not file from user home directory
            # nor file from /etc or any other directory.
            values = [((
                r"os\.path\.join\(os\.path.expanduser\(\'\~\'\),config_name\)",
                r"'%s'" % os.path.join(
                    self.getDir_std('sysconfdir'), 'fred', config_name)))]
        else:
            values = [((
                r"(glob_conf = )\'[\w/_ \-\.]*\'",
                r"\1'%s'" % os.path.join(
                    self.getDir_std('sysconfdir'), 'fred', config_name)))]
        self.replace_pattern(filename, None, values)
        print "session_config.py file has been updated"

    def run(self):
        self.update_session_config()
        install_lib.run(self)

class Install_data(install_data):
    def run(self):
        install_data.run(self)

def main(directory):
    if os.environ.has_key('BDIST_SIMPLE'):
        APP_SCRIPTS.append('fred-client.py')
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
                ('DATAROOTDIR/fred-client',[
                    'doc/fred_howto_cs.html',
                    'doc/niccz_console.ico', 
                    'doc/niccz_gui.ico', 
                    'doc/configure.ico',
                    'doc/help.ico',
                    'doc/README_EN.txt',
                    'doc/README_CS.txt',
                    'doc/README_CS.html',
                    'doc/README_QT4_CS.pdf']),
                ('DATAROOTDIR/fred-client/ssl', [
                    'fred/certificates/test-cert.pem',
                    'fred/certificates/test-key.pem']),
                # ('DATADIR/fred-client/schemas', file_util.all_files_in_2('fred/schemas')),
                # on posix: '/etc/fred/' 
                # on windows:  ALLUSERSPROFILE = C:\Documents and Settings\All Users
                # on windows if ALL... missing:  C:\Python25\ 
                #get_etc_config_name()
                ('SYSCONFDIR/fred', [os.path.join('build', config_name)]) 
                ]
            + all_files_in_4(
                os.path.join('DATADIR', 'fred-client', 'schemas'),
                os.path.join(directory, 'fred', 'schemas')),
            cmdclass = {
                    'sdist': EPPClientSDist, 
                    'install': EPPClientInstall, 
                    'install_scripts': EPPClientInstall_scripts,
                    'install_lib':Install_lib,
                    'install_data':Install_data,
                }, 
            )
        return True
    except OSError, msg:
        message = "%s" % msg
        log.error("OSError: %s.", message)
        if 'schemas' in message:
            log.error("Schemas missing. Use them from the project mod-eppd and "
                      "copy or make symlink fred/schemas.")
        return False
    except Exception, msg:
        log.error("Error: %s", msg)
        return False

if __name__ == '__main__':
    g_directory = os.path.dirname(sys.argv[0])
    filename = 'fred-client.py'
    if 'bdist_simple' in sys.argv:
        # when creating bdist_simple package, enviroment variable
        # ``BDIST_SIMPLE'' must be set
        os.environ['BDIST_SIMPLE'] = 'True'
        # copy fred-client to fred-client.py (windows do not recognize file
        # without .py extension as a python script)
        shutil.copy(
                os.path.join(g_directory, "fred-client"),
                os.path.join(g_directory, filename));
    print g_directory
    if main(g_directory):
        print "All done!"
    if os.environ.has_key('BDIST_SIMPLE'):
        # remove now useless fred-client.py file
        try:
            os.remove(os.path.join(g_directory, filename))
        except OSError:
            pass
