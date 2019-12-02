#!/usr/bin/env python
#
# Copyright (C) 2006-2019  CZ.NIC, z. s. p. o.
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

# Required default to fit missing config/options
"""
Internal variables are used as a default in case if configuration file missing.
It is used by client session Manager in session_base.py module.
"""

#---------------------------------------------------
# Here is defined FRED VERSION:
#---------------------------------------------------
fred_version = '2.12.4'
config_name = 'fred-client.conf'

required_defaults = {'port':700, 'timeout':10.0}
config = """
[connect]
dir = ~
# host = epp-test.ccreg.nic.cz
port = 700
# ssl_key = %(dir)s/epp_privatekey.pem
# ssl_cert = %(dir)s/epp_certificate.pem
timeout = 10.0
# registrant:
# username = regname
# password = regpass
# socket = IPv6     # valid values are: IPv4 and IPv6

[session]
validate = on
schema = all-1.1.xsd
poll_autoack = off
confirm_send_commands = on
# colors = on
# escaped_input = on
# verbose = 2
# If lang is not set, ti used value from os.environ.LANG
# lang = en
# null_value = None   # substitution of NULL value
# auto_login = off    # automatic login after start client (default is ON)
"""
