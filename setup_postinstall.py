#!/usr/bin/env python
"""
Create shortcuts on the Windows desktop agter installation.

Distribution create:

$ python setup.py bdist_wininst --install-script=setup_postinstall.py

"""

import sys, os, re
import distutils.sysconfig
from fred.internal_variables import fred_version, config_name
from fred.session_config import get_etc_config_name


if sys.platform[:3] != 'win':
    sys.stderr.write('This script is designed only for MS Windows platform.\n')
    sys.exit()

config_root = os.path.join(sys.prefix, r'etc\fred')

path = os.path.join(sys.prefix, 'share','fred-client')
FRED_CLIENT_SSL_PATH = os.path.join(path,'ssl')
FRED_CLIENT_SCHEMAS_FILEMANE = os.path.join(path, r'schemas\all-1.4.xsd')

# Name of the main console script
script_name = 'fred-client'
help_name = 'fred_howto_cs.html'

# BAT file is created to prevent closing the console after the script has been finished.
bat_file  = 'fred-client.bat'
readme_name = 'README_CS.html'

# Folder with icon
path_fred_doc = os.path.join('share','fred-client')


def replace_patterns(body, names):
    for varname in names:
        body = re.sub(varname, os.path.join(config_root, globals().get(varname)), body, 1)
    return body

def update_fred_config():
    'Update fred config after installation'
    filename = os.path.join(config_root, config_name)
    body = open(filename).read()
    body = replace_patterns(body, ('FRED_CLIENT_SSL_PATH', 'FRED_CLIENT_SCHEMAS_FILEMANE'))
    open(filename, 'w').write(body)



# Create paths for join files with desktop
desktopDir = get_special_folder_path('CSIDL_COMMON_DESKTOPDIRECTORY')
bat_file_path = os.path.join(distutils.sysconfig.PREFIX, 'Scripts', bat_file)


# Create BAT file
open(bat_file_path,'w').write('%s -i %s\n'%(os.path.join(distutils.sysconfig.PREFIX,'python.exe'), script_name))


# Shortcut to the BAT with the main console script on the desktop
create_shortcut(
    bat_file_path, 
    'Fred Client Console %s'%fred_version,
    os.path.join(desktopDir, '%s.lnk'%script_name), 
    '', 
    os.path.join(distutils.sysconfig.PREFIX, 'Scripts'),
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'niccz_console.ico'))

# Shortcut to the HOWTO on the desktop
create_shortcut(
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, help_name), 
    'How to configure',
    os.path.join(desktopDir, '%s.lnk'%help_name), 
    '', '', 
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'help.ico'))

    
# Shortcut to the configuration sample on the desktop
create_shortcut(
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, config_name), 
    'Fred Client configuration sample', 
    os.path.join(desktopDir, '%s.lnk'%config_name),
    '', '', 
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'configure.ico'))

# Shortcut to the README on the desktop
create_shortcut(
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, readme_name), 
    'Fred README',
    os.path.join(desktopDir, '%s.lnk'%readme_name), 
    '', '', 
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'help.ico'))


update_fred_config()
