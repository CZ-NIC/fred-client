import os, re
from distutils.command.install import install as _install
from distutils.debug import DEBUG

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

class install(_install):
    user_options = _install.user_options
    user_options.append(('sysconfdir=', None, 
        'System configuration directory [PREFIX/etc]'))
    user_options.append(('libexecdir=', None,
        'Program executables [PREFIX/libexec]'))
    user_options.append(('localstatedir=', None,
        'Modifiable single machine data [PREFIX/var]'))
    user_options.append(('libdir=', None,
        'object code libraries [PREFIX/lib]'))
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
    user_options.append(('dont-record', None,
        'do not record list of installed files'))

    boolean_options = _install.boolean_options
    boolean_options.append('preservepath')
    boolean_options.append('dont_record')

    def __init__(self, *attrs):
        _install.__init__(self, *attrs)

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
        Return actual root only in case if the process is not in creation of the package
        '''
        return ((self.is_bdist_mode or self.preservepath) and [''] or 
                [type(self.root) is not None and self.root or ''])[0]

    def initialize_options(self):
        _install.initialize_options(self)
        self.sysconfdir = None
        self.localstatedir = None
        self.libexecdir = None
        self.libdir = None
        self.datarootdir = None
        self.datadir = None
        self.infodir = None
        self.mandir = None
        self.docdir = None
        self.preservepath = None
        self.dont_record = None

    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        if not self.prefix:
            # prefix is empty - set it to the default value
            self.prefix = os.path.join('/', 'usr', 'local')
        if not self.sysconfdir:
            self.sysconfdir = os.path.join(self.prefix, 'etc')
        if not self.localstatedir:
            self.localstatedir = os.path.join(self.prefix, 'var')
        if not self.libexecdir:
            self.libexecdir = os.path.join(self.prefix, 'libexec')
        if not self.libdir:
            self.libdir = os.path.join(self.prefix, 'lib')
        if not self.datarootdir:
            self.datarootdir = os.path.join(self.prefix, 'share')
        if not self.datadir:
            self.datadir = self.datarootdir
        if not self.infodir:
            self.infodir = os.path.join(self.datarootdir, 'info')
        if not self.mandir:
            self.mandir = os.path.join(self.datarootdir, 'man')
        if not self.docdir:
            self.docdir = os.path.join(self.datarootdir, 'doc', self.distribution.metadata.name)
        print self.docdir

        _install.finalize_options(self)
        if not self.record and not self.dont_record:
            self.record = 'install.log'

    def run(self):
        _install.run(self)
