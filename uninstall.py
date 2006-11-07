#!/usr/bin/env python
# -*- coding: utf8 -*-
import re, os

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
    
def main():
    filelog = 'install.log'
    print 'Uninstall process. Run as root. Needs %s file.'%filelog
    try:
        body = open(filelog).read()
    except IOError, msg:
        print 'IOError',msg
        print 'For uninstallation process you need %s file.'%filelog
        print 'This file is created during installation. For more see INSTALL.'
        return 0
    # copying build/lib/fred/session_config.py -> /usr/lib/python2.4/site-packages/fred
    match = re.search('\S+site-packages\S+',body)
    if not match:
        print 'ERROR. Anchor "site-packages" was not found.'
        return 0
    path = match.group()
    print "REMOVE LIBRARY"
    print path
    if not remove_all(path): return
    # changing mode of /usr/bin/fred_client.py to 755
    scripts = re.findall('\S+fred_client.py',body)
    if not len(scripts):
        print 'ERROR. Anchor "fred_client.py" was not found.'
        return 0
    # 'build/scripts-2.4/fred_client.py'
    patt_build = re.compile('build')
    print "REMOVE SCRIPTS"
    for name in scripts:
        if patt_build.match(name): continue # not files in temporary folder
        print 'Remove script:',name
        try:
            os.remove(name)
        except OSError, msg:
            print 'OSError:',msg
            return 0
    #print 'REMOVE THIS FOLDER'
    #if not remove_all('.'): return
    return 1

if __name__ == '__main__':
    if main():
        print 'OK. Uninstall process completed successfully.'
    else:
        print 'Uninstall process failed.'
