#!/usr/bin/env python
# -*- coding: utf8 -*-
# Example: echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py
"""
This tool is aimed for using in batch files. It only does
create any XML EPP document or display errors when process failed.
Script accepts commands from the command line or from the pipe.
"""
import sys
try:
    # standard instalation
    import fred.creator
except ImportError:
    # run from actual folder with source codes
    sys.path.insert(0,'../')
    try:
        import fred.creator
    except ImportError, msg:
        print "ImportError:",msg
        print 'For runnig this application you need install fred module. See help.'
        sys.exit(0)
fred.creator.main()
