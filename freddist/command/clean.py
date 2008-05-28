import os
from distutils.dir_util import remove_tree
from distutils import log
from distutils.command.clean import clean as _clean

class clean(_clean):
    user_options = []
    user_options.append(('build-dir=', 'b',
        'base build directory [./build]'))
    user_options.append(('dist-dir=', 'd',
        'base dist directory [./dist]'))
    user_options.append(('manifest=', 'm',
        'manifest file [./MANIFEST]'))

    def initialize_options(self):
        self.build_dir = None
        self.dist_dir = None
        self.manifest = None

    def finalize_options(self):
        if not self.build_dir:
            self.build_dir = 'build'
        if not self.dist_dir:
            self.dist_dir = 'dist'
        if not self.manifest:
            self.manifest = 'MANIFEST'

    def run(self):
        # remove ./build directory and all under it
        if os.path.exists(self.build_dir):
            remove_tree(self.build_dir, self.verbose, self.dry_run)
            log.info("%s removed" % self.build_dir)

        if os.path.exists(self.dist_dir):
            remove_tree(self.dist_dir, self.verbose, self.dry_run)
            log.info("%s removed" % self.dist_dir)

        # remove srcdir/MANIFEST file
        if os.path.exists(self.manifest):
            os.remove(self.manifest)
            log.info("%s removed" % self.manifest)
