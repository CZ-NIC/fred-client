#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This module collect funcktion for access object to the configuration file.
It is used by session manager in session_base.py.
"""
import os
import ConfigParser
from translate import get_valid_lang

def load_config_from_file(filename, verbose):
    'Load config file from specifiend filename only.'
    config = ConfigParser.SafeConfigParser()
    error = ''
    names = missing = []
    filename = os.path.expanduser(filename)
    if os.path.isfile(filename):
        try:
            config.read(filename)
        except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError), msg:
            error = 'ConfigParserError: %s'%_T('File contains parsing errors.') + \
                (verbose > 1 and ('\n' + str(msg)) or ' %s'%_T('See details in verbose 2 or higher.'))
        else:
            names.append(filename)
    else:
        missing = ["Configuration file '%s' not found."%filename]
    return config, error, missing, names

def get_etc_config_name(name):
    'Returns shared folder depends on OS type.'
    if os.name == 'posix':
        glob_conf = '/etc/%s'%name
    else:
        # ALLUSERSPROFILE = C:\Documents and Settings\All Users
        glob_conf = os.path.join(os.path.expandvars('$ALLUSERSPROFILE'),name)
    return glob_conf
    
def load_default_config(config_name, verbose):
    'Load default config. First try home than etc.'
    config = ConfigParser.SafeConfigParser()
    # first try home
    missing = []
    error, names, not_found = load_config(config, os.path.join(os.path.expanduser('~'),config_name), verbose)
    if not_found:
        missing.extend(not_found)
        # than try etc
        error, names, not_found = load_config(config, get_etc_config_name(config_name[1:]), verbose)
        if not_found: missing.extend(not_found)
    return config, error, missing, names

def load_config(config, filename, verbose):
    "Load config file and init internal variables. Returns 0 if fatal error occured."
    missing = 1
    error = ''
    names = missing = []
    if os.path.isfile(filename):
        missing = 0
        try:
            # If you wand use mode config, uncomment next line and comment line after it.
            # names = config.read([modul_conf, glob_conf, os.path.join(os.path.expanduser('~'),config_name)])
            names = config.read(filename)
        except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError), msg:
            error = 'ConfigParserError: %s'%_T('File contains parsing errors.') + \
                (verbose > 1 and ('\n' + str(msg)) or ' %s'%_T('See details in verbose 2 or higher.'))
            config = None
    else:
        missing = ["Configuration file '%s' not found."%filename]
    return error, names, missing

def get_config_value(config, section, option, omit_errors=0):
    'Get value from config and catch exceptions.'
    value = error = ''
    try:
        value = config.get(section,option)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.InterpolationMissingOptionError), msg:
        if not omit_errors: error = 'ConfigError: %s (%s, %s)'%(msg,section,option)
    return value, error


#---------------------------
# LOAD CONFIG
#---------------------------
def main(config_name, options, verbose, OMIT_ERROR):
    'Load configuration file'
    errors = []
    if options.has_key('config') and len(options['config']):
        config, config_error, missing, config_names = load_config_from_file(options['config'], verbose)
    else:
        config, config_error, missing, config_names = load_default_config(config_name, verbose)
    if len(config_error): errors.append(config_error)
    if config:
        key, error = get_config_value(config, 'session','lang', OMIT_ERROR)
        if error:
            errors.append(error)
        elif key:
            options['lang'], error = get_valid_lang(key, 'configuration file')
            if error: errors.append(error)
    return config, config_names, errors, missing

if __name__ == '__main__':
    import sys
    conf_name = len(sys.argv) > 1 and sys.argv[1] or '/home/zdenek/.fred_client.conf'
    #config, config_names, errors, missing = main(conf_name,{'config':'pokus'}, 3, 0)
    config, config_names, errors, missing = main(conf_name,{}, 3, 0)
    print "config",config
    print "config_names",config_names
    print "errors",errors
    print 'missing',missing
