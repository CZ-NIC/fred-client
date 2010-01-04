#!/usr/bin/env python
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
This tool sends any file to an EPP server.

Whatever file can be sent but of course the EPP server
accepts only valid EPP XML documents. So expected
files are XML types. It is possible to specify their names
on command line or forward them through a pipe.

One file can contain more than one XML document.
Script recognizes it and splits it into chunks. There
might be any text between XML parts. This text
is only shown on the output. It is usualy error message 
from the previous process of the document creation.

Before sending a first command Sender makes login
except the first command is login one. Similary
at the end Sender makes logout.

"""
import sys
try:
    # standard installation
    import fred.sender
except ImportError:
    # run from actual folder with source codes
    sys.path.insert(0,'../') # for running from this folder
    sys.path.insert(0,'./') # for running from upper folder
    try:
        import fred.sender
    except ImportError, msg:
        print "ImportError:",msg
        print 'For running this application you need to install fred module. See help.'
        sys.exit(0)
fred.sender.main()
