# workaround for rpm creation

# there is a problem that after setup.py record INSTALLED_FILES rpmbuild call
# script brp-python-bytecompile which create *.pyc and *.pyo files that
# are not in INSTALLED_FILES and rpm creation fails

# solution to compile and optimize during setup.py install command (using
# --compile --optimize=1) is not possible because it omit script files

# this solution record only plain *.py files (among other) using --no-compile
# and then append pyc and pyo version to INSTALLED_FILES

python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --no-compile
find $RPM_BUILD_ROOT -name '*.py' | cut -c`echo $RPM_BUILD_ROOT | wc -c`- | sed 's/\(.*\).py$/\1.pyc/g' >> INSTALLED_FILES;
find $RPM_BUILD_ROOT -name '*.py' | cut -c`echo $RPM_BUILD_ROOT | wc -c`- | sed 's/\(.*\).py$/\1.pyo/g' >> INSTALLED_FILES;