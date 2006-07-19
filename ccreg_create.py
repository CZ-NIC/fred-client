#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Create EPP XML document from command line parameters.
"""
import sys
import ccReg

if __name__ == '__main__':
    if len(sys.argv) > 1:
        epp = ccReg.ClientSession()
        epp.load_config()
        epp.set_auto_connect(0) # set OFF auto connection
        command_name, epp_doc = epp.create_eppdoc(' '.join(sys.argv[1:]))
        errors = epp.get_messages()
        if errors:
            print '!!! %s:'%command_name,errors
        else:
            print epp_doc
    else:
        print """!!! ccReg Create !!!

Create EPP XML document from command line parameters.
If any error occurs, script returns error in format:

!!! command_name: error messages

Usage:
python ccreg_create.py command params

Example:
python ccreg_create.py info-domain nic.cz
python ccreg_create.py info-contact reg-id
"""
