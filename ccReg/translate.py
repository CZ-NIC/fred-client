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
optcols = ('s:session','l:lang','g:log','h:host','u:user','p:password',
        'v:verbose','c:command','r colors','? help')
options = {}
for key in optcols:
    options[key[2:]] = ''
#--------------------------
# Defaults:
#--------------------------
options['lang'] = 'en'
option_args = ()
option_errors = ''

if len(sys.argv) > 1:
    try:
        opts, option_args = getopt.getopt(sys.argv[1:], 
            ''.join(map(lambda s:s[:2].strip(),optcols)),
            map(lambda s:('%s','%s=')[s[1]==':']%s[2:],optcols))
    except getopt.GetoptError, msg:
        option_errors = "Options error: %s"%msg
    else:
        if len(option_args):
            option_errors = '%s: (%s)'%('Unknown options',', '.join(option_args))
        for k,v in opts:
            for key in optcols:
                keys = ('-%s'%key[0], '--%s'%key[2:])
                if k in keys:
                    if v=='': v='yes'
                    options[key[2:]] = v
else:
    # set language from environ
    code = os.environ.get('LANG') # 'cs_CZ.UTF-8'
    if type(code) is str and len(code) > 1:
        arg = code[:2]
        if arg in ('en','cs'): options['lang'] = arg
#--------------------------
        
encoding, warning = find_valid_encoding()
if options['lang'] == 'en':
    _T = gettext.gettext
else:
    try:
        _T = gettext.translation('cz_nic_ccreg_client',os.path.join(os.path.split(__file__)[0],'lang'),('cs',), codeset=encoding).gettext
    except IOError, (no,msg):
        print 'Translate IOError',no,msg
        _T = gettext.gettext
