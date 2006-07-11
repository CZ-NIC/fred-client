#!/usr/bin/env python
# -*- coding: utf8 -*-
# localization in lang folder.

import os, sys
import gettext

def set(lang=None):
    'Set language version. Default is cs.'
    if lang not in ('en','cs'): lang = 'cs'
    if lang == 'en':
        _T = gettext.gettext
    else:
        encoding = (sys.stdout.encoding,'utf-8')[sys.stdout.encoding == 'US-ASCII']
        try:
            _T = gettext.translation('cz_nic_ccreg_client',os.path.join(os.path.split(__file__)[0],'lang'),('cs',), codeset=encoding).gettext
        except IOError, (no,msg):
            print 'Translate IOError',no,msg
            _T = gettext.gettext
    return _T

_T = set()
