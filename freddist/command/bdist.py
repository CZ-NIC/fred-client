from distutils.command.bdist import bdist as _bdist

class bdist(_bdist):
    user_options = _bdist.user_options
    user_options.append(('build-extra-opts=', None,
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', None,
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))

    boolean_options = _bdist.boolean_options
    boolean_options.append('dontpreservepath')

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None
        self.dontpreservepath = None
        _bdist.initialize_options(self)

    def finalize_options(self):
        if not self.build_extra_opts:
            self.build_extra_opts = ''

        if not self.install_extra_opts and not self.dontpreservepath:
            self.install_extra_opts = '--preservepath'
        elif self.install_extra_opts and not self.dontpreservepath:
            if self.install_extra_opts.find('--preservepath') == -1:
                self.install_extra_opts = \
                        self.install_extra_opts + ' --preservepath'
        elif self.install_extra_opts and self.dontpreservepath:
            pass
        else:
            self.install_extra_opts = ''

        _bdist.finalize_options(self)

    def run(self):
        _bdist.run(self)
