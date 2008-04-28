import os
from distutils.command.build_scripts import build_scripts as _build_scripts

class build_scripts(_build_scripts):
    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        _build_scripts.finalize_options(self)

    def run(self):
        for i in range(len(self.scripts)):
            self.scripts[i] = os.path.join(self.srcdir, self.scripts[i])
        _build_scripts.run(self)
