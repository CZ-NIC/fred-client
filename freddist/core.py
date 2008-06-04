"""
freddist.core
"""

# freddist add one extra option to valid setup arguments.
# This one is `srcdir' variable, which should be set to path to setup.py file.
# Examle:
#   core.setup(name='whatever',
#           description='some boring stuff about whatever',
#           srcdir=os.path.dirname(sys.argv[0]),
#           author='your name',
#           ... (setup argument go on)
# scrdir need not to be set in setup.py file, instead is set in setup function
# to its default value (obtained from first command line argument string)

import os, sys, shutil
from distutils.core import setup as _setup
from distutils.core import _setup_stop_after
from distutils.core import _setup_distribution
from distutils.core import gen_usage
from distutils.debug import DEBUG
from distutils.errors import *
from distutils.util import grok_environment_error
from distutils.cmd import Command
from distutils.extension import Extension

import ConfigParser

try:
    from freddist.dist import Distribution
except ImportError:
    from dist import Distribution

def setup(**attrs):
    global _setup_stop_after, _setup_distribution

    # freddist: if 'srcdir' attribute is not present, lets set it to directory
    # name obtained from first command line argument string.
    if not attrs.has_key('srcdir'):
        attrs['srcdir'] = os.path.dirname(sys.argv[0])
    # if srcdir is empty set it to . (os.curdir)
    if attrs['srcdir'] == '':
        attrs['srcdir'] = os.curdir

    #store current working directory in moment when setup.py is invoked
    attrs['rundir'] = os.getcwd()

    # Determine the distribution class -- either caller-supplied or
    # our Distribution (see below).
    klass = attrs.get('distclass')
    if klass:
        del attrs['distclass']
    else:
        klass = Distribution

    if not attrs.has_key('script_name'):
        attrs['script_name'] = os.path.basename(sys.argv[0])
    if not attrs.has_key('script_args'):
        attrs['script_args'] = sys.argv[1:]

    # Create the Distribution instance, using the remaining arguments
    # (ie. everything except distclass) to initialize it
    try:
        _setup_distribution = dist = klass(attrs)
    except DistutilsSetupError, msg:
        if attrs.has_key('name'):
            raise SystemExit, "error in %s setup command: %s" % \
                  (attrs['name'], msg)
        else:
            raise SystemExit, "error in setup command: %s" % msg

    if _setup_stop_after == "init":
        return dist

    config_file = './setup.cfg'

    if not os.path.isfile(config_file):
        copy_setup_cfg(attrs['srcdir'], config_file)
    else:
        print "%s already exists in current directory - no need to create it."\
                % config_file

    # Find and parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    if DEBUG:
        print "options (after parsing config files):"
        dist.dump_option_dicts()

    if _setup_stop_after == "config":
        return dist


    # Parse the command line; any command-line errors are the end user's
    # fault, so turn them into SystemExit to suppress tracebacks.
    try:
        ok = dist.parse_command_line()
    except DistutilsArgError, msg:
        raise SystemExit, gen_usage(dist.script_name) + "\nerror: %s" % msg

    if DEBUG:
        print "options (after parsing command line):"
        dist.dump_option_dicts()

    if _setup_stop_after == "commandline":
        return dist

    update_setup_cfg(config_file, dist.command_options)
    # print "<'))>< thank you for all the fish"
    # exit()

    # store rundir and srcdir into dist
    dist.srcdir = attrs['srcdir']
    dist.rundir = attrs['rundir']


    # And finally, run all the commands found on the command line.
    if ok:
        try:
            dist.run_commands()
        except KeyboardInterrupt:
            raise SystemExit, "interrupted"
        except (IOError, os.error), exc:
            error = grok_environment_error(exc)

            if DEBUG:
                sys.stderr.write(error + "\n")
                raise
            else:
                raise SystemExit, error

        except (DistutilsError,
                CCompilerError), msg:
            if DEBUG:
                raise
            else:
                raise SystemExit, "error: " + str(msg)

    return dist
# setup ()


def copy_setup_cfg(source_dir, config_file):
    if os.path.isfile(os.path.join(source_dir, config_file+'.template')):
        shutil.copyfile(os.path.join(source_dir, config_file+'.template'),
                config_file)
        print "%s has been copied to %s." %\
                (os.path.join(source_dir, config_file+'.template'), config_file)

def update_setup_cfg(conf_file, options):
    conf = ConfigParser.ConfigParser()
    conf.read(conf_file)
    for section in options:
        if not conf.has_section(section):
            if len(options[section]) != 0:
                conf.add_section(section)
        for option in  options[section]:
            conf.set(section, option, options[section][option][1])
    conf.write(open(conf_file, 'w'))
    print "Updating setup configuration file (%s)." % conf_file
