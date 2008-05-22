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
    user_options.append(('preservepath', None, 
        'Preserve path(s) in configuration file(s).'))
    user_options.append(('localedir=', None,
        'locale-dependent data [DATAROOTDIR/locale]'))

    boolean_options = _install_lib.boolean_options
    boolean_options.append('preservepath')

    def __init__(self, *attrs):
        _install_lib.__init__(self, *attrs)

        self.is_bdist_mode = None

        for dist in attrs:
            for name in dist.commands:
                if re.match('bdist', name): #'bdist' or 'bdist_rpm'
                    self.is_bdist_mode = 1 #it is bdist mode - creating a package
                    break
            if self.is_bdist_mode:
                break
    def get_actual_root(self):
        '''
        Return actual root only in case if the process is not in creation of
        the package
        '''
        return ((self.is_bdist_mode or self.preservepath) and [''] or 
                [type(self.root) is not None and self.root or ''])[0]

    def initialize_options(self):
        _install_lib.initialize_options(self)
        self.prefix = None
        self.sysconfdir = None
        self.localstatedir = None
        self.libexecdir = None
        self.preservepath = None
        self.root = None
        self.libdir = None
        self.datarootdir = None
        self.datadir = None
        self.infodir = None
        self.mandir = None
        self.docdir = None
        self.bindir = None
        self.sbindir = None
        self.localedir = None
        self.pythondir = None
        self.purelibdir = None

    def finalize_options(self):
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
                ('infodir', 'infodir'))

        self.srcdir = self.distribution.srcdir
        _install_lib.finalize_options(self)

    def run(self):
        _install_lib.run(self)
