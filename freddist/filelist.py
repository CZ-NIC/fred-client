"""distutils.filelist

Provides the FileList class, used for poking about the filesystem
and building lists of files.
"""

# This module should be kept compatible with Python 2.1.

__revision__ = "$Id: filelist.py 37828 2004-11-10 22:23:15Z loewis $"

import os, string, re
import fnmatch
from types import *
from glob import glob
from distutils.util import convert_path
from distutils.errors import DistutilsTemplateError, DistutilsInternalError
from distutils import log
from distutils.filelist import FileList as _FileList
from distutils.filelist import findall
from distutils.filelist import glob_to_re
from distutils.filelist import translate_pattern

class FileList(_FileList):
    def __init__(self,
                 warn=None,
                 debug_print=None,
                 srcdir=None):
        # ignore argument to FileList, but keep them for backwards
        # compatibility

        self.allfiles = None
        self.files = []
        self.srcdir = srcdir

    # -- Filtering/selection methods -----------------------------------

    def include_pattern (self, pattern,
                         anchor=1, prefix=None, is_regex=0):
        if prefix:
            prefix = os.path.join(self.srcdir, prefix)
        return _FileList.include_pattern(self, pattern, anchor, prefix, is_regex)

