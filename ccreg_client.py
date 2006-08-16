#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import ccReg
from ccReg.translate import _T, options, option_errors

if __name__ == '__main__':
    if sys.version_info[:2] < (2,4):
        print _T('This program needs Python 2.4 or higher. Your version is'),sys.version
    else:
        if options['help']:
            print _T("""Usage: python ccreg_client.py [OPTIONS]
Client for communication with EPP server.

OPTIONS with values:
    -s --session  name of session used for connect to the EPP server
                  session values are read from config file
    -h --host     host name (overwrite config value)
    -u --user     user name (overwrite config value)
    -p --password (overwrite config value)
    -l --lang     language of session
    -v --verbose  display modes: 1,2,3; default: 1
                  1 - essensial values
                  2 - all returned values
                  3 - display XML sources
    -c --command  send command to the EPP server
                  example: --command='info-domain nic.cz'

OPTIONS:
    -r --colors   set on colored output
    -? --help     this help
""")
        elif option_errors:
            print option_errors
        else:
            if options['command']:
                import ccreg_create
                import ccreg_sender
                epp_doc, xml_error = ccreg_create.main(options['command'])
                if xml_error:
                    print xml_error
                else:
                    if len(epp_doc):
                        ccreg_sender.send_docs(((1,epp_doc),))
                    else:
                        print 'Internal error: epp_doc, xml_error = ccreg_create.main(options[command])'
            else:
                import ccreg_console
                ccreg_console.main(options['session'])
