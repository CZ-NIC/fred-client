#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Send any file (EPP XML) to the EPP server.
"""
import sys, os, re, time
import fred
from fred.session_receiver import FredError
from fred.session_transfer import BEGIN, END
from fred.translate import options, option_errors, option_args

def __auto_login__(epp, verbose):
    'Do login'
    try:
        # username a password musí být v config
        dansw = epp.api_command('login',epp.get_default_params_from_config('login'))
        ok = 1
    except FredError, msg:
        ok = 0
        dansw={}
    if dansw.get('code',0) != 1000:
        epp.append_error(fred.session_base.get_ltext(dansw.get('reason',_T('Login failed'))))
    epp.display()
    return ok

def split_docs(docset):
    docs = []
    xmltag = re.compile('\s*<\?xml', re.S)
    eppend = re.compile('(</epp>)', re.S)
    chops = re.split('(<\?xml)', docset)
    limit = len(chops)
    n=0
    while n < limit:
        if xmltag.match(chops[n]) and n+1 < limit:
            chunk = '%s%s'%(chops[n],chops[n+1])
            n+=1
            parts = eppend.split(chunk)
            if len(parts)>1:
                docs.append((1,'%s%s'%(parts[0],parts[1]))) # body + last tag
                rest = len(parts) > 2 and parts[2] or ''
            else:
                rest = _T('Invalid EPP XML document. Last tag missing.')
            mess = rest.strip()
            if mess: docs.append((0,mess))
        else:
            if chops[n]: docs.append((0,chops[n]))
        n+=1
    return docs


def send_docs(display_bar, docs=[]):
    names = ()
    #-------------------------------------------------
    # Inicializace klienta
    #-------------------------------------------------
    epp = fred.ClientSession()
    if not epp.load_config(): return
    
    if len(options['verbose']):
        verbose = epp.set_verbose(options['verbose'])
    else:
        verbose = '1'

    #-------------------------------------------------
    # Apped docs from argv params
    #-------------------------------------------------
    for filepath in option_args:
        if os.path.isfile(filepath):
            docs.extend(split_docs(open(filepath).read()))
        else:
            docs.append((0,'File not found: %s'%filepath))
    #-------------------------------------------------
    # For every loaded document
    #-------------------------------------------------
    if display_bar:
        verbose = epp.set_verbose(0)
        sart_at = time.time()
        bar = None
        bar_pos = 0
        max = len(docs)
        bar_step = (100.0/max)*0.01
        bar_header = '%s: %d'%(_T('Send files'),max)
    epp.print_tag(BEGIN) # enclose leak messages into tag (comment)
    for code, xmldoc in docs:
        epp.reset_round()
        if code:
            command_name = epp.grab_command_name_from_xml(xmldoc)
            if len(command_name):
                if command_name in ('hello','login'):
                    epp.connect() # No problem call connect() if we are connected already.
                elif not epp.is_connected():
                    if not __auto_login__(epp, verbose): break
                if command_name == 'logout':
                    verbose = epp.set_verbose(0) # silent logout
                #-------------------------------------------------
                # pokud je zalogováno, tak pošle soubor
                #-------------------------------------------------
                if epp.is_online(command_name) and epp.is_connected():
                    # send document if only we are online
                    epp.send(xmldoc)          # send to server
                    xml_answer = epp.receive()     # receive answer
                    epp.process_answer(xml_answer) # process answer
##                    epp.print_tag(END)
                    epp.print_answer()
##                    epp.print_tag(BEGIN)
            epp.display() # display errors or notes
        else:
            if not display_bar: print "ERRORS:",xmldoc
        if display_bar:
            if bar is None: bar = fred.terminal_controler.ProgressBar(fred.session_base.colored_output,bar_header)
            bar.clear()
            bar.update(bar_pos, _T('sending...'))
            bar_pos += bar_step
    epp.print_tag(END) # end of enclosing leak messages
    if display_bar:
        # print final 100%
        note = "Ran test in %.3f sec"%(time.time() - sart_at)
        bar.clear()
        bar.update(1.0, note)

    #-------------------------------------------------
    # END of transmition - automatic logout
    #-------------------------------------------------
    if epp.is_connected():
        epp.set_verbose(0) # Very important! If is not set, it can overwrite outputed data.
        try:
            epp.api_command('logout') # automatický logout
        except FredError, msg:
            pass # print 'ERROR:',msg
        #epp.print_answer()

if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if msg_invalid:
        print msg_invalid
    else:
        if not sys.stdin.isatty():
            send_docs(options['bar'], split_docs(sys.stdin.read())) # commands from pipe
        else:
            if not options['help'] and len(sys.argv) > 1:
                send_docs(options['bar']) # commands from argv
            else:
                from fred_console import help_option
                print '%s: %s [OPTIONS] [filenames]\n\n%s\n%s\n%s\n%s:\n%s\n\n%s\n'%(_T('Usage'), 'fred_sender.py',
                _T('Module for sending files to the EPP server.'),
                help_option,
                _T("""  -o OUTPUT_TYPE, --output=OUTPUT_TYPE
                   Display output as text (default), html, php"""),
                _T('EXAMPLES'),
"""
  ./fred_create.py info_domain nic.cz > cmd1.xml
  ./fred_create.py info_contact reg-id pokus > cmd2.xml
  ./fred_sender.py cmd1.xml cmd2.xml
  ./fred_sender.py -s epp_host -l cs cmd1.xml cmd2.xml
    
  echo -en "check_domain nic.cz\\ninfo_domain nic.cz" | ./fred_create.py | ./fred_sender.py""",
   _T('For more information, see README.'))
