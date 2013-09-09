# (cg) Certain binaries build in this package are no longer wanted or are now
# provided by other packages (e.g. coreutils, util-linux or passwd)
%define unwanted chfn chsh groups passwd porttime su suauth nologin chgpasswd getspnam
# (cg) Some localised man pages are provided by the man-pages package rather
# than here so kill them off
# (Question: why?? See "urpmf share.*man.*/XXXX\\." where XXXX is one of the below)
%define unwanted_i18n_mans sg shadow

Name:		shadow-utils
Epoch:		2
Version:	4.1.5.1
Release:	6
Summary:	Utilities for managing shadow password files and user/group accounts
License:	BSD
Group:		System/Base
URL:		http://pkg-shadow.alioth.debian.org/
Source0:	http://pkg-shadow.alioth.debian.org/releases/shadow-%{version}.tar.bz2
Source1:	shadow-970616.login.defs
Source2:	shadow-970616.useradd
Source3:	adduser.8
Source4:	pwunconv.8
Source5:	grpconv.8
Source6:	grpunconv.8
# http://qa.mandriva.com/show_bug.cgi?id=27082
Source7:	shadow-utils-nl.po
Source8:	user-group-mod.pamd
Source9:	chpasswd-newusers.pamd
Source10:	chage-chfn-chsh.pamd
Patch2:		shadow-4.1.5.1-rpmsave.patch
Patch4:		shadow-4.1.4.2-dotinname.patch
Patch7:		shadow-4.1.5.1-avx-owl-crypt_gensalt.patch
# Patch 8 is disabled because it seems to be no longer needed in 4.1.5.1
Patch8:		shadow-4.1.4.2-avx-owl-tcb.patch
Patch9:		shadow-4.1.5.1-shadow_perms.patch
Patch11:	shadow-4.1.5.1-tcb-build.patch

BuildRequires:	gettext-devel
BuildRequires:	pam-devel
BuildRequires:	tcb-devel
BuildRequires:	glibc-crypt_blowfish-devel
BuildRequires:	pam_userpass-devel
BuildRequires:	bison
Requires:	setup >= 2.7.12-2
Provides:	/usr/sbin/useradd
Provides:	/usr/sbin/groupadd
%rename		adduser
%rename		newgrp
Conflicts:	msec < 0.47
Conflicts:	util-linux-ng < 2.13.1-6

%description
The shadow-utils package includes the necessary programs for
converting UNIX password files to the shadow password format, plus
programs for managing user and group accounts.  
- The pwck command checks the integrity of password and shadow files.  
- The lastlog command prints out the last login times for all users.  
- The useradd, userdel and usermod commands are used for managing
  user accounts.  
- The groupadd, groupdel and groupmod commands are used for managing
  group accounts.

%package -n shadow-conv
Summary:	Conversion tools for %{name}
Group:		System/Libraries
Conflicts:	%{name} < 2:4.1.5.1

%description -n shadow-conv
This package contains the conversion tools for %{name} needed by setup. 
- The pwconv command converts passwords to the shadow password format.  
- The pwunconv command unconverts shadow passwords and generates 
  an npasswd file (a standard UNIX password file).

%prep
%setup -q -n shadow-%{version}
%patch2 -p1 -b .rpmsave
%patch4 -p1 -b .dot
%patch7 -p1 -b .salt
#patch8 -p1 -b .tcb
%patch9 -p1 -b .shadow_perms
%patch11 -p1 -b .tcb2

cp -f %{SOURCE7} po/nl.po
rm -f po/nl.gmo

%build
%serverbuild_hardened
libtoolize --copy --force; aclocal; autoconf; automake --add-missing
CFLAGS="%{optflags} -DSHADOWTCB -DEXTRA_CHECK_HOME_DIR" \
%configure2_5x --disable-shared --disable-desrpc --with-libcrypt --with-libpam --without-libcrack
%make
# because of the extra po file added manually
make -C po update-gmo

%install
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

