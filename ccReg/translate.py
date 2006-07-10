#!/usr/bin/env python
# -*- coding: utf8 -*-
# localization in lang folder.
import os
import gettext
try:
    t = gettext.translation('cz_nic_ccreg_client',os.path.join(os.path.split(__file__)[0],'lang'))
    _T = t.ugettext
except IOError, (no,msg):
    print 'Translate IOError',no,msg
    _T = gettext.ugettext
