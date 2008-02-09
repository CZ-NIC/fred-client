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

config_root = os.path.join(sys.prefix, 'etc/fred')
config_name_ini = re.sub(r'\.conf', '.ini', config_name)

path = os.path.join(sys.prefix, 'share/fred-client')
FRED_CLIENT_SSL_PATH = os.path.join(path,'ssl')
FRED_CLIENT_SCHEMAS_FILEMANE = os.path.join(path, 'schemas/all-1.4.xsd')

# Name of the main console script
script_name = 'fred-client'
gui_script_name = 'fred-client-qt4.pyw'
help_name = 'fred_howto_cs.html'

# BAT file is created to prevent closing the console after the script has been finished.
bat_file  = 'fred-client.bat'
bat_file_gui = 'fred-client-gui.bat'
readme_name = 'README_EN.txt'

# Folder with icon
path_fred_doc = os.path.join('share', 'fred-client')


def replace_patterns(body, names):
    for varname in names:
        body = re.sub(varname, os.path.join(config_root, globals().get(varname)), body, 1)
    return body

def update_fred_config():
    'Update fred config after installation'
    body = open(os.path.join(config_root, config_name)).read()
    # replace paths
    body = replace_patterns(body, ('FRED_CLIENT_SSL_PATH', 'FRED_CLIENT_SCHEMAS_FILEMANE'))
    # save changes
    open(os.path.join(config_root, config_name_ini), 'w').write(body)




# Create paths for join files with desktop
desktopDir = get_special_folder_path('CSIDL_COMMON_DESKTOPDIRECTORY')
bat_file_path = os.path.join(distutils.sysconfig.PREFIX, 'Scripts', bat_file)
bat_file_gui_path = os.path.join(distutils.sysconfig.PREFIX, 'Scripts', bat_file_gui)


# Create BAT file
open(bat_file_path,'w').write('"%s" -i "%s"\n'%(os.path.join(distutils.sysconfig.PREFIX,'python.exe'), script_name))
open(bat_file_gui_path,'w').write('"%s" "%s"'%(os.path.join(distutils.sysconfig.PREFIX,'pythonw.exe'), os.path.join(sys.prefix, 'Scripts', gui_script_name)))


# convert LF to CR/LF be cause of the MS Windows common end of lines
for name in (readme_name, 'README_CS.txt'):
    pathfile = os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, name)
    body = open(pathfile, 'r').read()
    open(pathfile, 'w').write(body)


# Shortcut to the BAT with the main console script on the desktop
create_shortcut(
    bat_file_path, 
    'Fred Client Console %s'%fred_version,
    os.path.join(desktopDir, '%s.lnk'%script_name), 
    '', 
    os.path.join(distutils.sysconfig.PREFIX, 'Scripts'),
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'niccz_console.ico'))

# Shortcut to the GUI EPP client on the desktop
create_shortcut(
    #'%s %s'%(os.path.join(distutils.sysconfig.PREFIX,'pythonw.exe'), os.path.join(sys.prefix, 'Scripts', gui_script_name)), 
    bat_file_gui_path,
    'Fred Client GUI %s'%fred_version,
    os.path.join(desktopDir, '%s.lnk'%gui_script_name), 
    '', 
    os.path.join(distutils.sysconfig.PREFIX, 'Scripts'),
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'niccz_gui.ico'))
    
## Shortcut to the HOWTO on the desktop
#create_shortcut(
#    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, help_name), 
#    'How to configure',
#    os.path.join(desktopDir, '%s.lnk'%help_name), 
#    '', '', 
#    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'help.ico'))

    
# Shortcut to the configuration file on the desktop
create_shortcut(
    os.path.join(sys.prefix, 'etc', 'fred', config_name_ini), 
    'Fred Client configuration file', 
    os.path.join(desktopDir, '%s.lnk'%config_name_ini),
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
