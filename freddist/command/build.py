from distutils.command.build import build as _build

class build(_build):
    def run(self):
        _build.run(self)
