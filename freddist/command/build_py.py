import string, os
from distutils.command.build_py import build_py as _build_py

class build_py(_build_py):
    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        _build_py.finalize_options(self)

    def get_package_dir(self, package):
        """
        Return the directory, relative to the top of the source
        distribution, where package 'package' should be found
        (at least according to the 'package_dir' option, if any).
        Standart distutils build_py does not support scrdir option.
        So Build_py class implements this funkcionality. This code
        is from http://lists.mysql.com/ndb-connectors/617 
        """
        path = string.split(package, '.')

        if not self.package_dir:
            if path:
                #FREDDIST line changed
                return os.path.join(self.srcdir, apply(os.path.join, path))
            else:
                #FREDDIST line changed
                return self.srcdir
        else:
            tail = []
            while path:
                try:
                    pdir = self.package_dir[string.join(path, '.')]
                except KeyError:
                    tail.insert(0, path[-1])
                    del path[-1]
                else:
                    tail.insert(0, pdir)
                    #FREDIST line changed
                    return os.path.join(self.srcdir, apply(os.path.join, tail))
            else:
                # Oops, got all the way through 'path' without finding a
                # match in package_dir.  If package_dir defines a directory
                # for the root (nameless) package, then fallback on it;
                # otherwise, we might as well have not consulted
                # package_dir at all, as we just use the directory implied
                # by 'tail' (which should be the same as the original value
                # of 'path' at this point).
                pdir = self.package_dir.get('')
                if pdir is not None:
                    tail.insert(0, pdir)

                if tail:
                    #FREDDIST line changed
                    return os.path.join(self.srcdir, apply(os.path.join, tail))
                else:
                    #FREDDIST line changed
                    return self.srcdir
    #get_package_dir()

    def run(self):
        _build_py.run(self)

