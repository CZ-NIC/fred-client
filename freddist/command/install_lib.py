import re, os, sys
from distutils.command.install_lib import install_lib as _install_lib
from install_parent import install_parent

class install_lib(_install_lib, install_parent):
    user_options = _install_lib.user_options
    boolean_options = _install_lib.boolean_options

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
    user_options.append(('no-record', None,
        'do not record list of installed files'))
    user_options.append(('no-pycpyo', None,
        'do not create compiled pyc and optimized pyo files'))
    user_options.append(('no-check-deps', None,
        'do not check dependencies'))

    user_options.append(('fgen-setupcfg', None,
        'force generate setup.cfg from template'))
    user_options.append(('no-update-setupcfg', None,
        'do not update setup.cfg file'))
    user_options.append(('no-gen-setupcfg', None,
        'do not generate setup.cfg file'))
    user_options.append(('no-setupcfg', None,
        'do not use setup.cfg file'))
    user_options.append(('setupcfg-template=', None,
        'template file for setup.cfg [setup.cfg.template]'))
    user_options.append(('setupcfg-output=', None,
        'output file with setup configuration [setup.cfg]'))

    boolean_options.append('preservepath')
    boolean_options.append('no_record')
    boolean_options.append('no_pycpyo')
    boolean_options.append('no_check_deps')
    boolean_options.append('fgen_setupcfg')
    boolean_options.append('no_update_setupcfg')
    boolean_options.append('no_gen_setupcfg')
    boolean_options.append('no_setupcfg')


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
        if 'install' in sys.argv:
            self.set_undefined_options('install',
                    ('root',                'root'),
                    ('prefix',              'prefix'),
                    ('record',              'record'),
                    ('bindir',              'bindir'),
                    ('sbindir',             'sbindir'),
                    ('sysconfdir',          'sysconfdir'),
                    ('libexecdir',          'libexecdir'),
                    ('localstatedir',       'localstatedir'),
                    ('libdir',              'libdir'),
                    ('pythondir',           'pythondir'),
                    ('purelibdir',          'purelibdir'),
                    ('datarootdir',         'datarootdir'),
                    ('datadir',             'datadir'),
                    ('infodir',             'infodir'),
                    ('mandir',              'mandir'),
                    ('docdir',              'docdir'),
                    ('localstatedir',       'localstatedir'),
                    ('preservepath',        'preservepath'),
                    ('no_record',           'no_record'),
                    ('no_pycpyo',           'no_pycpyo'),
                    ('no_check_deps',       'no_check_deps'),
                    ('fgen_setupcfg',       'fgen_setupcfg'),
                    ('no_update_setupcfg',  'no_update_setupcfg'),
                    ('no_gen_setupcfg',     'no_gen_setupcfg'),
                    ('no_setupcfg',         'no_setupcfg'),
                    ('setupcfg_template',   'setupcfg_template'),
                    ('setupcfg_output',     'setupcfg_output'))
        else:
            install_parent.finalize_options(self)
        self.set_directories(self.prefix)
        if not self.record and not self.no_record:
            self.record = 'install.log'
        self.srcdir = self.distribution.srcdir
        self.rundir = self.distribution.rundir

    def run(self):
        self.install_dir = self.getDir_nop('purelibdir')
        _install_lib.run(self)
