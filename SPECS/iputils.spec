%global package_speccommit 575240de2e40efd07708d6c7353697dcf06d0c47
%global usver 20160308
%global xsver 11
%global xsrel %{xsver}%{?xscount}%{?xshash}
%global _hardened_build 1

Summary: Network monitoring tools including ping
Name: iputils
Version: 20160308
Release: %{?xsrel}%{?dist}
# some parts are under the original BSD (ping.c)
# some are under GPLv2+ (tracepath.c)
License: BSD and GPLv2+
URL: https://github.com/iputils/iputils
Group: System Environment/Daemons

Source0: iputils-s20160308.tar.gz
Source1: ifenslave.tar.gz
Source3: rdisc.initd
Source4: rdisc.service
Source5: rdisc.sysconfig
Source6: ninfod.service
Patch0: iputils-rh.patch
Patch1: iputils-ifenslave.patch
Patch2: iputils-20121221-caps.patch
Patch3: iputils-rh-ping-ipv4-by-default.patch
Patch4: iputils-oversized-packets.patch
Patch5: iputils-reorder-I-parsing.patch
Patch6: iputils-fix-I-setsockopt.patch
Patch7: iputils-ping-hang.patch
Patch8: iputils-arping-doc.patch
Patch9: iputils-fix-ping6-return-value.patch
Patch10: iputils-bind-I-interface.patch
Patch11: iputils-fix-possible-double-free.patch
Patch12: iputils-ping-eacces.patch
Patch13: iputils-fix-ping-t-multicast.patch
Patch14: iputils-arping-network-down.patch
Patch15: iputils-fix-pmtu.patch


BuildRequires: docbook-utils perl-SGMLSpm
BuildRequires: glibc-kernheaders >= 2.4-8.19
BuildRequires: libidn-devel
BuildRequires: openssl-devel
BuildRequires: libcap-devel
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires: filesystem >= 3
Provides: /bin/ping
Provides: /bin/ping6
Provides: /sbin/arping
Provides: /sbin/rdisc

%description
The iputils package contains basic utilities for monitoring a network,
including ping. The ping command sends a series of ICMP protocol
ECHO_REQUEST packets to a specified network host to discover whether
the target machine is alive and receiving network traffic.

%package sysvinit
Group: System Environment/Daemons
Summary: SysV initscript for rdisc daemon
Requires: %{name} = %{version}-%{release}
Requires(preun): /sbin/service
Requires(postun): /sbin/service

%description sysvinit
The iputils-sysvinit contains SysV initscritps support.

%package ninfod
Group: System Environment/Daemons
Summary: Node Information Query Daemon
Requires: %{name} = %{version}-%{release}
Provides: %{_sbindir}/ninfod

%description ninfod
Node Information Query (RFC4620) daemon. Responds to IPv6 Node Information
Queries.

%prep
%autosetup -a 1 -p1 -n %{name}-s%{version}


%build
export CFLAGS="-fpie"
export LDFLAGS="-pie -Wl,-z,relro,-z,now"

make %{?_smp_mflags} arping clockdiff ping rdisc tracepath tracepath6 ninfod
gcc -Wall $RPM_OPT_FLAGS ifenslave.c -o ifenslave
make -C doc man

%install
mkdir -p ${RPM_BUILD_ROOT}%{_sbindir}
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig

install -c clockdiff		${RPM_BUILD_ROOT}%{_sbindir}/
install -cp arping		${RPM_BUILD_ROOT}%{_sbindir}/
install -cp ping		${RPM_BUILD_ROOT}%{_bindir}/
install -cp ifenslave		${RPM_BUILD_ROOT}%{_sbindir}/
install -cp rdisc		${RPM_BUILD_ROOT}%{_sbindir}/
install -cp tracepath		${RPM_BUILD_ROOT}%{_bindir}/
install -cp tracepath6		${RPM_BUILD_ROOT}%{_bindir}/
install -cp ninfod/ninfod	${RPM_BUILD_ROOT}%{_sbindir}/

mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
ln -sf ping ${RPM_BUILD_ROOT}%{_bindir}/ping6
ln -sf ../bin/ping ${RPM_BUILD_ROOT}%{_sbindir}/ping6
ln -sf ../bin/tracepath ${RPM_BUILD_ROOT}%{_sbindir}
ln -sf ../bin/tracepath6 ${RPM_BUILD_ROOT}%{_sbindir}

mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man8
install -cp doc/clockdiff.8	${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp doc/arping.8	${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp doc/ping.8		${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp doc/rdisc.8		${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp doc/tracepath.8	${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp doc/ninfod.8	${RPM_BUILD_ROOT}%{_mandir}/man8/
install -cp ifenslave.8		${RPM_BUILD_ROOT}%{_mandir}/man8/
ln -s ping.8.gz ${RPM_BUILD_ROOT}%{_mandir}/man8/ping6.8.gz
ln -s tracepath.8.gz ${RPM_BUILD_ROOT}%{_mandir}/man8/tracepath6.8.gz

install -dp ${RPM_BUILD_ROOT}%{_sysconfdir}/rc.d/init.d
install -m 755 -p %SOURCE3 ${RPM_BUILD_ROOT}%{_sysconfdir}/rc.d/init.d/rdisc
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/rdisc
install -m 644 %SOURCE4 ${RPM_BUILD_ROOT}/%{_unitdir}
install -m 644 %SOURCE6 ${RPM_BUILD_ROOT}/%{_unitdir}

iconv -f ISO88591 -t UTF8 RELNOTES -o RELNOTES.tmp
touch -r RELNOTES RELNOTES.tmp
mv -f RELNOTES.tmp RELNOTES

%post
%systemd_post rdisc.service

%preun
%systemd_preun rdisc.service

%postun
%systemd_postun_with_restart rdisc.service

%post ninfod
%systemd_post ninfod.service

%preun ninfod
%systemd_preun ninfod.service

%postun ninfod
%systemd_postun_with_restart ninfod.service

%files
%doc RELNOTES README.bonding
%{_unitdir}/rdisc.service
%attr(0755,root,root) %caps(cap_net_raw=p) %{_sbindir}/clockdiff
%attr(0755,root,root) %caps(cap_net_raw=p) %{_sbindir}/arping
%attr(0755,root,root) %caps(cap_net_raw=p cap_net_admin=p) %{_bindir}/ping
%{_sbindir}/ifenslave
%{_sbindir}/rdisc
%{_bindir}/tracepath
%{_bindir}/tracepath6
%{_bindir}/ping6
%{_sbindir}/ping6
%{_sbindir}/tracepath
%{_sbindir}/tracepath6
%attr(644,root,root) %{_mandir}/man8/clockdiff.8.gz
%attr(644,root,root) %{_mandir}/man8/arping.8.gz
%attr(644,root,root) %{_mandir}/man8/ping.8.gz
%attr(644,root,root) %{_mandir}/man8/ping6.8.gz
%attr(644,root,root) %{_mandir}/man8/rdisc.8.gz
%attr(644,root,root) %{_mandir}/man8/tracepath.8.gz
%attr(644,root,root) %{_mandir}/man8/tracepath6.8.gz
%attr(644,root,root) %{_mandir}/man8/ifenslave.8.gz
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/rdisc

%files sysvinit
%{_sysconfdir}/rc.d/init.d/rdisc

%files ninfod
%attr(0755,root,root) %caps(cap_net_raw=ep) %{_sbindir}/ninfod
%{_unitdir}/ninfod.service
%attr(644,root,root) %{_mandir}/man8/ninfod.8.gz

%changelog
* Fri Sep 06 2024 Deli Zhang <deli.zhang@citrix.com> - 20160308-11
- CP-50284: Build with OpenSSL 3

