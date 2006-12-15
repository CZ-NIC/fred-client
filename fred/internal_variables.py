# -*- coding: utf8 -*-
#!/usr/bin/env python
# Required default to fit missing config/options
"""
Internal variables are used as a default in case if configuration file missing.
It is used by client session Manager in session_base.py module.
"""
required_defaults = {'port':700, 'timeout':10.0}
config = """
[connect]
dir = ~
# host = epp-test.ccreg.nic.cz
port = 700
# ssl_key = %(dir)s/epp_test_ccreg_nic_cz_key.pem
# ssl_cert = %(dir)s/epp_test_ccreg_nic_cz_cert.pem
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
# colors = yes
# verbose = 2
# If lang is not set, ti used value from os.environ.LANG
# lang = en
# null_value = None   # substitution of NULL value
# auto_login = off    # automatic login after start client (default is ON)
"""
