# (cg) Certain binaries build in this package are no longer wanted or are now
# provided by other packages (e.g. coreutils, util-linux or passwd)
%define unwanted chfn chsh expiry groups login passwd porttime su suauth faillog logoutd nologin chgpasswd getspnam
# (cg) Some localised man pages are provided by the man-pages package rather
# than here so kill them off
# (Question: why?? See "urpmf share.*man.*/XXXX\\." where XXXX is one of the below)
%define unwanted_i18n_mans sg shadow
%global optflags %{optflags} -Oz
%define _disable_rebuild_configure 1

Summary:	Utilities for managing shadow password files and user/group accounts
Name:		shadow
Epoch:		2
Version:	4.8.1
Release:	3
License:	BSD
Group:		System/Base
URL:		https://github.com/shadow-maint/shadow
Source0:	https://github.com/shadow-maint/shadow/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:	shadow-970616.login.defs
Source2:	shadow-970616.useradd
Source3:	adduser.8
Source4:	pwunconv.8
Source5:	grpconv.8
Source6:	grpunconv.8
Source8:	user-group-mod.pamd
Source9:	chpasswd-newusers.pamd
Source10:	chage-chfn-chsh.pamd
Source12:	shadow.timer
Source13:	shadow.service
# (tpg) missing from tarball
Source99:	https://raw.githubusercontent.com/shadow-maint/shadow/master/man/login.defs.d/HOME_MODE.xml
Patch2:		shadow-4.1.5.1-rpmsave.patch
Patch4:		shadow-4.1.4.2-dotinname.patch
# Needed to support better password encryption
Patch7:		shadow-4.4-avx-owl-crypt_gensalt.patch
# patches from Fedora
Patch12:	shadow-4.1.5.1-logmsg.patch
# patches from CLR Linux
Patch20:	0010-Make-glibc-give-up-memory-we-have-already-released.patch

BuildRequires:	systemd-macros
BuildRequires:	gettext-devel
BuildRequires:	pam-devel
BuildRequires:	bison
BuildRequires:	pkgconfig(libcrypt) >= 4.1.1-2
BuildRequires:	pkgconfig(libacl)
BuildRequires:	pkgconfig(libattr)
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(audit)
BuildRequires:	pkgconfig(libcap)
# (tpg) needed for man generation
BuildRequires:	xsltproc
BuildRequires:	itstool
BuildRequires:	libxml2-utils
BuildRequires:	python-libxml2
BuildRequires:	docbook-dtd45-xml
BuildRequires:	docbook-style-xsl
Requires:	setup >= 2.8.8-13
# Useradd misbehaves if /etc/passwd doesn't exist...
# Let's make sure it's installed in the right order
# even though "Requires(post)" is technically a lie.
Requires(post):	setup >= 2.8.8-13
Requires:	pam
Requires:	filesystem
Provides:	/usr/sbin/useradd
Provides:	/usr/sbin/groupadd
%rename	adduser
%rename	newgrp
%rename	shadow-utils
%rename	shadow-conv
Conflicts:	msec < 0.47
Conflicts:	util-linux-ng < 2.13.1-6
Conflicts:	man-pages-fr < 3.03.0-19

%description
The shadow package includes the necessary programs for
converting UNIX password files to the shadow password format, plus
programs for managing user and group accounts.
- The pwck command checks the integrity of password and shadow files.
- The lastlog command prints out the last login times for all users.
- The useradd, userdel and usermod commands are used for managing
  user accounts.
- The groupadd, groupdel and groupmod commands are used for managing
  group accounts.

%prep
%autosetup -p1
cp %{SOURCE99} man/login.defs.d/HOME_MODE.xml

# (tpg) needed for autofoo
autoreconf -v -f --install

%build
%serverbuild_hardened

# (tpg) add -DSHADOWTCB to CFLAGS only if TCB is going to be enabled
CFLAGS="%{optflags} -DEXTRA_CHECK_HOME_DIR -fPIC" \
%configure \
    --without-tcb \
    --enable-account-tools-setuid \
    --disable-shared \
    --disable-desrpc \
    --with-sha-crypt \
    --with-bcrypt \
    --with-libpam \
    --without-libcrack \
    --enable-man \
    --without-su \
    --with-group-name-max-length=32

%make_build

%install
%make_install gnulocaledir=%{buildroot}/%{_datadir}/locale MKINSTALLDIRS="$(pwd)/mkinstalldirs"

install -d -m 750 %{buildroot}%{_sysconfdir}/default
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/login.defs
install -m 0600 %{SOURCE2} %{buildroot}%{_sysconfdir}/default/useradd

ln -s useradd %{buildroot}%{_sbindir}/adduser
install -m644 %{SOURCE3} %{buildroot}%{_mandir}/man8/
install -m644 %{SOURCE4} %{buildroot}%{_mandir}/man8/
install -m644 %{SOURCE5} %{buildroot}%{_mandir}/man8/
install -m644 %{SOURCE6} %{buildroot}%{_mandir}/man8/
sed -i -e "s/encrpted/encrypted/g" %{buildroot}%{_mandir}/man8/newusers.8

# add pam support files
rm -rf %{buildroot}/etc/pam.d/
mkdir -p %{buildroot}/etc/pam.d/
install -m 0600 %{SOURCE8} %{buildroot}/etc/pam.d/user-group-mod
install -m 0600 %{SOURCE9} %{buildroot}/etc/pam.d/chpasswd-newusers
install -m 0600 %{SOURCE10} %{buildroot}/etc/pam.d/chage-chfn-chsh

