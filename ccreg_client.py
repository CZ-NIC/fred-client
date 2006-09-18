#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import ccReg
from ccReg.translate import _T, options, option_errors

if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print "%s %s" % (msg_invalid)
    else:
        if options['help']:
            print '%s: %s [OPTIONS...]\n\n%s\n\n%s\n  %s\n\n  %s\n'%(_T('Usage'), 'ccreg_client',
_T('Client for communication with EPP server.'),
_T("""Connection options:
  -?, --help       show this help and exit
  -V, --version    Display program version information

  -l LANGUAGE, --lang=LANGUAGE
                   set user interface language
  -r, --colors     turn on colored output
  -v LEVEL, --verbose=LEVEL
                   set verbose level
                   1 - normal operation
                   2 - print more details
                   3 - print more details and display XML sources
  -h HOSTNAME, --host=HOSTNAME
                   ccReg server to connect 
  -u USERNAME, --user=USERNAME
                   authenticate to server as user
  -p PASSWORD, --password=PASSWORD
                   authenticate to server with password
  -s SESSION, --session=SESSION
                   read session name  used for connect to the EPP server
                   session values are read from config file
  -c CONFIG, --config=CONFIG
                   load config from filename"""),
   _T("""-d COMMAND, --command=COMMAND
                   send command to server and exit"""),
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
