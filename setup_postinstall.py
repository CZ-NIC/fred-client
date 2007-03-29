#!/usr/bin/env python
"""
Create shortcuts on the Windows desktop agter installation.

Distribution create:

$ python setup.py bdist_wininst --install-script=setup_postinstall.py

"""

import sys, os
import distutils.sysconfig
from fred.internal_variables import fred_version

if sys.platform[:3] != 'win':
    sys.exit()

# Name of the main console script
script_name = 'fred_client.py'
help_name = 'fred_howto_cs.html'

# BAT file is created to prevent closing the console after the script has been finished.
bat_file  = 'fred_client.bat'
readme_name = 'README_CS.html'

# Folder with icon
path_fred_doc = 'cznic_fred_docs'

# Name of the configuration sample
path_conf_sample = 'fred_client.conf.sample'




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
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, path_conf_sample), 
    'Fred Client configuration sample', 
    os.path.join(desktopDir, '%s.lnk'%path_conf_sample),
    '', '', 
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'configure.ico'))

# Shortcut to the README on the desktop
create_shortcut(
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, readme_name), 
    'Fred README',
    os.path.join(desktopDir, '%s.lnk'%readme_name), 
    '', '', 
    os.path.join(distutils.sysconfig.PREFIX, path_fred_doc, 'help.ico'))
