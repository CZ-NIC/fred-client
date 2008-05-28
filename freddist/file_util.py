"""
freddist.file_util
Utility function for operating on files
"""

import os, sys, fnmatch
from distutils.file_util import *

# by default exclude hidden files/directories
EXCLUDE_PATTERN = ['.*']
# and include all other
INCLUDE_PATTERN = ['*']

def curdir(path):
    """Return directory where setup.py file is situated."""
    return os.path.join(os.path.dirname(sys.argv[0]), path)

def fit_pattern(filename, excludePattern):
    """Return True if filename fit `excludePattern', otherwise False"""
    for patt in excludePattern:
        if fnmatch.fnmatch(filename, patt):
            return True
    return False

def all_files_in(dst_directory, directory, excludePattern=None,
        includePattern=None, recursive=True):
    """
    Returns couples (directory, directory/file) to all files in directory.
    Files (as well as directories must not fit `excludePattern' mask.
    """
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']
    paths = [] # list of couples (directory, directory/file) for all files

    for filename in os.listdir(curdir(directory)):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)
        if os.path.isfile(curdir(full_path)):
            # exclude first directory in path from dst path (this include
            # really only what is IN directory, not (directory AND files))
            splitted_directory = directory.split(os.path.sep, 1)
            if len(splitted_directory) > 1:
                dst_subdirectory = splitted_directory[1]
            else: # directory is only one directory yet
                dst_subdirectory = ''
            paths.append((os.path.join(dst_directory, dst_subdirectory),
                [full_path]))
        elif os.path.isdir(curdir(full_path)) and recursive:
            paths.extend(all_files_in(dst_directory, full_path, excludePattern,
                includePattern))   
           
    return paths


def all_files_in_2(directory, excludePattern=None, includePattern=None,
        recursive=False, onlyFilenames=False, cutSlashes=0):
    """
    Returns list (for example: ['filename1', 'filename2', ...]) of files in
    directory (directories if recursive). Files must not fit `excludePattern'
    mask. If parameter `onlyFilenames' is False, each record from list contain
    also its source directory (usually something like `directory/filename'),
    otherwise only filename. Exclude pattern is list of wildcard mask, for
    further help see fnmatch module reference.
    If cutSlashes is bigger than zero, then given number of path parts (divided
    by slashes) will be removed from final path. For example if return from
    function is ['home/whatever/foo/foo.c'] (cutSlashes is zero), then when
    cutSlashes is set to 2 return will be ['foo/foo.c']
    """
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']

    paths = []
    for filename in os.listdir(curdir(directory)):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)
        if os.path.isfile(curdir(full_path)):
            if onlyFilenames:
                paths.append(filename)
            else:
                if cutSlashes > 0:
                    paths.append(full_path.split(os.path.sep, cutSlashes)[-1])
                else:
                    paths.append(full_path)
        if os.path.isdir(curdir(full_path)) and recursive:
            paths.extend(all_files_in_2(full_path, excludePattern,
                includePattern, onlyFilenames, recursive, cutSlashes))
    return paths

def all_subpackages_in(package, excludePattern=None, includePattern=None):
    'Returns all subpackages (packages in subdirectories) (recursive)'
    subpackages = []

    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']
    
    for filename in os.listdir(curdir(package)):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(package, filename)
        if os.path.isdir(curdir(full_path)):
            subpackages.append(full_path.replace('/', '.'))
            subpackages.extend(all_subpackages_in(full_path))

    return subpackages

