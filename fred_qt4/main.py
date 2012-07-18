#!/usr/bin/env python
# -*- coding: utf8 -*-
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

#====================================
#
#       PyQt4
#
#====================================
try:
    from PyQt4 import QtGui, QtCore
except ImportError, e:
    sys.stderr.writelines(
        ('Missing module: ', str(e), '\n',
          'For runnig this application you need install PyQt4 module. For more see README and INSTALL.\n'
          ))
    sys.exit(-1)


#====================================
#
#       Fred API
#
#====================================
# first try import from standard library path
try:
    import fred
except ImportError:
    # and than from relative path
    sys.path.insert(0, '../')
    try:
        import fred
    except ImportError, e:
        sys.stderr.writelines(
            ('Missing module: ', str(e), '\n',
             'For runnig this application you need install fred module. See README and INSTALL.\n'
            ))
        sys.exit(-1)

import main_frame

#------------------------------------
# INIT language
#------------------------------------
from fred.translate import encoding, options, option_errors, get_valid_lang
if not (options.has_key('lang_option') or options.has_key('lang_environ')):
    locale_lang = '%s' % QtCore.QLocale.system().name().toAscii()
    lang, error = get_valid_lang(locale_lang[:2], 'QtCore.QLocale.system().name()')
    if error:
        fred.translate.warning += '\n%s' % error
    else:
        options['lang'] = options['lang_environ'] = lang
        fred.translate.install_translation(options['lang'])


def main():
    path = os.path.dirname(__file__)
    if path: os.chdir(path) # needs for correct load resources - images and translation
    epp = fred.Client()
    app = QtGui.QApplication([])
    window = main_frame.FredMainWindow(app, epp, encoding, fred.translate.warning)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if msg_invalid:
        print msg_invalid
    elif options['version']:
        epp = fred.ClientSession()
        print epp.version()
    else:
        if option_errors:
            print option_errors
        else:
            main()
