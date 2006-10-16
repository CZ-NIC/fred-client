#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import ccReg
from ccReg.translate import options, option_errors

if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print "%s %s" % (msg_invalid)
    else:
        from ccreg_console import help_option
        if options['help']:
            print '%s: %s [OPTIONS...]\n\n%s\n\n%s\n  %s\n  %s\n\n  %s\n'%(_T('Usage'), 'ccreg_client',
            _T('Client for communication with EPP server.'),
            help_option,
   _T("""-d COMMAND, --command=COMMAND
                   send command to server and exit"""),
   _T("""-q,  --qt
                   run client in grafical user interface"""),
   _T('For more information, see README.'))
        elif options['version']:
            epp = ccReg.ClientSession()
            print epp.version()
        elif option_errors:
            print option_errors
        else:
            if options['command']:
                import ccreg_create
                import ccreg_sender
                epp_doc, xml_error = ccreg_create.main(options)
                if xml_error:
                    print xml_error
                else:
                    if len(epp_doc):
                        ccreg_sender.send_docs(options['bar'], ((1,epp_doc),))
                    else:
                        print 'Internal error: epp_doc, xml_error = ccreg_create.main(options[command])'
            elif options['qt']:
                from guiqt.main import main
                main([],options['lang'])
            else:
                import ccreg_console
                ccreg_console.main(options)
