import os, re, sys
from install_parent import install_parent
from distutils.command.install import install as _install
from distutils.debug import DEBUG
from distutils.util import convert_path, subst_vars, change_root

# Difference between freddist.install and distutils.install class isn't wide.
# Only new options were added. Most of them are output directory related.
# These are used so far by freddist.install_data class.
# Others are `--preservepath' and `--dont-record'. Preservepath command is used
# to cut root part of installation path (of course if `--root' is used) when
# this installation path is e.g. used in config files.
#
# Default distutils bahaviour is not to create file with installed files list.
# Freddist change it. Default is to create that file (due to uninstall class)
# and `--dont-record' option prevent this.

class install(_install, install_parent):
    user_options = _install.user_options
    user_options.append(('bindir=', None,
        'user executables [PREFIX/bin]'))
    user_options.append(('sbindir=', None,
        'system admin executables [PREFIX/sbin]'))
    user_options.append(('sysconfdir=', None, 
        'System configuration directory [PREFIX/etc]'))
    user_options.append(('libexecdir=', None,
        'Program executables [PREFIX/libexec]'))
    user_options.append(('localstatedir=', None,
        'Modifiable single machine data [PREFIX/var]'))
    user_options.append(('libdir=', None,
        'object code libraries [PREFIX/lib]'))
    user_options.append(('pythondir=', None,
        'python directory [LIBDIR/python%d.%d]' %
        (sys.version_info[0], sys.version_info[1])))
    user_options.append(('purelibdir=', None,
        'python pure libraries [LIBDIR/python%d.%d/site-packages]' %
        (sys.version_info[0], sys.version_info[1])))
    user_options.append(('datarootdir=', None,
        'read only architecture-independent data root [PREFIX/share]'))
    user_options.append(('datadir=', None,
        'read only architecture-independent data [DATAROOTDIR]'))
    user_options.append(('infodir=', None,
        'info documentation [DATAROOTDIR/info]'))
    user_options.append(('mandir=', None,
        'man documentation [DATAROOTDIR/man]'))
    user_options.append(('docdir=', None,
        'documentation root [DATAROOTDIR/doc/NAME]'))
    user_options.append(('localedir=', None,
        'locale-dependent data [DATAROOTDIR/locale]'))
    user_options.append(('preservepath', None, 
        'Preserve path(s) in configuration file(s).'))
    user_options.append(('dont-record', None,
        'do not record list of installed files'))
    user_options.append(('dont-create-pycpyo', None,
        'do not create compiled pyc and optimized pyo files'))
    user_options.append(('no-check-deps', None,
        'do not check dependencie'))

    boolean_options = _install.boolean_options
    boolean_options.append('preservepath')
    boolean_options.append('dont_record')
    boolean_options.append('dont_create_pycpyo')
    boolean_options.append('no_check_deps')

    # user_options.extend(install_parent.user_options)
# 
    # boolean_options = _install.boolean_options
    # boolean_options.extend(install_parent.boolean_options)

    def __init__(self, *attrs):
        _install.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def initialize_options(self):
        _install.initialize_options(self)
        install_parent.initialize_options(self)


    def finalize_options(self):
        _install.finalize_options(self)
        install_parent.finalize_options(self)
        #self.set_directories()
        if not self.record and not self.dont_record:
            self.record = 'install.log'

    def run(self):
        _install.run(self)
        self.normalize_record()
