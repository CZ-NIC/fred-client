#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Create EPP XML document from command line parameters.
"""
import sys
import ccReg
from ccReg.translate import _T, options

def main(command):
    epp = ccReg.ClientSession()
    epp.set_options(options)
    epp.load_config()
    epp.set_auto_connect(0) # set OFF auto connection
    command_name, epp_doc = epp.create_eppdoc(command)
    errors = epp.fetch_errors()
    if not epp_doc and not errors: errors = _T('Unknown command!')
    xml_error = ''
    if errors:
        xml_error = ccReg.session_base.get_ltext("<?xml encoding='utf-8'?><errors>%s: %s</errors>"%(command_name,errors))
    return epp_doc, xml_error

if __name__ == '__main__':
    if sys.version_info[:2] < (2,4):
        print _T('This program needs Python 2.4 or higher. Your version is'),sys.version
    else:
        if not sys.stdin.isatty(): print sys.stdin.read() # keep previous output
        if len(sys.argv) > 1:
            epp_doc, xml_error = main(' '.join(sys.argv[1:]))
            if xml_error:
                print xml_error
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
