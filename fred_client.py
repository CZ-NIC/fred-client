#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This is main script handling all functions of this client.
Here it's deside what type of application will be running.
Default is console. Next choice is running as a batch - 
this is suitable using is in some shell scripts or for manage
web pages (php, html). It also run it in GUI mode GUI with
Qt environment.

Script check version of python at the beginning. This code is
in module fred. Next it use options from command line parsed
in module fred.translate during import.

MODES:
For console mode is used module fred.console.
For batch mode is used modules fred.creator and fred.sender.
For GUI moduel is used module guiqt.
"""
import sys
import fred
from fred.translate import options, option_errors

if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if len(msg_invalid):
        print "%s %s" % (msg_invalid)
    else:
        from fred.console import help_option
        if options['help']:
            print '%s: %s [OPTIONS...]\n%s%s\n%s\n\n%s\n'%(_T('Usage'), 'fred_console',
            help_option,
   _T("""  -d COMMAND, --command=COMMAND
                   Send command to server and exit
  -o OUTPUT_TYPE, --output=OUTPUT_TYPE
                   Display output as text (default), html, php"""),
   _T("""  -q,  --qt
                   Run client in Qt4 GUI"""),
            _T('For more information, see README.'))
        elif options['version']:
            epp = fred.ClientSession()
            print epp.version()
        elif option_errors:
            print option_errors
        else:
            if options['command']:
                import fred.creator
                import fred.sender
                epp_doc, xml_error = fred.creator.run_creation(options)
                if xml_error:
                    print xml_error
                else:
                    if len(epp_doc):
                        fred.sender.send_docs(options['bar'], ((1,epp_doc),))
                    else:
                        print 'Internal error: epp_doc, xml_error = fred_create.main(options[command])'
            elif options['qt']:
                from guiqt4.main import main
                main([],options['lang'])
            else:
                import fred.console
                fred.console.main(options)
