#!/usr/bin/python
# -*- coding: utf-8 -*-
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

old_cwd = os.getcwd()
try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass

# setup.py will change this path to reflect changes in prefix
# and/or root option during install
sys.path.insert(0, '.')

import fred
from fred.translate import encoding, options, option_errors

def check_modules():
    try:
        from PyQt4 import QtGui, QtCore
    except ImportError, e:
        error_message = 'ImportError: %s\n'%e
    else:
        return
    
    import Tkinter
    root = Tkinter.Tk() 
    root.title('Import error')
    label = Tkinter.Label(root, text=error_message +\
            'This application needs Qt4 and PyQt4 modules.\n'\
            'Download and install them from\n'\
            'http://trolltech.com/developer/downloads/qt/windows\n'\
            'http://www.riverbankcomputing.com/Downloads/PyQt4/GPL/'
            )
    label.pack() 
    button = Tkinter.Button(root, text="Cancel", command=root.destroy)
    button.pack()
    root.mainloop() 

if __name__ == '__main__':
    if sys.platform[:3] == 'win':
        check_modules()

    from guiqt4.main import main
    
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
            main([], options['lang'], os.getcwd(), options)

    os.chdir(old_cwd)
