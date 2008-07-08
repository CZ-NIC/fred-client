"""
Parent class for all install* classes
"""

import re, os, sys
from distutils.cmd import Command

class install_parent(Command):
    user_options = []
    boolean_options = []

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

    dirs = ['prefix', 'bindir', 'sbindir', 'sysconfdir', 'libexecdir',
            'localstatedir', 'libdir', 'pythondir', 'purelibdir', 'datarootdir',
            'datadir', 'infodir', 'mandir', 'docdir', 'localedir']
    # dirs = ['prefix', 'libexecdir', 'localstatedir', 'libdir', 'datarootdir',
            # 'datadir', 'infodir', 'mandir', 'docdir', 'bindir', 'sbindir',
            # 'localedir', 'pythondir', 'purelibdir']

    def __init__(self, *attrs):
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
        self.bindir         = None
        self.sbindir        = None
        self.sysconfdir     = None
        self.libexecdir     = None
        self.localstatedir  = None
        self.libdir         = None
        self.pythondir      = None
        self.purelibdir     = None
        self.datarootdir    = None
        self.datadir        = None
        self.infodir        = None
        self.mandir         = None
        self.docdir         = None
        self.localedir      = None

        self.preservepath   = None
        self.no_record      = None
        self.no_pycpyo      = None
        self.no_check_deps  = None

        self.fgen_setupcfg      = None
        self.no_update_setupcfg = None
        self.no_gen_setupcfg    = None
        self.no_setupcfg        = None
        self.setupcfg_template  = None
        self.setupcfg_output    = None

    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        if not self.prefix:
            # prefix is empty - set it to the default value
            self.prefix = os.path.join('/', 'usr', 'local')
        if not self.bindir:
            self.bindir = os.path.join(self.prefix, 'bin')
        if not self.sbindir:
            self.sbindir = os.path.join(self.prefix, 'sbin')
        if not self.sysconfdir:
            self.sysconfdir = os.path.join(self.prefix, 'etc')
        if not self.libexecdir:
            self.libexecdir = os.path.join(self.prefix, 'libexec')
        if not self.localstatedir:
            self.localstatedir = os.path.join(self.prefix, 'var')
        if not self.libdir:
            self.libdir = os.path.join(self.prefix, 'lib')
        if not self.pythondir:
            self.pythondir = os.path.join(self.libdir, 'python%d.%d' % 
                    (sys.version_info[0], sys.version_info[1]))
        if not self.purelibdir:
            self.purelibdir = os.path.join(self.pythondir, 'site-packages')
        if not self.datarootdir:
            self.datarootdir = os.path.join(self.prefix, 'share')
        if not self.datadir:
            self.datadir = self.datarootdir
        if not self.infodir:
            self.infodir = os.path.join(self.datarootdir, 'info')
        if not self.mandir:
            self.mandir = os.path.join(self.datarootdir, 'man')
        if not self.docdir:
            self.docdir = os.path.join(
                    self.datarootdir, 'doc', self.distribution.metadata.name)
        if not self.localedir:
            self.localedir = os.path.join(self.datarootdir, 'locale')
        if not self.setupcfg_template:
            self.setupcfg_template = 'setup.cfg.template'
        if not self.setupcfg_output:
            self.setupcfg_output = 'setup.cfg'

    def set_directories(self, prefix=None):
        if prefix:
            self.prefix = prefix

        if not self.bindir:
            self.bindir = os.path.join(self.prefix, 'bin')
        if not self.sbindir:
            self.sbindir = os.path.join(self.prefix, 'sbin')
        if not self.sysconfdir:
            self.sysconfdir = os.path.join(self.prefix, 'etc')
        if not self.libexecdir:
            self.libexecdir = os.path.join(self.prefix, 'libexec')
        if not self.localstatedir:
            self.localstatedir = os.path.join(self.prefix, 'var')
        if not self.libdir:
            self.libdir = os.path.join(self.prefix, 'lib')
        if not self.pythondir:
            self.pythondir = os.path.join(self.libdir, 'python%d.%d' % 
                    (sys.version_info[0], sys.version_info[1]))
        if not self.purelibdir:
            self.purelibdir = os.path.join(self.pythondir, 'site-packages')
        if not self.datarootdir:
            self.datarootdir = os.path.join(self.prefix, 'share')
        if not self.datadir:
            self.datadir = self.datarootdir
        if not self.infodir:
            self.infodir = os.path.join(self.datarootdir, 'info')
        if not self.mandir:
            self.mandir = os.path.join(self.datarootdir, 'man')
        if not self.docdir:
            self.docdir = os.path.join(
                    self.datarootdir, 'doc', self.distribution.metadata.name)
        if not self.localedir:
            self.localedir = os.path.join(self.datarootdir, 'locale')



    def replace_pattern(self, fileOpen, fileSave=None, values = []):
        """
        Replace given patterns with new values, for example in config files.
        Patterns and new values can contain regular expressions.
        Structure of values parameter looks like:
        [(pattern_1, new_val_1), (pattern_2, new_val_2), ...]
        If targer directory does not exists, method will create it.
        """
        if not fileSave:
            fileSave = fileOpen
        body = open(fileOpen).read()

        for value in values:
            body = re.sub(value[0], value[1], body)
        try:
            if not os.path.isdir(os.path.dirname(fileSave)):
                os.makedirs(os.path.dirname(fileSave))
        except Exception:
            pass
        open(fileSave, 'w').write(body)

    def getDir(self, directory):
        """
        Method returs actual value of some system directory and if needed it
        prepend self.root path (depend on preservepath option).
        """
        try:
            dir = getattr(self, directory.lower())
        except AttributeError:
            return ''
        if self.get_actual_root():
            return os.path.join(self.root, dir.lstrip(os.path.sep))
        else:
            return dir

    def getDir_nop(self, directory):
        """
        Variant of `getDir' method. Only difference is that `getDir' return
        path sometimes without self.root (if preserve path is set). `getDir_nop'
        return path always with root (but only if root is set). This method is
        used almost only inside freddist (but can be used everywhere as well).
        (rem: nop means NoPreservepath ;)
        """
        try:
            dir = getattr(self, directory.lower())
        except AttributeError:
            return ''
        if self.root:
            return os.path.join(self.root, dir.lstrip(os.path.sep))
        else:
            return dir

    def normalize_record(self):
        """
        Method normalize content of record file, prepend slashes (/) if needed
        and remove double slashes (//) from paths.
        """
        print "normalize_record"
        if self.record:
            oldRecord = open(self.record).readlines()
            newRecord = []
            for line in oldRecord:
                if not line.startswith(os.path.sep):
                    line = os.path.sep + line
                newRecord.append(os.path.normpath(line))
            open(self.record, 'w').writelines(newRecord)

    def update_record(self):
        """
        If needed prepend self.root to each path
        """
        print "update_record"
        if self.get_actual_root() and self.record:
            record = open(self.record).readlines()
            for i in range(len(record)):
                if os.path.normpath(record[i]).find(
                        os.path.normpath(self.root)) == -1:
                    record[i] = os.path.join(
                        self.root, record[i].lstrip(os.path.sep))
            open(self.record, 'w').writelines(record)

    def add_to_record(self, files):
        """
        This method take as parameter list of files, which are added
        into record file (if exists)
        """
        print "add_to_record"
        #proceed only if i record
        if self.record:
            record = open(self.record).readlines()
            for file in files:
                # i must ensure, that every file from files has new line
                # character at end
                file = file.strip() + '\n'
                if not file in record:
                    # file is not in record, so add it
                    record.append(file)
            open(self.record, 'w').writelines(record)
            print "record file has been updated"
