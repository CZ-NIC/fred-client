#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#
# localization in lang folder.
# OUTPUT OBJECTS:
# ------------------------------------
# options       - dict with options values
# option_errors - (str) error occured during parse config and options
# warning       - message about solved problems
# ------------------------------------
import __builtin__
import os, sys, re
import getopt
import gettext
"""
This module provide functions for language versions. This is used by all
moduels in the fred system.
This module is called as a first module in the application.

Next it provides parsing command line options and hold results for 
further display.
"""

def find_valid_encoding():
    """Find valid encoding in system, where sys.stdout.encodig doesnt be right value.
    Returns valid-charset and warning.
    """
    valid_charset,warning = ('',)*2
    for charset in (getattr(sys.stdout,'encoding','utf-8'), 'utf-8', 'cp852'):
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
    return valid_charset,warning

def get_valid_lang(code, type_of_value):
    available_langs = langs.keys()
    if code in available_langs:
        error = ''
    else:
        error = "Unsupported language code: '%s' in %s. Available codes are: %s."%(code, type_of_value, ', '.join(available_langs))
        code = default_lang
    return code, error

def install_translation(lang):
    'Install language translation'
    gt = langs[lang]
    gt.install()
    __builtin__.__dict__['_T'] = gt.gettext
    __builtin__.__dict__['_TP'] = gt.ngettext
    __builtin__.__dict__['_TU'] = gt.ugettext  # used in GUI
    __builtin__.__dict__['_TPU'] = gt.ungettext  # used in GUI

#---------------------------
# INIT options:
#---------------------------
app_name = 'FredClient'
##config_name = '.fred_client.conf'
domain = 'fred_client' # gettext translate domain
langs = {'en': 0, 'cs': 1} # 0 - no translate, 1 - make translation
default_lang = 'en'
optcols = (
    '? help',
    'b bar',      # Used by fred_sender for display bar instead of common output. Suitable for huge command sets.
    'c:cert',
    'd:command',  # used by creator
    'e:range',    # Used by fred_create for generate range of documents.
    'f:config',   # define your own config file
    'g:log',      # save log in unittest.
    'h:host',
    'i:versions',   # schmea versions "contact:1.0,nsset:1.1,domain:1.1"
    'k:privkey',
    'l:lang',
    'n nologin',  # turn off automatic login process after start up
    'o:output',
    'p:port',
    'q qt',       # run in Qt
    'r:cltrid', # define clTrID
    's:session',
    #'t timer',   # for debug only; display duration of processes
    'u:user',
    'v:verbose',
    'w:password',
    'V version',
    'x no_validate', # switch off using validation by extern program (xmllint)
    )
options = {}
for key in optcols:
    options[key[2:]] = ''
#---------------------------
# Defaults:
#---------------------------
option_args = ()
errors = []
warnings = []

#---------------------------
# PARSE COMMAND LINE OPTIONS
#---------------------------
if len(sys.argv) > 1:
    try:
        opts, option_args = getopt.getopt(sys.argv[1:], 
            ''.join(map(lambda s:s[:2].strip(),optcols)),
            map(lambda s:('%s','%s=')[s[1]==':']%s[2:],optcols))
    except getopt.GetoptError, msg:
        errors.append('%s'%msg)
    else:
        if len(option_args):
            errors.append('%s: (%s)'%('unknown options',', '.join(option_args)))
        for k,v in opts:
            for key in optcols:
                keys = ('-%s'%key[0], '--%s'%key[2:])
                key = key[2:]
                if k in keys:
                    if v=='': v='yes'
                    if key == 'lang':
                        options['lang'], error = get_valid_lang(v,'options')
                        if error:
                            errors.append(error)
                        else:
                            # need for overwrite value from config file:
                            options['lang_option'] = options['lang']
                    else:
                        options[key] = v

if not len(options['lang']):
    # set language from environ
    code = os.environ.get('LANG') # 'cs_CZ.UTF-8'
    if type(code) is str and len(code) > 1:
        arg = code[:2].lower() # Windows returns 'CS'
        options['lang_environ'], error = get_valid_lang(arg,'os.environ.LANG')
        if error: warnings.append("%s Set default to: '%s'."%(error, default_lang))
        options['lang'] = options['lang_environ']
    else:
        options['lang'] = default_lang

#---------------------------
# SET LANGUAGE VERSION
#---------------------------
encoding, w = find_valid_encoding()
if w: warnings.append(w)
tpath = os.path.join(os.path.split(__file__)[0],'lang')
for key,value in langs.items():
    if value:
        try:
            langs[key] = gettext.translation(domain,tpath,(key,), codeset=encoding)
        except TypeError, msg:
            print 'This program requires Python 2.4 or higher.\nYour version is',sys.version
            sys.exit(1)
        except IOError, (no,msg):
            langs[key] = gettext.NullTranslations() # no translation
            print 'Translate IOError',no,msg,'\nMISSING:','%s/%s/LC_MESSAGES/%s.mo'%(tpath,options.get('lang','???'),domain)
    else:
        langs[key] = gettext.NullTranslations() # no translation

# Install language support
install_translation(options['lang'])

match = re.search('(\w+)(\.py.?)?$',sys.argv[0])
if match:
    script_name = match.group(1)
elif len(sys.argv[0]):
    script_name = sys.argv[0]
else:
    script_name = 'fred_module'

if errors:
    #errors[0] = '%s%s'%(errors[0][0].upper(),errors[0][1:]) # First letter to uppercase
    option_errors = _T("""%s
Usage: %s [OPTIONS...]
Try '%s --help' for more information.""")%('\n'.join(errors),script_name,script_name)
else:
    option_errors = ''
warning = '\n'.join(warnings)

if __name__ == '__main__':
    print 'option_errors:',option_errors # errors
    print 'warning:',warning # warnings
    print '-'*60
    print 'option_args:',option_args
    print 'options:'
    for k,v in options.items():
        if not v: continue
        print k.ljust(20),v

