#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import fred
from fred.translate import options, option_errors

if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if msg_invalid:
        print "%s %s" % (msg_invalid)
    else:
        from fred_console import help_option
        if options['help']:
            print '%s: %s [OPTIONS...]\n%s%s\n%s\n\n%s\n'%(_T('Usage'), 'fred_console',
            help_option,
   _T("""  -d COMMAND, --command=COMMAND
                   Send command to server and exit
  -o OUTPUT_TYPE, --output=OUTPUT_TYPE
                   Display output as text (default), html, php"""),
    '', # GUI disabled
##   _T("""  -q,  --qt
##                   Run client in Qt GUI"""),
            _T('For more information, see README.'))
        elif options['version']:
            epp = fred.ClientSession()
            print epp.version()
        elif option_errors:
            print option_errors
        else:
            if options['command']:
                import fred_create
                import fred_sender
                epp_doc, xml_error = fred_create.main(options)
                if xml_error:
                    print xml_error
                else:
                    if len(epp_doc):
                        fred_sender.send_docs(options['bar'], ((1,epp_doc),))
                    else:
                        print 'Internal error: epp_doc, xml_error = fred_create.main(options[command])'
            elif options['qt']:
                from guiqt.main import main
                main([],options['lang'])
            else:
                import fred_console
                fred_console.main(options)
