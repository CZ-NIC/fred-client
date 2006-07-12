#!/usr/bin/env python
# -*- coding: utf8 -*-
# localization in lang folder.
import os, sys
import gettext

def find_valid_encoding():
    'Find valid encoding in system, where sys.stdout.encodig doesnt be right value.'
    valid_charset = None
    for charset in (sys.stdout.encoding, 'utf-8', 'cp852'):
        try:
            ltext = u'žščřďťňě'.encode(charset)
        except UnicodeEncodeError, msg:
            pass
        else:
            valid_charset = charset
            break
    if not valid_charset:
        print 'WARNING! Your terminal does not support UTF-8 encoding. Set locale to LANG=cs_CZ.UTF-8.'
        valid_charset = sys.stdout.encoding
    return valid_charset

#
# INIT language versions:
#
lang = 'cs'
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg in ('en','cs'):
            lang = arg
            break

encoding = find_valid_encoding()
if lang == 'en':
    _T = gettext.gettext
else:
    try:
        _T = gettext.translation('cz_nic_ccreg_client',os.path.join(os.path.split(__file__)[0],'lang'),('cs',), codeset=encoding).gettext
    except IOError, (no,msg):
        print 'Translate IOError',no,msg
        _T = gettext.gettext

