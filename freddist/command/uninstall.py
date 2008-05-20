"""
freddist.command.uninstall

Implements the freddist 'uninstall' command.
"""

# There is no uninstall command in classic distutils, so we added it.
# Command class is pretty simple. Uninstall expect `install.log' file in
# directory from which is executed. Or you can use `--record' option to set
# log file.
# Uninstall normally removed only directories installed explicitly with
# install_data script. Directories which must be created due to install files
# are not normally removed as long as `--remove-empty-dirs' options is used.

# TODO uninstall command do not work when installing to different root
# (param --root is used)

import os
from distutils.core import Command

class uninstall(Command):

    description = "uninstall everything"

    user_options = []
    user_options.append(('record=', 'r',
        'filename from which read list of installed files [install.log]'))
    user_options.append(('dont-remove-log', 'l',
        'do not remove log file'))
    user_options.append(('remove-empty-dirs', 'd',
        'uninstall also remove empty dirs'))

    boolean_options = ['dont_remove_log', 'remove_empty_dirs']

    def rmtree(self, tree):
        try:
            os.rmdir(tree)
            if self.rmtree(os.path.dirname(tree)) == 1:
                return 1
        except:
            return 1
        return 0

    def initialize_options(self):
        self.record = None
        self.dont_remove_log = None
        self.remove_empty_dirs = None

    def finalize_options(self):
        if not self.record:
            self.record = 'install.log'

    def run(self):
        print "uninstall"
        try:
            body = open(self.record).readlines()
        except:
            print "can not open file %s" % self.record
            exit()
        
        for line in body:
            line = line.strip()
            if os.path.isfile(line):
                os.unlink(line)
                print line, "removed"
            elif os.path.isdir(line):
                os.rmdir(line)
                print line, "directory removed"

            if self.remove_empty_dirs:
                self.rmtree(os.path.dirname(line))
        if not self.dont_remove_log:
            os.unlink(self.record)
            print self.record, "removed"

