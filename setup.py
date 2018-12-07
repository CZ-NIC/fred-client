#!/usr/bin/env python
#
# Copyright (C) 2006-2018  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import shutil
import sys

from freddist.command.install import install
from freddist.core import setup

from fred.internal_variables import config_name


PROJECT_NAME = 'fred-client'
PACKAGE_NAME = 'fred-client'

SCRIPT_FILENAME = PROJECT_NAME
WIN_SCRIPT_FILENAME = '%s.py' % SCRIPT_FILENAME
SCRIPTS = [SCRIPT_FILENAME]


class EPPClientInstall(install):
    user_options = install.user_options + [
        ('keeppatt', None,
         "do not change patterns in config file."),
        ('host=', None,
         "fred server host [localhost]"),
        ('port=', None,
         "fred server port [700]"),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.keeppatt = None
        self.host = None
        self.port = None

    def finalize_options(self):
        install.finalize_options(self)
        if not self.host:
            self.host = 'localhost'
        if not self.port:
            self.port = '700'
        # if we create package for windows, we change patterns in postinstall process
        if not self.keeppatt and 'bdist_wininst' in self.distribution.commands:
            self.keeppatt = 1

    def update_config(self, filename):
        '''Update config file'''
        # No change required
        if self.keeppatt:
            return
        content = open(filename).read()
        pattern = re.compile(r'^dir=.*$', re.MULTILINE)
        content = pattern.sub('dir = %s' % self.expand_filename('$data/share/%s/ssl' % PACKAGE_NAME), content)
        pattern = re.compile(r'^host = .*$', re.MULTILINE)
        content = pattern.sub('host = %s' % self.host, content)
        pattern = re.compile(r'^port = .*$', re.MULTILINE)
        content = pattern.sub('port = %s' % self.port, content)
        open(filename, 'w').write(content)
        self.announce("File %s was updated." % filename)

    def update_session_config(self, filename):
        content = open(filename).read()
        if os.environ.has_key('BDIST_SIMPLE'):
            content = content.replace("os.path.join(os.path.expanduser('~'), config_name)",
                                      "'%s'" % self.expand_filename('$sysconf/fred/%s' % config_name))
        else:
            content = content.replace("glob_conf = 'conf/fred-client.conf'",
                                      "glob_conf = '%s'" % self.expand_filename('$sysconf/fred/%s' % config_name))
        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)

    def update_version(self, filename):
        "Update version number for client"
        content = open(filename).read()
        content = content.replace('PACKAGE_VERSION', self.distribution.metadata.version)
        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)

    def update_script(self, filename):
        content = open(filename).read()
        content = content.replace('sys.path.insert(0, \'.\')',
                                  'sys.path.insert(0, \'%s\')' % self.expand_filename('$purelib'))
        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)


def main():
    srcdir = os.path.dirname(os.path.abspath(__file__))

    #XXX: Because of win, we have to create a copy of start script. This should be solved in repository, e.g. Provide
    # script that will run on win.
    copy_script = False
    if 'bdist_wininst' in sys.argv:
        # We have another set of scripts for win
        SCRIPTS.extend((WIN_SCRIPT_FILENAME, 'setup_postinstall.py'))
        SCRIPTS.remove(SCRIPT_FILENAME)
        copy_script = True
    elif 'sdist' in sys.argv:
        SCRIPTS.append(WIN_SCRIPT_FILENAME)
        copy_script = True

    if copy_script:
        win_script = '%s.py' % SCRIPT_FILENAME
        shutil.copy(os.path.join(srcdir, SCRIPT_FILENAME), os.path.join(srcdir, win_script))

    data_files = [('share/%s' % PACKAGE_NAME, ['doc/fred_howto_cs.html', 'doc/niccz_console.ico',
                                               'doc/configure.ico', 'doc/help.ico', 'doc/README_EN.txt',
                                               'doc/README_CS.txt', 'doc/README_CS.html']),
                  ('share/%s/ssl' % PACKAGE_NAME, ['fred/certificates/test-cert.pem',
                                                   'fred/certificates/test-key.pem']),
                  ('$sysconf/fred', [os.path.join('conf', config_name)])]
    setup(name=PROJECT_NAME,
          version='2.11.0',
          description='Client FRED (Free Registry for enum and domain)',
          author='Zdenek Bohm, CZ.NIC',
          author_email='zdenek.bohm@nic.cz',
          url='http://www.nic.cz',
          license='GNU GPL',
          packages=['fred'],
          package_data={'fred': ['INSTALL', 'LICENSE', 'CREDITS', '*.txt']},
          i18n_files=['fred/lang/cs/LC_MESSAGES/fred_client.po'],
          scripts=SCRIPTS,
          data_files=data_files,
          cmdclass={'install': EPPClientInstall},
          modify_files={'$purelib/fred/internal_variables.py': 'update_version',
                        '$purelib/fred/session_config.py': 'update_session_config',
                        '$scripts/%s' % SCRIPT_FILENAME: 'update_script',
                        '$sysconf/fred/%s' % config_name: 'update_config'})

    # Remove the copy of a script
    if copy_script:
        try:
            os.unlink(os.path.join(srcdir, win_script))
        except IOError:
            pass


if __name__ == '__main__':
    main()
