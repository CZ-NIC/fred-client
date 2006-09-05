#!/usr/bin/env python
# -*- coding: utf8 -*-
# localization in lang folder.
# OUTPUT OBJECTS:
# ------------------------------------
# config        - ConfigParser object
# options       - dict with options values
# option_errors - (str) error occured during parse config and options
# config_error  - error occured during parse config
# warning       - message about solved problems
# ------------------------------------
import os, sys
import getopt
import gettext
import ConfigParser

def find_valid_encoding():
    """Find valid encoding in system, where sys.stdout.encodig doesnt be right value.
    Returns valid-charset and warning.
    """
    valid_charset,warning = ('',)*2
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
    return valid_charset,warning

def load_config_from_file(filename):
    'Load config file from specifiend filename only.'
    config = None
    error = ''
    names = []
    if os.path.isfile(filename):
        try:
            config = ConfigParser.SafeConfigParser()
            config.read(filename)
        except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError), msg:
            error = 'ConfigParserError: %s'%str(msg)
            config = None
        else:
            names.append(filename)
    else:
        error = "Configuration file '%s' missing."%filename
    return config, error, names

def load_config(config_name):
    "Load config file and init internal variables. Returns 0 if fatal error occured."
    config = ConfigParser.SafeConfigParser()
    error = ''
    modul_conf = os.path.join(os.path.split(__file__)[0],config_name)
    if os.name == 'posix':
        glob_conf = '/etc/%s'%config_name
    else:
        # ALLUSERSPROFILE = C:\Documents and Settings\All Users
        glob_conf = os.path.join(os.path.expandvars('$ALLUSERSPROFILE'),config_name)
    try:
        names = config.read([glob_conf, modul_conf, os.path.join(os.path.expanduser('~'),config_name)])
    except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError), msg:
        error = 'ConfigParserError: %s'%str(msg)
        config = None
        names = []
    return config, error, names

def get_config_value(config, section, option, omit_errors=0):
    'Get value from config and catch exceptions.'
    value = error = ''
    try:
        value = config.get(section,option)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.InterpolationMissingOptionError), msg:
        if not omit_errors: error = 'ConfigError: %s (%s, %s)'%(msg,section,option)
    return value, error

def get_valid_lang(key, msg):
    if key in available_langs:
        error = ''
    else:
        error = "Unsupported language in %s: '%s'. Available values are: (%s)"%(msg, key,', '.join(available_langs))
        key = default_lang
    return key, error

#---------------------------
# INIT options:
#---------------------------
config_name = '.ccreg_client.conf' # .ccReg.conf
available_langs = ('en','cs')
default_lang = 'en'
optcols = (
    '? help',
    'b bar',
    'c:config',
    'd:command',
    'e:range',
    'g:log',
    'h:host',
    'l:lang',
    'p:password',
    'r colors',
    's:session',
    'u:user',
    'v:verbose',
    'V version',
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
        errors.append("Options error: %s"%msg)
    else:
        if len(option_args):
            errors.append('%s: (%s)'%('Unknown options',', '.join(option_args)))
        for k,v in opts:
            for key in optcols:
                keys = ('-%s'%key[0], '--%s'%key[2:])
                key = key[2:]
                if k in keys:
                    if v=='': v='yes'
                    if key == 'lang':
                        options['lang'], error = get_valid_lang(v,'options')
                        if error: errors.append(error)
                    else:
                        options[key] = v

#---------------------------
# LOAD CONFIG
#---------------------------
if options['config']:
    config, config_error, config_names = load_config_from_file(options['config'])
else:
    config, config_error, config_names = load_config(config_name)
if config and not options['lang']:
    key, error = get_config_value(config, 'session','lang',1)
    if error:
        errors.append(error)
    elif key:
        options['lang'], error = get_valid_lang(key, 'config')
        if error: errors.append(error)


if not len(options['lang']):
    # set language from environ
    code = os.environ.get('LANG') # 'cs_CZ.UTF-8'
    if type(code) is str and len(code) > 1:
        arg = code[:2]
        options['lang'], error = get_valid_lang(arg,'os.environ.LANG')
        if error: warnings.append("%s Set default to: '%s'."%(error, default_lang))
    else:
        options['lang'] = default_lang

#---------------------------
# SET LANGUAGE VERSION
#---------------------------
encoding, w = find_valid_encoding()
if w: warnings.append(w)
if options['lang'] == 'en':
    _T = gettext.gettext
    _TP = gettext.ngettext
else:
    domain = 'cz_nic_ccreg_client'
    tpath = os.path.join(os.path.split(__file__)[0],'lang')
    try:
        gt = gettext.translation(domain,tpath,(options['lang'],), codeset=encoding)
        _T = gt.gettext
        _TP = gt.ngettext
    except IOError, (no,msg):
        print 'Translate IOError',no,msg,'\nMISSING:','%s/%s/LC_MESSAGES/%s.mo'%(tpath,options['lang'],domain)
        _T = gettext.gettext
        _TP = gettext.ngettext

option_errors = '\n'.join(errors)
warning = '\n'.join(warnings)

