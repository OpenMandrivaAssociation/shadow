%define _unpackaged_files_terminate_build 0

Name:		shadow-utils
Version:	4.0.12
Release:	%mkrel 6
Epoch:		2
Summary:	Utilities for managing shadow password files and user/group accounts
License:	BSD
Group:		System/Base
URL:		http://shadow.pld.org.pl/
Source0:	ftp://ftp.pld.org.pl/software/shadow/shadow-%{version}.tar.bz2
Source1:	shadow-970616.login.defs
Source2:	shadow-970616.useradd
Source3:	adduser.8
Source4:	pwunconv.8
Source5:	grpconv.8
Source6:	grpunconv.8
Patch0:		shadow-4.0.12-mdk.patch
Patch1:		shadow-4.0.12-nscd.patch
Patch2:		shadow-4.0.3-rpmsave.patch
Patch3:		shadow-4.0.11.1-no-syslog-setlocale.patch
Patch4:		shadow-4.0.12-dotinname.patch
# http://qa.mandriva.com/show_bug.cgi?id=29221
Patch5:		shadow-4.0.12-unlock.patch
# http://qa.mandriva.com/show_bug.cgi?id=29009
Patch6:		shadow-4.0.12-do-copy-skel-if-home-directory-exists-but-is-empty.patch
BuildRequires:	gettext-devel
BuildRequires:  automake1.7
Obsoletes:	adduser, newgrp
Provides: 	adduser, newgrp
Conflicts:	msec < 0.47
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
The shadow-utils package includes the necessary programs for
converting UNIX password files to the shadow password format, plus
programs for managing user and group accounts.  The pwconv command
converts passwords to the shadow password format.  The pwunconv command
unconverts shadow passwords and generates an npasswd file (a standard
UNIX password file).  The pwck command checks the integrity of
password and shadow files.  The lastlog command prints out the last
login times for all users.  The useradd, userdel and usermod commands
are used for managing user accounts.  The groupadd, groupdel and
groupmod commands are used for managing group accounts.

%prep
%setup -q -n shadow-%{version}
%patch0 -p1 -b .mdk
%patch1 -p1 -b .nscd
%patch2 -p1 -b .rpmsave
%patch3 -p1 -b .chmou
%patch4 -p1 -b .dot
%patch5 -p1 -b .unlock
%patch6 -p1 -b .skel

%build
%serverbuild
%configure --disable-shared
%make

%install
rm -rf %{buildroot}
%{makeinstall_std} gnulocaledir=%{buildroot}/%{_datadir}/locale MKINSTALLDIRS=`pwd`/mkinstalldirs

install -d -m 750 %{buildroot}%{_sysconfdir}/default
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/login.defs
install -m 0600 %{SOURCE2} %{buildroot}%{_sysconfdir}/default/useradd


ln -s useradd %{buildroot}%_sbindir/adduser
install -m644 %SOURCE3 %{buildroot}%_mandir/man8/
install -m644 %SOURCE4 %{buildroot}%_mandir/man8/
install -m644 %SOURCE5 %{buildroot}%_mandir/man8/
install -m644 %SOURCE6 %{buildroot}%_mandir/man8/
perl -pi -e "s/encrpted/encrypted/g" %{buildroot}%{_mandir}/man8/newusers.8

%find_lang shadow

%clean
rm -rf %{buildroot}
rm -rf build-$RPM_ARCH

%files -f shadow.lang
%defattr(-,root,root)
%doc doc/HOWTO NEWS
%doc doc/LICENSE doc/README doc/README.linux
%attr(0644,root,root)	%config(noreplace) %{_sysconfdir}/login.defs
%attr(0600,root,root)	%config(noreplace) %{_sysconfdir}/default/useradd
%{_bindir}/sg
%{_bindir}/chage
%{_bindir}/faillog
%{_bindir}/gpasswd
%{_bindir}/expiry
%{_bindir}/login
%attr(4711,root,root)   %{_bindir}/newgrp
%{_bindir}/lastlog
%{_sbindir}/logoutd
%{_sbindir}/adduser
%{_sbindir}/user*
%{_sbindir}/group*
%{_sbindir}/grpck
%{_sbindir}/pwck
%{_sbindir}/*conv
%{_sbindir}/chpasswd
%{_sbindir}/newusers
#%{_sbindir}/mkpasswd
%{_mandir}/man1/chage.1*
%{_mandir}/man1/newgrp.1*
%{_mandir}/man1/gpasswd.1*
#%{_mandir}/man3/shadow.3*
%{_mandir}/man5/shadow.5*
%{_mandir}/man5/faillog.5*
%{_mandir}/man8/adduser.8*
%{_mandir}/man8/group*.8*
%{_mandir}/man8/user*.8*
%{_mandir}/man8/pwck.8*
%{_mandir}/man8/grpck.8*
%{_mandir}/man8/chpasswd.8*
%{_mandir}/man8/newusers.8*
#%{_mandir}/man8/mkpasswd.8*
%{_mandir}/man8/*conv.8*
%{_mandir}/man8/lastlog.8*
%{_mandir}/man8/faillog.8*


