import os, sys, string
from distutils.debug import DEBUG
from distutils.util import check_environ
from distutils.dist import Distribution as _Distribution
from distutils.dist import DistributionMetadata

try:
    from freddist.command.config import config 
except ImportError:
    from command.config import config

try:
    from freddist.command.build import build 
except ImportError:
    from command.build import build

try:
    from freddist.command.build_scripts import build_scripts
except ImportError:
    from command.build_scripts import build_scripts

try:
    from freddist.command.build_py import build_py
except ImportError:
    from command.build_py import build_py

try:
    from freddist.command.install import install
except ImportError:
    from command.install import install

try:
    from freddist.command.install_data import install_data
except ImportError:
    from command.install_data import install_data

try:
    from freddist.command.install_scripts import install_scripts
except ImportError:
    from command.install_scripts import install_scripts

try:
    from freddist.command.sdist import sdist 
except ImportError:
    from command.sdist import sdist

try:
    from freddist.command.bdist import bdist
except ImportError:
    from command.bdist import bdist

try:
    from freddist.command.bdist_rpm import bdist_rpm
except ImportError:
    from command.bdist_rpm import bdist_rpm

try:
    from freddist.command.clean import clean
except ImportError:
    from command.clean import clean

try:
    from freddist.command.uninstall import uninstall
except ImportError:
    from command.uninstall import uninstall

class Distribution(_Distribution):
    def __init__(self, attrs=None):
        self.srcdir = None
        self.rundir = None
        self.requires = None
        

        self.cmdclass = {}
        _Distribution.__init__(self, attrs)

        if not self.cmdclass.get('config'):
            self.cmdclass['config'] = config
        if not self.cmdclass.get('build'):
            self.cmdclass['build'] = build
        if not self.cmdclass.get('build_scripts'):
            self.cmdclass['build_scripts'] = build_scripts
        if not self.cmdclass.get('build_py'):
            self.cmdclass['build_py'] = build_py
        if not self.cmdclass.get('install'):
            self.cmdclass['install'] = install
        if not self.cmdclass.get('install_data'):
            self.cmdclass['install_data'] = install_data
        if not self.cmdclass.get('install_scripts'):
            self.cmdclass['install_scripts'] = install_scripts
        if not self.cmdclass.get('sdist'):
            self.cmdclass['sdist'] = sdist
        if not self.cmdclass.get('bdist'):
            self.cmdclass['bdist'] = bdist
        if not self.cmdclass.get('bdist_rpm'):
            self.cmdclass['bdist_rpm'] = bdist_rpm
        if not self.cmdclass.get('clean'):
            self.cmdclass['clean'] = clean
        if not self.cmdclass.get('uninstall'):
            self.cmdclass['uninstall'] = uninstall

    def has_srcdir (self):
        return self.srcdir or '.'

    def has_rundir(self):
        return self.rundir or '.'

    def find_config_files (self):
        """Find as many configuration files as should be processed for this
        platform, and return a list of filenames in the order in which they
        should be parsed.  The filenames returned are guaranteed to exist
        (modulo nasty race conditions).

        There are three possible config files: distutils.cfg in the
        Distutils installation directory (ie. where the top-level
        Distutils __inst__.py file lives), a file in the user's home
        directory named .pydistutils.cfg on Unix and pydistutils.cfg
        on Windows/Mac, and setup.cfg in the current directory.
        """
        files = []
        check_environ()

        # Where to look for the system-wide Distutils config file
        sys_dir = os.path.dirname(sys.modules['distutils'].__file__)

        # Look for the system config file
        sys_file = os.path.join(sys_dir, "distutils.cfg")
        if os.path.isfile(sys_file):
            files.append(sys_file)

        # What to call the per-user config file
        if os.name == 'posix':
            user_filename = ".pydistutils.cfg"
        else:
            user_filename = "pydistutils.cfg"

        # And look for the user config file
        if os.environ.has_key('HOME'):
            user_file = os.path.join(os.environ.get('HOME'), user_filename)
            if os.path.isfile(user_file):
                files.append(user_file)

        # All platforms support local setup.cfg
        #FREDDIST added self.srcdir
        local_file = os.path.join(os.curdir, "setup.cfg")#os.path.join(self.srcdir, "setup.cfg")
        if os.path.isfile(local_file):
            files.append(local_file)

        return files
    # find_config_files ()
