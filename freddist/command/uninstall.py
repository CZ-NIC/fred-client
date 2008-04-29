import os
from distutils.core import Command

class uninstall(Command):

    description = "uninstall everything"

    user_options = []
    user_options.append(('record=', None,
        'filename from which read list of installed files [install.log]'))
    user_options.append(('dont-remove-log', None,
        'do not remove log file'))

    boolean_options = ['dont_remove_log']

    def initialize_options(self):
        self.record = None
        self.dont_remove_log = None

    def finalize_options(self):
        if not self.record:
            self.record = 'install.log'

    def run(self):
        print "uninstall"
        body = open(self.record).readlines()
        
        for line in body:
            if os.path.isfile(line.strip()):
                os.unlink(line.strip())
                print line.strip(), "removed"
        if not self.dont_remove_log:
            os.unlink(self.record)
            print self.record, "removed"

