import re, os, sys
from distutils.command.install_lib import install_lib as _install_lib
from install_parent import install_parent

class install_lib(_install_lib, install_parent):
    user_options = _install_lib.user_options
    user_options.append(('root=', None,
        'install everything relative to this alternate root directory'))
    user_options.append(('prefix=', None,
        'installation prefix'))
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
        'do not check dependencies'))

    boolean_options = _install_lib.boolean_options
    boolean_options.append('preservepath')
    boolean_options.append('dont_record')
    boolean_options.append('dont_create_pycpyo')
    boolean_options.append('no_check_deps')

    # user_options.extend(install_parent.user_options)
    # boolean_options = _install_lib.boolean_options
    # boolean_options.extend(install_parent.boolean_options)

    def __init__(self, *attrs):
        _install_lib.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def initialize_options(self):
        self.root = None
        self.prefix = None
        self.record = None
        _install_lib.initialize_options(self)
        install_parent.initialize_options(self)

    def finalize_options(self):
        _install_lib.finalize_options(self)
        #install_parent.finalize_options(self)
        if 'install' in sys.argv:
            self.set_undefined_options('install',
                    ('prefix', 'prefix'),
                    ('sysconfdir', 'sysconfdir'),
                    ('localstatedir', 'localstatedir'),
                    ('libexecdir', 'libexecdir'),
                    ('preservepath', 'preservepath'),
                    ('root', 'root'),
                    ('libdir', 'libdir'),
                    ('datarootdir', 'datarootdir'),
                    ('datadir', 'datadir'),
                    ('mandir', 'mandir'),
                    ('docdir', 'docdir'),
                    ('bindir', 'bindir'),
                    ('sbindir', 'sbindir'),
                    ('localedir', 'localedir'),
                    ('pythondir', 'pythondir'),
                    ('purelibdir', 'purelibdir'),
                    ('infodir', 'infodir'),
                    ('dont_create_pycpyo', 'dont_create_pycpyo'),
                    ('dont_record', 'dont_record'),
                    ('no_check_deps', 'no_check_deps'),
                    ('record', 'record'))
        else:
            install_parent.finalize_options(self)
        self.set_directories(self.prefix)
        if not self.record and not self.dont_record:
            self.record = 'install.log'

    def run(self):
        self.install_dir = self.getDir_nop('purelibdir')
        _install_lib.run(self)
