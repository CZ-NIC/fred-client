#!/usr/bin/env python
# -*- coding: utf8 -*-
# Example: echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./ccreg_create.py
"""Create EPP XML document from command line parameters.
"""
import sys, re
import ccReg
from ccReg.translate import _T, options, option_args, config_error, encoding

epp = None

def main(options):
    global epp
    if epp is None:
        epp = ccReg.ClientSession()
        epp.load_config(options)
        epp.set_auto_connect(0) # set OFF auto connection
    command_name, epp_doc, stop = epp.create_eppdoc(options['command'])
    errors = epp.fetch_errors()
    if not epp_doc and not errors: errors = _T('Unknown command')
    xml_error = ''
    if errors:
        if type(command_name) == unicode: command_name = command_name.encode(encoding)
        if type(errors) == unicode: errors = errors.encode(encoding)
        xml_error = "<?xml encoding='utf-8'?><errors>%s: %s</errors>"%(command_name,errors)
    return epp_doc, xml_error

def display(epp_doc, xml_error):
    if xml_error:
        print xml_error
    else:
        print epp_doc
  
if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if not sys.stdin.isatty():
            for cmd in re.split('[\r\n]+',sys.stdin.read()):
                command = cmd.strip()
                if command:
                    options['command'] = command
                    epp_doc, xml_error = main(options)
                    display(epp_doc, xml_error)
        elif len(sys.argv) > 1:
            command = ' '.join(option_args)
            if options['range']:
                epp_doc = xml_error = ''
                m = re.match('([^\[]+)\[(\d+)(?:\s*,\s*(\d+))?\]',options['range'])
                if m:
                    min = 0
                    anchor = m.group(1)
                    if m.group(3) is None:
                        max = int(m.group(2))
                    else:
                        min = int(m.group(2))
                        max = int(m.group(3))
                    for n in range(min,max):
                        options['command'] = re.sub(anchor,'%s%d'%(anchor,n),command)
                        epp_doc, xml_error = main(options)
                        display(epp_doc, xml_error)
                else:
                    print "<?xml encoding='utf-8'?><errors>Invalid range pattern: %s</errors>"%options['range']
            else:
                epp_doc, xml_error = main(options)
                display(epp_doc, xml_error)
        else:
            print '%s: %s command params\n\n%s\n\n%s%s\n%s\n\n  %s\n'%(_T('Usage'), 'ccreg_create.py',
                _T('Create EPP XML document from command line parameters.'),
                _T('EXAMPLES'),
                """
./ccreg_create.py info_domain nic.cz
./ccreg_create.py info_contact reg-id
echo -en "check_domain nic.cz\\ninfo_domain nic.cz" | ./ccreg_create.py
cat file-with-commands.txt | ./ccreg_create.py
""",
                _T('Eventual errors are return in XML format: <errors>... msg ...</errors>.'),
                _T('For more information, see README.')
                )
