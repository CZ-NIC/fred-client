#!/usr/bin/env python
#
# Copyright (C) 2006-2018  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

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
    sys.path.insert(0, '../') # for running from this folder
    sys.path.insert(0, './') # for running from upper folder
    try:
        import fred.creator
    except ImportError, msg:
        print "ImportError:", msg
        print 'For runnig this application you need install fred module. See help.'
        sys.exit(0)
fred.creator.main()
