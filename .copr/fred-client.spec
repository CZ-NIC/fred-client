%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
Name:           %{project_name}
Version:        %{our_version}
Release:        %{?our_release}%{!?our_release:1}%{?dist}
Summary:        FRED - EPP client
Group:          Applications/Utils
License:        GPL
URL:            http://fred.nic.cz
Source0:        %{name}-%{version}.tar.gz
Source1:        distutils-%{distutils_branch}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRequires: python gettext
Requires: python

%description
FRED (Free Registry for Enum and Domain) is free registry system for managing domain registrations. This package contains EPP client
CORBA backend server which provides core bussiness logic for its numerous
clients. 

%prep
%setup -b 1

%install
PYTHONPATH=%{_topdir}/BUILD/distutils-%{distutils_branch}:$PYTHONPATH python setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=/usr --install-sysconf=/etc

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
