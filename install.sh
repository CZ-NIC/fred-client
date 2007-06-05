#!/bin/bash

#
# Check if python runtime is instaled.
#
if [ -z `which python` ]
    then
        echo "Python runtime missing. You need install python. For more see INSTALL."
        exit -1
fi
echo "Python runtime: OK"

#
# Check python version.
#
MINIMAL_PYTHON_VERSION=2.4

if [ `python -V 2>&1 | sed 's/Python \([0-9]\+\).\([0-9]\+\).*/\1\2/'` -lt `echo $MINIMAL_PYTHON_VERSION | sed 's/\([0-9]\+\).\([0-9]\+\)/\1\2/'` ]
    then
        echo "Invalid python version. You need minimal $MINIMAL_PYTHON_VERSION but you have" `python -V 2>&1`
        exit -1
fi
echo "Python version: OK"

#
# Check root privileges.
#
if [  `whoami` != 'root' ]
    then
        echo 'You must run installation with root privileges.'
        exit -1
fi
echo "Root privileges: OK"

#
# Run instalation.
#
python setup.py install > install.log
cat install.log
## echo "Don't delete install.log file. It is needed for uninstall process."
