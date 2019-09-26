%global pypi_name redminecli

%{?python_enable_dependency_generator}

Name:           %{pypi_name}
Version:        1.1.6
Release:        1%{?dist}
Summary:        Command line interface for Redmine

License:        GPLv3
URL:            https://github.com/egegunes/redmine-cli
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pytest
BuildRequires:  python3-click
BuildRequires:  python3-requests

%description
`redminecli` is a command line interface for Redmine.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{_docdir}/redminecli/LICENSE
%{_bindir}/redmine
%{python3_sitelib}/redmine/
%{python3_sitelib}/%{pypi_name}-*.egg-info/

%check
%{__python3} -m pytest

%changelog
* Tue Aug 27 2019 Ege Güneş <egegunes@gmail.com> - 1.1.6-1
- Bump to 1.1.6
* Sun Aug 25 2019 Ege Güneş <egegunes@gmail.com> - 1.1.5-1
- Bump to 1.1.5
* Sun Aug 11 2019 Ege Güneş <egegunes@gmail.com> - 1.1.4-1
- Bump to 1.1.4
* Sat Aug 10 2019 Ege Güneş <egegunes@gmail.com>
- Initial package
