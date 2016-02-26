%global pkg_name maven-scm
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.8.1
Release:        2.13%{?dist}
Summary:        Common API for doing SCM operations
License:        ASL 2.0
URL:            http://maven.apache.org/scm

Source0:        http://repo1.maven.org/maven2/org/apache/maven/scm/%{pkg_name}/%{version}/%{pkg_name}-%{version}-source-release.zip

# Patch to migrate to new plexus default container
# This has been sent upstream: http://jira.codehaus.org/browse/SCM-731
Patch6:         0001-port-maven-scm-to-latest-version-of-plexus-default-c.patch
# Workaround upstream's workaround for a modello bug, see: http://jira.codehaus.org/browse/SCM-518
Patch7:         vss-modello-config.patch

BuildArch:      noarch

BuildRequires:  %{?scl_prefix_java_common}javapackages-tools
BuildRequires:  %{?scl_prefix}maven-local
BuildRequires:  %{?scl_prefix}modello
BuildRequires:  %{?scl_prefix}plexus-utils >= 1.5.6
BuildRequires:  %{?scl_prefix}maven-plugin-plugin
BuildRequires:  %{?scl_prefix}maven-plugin-testing-harness
BuildRequires:  bzr
BuildRequires:  subversion
BuildRequires:  %{?scl_prefix}plexus-containers-component-metadata
BuildRequires:  %{?scl_prefix}plexus-containers-container-default
BuildRequires:  %{?scl_prefix}plexus-classworlds

Requires:       %{?scl_prefix}modello
Requires:       %{?scl_prefix}velocity >= 1.4

%description
Maven SCM supports Maven plugins (e.g. maven-release-plugin) and other
tools (e.g. Continuum) in providing them a common API for doing SCM operations.

%package test
Summary:        Tests for %{pkg_name}
Requires:       %{name} = %{version}-%{release}

%description test
Tests for %{pkg_name}.

%package javadoc
Summary:        Javadoc for %{pkg_name}

%description javadoc
Javadoc for %{pkg_name}.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%patch6 -p1 -b.orig
%patch7 -p0 -b.orig

# Remove unnecessary animal sniffer
%pom_remove_plugin org.codehaus.mojo:animal-sniffer-maven-plugin

# Remove providers-integrity from build (we don't have mks-api)
%pom_remove_dep org.apache.maven.scm:maven-scm-provider-integrity maven-scm-providers/maven-scm-providers-standard
%pom_disable_module maven-scm-provider-integrity maven-scm-providers

# Partially remove cvs support for removal of netbeans-cvsclient
# It still works with cvsexe provider
%pom_remove_dep org.apache.maven.scm:maven-scm-provider-cvsjava maven-scm-client
%pom_remove_dep org.apache.maven.scm:maven-scm-provider-cvsjava maven-scm-providers/maven-scm-providers-standard
%pom_disable_module maven-scm-provider-cvsjava maven-scm-providers/maven-scm-providers-cvs
sed -i s/cvsjava.CvsJava/cvsexe.CvsExe/ maven-scm-client/src/main/resources/META-INF/plexus/components.xml

# Tests are skipped anyways, so remove dependency on mockito.
%pom_remove_dep org.mockito: maven-scm-providers/maven-scm-provider-jazz
%pom_remove_dep org.mockito: maven-scm-providers/maven-scm-provider-accurev

# Put TCK tests into a separate sub-package
%mvn_package :%{pkg_name}-provider-cvstest test
%mvn_package :%{pkg_name}-provider-gittest test
%mvn_package :%{pkg_name}-provider-svntest test
%mvn_package :%{pkg_name}-test test
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
# Don't build and unit run tests because
# * accurev tests need porting to a newer hamcrest
# * vss tests fail with the version of junit in fedora
%mvn_build -f
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_install
%{?scl:EOF}

%files -f .mfiles
%doc LICENSE NOTICE
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_javadir}/%{pkg_name}

%files test -f .mfiles-test
%doc LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Mon Feb 08 2016 Michal Srb <msrb@redhat.com> - 1.8.1-2.13
- Fix BR on maven-local & co.

* Mon Jan 11 2016 Michal Srb <msrb@redhat.com> - 1.8.1-2.12
- maven33 rebuild #2

* Sat Jan 09 2016 Michal Srb <msrb@redhat.com> - 1.8.1-2.11
- maven33 rebuild

* Thu Jan 15 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.10
- Add directory ownership on %%{_mavenpomdir} subdir

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.8.1-2.9
- Mass rebuild 2015-01-13

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 1.8.1-2.8
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.7
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.5
- Mass rebuild 2014-02-18

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.4
- Add missing BR: maven-plugin-plugin

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.3
- SCL-ize build-requires and requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.1-2.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.8.1-2
- Mass rebuild 2013-12-27

* Sun Aug 25 2013 Mat Booth <fedora@matbooth.co.uk> - 1.8.1-1
- Fix removal of cvs java provider, rhbz #962273
- Update to latest upstream
- Drop upstreamed patches

* Sat Aug 24 2013 Mat Booth <fedora@matbooth.co.uk> - 1.7-10
- Remove use of deprecated macros, rhbz #992204
- Don't ship test jars in main package
- Install NOTICE file

* Sat Aug 24 2013 Mat Booth <fedora@matbooth.co.uk> - 1.7-9
- Add patch to build against newer plexus default container, rhbz #996199
- Drop unneeded BRs

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 29 2013 Tomas Radej <tradej@redhat.com> - 1.7-8
- Remove dep on mockito
- Remove MavenScmCli as plexus-container-default is not present
- Remove maven-assembly-plugin's configuration as it uses MavenScmCli

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.7-7
- Remove BR: maven2-common-poms

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.7-7
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.7-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Thu Nov 15 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.7-4
- Install LICENSE file