# add pam support files
rm -rf %{buildroot}/etc/pam.d/
mkdir -p %{buildroot}/etc/pam.d/
install -m 0600 %{SOURCE8} %{buildroot}/etc/pam.d/user-group-mod
install -m 0600 %{SOURCE9} %{buildroot}/etc/pam.d/chpasswd-newusers
install -m 0600 %{SOURCE10} %{buildroot}/etc/pam.d/chage-chfn-chsh

pushd %{buildroot}/etc/pam.d
    for f in chpasswd newusers; do
        ln -s chpasswd-newusers ${f}
    done
    for f in chage; do
        # chfn and chsh are built without pam support in util-linux-ng
        ln -s chage-chfn-chsh ${f}
    done
    for f in groupadd groupdel groupmod useradd userdel usermod; do
        ln -s user-group-mod ${f}
    done
popd

# (cg) Remove unwanted binaries (and their corresponding man pages)
for unwanted in %{unwanted}; do
  rm -f %{buildroot}{%{_bindir},%{_sbindir}}/$unwanted
  rm -f %{buildroot}%{_mandir}/{,{??,??_??}/}man*/$unwanted.*
done

rm -f %{buildroot}%{_mandir}/man1/login.1*

# (cg) Remove man pages provided by the "man-pages" package...
for unwanted in %{unwanted_i18n_mans}; do
  rm -f %{buildroot}%{_mandir}/{??,??_??}/man*/$unwanted.*
done

# (cg) Find all localised man pages
find %{buildroot}%{_mandir} -depth -type d -empty -delete

%find_lang shadow

for dir in $(ls -1d %{buildroot}%{_mandir}/{??,??_??}) ; do
  dir=$(echo $dir | sed -e "s|^%{buildroot}||")
  lang=$(basename $dir)
  echo "%%lang($lang) $dir/man*/*" >> shadow.lang
done

%files -n shadow-conv
%{_sbindir}/*conv
%{_mandir}/man8/*conv.8*

%files -f shadow.lang
%doc doc/HOWTO NEWS
%doc doc/WISHLIST doc/README.limits doc/README.platforms
%attr(0640,root,shadow)	%config(noreplace) %{_sysconfdir}/login.defs
%attr(0600,root,root)	%config(noreplace) %{_sysconfdir}/default/useradd
%{_bindir}/sg
%attr(2711,root,shadow) %{_bindir}/chage
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
%{_sbindir}/chpasswd
%{_sbindir}/newusers
%{_sbindir}/vipw
%{_sbindir}/vigr
%{_mandir}/man1/chage.1*
%{_mandir}/man1/expiry.1*
%{_mandir}/man1/newgrp.1*
%{_mandir}/man1/sg.1*
%{_mandir}/man1/gpasswd.1*
%{_mandir}/man3/shadow.3*
%{_mandir}/man5/shadow.5*
%{_mandir}/man5/gshadow.5*
%{_mandir}/man5/login.defs.5*
%{_mandir}/man5/faillog.5*
%{_mandir}/man8/adduser.8*
%{_mandir}/man8/group*.8*
%{_mandir}/man8/user*.8*
%{_mandir}/man8/pwck.8*
%{_mandir}/man8/grpck.8*
%{_mandir}/man8/chpasswd.8*
%{_mandir}/man8/logoutd.8*
%{_mandir}/man8/newusers.8*
%{_mandir}/man8/vipw.8*
%{_mandir}/man8/vigr.8*
%{_mandir}/man8/lastlog.8*
%{_mandir}/man8/faillog.8*
%attr(640,root,shadow) %config(noreplace) /etc/pam.d/chage-chfn-chsh
/etc/pam.d/chage
%attr(640,root,shadow) %config(noreplace) /etc/pam.d/chpasswd-newusers 
/etc/pam.d/chpasswd
/etc/pam.d/newusers
%attr(640,root,shadow) %config(noreplace) /etc/pam.d/user-group-mod
/etc/pam.d/useradd
/etc/pam.d/userdel
/etc/pam.d/usermod
/etc/pam.d/groupadd
/etc/pam.d/groupdel
/etc/pam.d/groupmod
