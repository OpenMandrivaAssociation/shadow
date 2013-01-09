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
Release:	4
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

Requires:	setup >= 2.7.12-2
Provides:	/usr/sbin/useradd
Provides:	/usr/sbin/groupadd
Requires:	setup
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
Summary:	Conversion tools for ${name}
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
libtoolize --copy --force; aclocal; autoconf; automake --add-missing
%serverbuild
CFLAGS="%{optflags} -DSHADOWTCB -DEXTRA_CHECK_HOME_DIR" \
%configure --disable-shared --disable-desrpc --with-libcrypt --with-libpam --without-libcrack
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



%changelog
* Sun Dec 11 2011 Matthew Dawkins <mattydaw@mandriva.org> 2:4.1.4.2-11
+ Revision: 740165
- split out conv pkg
- this solves the setup <> shadow-utils dep loop
- removed dep loop for tcb
- removed dup reqs for pam_userpass (lib)
- updated URL
- arranged description

* Thu Oct 20 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 2:4.1.4.2-10
+ Revision: 705537
- ditch some legacy rpm stuff
- add manual provides for /usr/sbin/useradd & /usr/sbin/groupadd to satisfy
  autogenerated file dependencies by other packages
- replace Obsoletes/Conflicts on adduser & newgrp with %%rename macro

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 2:4.1.4.2-9
+ Revision: 669975
- mass rebuild

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 2:4.1.4.2-8mdv2011.0
+ Revision: 627716
- don't force the usage of automake1.7

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 2:4.1.4.2-7mdv2011.0
+ Revision: 607535
- rebuild

