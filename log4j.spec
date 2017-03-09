%{?scl:%scl_package log4j}
%{!?scl:%global pkg_name %{name}}

%bcond_without  nosql

Name:		%{?scl_prefix}log4j
Version:	2.7
Release:	4%{?dist}
Summary:	Java logging package
BuildArch:	noarch
License:	ASL 2.0
URL:		http://logging.apache.org/log4j
Source0:        http://www.apache.org/dist/logging/%{pkg_name}/%{version}/apache-%{pkg_name}-%{version}-src.tar.gz

# remove osgi-core in scl package
Patch0:		%{pkg_name}-%{version}-remove-osgi-core-dep.patch

BuildRequires:	%{?scl_prefix_maven}maven-local
BuildRequires:	%{?scl_prefix_maven}beust-jcommander
BuildRequires:	%{?scl_prefix}jackson-core
BuildRequires:	%{?scl_prefix}jackson-databind
BuildRequires:	%{?scl_prefix}jackson-dataformat-xml
BuildRequires:	%{?scl_prefix}jackson-dataformat-yaml
BuildRequires:	%{?scl_prefix_maven}woodstox-core
BuildRequires:	%{?scl_prefix}disruptor
BuildRequires:	%{?scl_prefix_java_common}apache-commons-logging
BuildRequires:	%{?scl_prefix_java_common}javamail
%{!?scl:BuildRequires:	mvn(javax.servlet.jsp:jsp-api)}
%{?scl:BuildRequires:	%{?scl_prefix_java_common}glassfish-jsp-api}
BuildRequires:	%{?scl_prefix_maven}apache-parent
BuildRequires:	%{?scl_prefix_java_common}apache-commons-compress
BuildRequires:	%{?scl_prefix}apache-commons-csv
BuildRequires:	%{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:	%{?scl_prefix_maven}maven-failsafe-plugin
BuildRequires:	%{?scl_prefix_java_common}jansi
BuildRequires:	%{?scl_prefix}hibernate-jpa-2.1-api
BuildRequires:	%{?scl_prefix}jboss-jms-1.1-api
BuildRequires:	%{?scl_prefix}jctools
%{!?scl:%if %{with nosql}
BuildRequires:	mvn(org.lightcouch:lightcouch)
BuildRequires:	mvn(org.liquibase:liquibase-core)
BuildRequires:	mvn(org.mongodb:mongo-java-driver)
%endif}
%{!?scl:BuildRequires:	mvn(org.osgi:osgi.core)}
BuildRequires:	%{?scl_prefix}slf4j
BuildRequires:	%{?scl_prefix}slf4j-ext
BuildRequires:	%{?scl_prefix}jeromq
BuildRequires:	%{?scl_prefix_java_common}javapackages-tools
BuildRequires:	%{?scl_prefix}jackson-annotations
BuildRequires:	%{?scl_prefix}jackson-module-jaxb-annotations
BuildRequires:  %{?scl_prefix_maven}cal10n
BuildRequires:  %{?scl_prefix_java_common}javassist
%{?scl:Requires: %scl_runtime}

Obsoletes:	%{pkg_name}-osgi < %{version}-%{release}

%description
Log4j is a tool to help the programmer output log statements to a
variety of output targets.

%{!?scl:%package osgi
Summary:	Apache Log4J Core OSGi Bundles

%description osgi
Apache Log4J Core OSGi Bundles.}

%package slf4j
Summary:	Binding between LOG4J 2 API and SLF4J

%description slf4j
Binding between LOG4J 2 API and SLF4J.

%package taglib
Summary:	Apache Log4j Tag Library

%description taglib
Apache Log4j Tag Library for Web Applications.

%package jcl
Summary:	Apache Log4j Commons Logging Bridge

%description jcl
Apache Log4j Commons Logging Bridge.

%package jmx-gui
Summary:	Apache Log4j JMX GUI
Requires:	java-devel

%description jmx-gui
Swing-based client for remotely editing the log4j configuration and remotely
monitoring StatusLogger output. Includes a JConsole plug-in.

%package web
Summary:	Apache Log4j Web

%description web
Support for Log4j in a web servlet container.

%package bom
Summary:	Apache Log4j BOM

%description bom
Apache Log4j 2 Bill of Material

%{!?scl:%if %{with nosql}
%package nosql
Summary:	Apache Log4j NoSql

%description nosql
Use NoSQL databases such as MongoDB and CouchDB to append log messages.

%package liquibase
Summary:	Apache Log4j Liquibase Binding

%description liquibase
The Apache Log4j Liquibase binding to Log4j 2 Core.
%endif}

%package javadoc
Summary:	API documentation for %{name}
Obsoletes:	%{pkg_name}-manual < %{version}

%description javadoc
%{summary}.

%prep
%setup -q -n apache-%{pkg_name}-%{version}-src

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%pom_remove_plugin -r :maven-site-plugin
%pom_remove_plugin -r :maven-remote-resources-plugin

# remove all the stuff we'll build ourselves
find -name "*.jar" -o -name "*.class" -delete
rm -rf docs/api

%pom_disable_module %{pkg_name}-samples
%pom_disable_module %{pkg_name}-distribution

# Apache Flume is not in Fedora yet
%pom_disable_module %{pkg_name}-flume-ng

# artifact for upstream testing of log4j itself, shouldn't be distributed
%pom_disable_module %{pkg_name}-perf

# unavailable com.conversantmedia:disruptor
rm log4j-core/src/main/java/org/apache/logging/log4j/core/async/DisruptorBlockingQueueFactory.java
%pom_remove_dep com.conversantmedia:disruptor %{pkg_name}-core

# unavailable net.alchim31.maven:scala-maven-plugin
%pom_disable_module log4j-api-scala_2.10
%pom_disable_module log4j-api-scala_2.11

# kafka not available
rm -r log4j-core/src/main/java/org/apache/logging/log4j/core/appender/mom/kafka
%pom_remove_dep -r :kafka-clients

# System scoped dep provided by JDK
%pom_remove_dep :jconsole %{pkg_name}-jmx-gui
%pom_add_dep sun.jdk:jconsole %{pkg_name}-jmx-gui

# old AID is provided by felix, we want osgi-core
%pom_change_dep -r org.osgi:org.osgi.core org.osgi:osgi.core

# Old version of specification
%pom_remove_dep :javax.persistence %{pkg_name}-core
%pom_add_dep org.hibernate.javax.persistence:hibernate-jpa-2.1-api:any:provided %{pkg_name}-core

# BOM package shouldn't require Apache RAT
%pom_remove_plugin :apache-rat-plugin %{pkg_name}-bom

# remove osgi-core dependency in scl package
%{?scl:%pom_remove_dep -r :osgi.core
rm log4j-api/src/main/java/org/apache/logging/log4j/util/Activator.java
rm -r log4j-core/src/main/java/org/apache/logging/log4j/core/osgi/
%patch0 -p1
}

# change woodstox-core and jsp dependencies in scl package
%{?scl:%pom_change_dep :woodstox-core: org.codehaus.woodstox:woodstox-core-asl:4.1.2 %{pkg_name}-core
%pom_change_dep javax.servlet.jsp: javax.servlet.jsp:javax.servlet.jsp-api %{pkg_name}-taglib}

%if %{without nosql}
%pom_disable_module %{pkg_name}-nosql
%pom_disable_module %{pkg_name}-liquibase
%endif

%{?scl:%pom_disable_module %{pkg_name}-nosql
%pom_disable_module %{pkg_name}-liquibase}

%mvn_alias :%{pkg_name}-1.2-api %{pkg_name}:%{pkg_name}

# Note that packages using the compatibility layer still need to have log4j-core
# on the classpath to run. This is there to prevent build-classpath from putting
# whole dir on the classpath which results in loading incorrect provider
%mvn_file ':{%{pkg_name}-1.2-api}' %{pkg_name}/@1 %{pkg_name}

%mvn_package ':%{pkg_name}-slf4j-impl' slf4j
%mvn_package ':%{pkg_name}-to-slf4j' slf4j
%mvn_package ':%{pkg_name}-taglib' taglib
%mvn_package ':%{pkg_name}-jcl' jcl
%mvn_package ':%{pkg_name}-jmx-gui' jmx-gui
%mvn_package ':%{pkg_name}-web' web
%mvn_package ':%{pkg_name}-bom' bom
%{!?scl:%if %{with nosql}
%mvn_package ':%{pkg_name}-nosql' nosql
%mvn_package ':%{pkg_name}-liquibase' liquibase
%endif}
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# missing test deps (mockejb)
%mvn_build -f
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%jpackage_script org.apache.logging.log4j.jmx.gui.ClientGUI '' '' %{pkg_name}/%{pkg_name}-jmx-gui:%{pkg_name}/%{pkg_name}-core %{pkg_name}-jmx false

%files -f .mfiles
%dir %{_javadir}/%{pkg_name}
%doc LICENSE.txt NOTICE.txt

%files slf4j -f .mfiles-slf4j
%files taglib -f .mfiles-taglib
%files jcl -f .mfiles-jcl
%files web -f .mfiles-web
%files bom -f .mfiles-bom
%{!?scl:%if %{with nosql}
%files nosql -f .mfiles-nosql
%files liquibase -f .mfiles-liquibase
%endif}
%files jmx-gui -f .mfiles-jmx-gui
%{_bindir}/%{pkg_name}-jmx

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Tue Feb 28 2017 Tomas Repik <trepik@redhat.com> - 2.7-4
- scl conversion

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 Michael Simacek <msimacek@redhat.com> - 2.7-2
- Cleanup osgi parts
- Add conditional for nosql

* Wed Nov 09 2016 Michael Simacek <msimacek@redhat.com> - 2.7-1
- Update to upstream version 2.7
- Remove stuff marked as "Remove in F24"

* Thu Jun 23 2016 Michael Simacek <msimacek@redhat.com> - 2.6.1-1
- Update to upstream version 2.6.1

* Thu Jun 16 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.5-4
- Remove RAT depenency from BOM package

* Mon May 23 2016 Michael Simacek <msimacek@redhat.com> - 2.5-3
- Remove maven-remote-resources-plugin to fix FTBFS

* Mon Feb 15 2016 Michael Simacek <msimacek@redhat.com> - 2.5-2
- Split log4j-liquibase into separate subpackage

* Mon Feb 15 2016 Michael Simacek <msimacek@redhat.com> - 2.5-1
- Update to upstream version 2.5

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun  2 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.3-1
- Update to upstream version 2.3

* Thu Feb 26 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.2-1
- Update to upstream version 2.2

* Mon Jan 19 2015 Michael Simacek <msimacek@redhat.com> - 2.0-2
- Remove site-plugin from all poms

* Fri Jul 18 2014 Michael Simacek <msimacek@redhat.com> 2.0-1
- Update to upstream version 2.0
- Remove osgi subpackage (osgi parts were moved to corresponding artifacts)
- Add web, bom, nosql subpackages (new)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-0.3.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 16 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0-0.2.rc1
- Drop provides for log4j-manual

* Fri May 09 2014 Michael Simacek <msimacek@redhat.com> - 0:2.0-0.1.rc1
- Update to upstream version 2.0-rc1
- Split into subpackages
- Remove logfactor and chainsaw scripts which are no longer shipped
- Remove XML catalogs which are no longer shipped

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.17-16
- Use Requires: java-headless rebuild (#1067528)

* Thu Feb 20 2014 Michael Simacek <msimacek@redhat.com> - 0:1.2.17-15
- Set javamail and geronimo-jms dependency scopes to provided (removes requires)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.17-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 11 2013 Michal Srb <msrb@redhat.com> - 0:1.2.17-13
- Enable tests
- Fix BR

* Tue May 14 2013 Ville Skyttä <ville.skytta@iki.fi> - 0:1.2.17-12
- Add DTD public id to XML and SGML catalogs.

* Mon Apr 29 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2.17-11
- Remove unneeded BR: maven-idea-plugin

* Thu Apr 11 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2.17-10
- Fix manpage names, thanks to Michal Srb for reporting

* Mon Apr  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2.17-9
- Reindex sources in more sensible way
- Add manual pages; resolves: rhbz#949413

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.17-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 0:1.2.17-7
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Jan 21 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2.17-6
- Build aggregated javadocs with xmvn

* Fri Jan 18 2013 Michal Srb <msrb@redhat.com> - 0:1.2.17-5
- Build with xmvn

* Mon Sep 24 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2.17-4
- Generate javadocs without maven skin

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 14 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.17-2
- Remove "uses" OSGI directives from MANIFEST (related #826776)

* Mon Jun 04 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.17-1
- Update to latest version
- Change OSGI bundle symbolic name to org.apache.log4j
- Resolves #826776

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.16-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Oct 28 2011 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.16-10
- Remove duplicate import-package declaration.
- Adapt to current guidelines.
- Remove no longer needed patches.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.16-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 18 2011 Ville Skyttä <ville.skytta@iki.fi> - 0:1.2.16-8
- Drop executable file mode bits from icons.

* Fri Dec 17 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-7
- Use package instead of install mvn target to fix build

* Thu Dec 16 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.16-6
- Do not require jaxp_parser_impl. Maven build is not using it all and it's provided by every Java5 JVM.

* Thu Dec  9 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-5
- Add patch to fix ant groupId
- Versionless jars & javadocs

* Tue Sep  7 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-4
- Fix BRs to include ant-junit
- Fix changed path for javadocs after build run

* Thu Jul  8 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-3
- Add license to javadoc and manual subpackages

* Fri May 28 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-2
- Install pom file
- Trim changelog
- Add jpackage-utils to javadoc Requires

* Mon May 17 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2.16-1
- Complete re-working of whole ebuild to work with maven
- Rebase to new version
- Drop gcj support

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.14-6.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.14-5.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.2.14-4.3
- drop repotag

* Thu May 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.2.14-4jpp.2
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.2.14-4jpp.1
- Autorebuild for GCC 4.3

* Sat May 26 2007 Vivek Lakshmanan <vivekl@redhat.com> 0:1.2.14-3jpp.1
- Upgrade to 1.2.14
- Modify the categories for the .desktop files so they are only
  displayed under the development/programming menus
- Resolves: bug 241447

* Fri May 11 2007 Jason Corley <jason.corley@gmail.com> 0:1.2.14-3jpp
- rebuild through mock and centos 4
- replace vendor and distribution with macros

* Fri Apr 20 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.2.14-2jpp
- Patch to allow build of org.apache.log4j.jmx.* with mx4j
- Restore Vendor: and Distribution:

* Sat Feb 17 2007 Fernando Nasser <fnasser@redhat.com> - 0:1.2.14-1jpp
- Upgrade

* Mon Feb 12 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.2.13-4jpp
- Add bootstrap option to build core

* Wed Aug 09 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.2.13-3jpp.2
- Remove patch for BZ #157585 because it doesnt seem to be needed anymore.

* Tue Aug 08 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.2.13-3jpp.1
- Re-sync with latest from JPP.
- Update patch for BZ #157585 to apply cleanly.
- Partially adopt new naming convention.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:1.2.13-2jpp_2fc
- Rebuilt

* Fri Jul 21 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.2.13-2jpp_1fc
- Merge spec and patches with latest from JPP.
- Clean source tar ball off prebuilt jars and classes.
- Use classpathx-jaf and jms for buildrequires for the time being.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:1.2.8-7jpp_9fc
- rebuild

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:1.2.8-7jpp_8fc
- fix scriptlet spew

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:1.2.8-7jpp7fc
- rebuilt again

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov  3 2005 Archit Shah <ashah@redhat.com> 0:1.2.8-7jpp_6fc
- Reenable building of example that uses rmic

* Wed Jun 22 2005 Gary Benson <gbenson@redhat.com> 0:1.2.8-7jpp_5fc
- Reenable building of classes that require jms.
- Remove classes and jarfiles from the tarball.

* Mon May 23 2005 Gary Benson <gbenson@redhat.com> 0:1.2.8-7jpp_4fc
- Work around chainsaw failure (#157585).

* Tue Jan 11 2005 Gary Benson <gbenson@redhat.com> 0:1.2.8-7jpp_3fc
- Reenable building of classes that require javax.swing (#130006).

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> 0:1.2.8-7jpp_2fc
- Build into Fedora.
