import os
from distutils.debug import DEBUG
from distutils.command.bdist_rpm import bdist_rpm as _bdist_rpm

import sys, os, string
from types import *
from distutils.file_util import write_file
from distutils import log

class bdist_rpm(_bdist_rpm):
    user_options = _bdist_rpm.user_options
    user_options.append(('build-extra-opts=', None,
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', None,
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))

    boolean_options = _bdist_rpm.boolean_options
    boolean_options.append('dontpreservepath')

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None
        self.dontpreservepath = None
        _bdist_rpm.initialize_options(self)

    #FREDDIST new method
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
                ('install_extra_opts', 'install_extra_opts'))
        self.srcdir = self.distribution.srcdir
        
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        if self.rpm_base is None:
            if not self.rpm3_mode:
                raise DistutilsOptionError, \
                      "you must specify --rpm-base in RPM 2 mode"
            self.rpm_base = os.path.join(self.bdist_base, "rpm")

        if self.python is None:
            if self.fix_python:
                self.python = sys.executable
            else:
                self.python = "python"
        elif self.fix_python:
            raise DistutilsOptionError, \
                  "--python and --fix-python are mutually exclusive options"

        if os.name != 'posix':
            raise DistutilsPlatformError, \
                  ("don't know how to create RPM "
                   "distributions on platform %s" % os.name)
        if self.binary_only and self.source_only:
            raise DistutilsOptionError, \
                  "cannot supply both '--source-only' and '--binary-only'"

        # don't pass CFLAGS to pure python distributions
        if not self.distribution.has_ext_modules():
            self.use_rpm_opt_flags = 0

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

        #FREDDIST next 9 lines added
        self.prep_script = self.joinsrcdir(self.prep_script) 
        self.build_script = self.joinsrcdir(self.build_script) 
        self.install_script = self.joinsrcdir(self.install_script) 
        self.clean_script = self.joinsrcdir(self.clean_script) 
        self.verify_script = self.joinsrcdir(self.verify_script) 
        self.pre_install = self.joinsrcdir(self.pre_install) 
        self.post_install = self.joinsrcdir(self.post_install) 
        self.pre_uninstall = self.joinsrcdir(self.pre_uninstall) 
        self.post_uninstall = self.joinsrcdir(self.post_uninstall) 

        self.finalize_package_data()

    def run(self):
        _bdist_rpm.run(self)

    def _dist_path(self, path):
        return os.path.join(self.dist_dir, os.path.basename(path))

    def _make_spec_file(self):
        """Generate the text of an RPM spec file and return it as a
        list of strings (one per line).
        """
        # definitions and headers
        spec_file = [
            '%define name ' + self.distribution.get_name(),
            '%define version ' + self.distribution.get_version().replace('-','_'),
            '%define unmangled_version ' + self.distribution.get_version(),
            '%define release ' + self.release.replace('-','_'),
            '',
            'Summary: ' + self.distribution.get_description(),
            ]

        # put locale summaries into spec file
        # XXX not supported for now (hard to put a dictionary
        # in a config file -- arg!)
        #for locale in self.summaries.keys():
        #    spec_file.append('Summary(%s): %s' % (locale,
        #                                          self.summaries[locale]))

        spec_file.extend([
            'Name: %{name}',
            'Version: %{version}',
            'Release: %{release}',])

        # XXX yuck! this filename is available from the "sdist" command,
        # but only after it has run: and we create the spec file before
        # running "sdist", in case of --spec-only.
        if self.use_bzip2:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.bz2')
        else:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.gz')

        spec_file.extend([
            'License: ' + self.distribution.get_license(),
            'Group: ' + self.group,
            'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot',
            'Prefix: %{_prefix}', ])

        if not self.force_arch:
            # noarch if no extension modules
            if not self.distribution.has_ext_modules():
                spec_file.append('BuildArch: noarch')
        else:
            spec_file.append( 'BuildArch: %s' % self.force_arch )

        for field in ('Vendor',
                      'Packager',
                      'Provides',
                      'Requires',
                      'Conflicts',
                      'Obsoletes',
                      ):
            val = getattr(self, string.lower(field))
            if type(val) is ListType:
                spec_file.append('%s: %s' % (field, string.join(val)))
            elif val is not None:
                spec_file.append('%s: %s' % (field, val))


        if self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())

        if self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)

        if self.build_requires:
            spec_file.append('BuildRequires: ' +
                             string.join(self.build_requires))

        if self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))

        if self.no_autoreq:
            spec_file.append('AutoReq: 0')

        spec_file.extend([
            '',
            '%description',
            self.distribution.get_long_description()
            ])

        # put locale descriptions into spec file
        # XXX again, suppressed because config file syntax doesn't
        # easily support this ;-(
        #for locale in self.descriptions.keys():
        #    spec_file.extend([
        #        '',
        #        '%description -l ' + locale,
        #        self.descriptions[locale],
        #        ])

        # rpm scripts
        # figure out default build script
        def_setup_call = "%s %s" % (self.python,os.path.basename(sys.argv[0]))
        def_build = "%s build" % def_setup_call
        if self.use_rpm_opt_flags:
            def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build

        if self.build_extra_opts:
            def_build = def_build + ' ' + self.build_extra_opts.strip()

        if self.install_extra_opts.find('preservepath') == -1:
            self.install_extra_opts = self.install_extra_opts + ' --preservepath'

        # insert contents of files

        # XXX this is kind of misleading: user-supplied options are files
        # that we open and interpolate into the spec file, but the defaults
        # are just text that we drop in as-is.  Hmmm.
        script_options = [
            ('prep', 'prep_script', "%setup -n %{name}-%{unmangled_version}"),
            ('build', 'build_script', def_build),
            ('install', 'install_script',
             ("%s install "
              "-cO2 "
              "--root=$RPM_BUILD_ROOT "
              "--record=INSTALLED_FILES %s") % 
               (def_setup_call, self.install_extra_opts or '')),
            ('clean', 'clean_script', "rm -rf $RPM_BUILD_ROOT"),
            ('verifyscript', 'verify_script', None),
            ('pre', 'pre_install', None),
            ('post', 'post_install', None),
            ('preun', 'pre_uninstall', None),
            ('postun', 'post_uninstall', None),
        ]

        for (rpm_opt, attr, default) in script_options:
            # Insert contents of file referred to, if no file is referred to
            # use 'default' as contents of script
            val = getattr(self, attr)
            if val or default:
                spec_file.extend([
                    '',
                    '%' + rpm_opt,])
                if val:
                    print "read val"
                    spec_file.extend(string.split(open(val, 'r').read(), '\n'))
                else:
                    print "not print var; default:", default
                    spec_file.append(default)


        # files section
        spec_file.extend([
            '',
            '%files -f INSTALLED_FILES',
            '%defattr(-,root,root)',
            ])

        if self.doc_files:
            spec_file.append('%doc ' + string.join(self.doc_files))

        if self.changelog:
            spec_file.extend([
                '',
                '%changelog',])
            spec_file.extend(self.changelog)

        return spec_file

    # _make_spec_file ()

