import os
from distutils.dir_util import remove_tree
from distutils import log
from distutils.command.clean import clean as _clean

class clean(_clean):
    user_options = []
    user_options.append(('build-dir=', None,
        'base build directory [./build]'))
    user_options.append(('dist-dir=', None,
        'base dist directory [./dist]'))
    user_options.append(('all', 'a',
        'remove all output, this includes build, sdist and bdist outputs \
                (if exists)'))

    boolean_options = ['all']
    
    def initialize_options(self):
        self.build_dir = None
        self.dist_dir = None
        self.all = None
        self.build_base = None
        self.build_lib = None
        self.build_temp = None
        self.build_scripts = None
        self.bdist_base = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'),
                                   ('build_scripts', 'build_scripts'),
                                   ('build_temp', 'build_temp'))
        self.set_undefined_options('bdist',
                                   ('bdist_base', 'bdist_base'))
        if not self.build_dir:
            self.build_dir = 'build'
        if not self.dist_dir:
            self.dist_dir = 'dist'

        self.srcdir = self.distribution.srcdir

    def run(self):
        # remove ./build directory and all under it
        if os.path.exists(self.build_dir):
            remove_tree(self.build_dir, self.verbose, self.dry_run)
            log.info("%s removed" % self.build_dir)

        if self.all == 1:
            if os.path.exists(self.dist_dir):
                remove_tree(self.dist_dir, self.verbose, self.dry_run)
                log.info("%s removed" % self.dist_dir)

        # remove srcdir/MANIFEST file
        if os.path.exists(os.path.join(self.srcdir, 'MANIFEST')):
            os.remove(os.path.join(self.srcdir, 'MANIFEST'))
            log.info("%s removed" % os.path.join(self.srcdir, 'MANIFEST'))
