#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Create EPP XML document from command line parameters.
"""
import sys
import ccReg
from ccReg.translate import _T, options, encoding

def main(command):
    epp = ccReg.ClientSession()
    epp.load_config(options['session'])
    epp.set_auto_connect(0) # set OFF auto connection
    command_name, epp_doc = epp.create_eppdoc(command)
    errors = epp.fetch_errors()
    if not epp_doc and not errors: errors = _T('Unknown command')
    xml_error = ''
    if errors:
        if type(command_name) == unicode: command_name = command_name.encode(encoding)
        if type(errors) == unicode: errors = errors.encode(encoding)
        xml_error = "<?xml encoding='utf-8'?><errors>%s: %s</errors>"%(command_name,errors)
    return epp_doc, xml_error

if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if not sys.stdin.isatty(): print sys.stdin.read() # keep previous output
        if len(sys.argv) > 1:
            epp_doc, xml_error = main(' '.join(sys.argv[1:]))
            if xml_error:
                print xml_error
            else:
                print epp_doc
        else:
            print '%s: %s command params\n\n%s\n\n%s%s\n%s\n\n  %s\n'%(_T('Usage'), 'ccreg_create.py',
                _T('Create EPP XML document from command line parameters.'),
                _T('EXAMPLES'),
                """
./ccreg_create.py info_domain nic.cz
./ccreg_create.py info_contact reg-id
""",
                _T('Eventual errors are return in XML format: <errors>... msg ...</errors>.'),
                _T('For more information, see README.')
                )
