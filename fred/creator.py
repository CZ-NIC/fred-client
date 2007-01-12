#!/usr/bin/env python
# -*- coding: utf8 -*-
# Example: echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py
"""Creator is one of the top modules what deals Fred client system. It can be used
for create EPP XML document without sending anything to the server. 

Script receive text from standart input and returns XML text on the standard output.
If any error occurs it is outputed in XML format for better process of the next XML
parsers.

Srcipt waiting for EPP commands one command on the one line.
"""
import sys, re
from cgi import escape as escape_html
from __init__ import ClientSession, check_python_version
from session_transfer import php_string
from translate import options, option_args, encoding

epp = None

def run_creation(options):
    global epp
    if epp is None:
        epp = ClientSession()
        epp.load_config()
        epp.set_auto_connect(0) # set OFF auto connection
    command_name, epp_doc, stop = epp.create_eppdoc(options['command'])
    errors = epp.fetch_errors()
    if not epp_doc and not errors:
        errors = '%s %s'%(_T('Unknown command'),command_name.encode(encoding))
    str_error = ''
    if errors:
        if type(command_name) == unicode: command_name = command_name.encode(encoding)
        if type(errors) == unicode: errors = errors.encode(encoding)
        if options['output'] == 'html':
            str_error = '<div class="fred_errors">\n<strong>%s errors:</strong>\n<pre>\n%s</pre><div>'%(command_name,escape_html(errors))
        elif options['output'] == 'php':
            str_error = '<?php\n$fred_error_create_name = %s;\n$fred_error_create_value = %s;\n%s\n?>'%(php_string(command_name),php_string(errors),epp.get_empty_php_code())
        else:
            # default 'text'
            str_error = "%s: %s"%(_T('ERROR'),errors)
    return epp_doc, str_error

def display(epp_doc, str_error):
    if str_error:
        print str_error
    else:
        print epp_doc
  
def main():
    msg_invalid = check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if not sys.stdin.isatty():
            for cmd in re.split('[\r\n]+',sys.stdin.read()):
                command = cmd.strip()
                if command:
                    options['command'] = command
                    epp_doc, str_error = run_creation(options)
                    display(epp_doc, str_error)
        elif len(sys.argv) > 1:
            command = ' '.join(option_args)
            if options['range']:
                epp_doc = str_error = ''
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
                        epp_doc, str_error = run_creation(options)
                        display(epp_doc, str_error)
                else:
                    print "<?xml encoding='utf-8'?><errors>Invalid range pattern: %s</errors>"%options['range']
            else:
                options['command'] = command
                epp_doc, str_error = run_creation(options)
                display(epp_doc, str_error)
        else:
            print '%s: %s command params\n\n%s\n\n%s%s\n\n  %s\n'%(_T('Usage'), 'fred_create.py',
                _T('Create EPP XML document from command line parameters.'),
                _T('EXAMPLES'),
                """
./fred_create.py info_domain nic.cz
./fred_create.py info_contact cid:regid
echo -en "check_domain nic.cz\\ninfo_domain nic.cz" | ./fred_create.py
cat file-with-commands.txt | ./fred_create.py
""",
                _T('See README for more information.')
                )

if __name__ == '__main__':
    main()
