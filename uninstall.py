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
import re, os
from distutils.sysconfig import get_config_var, get_python_lib
from setup import APP_SCRIPTS

def remove_all(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            print 'Remove file:',path
            try:
                os.remove(path)
            except OSError, msg:
                print 'OSError:',msg
                return 0
        for name in dirs:
            path = os.path.join(root, name)
            print 'Remove folder:',path
            try:
                os.rmdir(path)
            except OSError, msg:
                print 'OSError:',msg
                return 0
    return 1

def check_root_privileges():
    try:
        import pwd
    except ImportError:
        return 1 # platform is not Unix
    if pwd.getpwuid(os.getuid())[0] != 'root':
        print 'Error: Unsufficient privileges. For uninstallation you need root privileges.'
        return 0
    return 1

def main():
    if not check_root_privileges():
        return 0

    status = 1
    
    print "REMOVE LIBRARY"
    for name in ('fred', 'guiqt4'):
        pathname = os.path.join(get_python_lib(), name)
        print pathname
        if not remove_all(pathname):
            status = 0

    print "REMOVE SCRIPTS"
    for name in APP_SCRIPTS:
        pathname = os.path.join(get_config_var('BINDIR'), name)
        print 'Remove script:',pathname
        try:
            os.remove(pathname)
        except OSError, msg:
            print 'OSError:',msg
            status = 0
    
    return status


if __name__ == '__main__':
    if main():
        print 'OK. Uninstall process completed successfully.'
    else:
        print 'Uninstall process failed.'
