import os, types, sys
from glob import glob
from distutils import dep_util, log, dir_util
from distutils.text_file import TextFile
from distutils.command.sdist import sdist as _sdist
from distutils.errors import *

sys.path.append('..')
from freddist.filelist import FileList

class sdist(_sdist):
    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        _sdist.finalize_options(self)
        self.template = os.path.join(self.srcdir, self.template)

    def get_file_list (self):
        """Figure out the list of files to include in the source
        distribution, and put it in 'self.filelist'.  This might involve
        reading the manifest template (and writing the manifest), or just
        reading the manifest, or just using the default file set -- it all
        depends on the user's options and the state of the filesystem.
        """

        # If we have a manifest template, see if it's newer than the
        # manifest; if so, we'll regenerate the manifest.
        template_exists = os.path.isfile(self.template)
        if template_exists:
            template_newer = dep_util.newer(self.template, self.manifest)

        # The contents of the manifest file almost certainly depend on the
        # setup script as well as the manifest template -- so if the setup
        # script is newer than the manifest, we'll regenerate the manifest
        # from the template.  (Well, not quite: if we already have a
        # manifest, but there's no template -- which will happen if the
        # developer elects to generate a manifest some other way -- then we
        # can't regenerate the manifest, so we don't.)
        #FREDDIST next command changed
        self.distribution.script_name = os.path.join(
                self.srcdir, self.distribution.script_name)
        self.debug_print("checking if %s newer than %s" %
                         (self.distribution.script_name, self.manifest))
        setup_newer = dep_util.newer(self.distribution.script_name,
                                     self.manifest)

        # cases:
        #   1) no manifest, template exists: generate manifest
        #      (covered by 2a: no manifest == template newer)
        #   2) manifest & template exist:
        #      2a) template or setup script newer than manifest:
        #          regenerate manifest
        #      2b) manifest newer than both:
        #          do nothing (unless --force or --manifest-only)
        #   3) manifest exists, no template:
        #      do nothing (unless --force or --manifest-only)
        #   4) no manifest, no template: generate w/ warning ("defaults only")

        manifest_outofdate = (template_exists and
                              (template_newer or setup_newer))
        force_regen = self.force_manifest or self.manifest_only
        manifest_exists = os.path.isfile(self.manifest)
        neither_exists = (not template_exists and not manifest_exists)

        # Regenerate the manifest if necessary (or if explicitly told to)
        if manifest_outofdate or neither_exists or force_regen:
            if not template_exists:
                self.warn(("manifest template '%s' does not exist " +
                           "(using default file list)") %
                          self.template)
            #FREDDIST changes in next six lines
            self.filelist.findall(self.srcdir)
            if self.srcdir == os.curdir:
                for i in range(len(self.filelist.allfiles)):
                    self.filelist.allfiles[i] = os.path.join(
                            self.srcdir, self.filelist.allfiles[i])

            if self.use_defaults:
                self.add_defaults()

            if template_exists:
                self.read_template()

            if self.prune:
                self.prune_file_list()

            self.filelist.sort()
            self.filelist.remove_duplicates()
            self.write_manifest()

        # Don't regenerate the manifest, just read it in.
        else:
            self.read_manifest()

    # get_file_list ()


    def add_defaults (self):
        """Add all the default files to self.filelist:
          - README or README.txt
          - setup.py
          - test/test*.py
          - all pure Python modules mentioned in setup script
          - all C sources listed as part of extensions or C libraries
            in the setup script (doesn't catch C headers!)
        Warns if (README or README.txt) or setup.py are missing; everything
        else is optional.
        """

        #FREDDIST self.srcdir added
        standards = [(
            os.path.join(self.srcdir, 'README'),
            os.path.join(self.srcdir, 'README.txt')),
            self.distribution.script_name]

        for fn in standards:
            if type(fn) is types.TupleType:
                alts = fn
                got_it = 0
                for fn in alts:
                    if os.path.exists(fn):
                        got_it = 1
                        self.filelist.append(fn)
                        break

                if not got_it:
                    self.warn("standard file not found: should have one of " +
                              string.join(alts, ', '))
            else:
                if os.path.exists(fn):
                    self.filelist.append(fn)
                else:
                    self.warn("standard file '%s' not found" % fn)

        #FREDDIST self.srcdir added
        optional = [
                os.path.join(self.srcdir, 'test/test*.py'),
                os.path.join(self.srcdir, 'setup.cfg')]
        for pattern in optional:
            files = filter(os.path.isfile, glob(pattern))
            if files:
                self.filelist.extend(files)

        if self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            self.filelist.extend(build_py.get_source_files())

        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())

        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.filelist.extend(build_clib.get_source_files())

        if self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            #it is a little bit interesting that other parts has got
            #proper paths (e.g. full paths), only build_scripts
            #hasn't. So we must expand filenames with srcdir
            scripts_sources = build_scripts.get_source_files()
            #FREDDIST self.srcdir added
            for i in range(len(scripts_sources)):
                scripts_sources[i] = os.path.join(
                        self.srcdir, scripts_sources[i])
            self.filelist.extend(scripts_sources)

    # add_defaults ()


    def read_template (self):
        """Read and parse manifest template file named by self.template.

        (usually "MANIFEST.in") The parsing and processing is done by
        'self.filelist', which updates itself accordingly.
        """
        log.info("reading manifest template '%s'", self.template)
        template = TextFile(self.template,
                            strip_comments=1,
                            skip_blanks=1,
                            join_lines=1,
                            lstrip_ws=1,
                            rstrip_ws=1,
                            collapse_join=1)
        while 1:
            line = template.readline()
            if line is None:            # end of file
                break

            chopped = line.split()
            if chopped[0] in ('include', 'exclude', 'global-include',
                    'global-exclude'):
                for i in range(1, len(chopped)):
                    #FREDDIST self.srcdir added
                    chopped[i] = os.path.join(self.srcdir, chopped[i])
                line = ' '.join(chopped)
            elif chopped[0] in ('resursive-include', 'recursive-exclude'):
                #FREDDIST self.srcdir added
                chopped[1] = os.path.join(self.srcdir, chopped[1])
                line = ' '.join(chopped)
            elif chopped[0] in ('graft', 'prune'):
                #FREDDIST self.srcdir added
                chopped[1] = os.path.join(self.srcdir, chopped[1])
                line = ' '.join(chopped)
            try:
                self.filelist.process_template_line(line)
            except DistutilsTemplateError, msg:
                self.warn("%s, line %d: %s" % (template.filename,
                                               template.current_line,
                                               msg))
    # read_template ()

    def make_release_tree (self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        #same as files but with striped full path
        files_wo_path = []
        for file in files:
            #FREDDIST self.srcdir added
            files_wo_path.append(file[len(self.srcdir)+1:])
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files_wo_path, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        if hasattr(os, 'link'):        # can make hard links on this system
            #link = 'hard'
            # XXX do something with this
            link = None
            msg = "making hard links in %s..." % base_dir
        else:                           # nope, have to copy
            link = None
            msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file):
                log.warn("'%s' not a regular file -- skipping" % file)
            else:
                #FREDDIST self.srcdir added
                dest = os.path.join(base_dir, file[len(self.srcdir)+1:])
                self.copy_file(file, dest, link=link)

        #copy setup.cfg into base_dir (because in base_dir is now setup.cfg
        #from srcdir directory
        self.copy_file('setup.cfg', os.path.join(base_dir, 'setup.cfg'))

        self.distribution.metadata.write_pkg_info(base_dir)
    # make_release_tree ()

    def run(self):
        # 'filelist' contains the list of files that will make up the
        # manifest
        self.filelist = FileList(srcdir=self.srcdir)

        # Ensure that all required meta-data is given; warn if not (but
        # don't die, it's not *that* serious!)
        self.check_metadata()

        # Do whatever it takes to get the list of files to process
        # (process the manifest template, read an existing manifest,
        # whatever).  File list is accumulated in 'self.filelist'.
        self.get_file_list()

        # If user just wanted us to regenerate the manifest, stop now.
        if self.manifest_only:
            return

        # Otherwise, go ahead and create the source distribution tarball,
        # or zipfile, or whatever.
        self.make_distribution()
        # _sdist.run(self)
#class Sdist
