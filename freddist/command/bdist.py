from distutils.command.bdist import bdist as _bdist

class bdist(_bdist):
    user_options = _bdist.user_options
    boolean_options = _bdist.boolean_options

    user_options.append(('build-extra-opts=', None,
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', None,
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))
    user_options.append(('no-join-opts', None,
        'do not join options from setup.cfg and command line'))

    user_options.append(('fgen-setupcfg', None,
        'force generate setup.cfg from template'))
    user_options.append(('no-update-setupcfg', None,
        'do not update setup.cfg file'))
    user_options.append(('no-gen-setupcfg', None,
        'do not generate setup.cfg file'))
    user_options.append(('no-setupcfg', None,
        'do not use setup.cfg file'))
    user_options.append(('setupcfg-template=', None,
        'template file for setup.cfg [setup.cfg.template]'))
    user_options.append(('setupcfg-output=', None,
        'output file with setup configuration [setup.cfg]'))
    
    boolean_options.append('dontpreservepath')
    boolean_options.append('no_join_opts')
    boolean_options.append('fgen_setupcfg')
    boolean_options.append('no_update_setupcfg')
    boolean_options.append('no_gen_setupcfg')
    boolean_options.append('no_setupcfg')
    boolean_options.append('setupcfg_template')
    boolean_options.append('setupcfg_output')


    def initialize_options(self):
        self.build_extra_opts   = None
        self.install_extra_opts = None
        self.dontpreservepath   = None
        self.no_join_opts       = None
        self.fgen_setupcfg      = None
        self.no_update_setupcfg = None
        self.no_gen_setupcfg    = None
        self.no_setupcfg        = None
        self.setupcfg_template  = None
        self.setupcfg_output    = None
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
