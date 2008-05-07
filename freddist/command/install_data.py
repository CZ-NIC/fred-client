import types, os, re
from distutils import util
from distutils.command.install_data import install_data as _install_data

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

class install_data(_install_data):
    user_options = _install_data.user_options
    user_options.append(('prefix=', None,
        'installation prefix'))
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
    dir_patts = ['PREFIX', 'SYSCONFDIR', 'LOCALSTATEDIR', 'LIBEXECDIR',
            'LIBDIR', 'DATAROOTDIR', 'DATADIR', 'MANDIR', 'DOCDIR',
            'INFODIR']

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
            s = re.search(str, dir)
            if s:
                dir = self.__dict__[str.lower()] + dir[s.end():]
        return dir

    def initialize_options(self):
        _install_data.initialize_options(self)
        self.prefix = None
        self.sysconfdir = None
        self.libexecdir = None
        self.localstatedir = None
        self.libdir = None
        self.datarootdir = None
        self.datadir = None
        self.infodir = None
        self.mandir = None
        self.docdir = None

    def finalize_options(self):
        self.set_undefined_options('install',
                ('prefix', 'prefix'),
                ('sysconfdir', 'sysconfdir'),
                ('localstatedir', 'localstatedir'),
                ('libexecdir', 'libexecdir'),
                ('libdir', 'libdir'),
                ('datarootdir', 'datarootdir'),
                ('datadir', 'datadir'),
                ('mandir', 'mandir'),
                ('docdir', 'docdir'),
                ('infodir', 'infodir'))
        self.srcdir = self.distribution.srcdir
        _install_data.finalize_options(self)

    def run(self):
        #FREDDIST line added
        self.mkpath(self.install_dir)
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

                if out.endswith('.py'):
                    os.system('python -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating compiled %s" % out + 'c'
                    os.system('python -O -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating optimized %s" % out + 'o'
            else:
                # it's a tuple with path to install to and a list of files
                dir = util.convert_path(self.replaceSpecialDir(f[0]))
                if not os.path.isabs(dir):
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

                        if out.endswith('.py'):
                            os.system('python -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'c')
                            print "creating compiled %s" % out + 'c'
                            os.system('python -O -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'o')
                            print "creating optimized %s" % out + 'o'
