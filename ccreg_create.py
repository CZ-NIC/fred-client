#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Create EPP XML document from command line parameters.
"""
import sys
import ccReg
from ccReg.translate import _T

if __name__ == '__main__':
    if sys.version_info[:2] < (2,4):
        print _T('This program needs Python 2.4 or higher. Your version is'),sys.version
    else:
        if not sys.stdin.isatty(): print sys.stdin.read() # keep previous output
        if len(sys.argv) > 1:
            epp = ccReg.ClientSession()
            epp.load_config()
            epp.set_auto_connect(0) # set OFF auto connection
            command_name, epp_doc = epp.create_eppdoc(' '.join(sys.argv[1:]))
            errors = epp.fetch_errors()
            if errors:
                ccReg.session_base.print_unicode("<?xml encoding='utf-8'?><errors>%s: %s</errors>"%(command_name,errors))
            else:
                print epp_doc
        else:
            print """*** ccReg Create ***

Create EPP XML document from command line parameters.

Usage:
python ccreg_create.py command params

Example:
python ccreg_create.py info-domain nic.cz
python ccreg_create.py info-contact reg-id

If any error occurs, script returns errors in XML with top node errors.
"""
