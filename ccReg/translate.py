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
import __builtin__
import os, sys
import getopt
import gettext
import ConfigParser

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

def get_etc_config_name(name):
    'Returns shared folder depends on OS type.'
    if os.name == 'posix':
        glob_conf = '/etc/%s'%config_name
    else:
        # ALLUSERSPROFILE = C:\Documents and Settings\All Users
        glob_conf = os.path.join(os.path.expandvars('$ALLUSERSPROFILE'),config_name)
    return glob_conf
    
def load_config(config_name):
    "Load config file and init internal variables. Returns 0 if fatal error occured."
    config = ConfigParser.SafeConfigParser()
    error = ''
    names = []
    ## modul_conf = os.path.join(os.path.split(__file__)[0],config_name)
    glob_conf = get_etc_config_name(config_name)
    if os.path.isfile(glob_conf):
        try:
            # If you wand use mode config, uncomment next line and comment line after it.
            # names = config.read([modul_conf, glob_conf, os.path.join(os.path.expanduser('~'),config_name)])
            names = config.read(glob_conf)
        except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError), msg:
            error = 'ConfigParserError: %s'%str(msg)
            config = None
    else:
        error = "Configuration file '%s' missing."%glob_conf
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
    available_langs = langs.keys()
    if key in available_langs:
        error = ''
    else:
        error = "Unsupported language in %s: '%s'. Available values are: (%s)"%(msg, key,', '.join(available_langs))
        key = default_lang
    return key, error

def install_translation(lang):
    'Install language translation'
    gt = langs[lang]
    gt.install()
    __builtin__.__dict__['_T'] = gt.gettext
    __builtin__.__dict__['_TP'] = gt.ngettext

#---------------------------
# INIT options:
#---------------------------
config_name = '.ccreg_client.conf' # .ccReg.conf
domain = 'ccreg_client' # gettext translate domain
langs = {'en': 0, 'cs': 1} # 0 - no translate, 1 - make translation
default_lang = 'en'
optcols = (
    '? help',
    'b bar',   # Used by ccreg_sender for display bar instead of common output. Suitable for huge command sets.
    'c:cert',
    'd:command',
    'e:range', # Used by ccreg_create for generate range of documents.
    'f:config',
    'g:log',   # save log in unittest.
    'h:host',
    'k:privkey',
    'l:lang',
    'o:output',
    'p:port',
    'q qt',    # run in Qt
    's:session',
    't timer', # for debug only; display duration of processes
    'u:user',
    'v:verbose',
    'w:password',
    'V version',
    'x no_validate',
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
tpath = os.path.join(os.path.split(__file__)[0],'lang')
for key,value in langs.items():
    if value:
        try:
            langs[key] = gettext.translation(domain,tpath,(key,), codeset=encoding)
        except IOError, (no,msg):
            langs[key] = gettext.NullTranslations() # no translation
            print 'Translate IOError',no,msg,'\nMISSING:','%s/%s/LC_MESSAGES/%s.mo'%(tpath,options['lang'],domain)
    else:
        langs[key] = gettext.NullTranslations() # no translation

# Install language support
install_translation(options['lang'])

option_errors = '\n'.join(errors)
warning = '\n'.join(warnings)