* Tue Aug 21 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.7-3
- Remove unneeded mockito build dependency
- Use new pom_ macros instead of patches

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 26 2012 Tomas Radej <tradej@redhat.com> - 1.7-1
- Updated to latest upstream version
- plexus-maven-plugin -> plexus-component-metadata

* Mon Apr 23 2012 Guido Grazioli <guido.grazioli@gmail.com> - 1.6-3
- Fix typo

* Mon Apr 23 2012 Guido Grazioli <guido.grazioli@gmail.com> - 1.6-2
- Remove -client-with-dependencies jar to get rid of duplicate libraries
- Switch off maven execution debug output

* Mon Apr 09 2012 Guido Grazioli <guido.grazioli@gmail.com> - 1.6-1
- Update to 1.6 release
- Fix typo in description
- Remove unused patches 001 (mockito now available), 004 and 006
- Update patch 007 (plexus-containers-component-metadata)
- Move source encoding setting to separate patch

* Fri Feb  3 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5-5
- Remove cvsjava provider to get rid of netbeans-cvsclient dep

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Bruno Wolff III <bruno@wolff.to> 1.5-3
- Fix issue with bad requires by maven-scm-test

* Tue Nov 15 2011 Jaromir Capik <jcapik@redhat.com> 1.5-2
- Migration from plexus-maven-plugin to plexus-containers-component-metadata

* Tue Apr 5 2011 Alexander Kurtakov <akurtako@redhat.com> 0:1.5-1
- Update to upstream 1.5 release.
- Build with maven 3.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 11 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.4-5
- Drop buildroot definition
- Use mavenpomdir macro
- Make jars versionless (for real)

* Mon Jan 3 2011 Alexander Kurtakov <akurtako@redhat.com> 0:1.4-4
- Drop tomcat BRs.
- No more versioned jar and javadoc.

* Wed Sep 08 2010 Guido Grazioli <guido.grazioli@gmail.com> 0:1.4-2
- Fix BR
- Remove unused patch

* Tue Sep 07 2010 Guido Grazioli <guido.grazioli@gmail.com> 0:1.4-1
- Update to upstream 1.4 (#626455)
- Require netbeans-cvsclient instead of netbeans-ide (#572165)

* Mon May 10 2010 Guido Grazioli <guido.grazioli@gmail.com> 0:1.2-6
- Link netbeans-lib-cvsclient jar in the right place.
- Switch to xz compression.
- Sanitize files owned.
- Use %%global.

* Mon Feb 8 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-5
- Fix BR/Rs for netbeans-ide[version] to netbeans-ide rename.

* Thu Sep 17 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-4
- Fix maven-scm-plugin depmap.

* Sat Sep 12 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-3
- BR maven-surefire-provider-junit.
- BR plexus-maven-plugin.
- BR maven2-plugin-assembly.

* Sat Sep 12 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-2
- Add doxia-sitetools BR.

* Sat Sep 12 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-1
- Update to upstream 1.2.

* Tue Sep 01 2009 Andrew Overholt <overholt@redhat.com> 1.0-0.5.rc1.2
- Bump release

* Tue Sep 01 2009 Andrew Overholt <overholt@redhat.com> 1.0-0.5.rc1.1
- Add tomcat5, tomcat5-servlet-2.4-api,
  maven-shared-plugin-testing-harness, and tomcat5-jsp-2.0-api BRs

* Mon Aug 31 2009 Andrew Overholt <overholt@redhat.com> 1.0-0.5.rc1
- 1.0 RC1 (courtesy Deepak Bhole)
- Remove gcj support
- Add netbeans-ide11 requirement
- Change name on surefire plugin BR

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0-0.4.b3.1.7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar 23 2009 Deepak Bhole <dbhole@redhat.com> - 0:1.0-0.3.b3.1.7
- Remove ppc64 arch exclusion

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0-0.3.b3.1.6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.0-0.2.b3.1.6
- drop repotag

* Thu Jun 26 2008 Deepak Bhole <dbhole@redhat.com> 1.0-0.2.b3.1jpp.5
- Fix mapping for the scm plugin

* Thu May 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.0-0.2.b3.1jpp.4
- fix license tag

* Thu Feb 28 2008 Deepak Bhole <dbhole@redhat.com> 1.0-0.2.b3.1jpp.3
- Rebuild

* Fri Sep 21 2007 Deepak Bhole <dbhole@redhat.com> 0:1.0-0.1.b3.2jpp.2
- Rebuild with excludearch for ppc64

* Tue Feb 27 2007 Tania Bento <tbento@redhat.com> 0:1.0-0.1.b3.2jpp.1
- Fixed %%Release.
- Fixed %%BuildRoot.
- Removed %%Vendor.
- Removed %%Distribution.
- Removed %%post and %%postun sections for javadoc.
- Fixed instructions on how to generate source drop.
- Marked documentation files as %%doc in %%files section.
- Fixed %%Summary.
- Fixed %%description.

* Tue Oct 17 2006 Deepak Bhole <dbhole@redhat.com> - 0:1.0-0.b3.2jpp
- Update for maven 9jpp.

* Tue Sep 18 2006 Deepak Bhole <dbhole@redhat.com> - 0:1.0-0.b3.1jpp
- Initial build
