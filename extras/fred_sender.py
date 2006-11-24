#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This tool sends any file to the EPP server.

Whatever file can be sent but of course EPP server
accept only valid EPP XML documents. So expected
files are XML types. It possible type their names
in command line or forward them throught pipe.

One file can to contain more than one XML document.
Script recognise it and split into chunks. Between
XML parts is possible have got any text. This text
is only shown on the output. It is usualy error message 
from the previous process of the document creation.

Before sending a first command Sender makes login
except the first command is login one. Similary
at the end Sender makes logout.

"""
import sys
try:
    # standard instalation
    import fred.sender
except ImportError:
    # run from actual folder with source codes
    sys.path.insert(0,'../') # for running from this folder
    sys.path.insert(0,'./') # for running from upper folder
    try:
        import fred.sender
    except ImportError, msg:
        print "ImportError:",msg
        print 'For runnig this application you need install fred module. See help.'
        sys.exit(0)
fred.sender.main()
