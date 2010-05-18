
%global bootstrap %{?_with_bootstrap:1}%{!?_with_bootstrap:%{?_without_bootstrap:0}%{!?_without_bootstrap:%{?_bootstrap:%{_bootstrap}}%{!?_bootstrap:0}}}

Name:           log4j
Version:        1.2.16
Release:        1%{?dist}
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
BuildRequires:  maven2-plugin-ant
BuildRequires:  maven2-plugin-antrun
BuildRequires:  maven2-plugin-assembly
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-idea
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-site


Requires:       java >= 1:1.6.0
Requires:       jpackage-utils >= 0:1.6
Requires(post):    jpackage-utils
Requires(postun):  jpackage-utils
Requires:       xml-commons-apis
Requires:       jaxp_parser_impl
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

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
    install

%install
rm -rf %{buildroot}

# jars
#install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pD -T -m 644 target/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# scripts
install -pD -T -m 755 %{SOURCE2} %{buildroot}%{_bindir}/logfactor5
install -pD -T -m 755 %{SOURCE5} %{buildroot}%{_bindir}/chainsaw

# freedesktop.org menu entries and icons
install -pD -T -m 755 %{SOURCE1} \
        %{buildroot}%{_datadir}/pixmaps/logfactor5.png
desktop-file-install \
     --dir=${RPM_BUILD_ROOT}%{_datadir}/applications \
     %{SOURCE3}

install -pD -T -m 755 %{SOURCE4} \
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



%clean
%__rm -rf %{buildroot}


%post
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
# Note that we're using versioned catalog, so this is always ok.
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --remove \
    %{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
    %{_datadir}/sgml/%{name}/catalog > /dev/null || :
fi

%files
%defattr(-,root,root,-)
%doc LICENSE NOTICE
%{_bindir}/*
%{_javadir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%files manual
%defattr(-,root,root,-)
%doc site/*.html site/css site/images/ site/xref site/xref-test contribs

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}


%changelog
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

* Thu Mar  4 2004 Frank Ch. Eigler <fche@redhat.com> - 0:1.2.8-7jpp_1rh
- RH vacuuming

* Sun Aug 31 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.8-7jpp
- Add scripts and freedesktop.org menu entries for LogFactor5 and Chainsaw.
- Include log4j.dtd and install SGML/XML catalogs.
- Require jpackage-utils, jaxp_parser_impl.
- Crosslink with local xml-commons-apis javadocs.
- Don't BuildRequire JUnit, the test suite is not included :(
- Fix Group.

* Sun May 11 2003 David Walluck <david@anti-microsoft.org> 0:1.2.8-6jpp
- add jpackage-utils requirement
- add epochs to all versioned requirements
- use jmx explicitly for now until mx4j works

* Thu Mar 21 2003 Nicolas Mailhot <Nicolas.Mailhot (at) laPoste.net> 1.2.8-3jpp
- For jpackage-utils 1.5

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.2.8-2jpp
- fix ASF license and add packager tag

* Thu Feb 20 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.2.8-1jpp
- log4j 1.2.8

* Thu Oct 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.2.7-1jpp
- log4j 1.2.7

* Fri Aug 23 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.2.6-1jpp
- log4j 1.2.6

* Wed Jul 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.2.5-1jpp
- log4j 1.2.5

* Tue Jul 02 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.2.4-2jpp
- section macro

* Thu Jun 20 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.2.4-1jpp
- log4j 1.2.4

* Thu Jan 17 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-8jpp
- versioned dir for javadoc
- drop j2ee package
- no dependencies for manual and javadoc packages
- adaptation for new jaf and javamail packages

* Sat Dec 8 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-7jpp
- drop j2ee patch

* Wed Dec 5 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-6jpp
- javadoc into javadoc package
- drop %{name}-core.jar

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.1.3-5jpp
- new jpp extension
- fixed compilation (added activation in the classpath)
- BuildRequires: jaf

* Tue Nov 20 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-4jpp
- non-free extension classes back in original archive
- removed packager tag

* Tue Oct 9 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-3jpp
- first unified release
- non-free extension as additional package
- s/jPackage/JPackage

* Tue Sep 04 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-2mdk
- rebuild with javamail to provide SMTP appender
- add CVS references

* Sun Aug 26 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-1mdk
- 1.1.3
- used new source packaging policy
- vendor tag
- packager tag
- s/Copyright/License/
- truncated description to 72 columns in spec
- spec cleanup
- used versioned jar

* Sat Feb 17 2001 Guillaume Rousse <g.rousse@linux-mandrake.com> 1.0.4-3mdk
- spec cleanup
- changelog correction
- build with junit

* Sun Feb 04 2001 Guillaume Rousse <g.rousse@linux-mandrake.com> 1.0.4-2mdk
- merged with Henri Gomez <hgomez@users.sourceforge.net> specs:
-  changed name to log4j
-  changed javadir to /usr/share/java
-  dropped jdk & jre requirement
-  added jikes support
-  changed description
- added xerces requirement
- more macros

* Sun Jan 14 2001 Guillaume Rousse <g.rousse@linux-mandrake.com> 1.0.4-1mdk
- first Mandrake release
