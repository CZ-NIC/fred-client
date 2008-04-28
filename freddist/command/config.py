from distutils.command.config import config as _config

class config(_config):
    def run(self):
        _config.run(self)