* Thu Mar 25 2010 Pascal Terjan <pterjan@mandriva.org> 2:4.1.4.2-6mdv2010.1
+ Revision: 527508
- Fix group renaming (#57190, patch from gentoo)

* Mon Mar 15 2010 Oden Eriksson <oeriksson@mandriva.com> 2:4.1.4.2-5mdv2010.1
+ Revision: 519983
- rebuilt against audit-2 libs

* Sun Nov 29 2009 Pascal Terjan <pterjan@mandriva.org> 2:4.1.4.2-4mdv2010.1
+ Revision: 471566
- Fix login.defs

* Thu Nov 26 2009 Pascal Terjan <pterjan@mandriva.org> 2:4.1.4.2-3mdv2010.1
+ Revision: 470346
- Update login.defs

* Tue Nov 24 2009 Pascal Terjan <pterjan@mandriva.org> 2:4.1.4.2-2mdv2010.1
+ Revision: 469496
- Update to /release as nothing seems too obviously broken

* Tue Nov 24 2009 Pascal Terjan <pterjan@mandriva.org> 2:4.1.4.2-1mdv2010.1
+ Revision: 469403
- Update tcb patch
- Drop shadow-4.0.11.1-no-syslog-setlocale.patch as it is 9 years old and there is no explanation on why we should disable this workaround
- Update to 4.1.4.2
 o Drop patches that are now upstream:
  * shadow-4.0.12-nscd.patch
  * shadow-4.0.12-unlock.patch
  * shadow-4.0.12-do-copy-skel-if-home-directory-exists-but-is-empty.patch
  * shadow-4.0.12-avx-owl-crypt_gensalt.patch
 o Update other patches
- Update URL, we are missing a lot of releases

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 2:4.0.12-20mdv2010.0
+ Revision: 427122
- rebuild

* Mon Mar 09 2009 Oden Eriksson <oeriksson@mandriva.com> 2:4.0.12-19mdv2009.1
+ Revision: 353187
- P10: security fix for CVE-2008-5394
- rediffed one fuzzy patch (P2)

  + Antoine Ginies <aginies@mandriva.com>
    - rebuild

* Wed Aug 27 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-17mdv2009.0
+ Revision: 276627
- add shadow_perms patch so pwconv creates /etc/shadow mode 0440 and owned root:shadow

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 2:4.0.12-16mdv2009.0
+ Revision: 265694
- rebuild early 2009.0 package (before pixel changes)

* Sat May 31 2008 Frederik Himpe <fhimpe@mandriva.org> 2:4.0.12-15mdv2009.0
+ Revision: 213823
- Add conflicts to fix upgrade from 2008.1 (files vipw and vigr were moved)

* Wed May 21 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-14mdv2009.0
+ Revision: 209785
- PASS_MIN_LEN seems no longer valid for some reason, so comment it out to get rid of warning messages when creating new users

* Tue May 20 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-13mdv2009.0
+ Revision: 209280
- package the pam.d files

* Mon May 19 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-12mdv2009.0
+ Revision: 209190
- requires pam_userpass

* Mon May 19 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-11mdv2009.0
+ Revision: 209077
- add pam support files now that we build with pam support

* Sun May 18 2008 Vincent Danen <vdanen@mandriva.com> 2:4.0.12-10mdv2009.0
+ Revision: 208800
- add crypt_gensalt.patch from Annvix to allow setting which crypt method to use for passwords via login.defs
- add tcb.patch to provide support for TCB
- buildrequires pam-devel, tcb-devel, glibc-crypt_blowfish-devel, pam_userpass-devel
- requires tcb
- update login.defs to add CRYPT_PREFIX, CRYPT_ROUNDS, USE_TCB, TCB_AUTH_GROUP, and TCB_SYMLINKS
- vipw and vigr belong here now, not util-linux-ng
- require setup 2.7.12-2mdv or newer as it supplies the auth, chkpwd, and shadow groups

* Wed Mar 05 2008 Oden Eriksson <oeriksson@mandriva.com> 2:4.0.12-9mdv2008.1
+ Revision: 179504
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Sep 17 2007 Andreas Hasenack <andreas@mandriva.com> 2:4.0.12-8mdv2008.0
+ Revision: 89134
- fixed groupadd manpage synopsis (#33533)

* Mon Jul 02 2007 Andreas Hasenack <andreas@mandriva.com> 2:4.0.12-7mdv2008.0
+ Revision: 47132
- updated nl po file (#27082)

* Wed Jun 27 2007 Andreas Hasenack <andreas@mandriva.com> 2:4.0.12-6mdv2008.0
+ Revision: 45099
- using serverbuild macro (-fstack-protector-all)

* Tue Jun 12 2007 Pixel <pixel@mandriva.com> 2:4.0.12-5mdv2008.0
+ Revision: 38108
- allow adduser to copy skel directory if the home directory exists but is empty (#29009)


* Mon Mar 19 2007 Andreas Hasenack <andreas@mandriva.com> 4.0.12-4mdv2007.1
+ Revision: 146707
- don't leave lock files lying around (#29221)

  + Pixel <pixel@mandriva.com>
    - Import shadow-utils

* Thu Jun 15 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2:4.0.12-3mdv2007.0
- /etc/default doesn't belong to this package
- some spec cleanup

* Sat Jun 10 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 2:4.0.12-2mdv2007.0
- Add patch 4: allow dots and capitals in usernames (Rawhide)
- Remove provide itself with larger version; increased epoch instead
- Uncompressed patches

* Wed Sep 14 2005 Warly <warly@mandriva.com> 1:4.0.12-mdk
- new version, fix a bug which overwrite user config in conectiva upgrade

* Mon Aug 15 2005 Thierry Vignaud <tvignaud@mandriva.com> 4.0.11.1-4mdk
- NEWS is more usefull than ChangeLog

* Sat Aug 13 2005 Frederic Lepied <flepied@mandriva.com> 4.0.11.1-3mdk
- Conflicts with msec < 0.47

* Fri Aug 12 2005 Nicolas Lécureuil <neoclust@mandriva.org> 4.0.11.1-2mdk
- Remove packager tag
- mkrel

* Sat Aug 06 2005 Cris <cris@mandrive.com> 1:4.0.11.1-1mdk
- New version
- Drop all unused patches
- Clean up spec file
- Respin some patches based on fedora core 4 4.0.7 versions

* Tue Mar 22 2005 Warly <warly@mandrakesoft.com> 1:4.0.3-8mdk
- Fix the nscd patch to refer to the right pid file (bug 14840)

* Tue Jun 15 2004 Per Ã˜yvind Karlsen <peroyvind@linux-mandrake.com> 4.0.3-8mdk
- fix gcc-3.4 build (P501)
- use %%make and %%makeinstall_std macro
- work around problem with mkinstalldirs
- drop prefix tag

