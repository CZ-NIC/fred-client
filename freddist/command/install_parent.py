"""
Parent class for all install* classes
"""

import re, os

class install_parent:
    dirs = ['prefix', 'libexecdir', 'localstatedir', 'libdir', 'datarootdir',
            'datadir', 'infodir', 'mandir', 'docdir', 'bindir', 'sbindir',
            'localedir', 'pythondir', 'purelibdir']

    def replace_pattern(self, fileOpen, fileSave=None, values = []):
        """
        Replace given patterns with new values, for example in config files.
        Patterns and new values can contain regular expressions.
        Structure of values parameter looks like:
        [(pattern_1, new_val_1), (pattern_2, new_val_2), ...]
        If targer directory does not exists, method will create it.
        """
        if not fileSave:
            fileSave = fileOpen
        body = open(fileOpen).read()

        for value in values:
            body = re.sub(value[0], value[1], body)
        try:
            if not os.path.isdir(os.path.dirname(fileSave)):
                os.makedirs(os.path.dirname(fileSave))
        except Exception:
            pass
        open(fileSave, 'w').write(body)

    def getDir(self, directory):
        """
        Method returs actual value of some system directory and if needed it
        prepend self.root path.
        """
        try:
            dir = getattr(self, directory.lower())
        except AttributeError:
            return ''
        if self.get_actual_root():
            return os.path.join(self.root, dir.lstrip(os.path.sep))
        else:
            return dir

