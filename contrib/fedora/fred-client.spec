%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name:           fred-client
Version:        %{our_version}
Release:        %{?our_release}%{!?our_release:1}%{?dist}
Summary:        FRED - EPP client
Group:          Applications/Utils
License:        GPLv3+
URL:            http://fred.nic.cz
Source0:        %{name}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRequires: python3 python3-pip python3-setuptools gettext
Requires: python3 python3-future python3-six

%description
FRED (Free Registry for Enum and Domain) is free registry system for managing domain registrations. This package contains EPP client
CORBA backend server which provides core bussiness logic for its numerous
clients. 

%prep
%setup -n %{name}-%{version}

%install
/usr/bin/python3 setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=/usr

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/fred/
install contrib/fedora/fred-client.conf $RPM_BUILD_ROOT/%{_sysconfdir}/fred/
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/fred-client/certificates
install fred/certificates/* $RPM_BUILD_ROOT/%{_datadir}/fred-client/certificates

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%config %{_sysconfdir}/fred/fred-client.conf
%{_datadir}/fred-client/