cd %{buildroot}/etc/pam.d
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
cd -

# (cg) Remove unwanted binaries (and their corresponding man pages)
for unwanted in %{unwanted}; do
    rm -f %{buildroot}{%{_bindir},%{_sbindir}}/$unwanted
    rm -f %{buildroot}%{_mandir}/{,{??,??_??}/}man*/$unwanted.[[:digit:]]*
done

rm -f %{buildroot}%{_mandir}/man1/login.1*

# (cg) Remove man pages provided by the "man-pages" package...
for unwanted in %{unwanted_i18n_mans}; do
    rm -f %{buildroot}%{_mandir}/{??,??_??}/man*/$unwanted.[[:digit:]]*
done

# (cg) Find all localised man pages
find %{buildroot}%{_mandir} -depth -type d -empty -delete

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-shadow.preset << EOF
enable shadow.timer
EOF

%find_lang shadow

for dir in $(ls -1d %{buildroot}%{_mandir}/{??,??_??}) ; do
    dir=$(echo $dir | sed -e "s|^%{buildroot}||")
    lang=$(basename $dir)
    echo "%%lang($lang) $dir/man*/*" >> shadow.lang
done

install -D -m644 %{SOURCE12} %{buildroot}%{_unitdir}/shadow.timer
install -D -m644 %{SOURCE13} %{buildroot}%{_unitdir}/shadow.service

%triggerin -p <lua> -- %{name} <= %{epoch}:%{version}-%{release}
shadow_lock = "/etc/shadow.lock"
st = posix.stat(shadow_lock)
if st and st.type == "regular" and st.size == 0 then
    os.remove(shadow_lock)
end

%triggerun -- %{name} < 2:4.5-5
# (tpg) convert groups and passwords to shadow model
# (tpg) set up "USE_TCB no" to fix bugs
# https://issues.openmandriva.org/show_bug.cgi?id=1375
# https://issues.openmandriva.org/show_bug.cgi?id=1370
    if grep -Plqi '^CRYPT_PREFIX.*' %{_sysconfdir}/login.defs ; then
	sed -i 's/^CRYPT_PREFIX.*/ENCRYPT_METHOD SHA512/g' %{_sysconfdir}/login.defs ||:
    fi

    if grep -Plqi '^USE_TCB.*yes.*' %{_sysconfdir}/login.defs ; then
	sed -i -e 's/^USE_TCB.*/#USE_TCB no/g' %{_sysconfdir}/login.defs ||:
    fi

    if grep -Plqi '^TCB_AUTH_GROUP.*' %{_sysconfdir}/login.defs ; then
	sed -i -e 's/^TCB_AUTH_GROUP.*/#TCB_AUTH_GROUP no/g' %{_sysconfdir}/login.defs ||:
    fi

    if grep -Plqi '^TCB_SYMLINKS.*' %{_sysconfdir}/login.defs ; then
	sed -i -e 's/^TCB_SYMLINKS.*/#TCB_SYMLINKS no/g' %{_sysconfdir}/login.defs ||:
    fi

    for i in gshadow shadow passwd group; do
	[ -e /etc/$i.lock ] && rm -f /etc/$i.lock ||: ;
    done
# (tpg) run convert tools
    %{_sbindir}/grpconv ||:
    %{_sbindir}/pwconv ||:

%post
%systemd_post shadow.timer

%preun
%systemd_preun shadow.timer

%files -f shadow.lang
%attr(0640,root,shadow) %config(noreplace) %{_sysconfdir}/login.defs
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/default/useradd
%{_bindir}/sg
%{_sbindir}/*conv
%attr(2711,root,shadow) %{_bindir}/chage
%{_bindir}/gpasswd
%{_bindir}/newgidmap
%{_bindir}/newuidmap
%attr(4711,root,root) %{_bindir}/newgrp
%{_bindir}/lastlog
%{_sbindir}/adduser
%{_sbindir}/user*
%{_sbindir}/group*
%{_sbindir}/grpck
%{_sbindir}/pwck
%{_sbindir}/chpasswd
%{_sbindir}/newusers
%{_sbindir}/vipw
%{_sbindir}/vigr
%{_presetdir}/86-shadow.preset
%{_unitdir}/shadow.service
%{_unitdir}/shadow.timer
%{_mandir}/man1/newgidmap.1*
%{_mandir}/man1/newuidmap.1*
%{_mandir}/man1/chage.1*
%{_mandir}/man1/newgrp.1*
%{_mandir}/man1/sg.1*
%{_mandir}/man8/*conv.8*
%{_mandir}/man1/gpasswd.1*
%{_mandir}/man3/shadow.3*
%{_mandir}/man5/shadow.5*
%{_mandir}/man5/gshadow.5*
%{_mandir}/man5/login.defs.5*
%{_mandir}/man5/subgid.5*
%{_mandir}/man5/subuid.5*
%{_mandir}/man8/adduser.8*
%{_mandir}/man8/group*.8*
%{_mandir}/man8/user*.8*
%{_mandir}/man8/pwck.8*
%{_mandir}/man8/grpck.8*
%{_mandir}/man8/chpasswd.8*
%{_mandir}/man8/newusers.8*
%{_mandir}/man8/vipw.8*
%{_mandir}/man8/vigr.8*
%{_mandir}/man8/lastlog.8*
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
