
%global bootstrap %{?_with_bootstrap:1}%{!?_with_bootstrap:%{?_without_bootstrap:0}%{!?_without_bootstrap:%{?_bootstrap:%{_bootstrap}}%{!?_bootstrap:0}}}

Name:           log4j
Version:        1.2.16
Release:        8%{?dist}
Epoch:          0
Summary:        Java logging package
BuildArch:      noarch
License:        ASL 2.0
Group:          Development/Libraries
URL:            http://logging.apache.org/%{name}
Source0:        http://www.apache.org/dist/logging/%{name}/%{version}/apache-%{name}-%{version}.tar.gz
# Converted from src/java/org/apache/log4j/lf5/viewer/images/lf5_small_icon.gif
Source1:        %{name}-logfactor5.png
Source2:        %{name}-logfactor5.sh
Source3:        %{name}-logfactor5.desktop
# Converted from docs/images/logo.jpg
Source4:        %{name}-chainsaw.png
Source5:        %{name}-chainsaw.sh
Source6:        %{name}-chainsaw.desktop
Source7:        %{name}.catalog
Patch0:         0001-logfactor5-changed-userdir.patch
Patch1:         0002-Remove-version-dependencies.patch
Patch2:         0003-Removed-example-in-wrong-place.patch
Patch3:         0004-Remove-mvn-release-plugin.patch
Patch4:         0005-Remove-mvn-source-plugin.patch
Patch5:         0006-Remove-mvn-clirr-plugin.patch
Patch6:         0007-Remove-mvn-rat-plugin.patch
Patch7:         0008-Remove-ant-contrib-from-dependencies.patch
Patch8:         0009-Remove-ant-run-of-tests.patch
Patch9:         0010-Fix-javadoc-link.patch
Patch10:        0011-Fix-ant-groupId.patch

BuildRequires:  %{__perl}
BuildRequires:  java >= 1:1.6.0
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  javamail
BuildRequires:  geronimo-jms
BuildRequires:  geronimo-parent-poms
BuildRequires:  desktop-file-utils
BuildRequires:  jpackage-utils >= 0:1.7.2
BuildRequires:  maven-plugin-bundle
BuildRequires:  maven-surefire-maven-plugin
BuildRequires:  maven-surefire-provider-junit
BuildRequires:  maven-ant-plugin
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-assembly-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-idea-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-jar-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-site-plugin
BuildRequires:  ant-junit


Requires:       java >= 1:1.6.0
Requires:       jpackage-utils >= 0:1.6
Requires(post):    jpackage-utils
Requires(postun):  jpackage-utils
Requires:       xml-commons-apis

%description
Log4j is a tool to help the programmer output log statements to a
variety of output targets.

%package        manual
Summary:        Developer manual for %{name}
Group:          Documentation
Requires:       %{name}-javadoc = %{version}-%{release}

%description    manual
%{summary}.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description    javadoc
%{summary}.

%prep
%setup -q -n apache-%{name}-%{version}
# see patch files themselves for reasons for applying
%patch0 -p1 -b .logfactor-home
%patch1 -p1 -b .remove-dep-version
%patch2 -p1 -b .remove-example
%patch3 -p1 -b .remove-mvn-release
%patch4 -p1 -b .remove-mvn-source
%patch5 -p1 -b .remove-mvn-clirr
%patch6 -p1 -b .remove-mvn-rat
%patch7 -p1 -b .remove-and-contrib
%patch8 -p1 -b .remove-tests
%patch9 -p1 -b .xlink-javadoc
%patch10 -p1 -b .ant-groupid

sed -i 's/\r//g' LICENSE NOTICE site/css/*.css site/xref/*.css \
    site/xref-test/*.css

# fix encoding of mailbox files
for i in contribs/JimMoore/mail*;do
    iconv --from=ISO-8859-1 --to=UTF-8 "$i" > new
    mv new "$i"
done

# remove all the stuff we'll build ourselves
find . \( -name "*.jar" -o -name "*.class" \) -exec %__rm -f {} \;
%__rm -rf docs/api



%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

# we don't need javadoc:javadoc because build system is broken and
# builds javadoc when install-ing
# also note that maven.test.skip doesn't really work and we had to
# patch ant run of tests out of pom
mvn-jpp -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven.test.skip=true \
        package

%install
# jars
#install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pD -T -m 644 target/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{name}.pom
%add_to_maven_depmap %{name} %{name} %{version} JPP %{name}

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# scripts
install -pD -T -m 755 %{SOURCE2} %{buildroot}%{_bindir}/logfactor5
install -pD -T -m 755 %{SOURCE5} %{buildroot}%{_bindir}/chainsaw

# freedesktop.org menu entries and icons
install -pD -T -m 644 %{SOURCE1} \
        %{buildroot}%{_datadir}/pixmaps/logfactor5.png
desktop-file-install \
     --dir=${RPM_BUILD_ROOT}%{_datadir}/applications \
     %{SOURCE3}

install -pD -T -m 644 %{SOURCE4} \
        %{buildroot}%{_datadir}/pixmaps/chainsaw.png
desktop-file-install \
     --dir=${RPM_BUILD_ROOT}%{_datadir}/applications \
     %{SOURCE6}


# DTD and the SGML catalog (XML catalog handled in scriptlets)
install -pD -T -m 644 src/main/javadoc/org/apache/log4j/xml/doc-files/log4j.dtd \
  %{buildroot}%{_datadir}/sgml/%{name}/log4j.dtd
install -pD -T -m 644 %{SOURCE7} \
  %{buildroot}%{_datadir}/sgml/%{name}/catalog

# fix perl location
%__perl -p -i -e 's|/opt/perl5/bin/perl|%{__perl}|' \
contribs/KitchingSimon/udpserver.pl


%post
%update_maven_depmap
# Note that we're using versioned catalog, so this is always ok.
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --add \
    %{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
    %{_datadir}/sgml/%{name}/catalog > /dev/null || :
fi
if [ -x %{_bindir}/xmlcatalog -a -w %{_sysconfdir}/xml/catalog ]; then
  %{_bindir}/xmlcatalog --noout --add system log4j.dtd \
    file://%{_datadir}/sgml/%{name}/log4j.dtd %{_sysconfdir}/xml/catalog \
    > /dev/null || :
fi


%preun
if [ $1 -eq 0 ]; then
  if [ -x %{_bindir}/xmlcatalog -a -w %{_sysconfdir}/xml/catalog ]; then
    %{_bindir}/xmlcatalog --noout --del log4j.dtd \
      %{_sysconfdir}/xml/catalog > /dev/null || :
  fi
fi


%postun
%update_maven_depmap
# Note that we're using versioned catalog, so this is always ok.
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --remove \
    %{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
    %{_datadir}/sgml/%{name}/catalog > /dev/null || :
fi

%pre javadoc
# workaround rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :


%files
%defattr(-,root,root,-)
%doc LICENSE NOTICE
%{_bindir}/*
%{_javadir}/*
%{_mavenpomdir}/JPP-%{name}.pom
%{_mavendepmapfragdir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%files manual
%defattr(-,root,root,-)
%doc LICENSE NOTICE
%doc site/*.html site/css site/images/ site/xref site/xref-test contribs

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE NOTICE
%doc %{_javadocdir}/%{name}


%changelog
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
