from distutils.debug import DEBUG
from distutils.command.bdist_wininst import bdist_wininst as _bdist_wininst

import sys, os, string
from types import *
from distutils import log

from distutils.util import get_platform
from distutils.dir_util import create_tree, remove_tree
from distutils.errors import *
from distutils.sysconfig import get_python_version
from distutils.sysconfig import get_python_lib
from install_parent import install_parent

class bdist_wininst(_bdist_wininst, install_parent):
    user_options = _bdist_wininst.user_options
    boolean_options = _bdist_wininst.boolean_options

    user_options.append(('build-extra-opts=', 'b',
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', 'i',
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))
    user_options.append(('no-join-opts', None,
        'do not join options from setup.cfg and command line'))

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
    
    boolean_options.append('dontpreservepath')
    boolean_options.append('no_join_opts')
    boolean_options.append('fgen_setupcfg')
    boolean_options.append('no_update_setupcfg')
    boolean_options.append('no_gen_setupcfg')
    boolean_options.append('no_setupcfg')
    boolean_options.append('setupcfg_template')
    boolean_options.append('setupcfg_output')

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None
        self.dontpreservepath = None
        self.no_join_opts = None

        self.fgen_setupcfg      = None
        self.no_update_setupcfg = None
        self.no_gen_setupcfg    = None
        self.no_setupcfg        = None
        self.setupcfg_template  = None
        self.setupcfg_output    = None
        _bdist_wininst.initialize_options(self)

    def joinsrcdir(self, what):
        """join self.srcdir and what together"""
        if what != None:
            return os.path.join(self.srcdir, what)
        else:
            return None

    def finalize_options(self):
        self.set_undefined_options('bdist',
                ('dontpreservepath', 'dontpreservepath'),
                ('build_extra_opts', 'build_extra_opts'),
                ('install_extra_opts', 'install_extra_opts'),
                ('no_join_opts', 'no_join_opts'),
                ('fgen_setupcfg', 'fgen_setupcfg'),
                ('no_update_setupcfg', 'no_update_setupcfg'),
                ('no_gen_setupcfg', 'no_gen_setupcfg'),
                ('no_setupcfg', 'no_setupcfg'),
                ('setupcfg_template', 'setupcfg_template'),
                ('setupcfg_output', 'setupcfg_output')
                )
        self.srcdir = self.distribution.srcdir
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'wininst')
        if not self.target_version:
            self.target_version = ""
        if not self.skip_build and self.distribution.has_ext_modules():
            short_version = get_python_version()
            if self.target_version and self.target_version != short_version:
                raise DistutilsOptionError, \
                      "target version can only be %s, or the '--skip_build'" \
                      " option must be specified" % (short_version,)
            self.target_version = short_version

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

        if self.install_script:
            for script in self.distribution.scripts:
                if self.install_script == os.path.basename(script):
                    break
            else:
                raise DistutilsOptionError, \
                      "install_script '%s' not found in scripts" % \
                      self.install_script
    # finalize_options()

    def run (self):
        if (sys.platform != "win32" and
            (self.distribution.has_ext_modules() or
             self.distribution.has_c_libraries())):
            raise DistutilsPlatformError \
                  ("distribution contains extensions and/or C libraries; "
                   "must be compiled on a Windows 32 platform")

        if not self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.is_wininst = True
        install.skip_build = self.skip_build
        install.warn_dir = 0


        install_lib = self.reinitialize_command('install_lib')
        # we do not want to include pyc or pyo files
        install_lib.is_wininst = True
        install_lib.compile = 0
        install_lib.optimize = 0

        install_scripts = self.reinitialize_command('install_scripts')
        install_scripts.is_wininst = True
        install_scripts.compile = 0
        install_scripts.optimize = 0

        install_data = self.reinitialize_command('install_data')
        install_data.is_wininst = True
        install_data.compile = 0
        install_data.optimize = 0

        if self.distribution.has_ext_modules():
            # If we are building an installer for a Python version other
            # than the one we are currently running, then we need to ensure
            # our build_lib reflects the other Python version rather than ours.
            # Note that for target_version!=sys.version, we must have skipped the
            # build step, so there is no issue with enforcing the build of this
            # version.
            target_version = self.target_version
            if not target_version:
                assert self.skip_build, "Should have already checked this"
                target_version = sys.version[0:3]
            plat_specifier = ".%s-%s" % (get_platform(), target_version)
            build = self.get_finalized_command('build')
            build.build_lib = os.path.join(build.build_base,
                                           'lib' + plat_specifier)

        # Use a custom scheme for the zip-file, because we have to decide
        # at installation time which scheme to use.
        for key in ('purelib', 'platlib', 'headers', 'scripts', 'data'):
            value = string.upper(key)
            if key == 'headers':
                value = value + '/Include/$dist_name'
            setattr(install,
                    'install_' + key,
                    value)

        log.info("installing to %s", self.bdist_dir)
        install.ensure_finalized()

        # avoid warning of 'install_lib' about installing
        # into a directory not in sys.path
        sys.path.insert(0, os.path.join(self.bdist_dir, 'PURELIB'))

        install.run()

        del sys.path[0]

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        from tempfile import mktemp
        archive_basename = mktemp()
        fullname = self.distribution.get_fullname()
        arcname = self.make_archive(archive_basename, "zip",
                                    root_dir=self.bdist_dir)
        # create an exe containing the zip-file
        self.create_exe(arcname, fullname, self.bitmap)
        if self.distribution.has_ext_modules():
            pyversion = get_python_version()
        else:
            pyversion = 'any'
        self.distribution.dist_files.append(('bdist_wininst', pyversion,
                                             self.get_installer_filename(fullname)))
        # remove the zip-file again
        log.debug("removing temporary file '%s'", arcname)
        os.remove(arcname)

        if not self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    # run()

    def get_exe_bytes (self):
        from distutils.msvccompiler import get_build_version
        # If a target-version other than the current version has been
        # specified, then using the MSVC version from *this* build is no good.
        # Without actually finding and executing the target version and parsing
        # its sys.version, we just hard-code our knowledge of old versions.
        # NOTE: Possible alternative is to allow "--target-version" to
        # specify a Python executable rather than a simple version string.
        # We can then execute this program to obtain any info we need, such
        # as the real sys.version string for the build.
        cur_version = get_python_version()
        if self.target_version and self.target_version != cur_version:
            # If the target version is *later* than us, then we assume they
            # use what we use
            # string compares seem wrong, but are what sysconfig.py itself uses
            if self.target_version > cur_version:
                bv = get_build_version()
            else:
                if self.target_version < "2.4":
                    bv = "6"
                else:
                    bv = "7.1"
        else:
            # for current version - use authoritative check.
            bv = get_build_version()

        # wininst-x.y.exe is in the same directory as this file
        directory = os.path.join(os.path.split(get_python_lib())[0], 'distutils', 'command')
        # we must use a wininst-x.y.exe built with the same C compiler
        # used for python.  XXX What about mingw, borland, and so on?
        filename = os.path.join(directory, "wininst-%s.exe" % bv)
        return open(filename, "rb").read()
# class bdist_wininst
