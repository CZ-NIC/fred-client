#!/usr/bin/env python
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
"""
This module collect funcktion for access object to the configuration file.
It is used by session manager in session_base.py.
"""
import os, sys, re
import ConfigParser
import pdb
from translate import get_valid_lang

def load_config_from_file(filename, verbose):
    'Load config file from specifiend filename only.'
    config = ConfigParser.SafeConfigParser()
    error = ''
    names = []
    missing = []
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

def get_etc_config_name(name=''):
    'Returns shared folder depends on OS type.'
    if os.name == 'posix':
        # this line will be changed during setup process
        glob_conf = 'conf/fred-client.conf'
        if glob_conf == '':
            glob_conf = os.path.join('/etc/fred', name.strip('.'))
    else:
        # ALLUSERSPROFILE = C:\Documents and Settings\All Users
        glob_conf = os.path.join(os.path.expandvars('$ALLUSERSPROFILE'),name)
    return glob_conf

def load_default_config(config_name, verbose):
    'Load default config. First try home than etc.'
    config = ConfigParser.SafeConfigParser()
    # first try home
    missing = []

    # ugly HACK: part of next code line is changed during ``setup.py bdist_simple'':
    #   This part -> ``os.path.join(os.path.expanduser('~'),config_name)''
    # it is important to update regexp in InstallLib.update_session_config method (setup.py)
    # to proper new value if mentioned part is changed (otherwise bdist simple package
    # will load wrong (if any) configuration file). See setup.py file for some further information
    error, names, not_found = load_config(config, os.path.join(os.path.expanduser('~'),config_name), verbose)
    if not_found:
        missing.extend(not_found)
        # than try etc
        error, names, not_found = load_config(config, get_etc_config_name(config_name), verbose)
        if not_found and sys.platform[:3] == 'win':
            # In Windows try also open filename.ini
            match = re.match(r'\.?([^\.]+)',config_name)
            if match:
                config_name = '%s.ini'%match.group(1)
                error, names, not_found = load_config(config, get_etc_config_name(config_name), verbose)
            if not_found:
                error, names, not_found = load_config(config, os.path.join(sys.prefix, 'etc', 'fred', config_name), verbose)
                
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
        if missing:
            # always display error message when explicit config missing
            errors.extend(missing)
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
    #conf_name = len(sys.argv) > 1 and sys.argv[1] or '/home/zdenek/.fred_client.conf'
    if len(sys.argv) > 1 and sys.argv[1]:
        conf_name = sys.argv[1]
    else:
        conf_name = ''
    #config, config_names, errors, missing = main(conf_name,{'config':'pokus'}, 3, 0)
    config, config_names, errors, missing = main(conf_name,{}, 3, 0)
    print "config",config
    print "config_names",config_names
    print "errors",errors
    print 'missing',missing
