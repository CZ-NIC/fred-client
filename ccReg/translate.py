#!/usr/bin/env python
# -*- coding: utf8 -*-
# localization in lang folder.
import os, sys
import getopt
import gettext

def find_valid_encoding():
    """Find valid encoding in system, where sys.stdout.encodig doesnt be right value.
    Returns valid-charset and warning.
    """
    valid_charset,warning = None,None
    for charset in (sys.stdout.encoding, 'utf-8', 'cp852'):
        try:
            ltext = u'žščřďťňě'.encode(charset)
        except (UnicodeEncodeError, TypeError), msg:
            pass
        else:
            valid_charset = charset
            break
    if not valid_charset:
        warning = 'WARNING! Your terminal does not support UTF-8 encoding. Unicode will be shown on the raw format.'
        #On the POSIX systems set locale to LANG=cs_CZ.UTF-8.
        valid_charset = sys.stdout.encoding
    #print 'Actual unicode encoding is %s.'%valid_charset
    return valid_charset,warning

#--------------------------
# INIT options:
#--------------------------
session_name = None
session_lang = 'cs'
option_errors = ''
option_help = False
option_log_name = ''
option_args = ()
if len(sys.argv) > 1:
    try:
        opts, option_args = getopt.getopt(sys.argv[1:], 's:l:g:h', ('session=', 'lang=','log=','help'))
    except getopt.GetoptError, msg:
        option_errors = "Options error: %s"%msg
    else:
        if len(option_args):
            option_errors = '%s: (%s)'%('Unknown options',', '.join(option_args))
        for k,v in opts:
            if k in ('-s','--session'): session_name = v
            if k in ('-l','--lang'): session_lang = v
            if k in ('-h','--help'): option_help = True
            if k in ('-g','--log'): option_log_name = v
else:
    # set language from environ
    code = os.environ.get('LANG') # 'cs_CZ.UTF-8'
    if type(code) is str and len(code) > 1:
        arg = code[:2]
        if arg in ('en','cs'): session_lang = arg
#--------------------------
        
encoding, warning = find_valid_encoding()
if session_lang == 'en':
    _T = gettext.gettext
else:
    try:
        _T = gettext.translation('cz_nic_ccreg_client',os.path.join(os.path.split(__file__)[0],'lang'),('cs',), codeset=encoding).gettext
    except IOError, (no,msg):
        print 'Translate IOError',no,msg
        _T = gettext.gettext
