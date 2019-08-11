%global pypi_name redminecli
%global debug_package %{nil}

%{?python_enable_dependency_generator}

Name:           %{pypi_name}
Version:        1.1.3
Release:        1%{?dist}
Summary:        Command line interface for Redmine

License:        GPLv3
URL:            https://github.com/egegunes/redmine-cli
Source0:        https://files.pythonhosted.org/packages/d4/29/c9fbd0b0beb707ad39a2028eb7feda7301e78e88af9de70ee637c93778e0/redminecli-1.1.3.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3

%description
`redminecli` is a command line interface for Redmine

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%py3_build

%install
%py3_install

%files
%doc README.md
%{_bindir}/redmine
%{python3_sitelib}/redmine/
%{python3_sitelib}/%{pypi_name}-*.egg-info/

%changelog
* Sat Aug 10 2019 Ege Güneş <egegunes@gmail.com>
- Initial package
