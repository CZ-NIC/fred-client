import types, os, re, sys
from distutils import util
from distutils.command.install_data import install_data as _install_data
from install_parent import install_parent

# freddist install_data came with one enhancement. It regards system directories.
# And first simple example. This is part of core.setup function:
#
# 01     setup(name='some_name',
# 02             author='your name',
# 03             #important part goes now
# 04             data_files = [
# 05                 ('SYSCONFDIR/some_name',
# 06                     [
# 07                         'file_no1.conf',
# 08                         'file_no2.conf'
# 09                     ]
# 10                 ),
# 11                 ('DOCDIR',
# 12                     [
# 13                         'document_no1.html'
# 14                     ]
# 15                 ),
# 16                 ('LOCALSTATEDIR/whatever', ),
# 17             ],
# 18             another setup stuff....,
#
# As you can see, in data_files is used some strange `SYSCONFDIR' and `DOCDIR'
# option. These are during install phase replaced by fully expanded directory
# names. For example `file_no1.conf' and `file_no2.conf' will be installed into
# `PREFIX/etc/some_name' directory. And since `PREFIX' is normally `/usr/local'
# then full path to first file will be `/usr/local/etc/some_name/file_no1.conf'.
# All these setting can be overriden by proper options.
# On line 16 is example of creating empty directory.

class install_data(_install_data, install_parent):
    user_options = _install_data.user_options
    boolean_options = _install_data.boolean_options

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
    user_options.append(('replace-path-rel', None,
        'When setup.py replace some path, replace it with relative path'))

    boolean_options.append('preservepath')
    boolean_options.append('no_record')
    boolean_options.append('no_pycpyo')
    boolean_options.append('no_check_deps')
    boolean_options.append('fgen_setupcfg')
    boolean_options.append('no_update_setupcfg')
    boolean_options.append('no_gen_setupcfg')
    boolean_options.append('no_setupcfg')
    boolean_options.append('replace_path_rel')

    # directory patterns which install_data recognize
    dir_patts = ['PREFIX', 'SYSCONFDIR', 'LOCALSTATEDIR', 'LIBEXECDIR',
            'LIBDIR', 'DATAROOTDIR', 'DATADIR', 'MANDIR', 'DOCDIR',
            'INFODIR', 'SBINDIR', 'BINDIR', 'LOCALEDIR', 'PYTHONDIR',
            'PURELIBDIR', 'APPDIR', 'SRCDIR']

    def __init__(self, *attrs):
        self.compile = 1
        self.optimize = 1
        _install_data.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def replaceSpecialDir(self, dir):
        """
        Method purpose is to replace `special directory' pattern passed to
        freddist.core.setup function in its data_files list. For example
        data_files could look like this:
            data_files = [('SYSCONFDIR/some_dir', ['file_no1', 'file_no2'])]
        In this example `file_no1' and `file_no2' will be copied into
        `SYSCONFDIR/some_dir' directory where `SYSCONFDIR' will be replaced
        with actual setting (by default it is `prefix/etc' where prefix is
        `/usr/local'. So whole path will be `/usr/local/etc/some_dir').
        Valid patterns are emplaced in self.`dir_patts' variable.
        """
        for str in self.dir_patts:
            s = re.search("^"+str, dir)
            if s:
                if self.is_wininst:
                    self.is_wininst = False
                    ret = os.path.join(self.getDir_noprefix(str.lower()), dir[s.end():].lstrip(os.path.sep))
                    if str == 'SYSCONFDIR':
                        ret = "+" + ret
                    self.is_wininst = True
                    return ret
                dir = self.getDir(str.lower()) + dir[s.end():]
        return dir

    def initialize_options(self):
        _install_data.initialize_options(self)
        install_parent.initialize_options(self)
        self.prefix = None
        self.root = None
        self.record = None

    def finalize_options(self):
        _install_data.finalize_options(self)
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
                    ('setupcfg_output',     'setupcfg_output'),
                    ('replace_path_rel',    'replace_path_rel'))
        else:
            install_parent.finalize_options(self)
        self.set_directories(self.prefix)
        if not self.record and not self.no_record:
            self.record = 'install.log'
        self.srcdir = self.distribution.srcdir
        self.rundir = self.distribution.rundir

    def run(self):
        #FREDDIST line added
        self.mkpath(self.install_dir)

        if self.no_pycpyo:
            self.compile = 0
            self.optimize = 0

        for f in self.data_files:
            if type(f) is types.StringType:
                #FREDDIST next line changed
                if not os.path.exists(f):
                    f = util.convert_path(os.path.join(self.srcdir, f))
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing right in '%s'" %
                              (f, self.install_dir))
                # it's a simple file, so copy it
                (out, _) = self.copy_file(f, self.install_dir)
                self.outfiles.append(out)

                if out.endswith('.py') and self.compile == 1:
                    os.system('python -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating compiled %s" % out + 'c'
                if out.endswith('.py') and self.optimize == 1:
                    os.system('python -O -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating optimized %s" % out + 'o'
            else:
                # it's a tuple with path to install to and a list of files
                dir = util.convert_path(self.replaceSpecialDir(f[0]))
                if not os.path.isabs(dir):
                    if self.is_wininst and dir[0] == '+':
                        dir = os.path.join(self.install_dir[:self.install_dir.rfind(os.path.sep)], dir[1:])
                    else:
                        dir = os.path.join(self.install_dir, dir)
                elif self.root:
                    dir = util.change_root(self.root, dir)
                self.mkpath(dir)

                if len(f) == 1 or f[1] == []:
                    # If there are no files listed, the user must be
                    # trying to create an empty directory, so add the
                    # directory to the list of output files.
                    self.outfiles.append(dir)
                    print "creating directory %s" % dir
                else:
                    # Copy files, adding them to the list of output files.
                    for data in f[1]:
                        #FREDDIST next line changed
                        if not os.path.exists(data):
                            data = util.convert_path(
                                    os.path.join(self.srcdir, data))
                        (out, _) = self.copy_file(data, dir)
                        self.outfiles.append(out)
                        if 'bin' in out.split(os.path.sep) or\
                                'sbin' in out.split(os.path.sep) or\
                                'init.d' in out.split(os.path.sep):
                            os.chmod(out, 0755)

                        if out.endswith('.py') and self.compile == 1:
                            os.system('python -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'c')
                            print "creating compiled %s" % out + 'c'

                        if out.endswith('.py') and self.optimize == 1:
                            os.system('python -O -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'o')
                            print "creating optimized %s" % out + 'o'

