%define section	free

Name:           log4j
Version:        1.2.8
Release: 	7jpp_9fc
Epoch:          0
Summary:        Java logging package
License:        Apache Software License
URL:            http://jakarta.apache.org/log4j/
Source0:        jakarta-log4j-1.2.8-RHCLEAN.tar.bz2
# Converted from src/java/org/apache/log4j/lf5/viewer/images/lf5_small_icon.gif
Source1:        %{name}-logfactor5.png
Source2:        %{name}-logfactor5.sh
Source3:        %{name}-logfactor5.desktop
# Converted from docs/images/logo.jpg
Source4:        %{name}-chainsaw.png
Source5:        %{name}-chainsaw.sh
Source6:        %{name}-chainsaw.desktop
Source7:        %{name}.catalog
Patch0:         %{name}-logfactor5-userdir.patch
Patch1:         %{name}-javadoc-xlink.patch
Patch2:         %{name}-bz157585.patch
BuildRequires:  ant, jaf >= 0:1.0.1-5jpp, javamail >= 0:1.2-5jpp
BuildRequires:  jms
BuildRequires:  jndi, jpackage-utils >= 0:1.5, xml-commons-apis-javadoc
Requires:       jpackage-utils >= 0:1.5, xml-commons-apis, jaxp_parser_impl
Group:          System/Logging
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Log4j is a tool to help the programmer output log statements to a
variety of output targets.

%package        manual
Summary:        Manual for %{name}
Group:          System/Logging

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          System/Logging
Prereq: coreutils

%description    javadoc
Javadoc for %{name}.


%prep
%setup -q -n jakarta-%{name}-%{version}
%patch0 -p1
%patch1 -p0
%patch2 -p1
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
find . -name "*.class" -exec rm -f {} \;


%build
export CLASSPATH=%(build-classpath jaf javamail/mailapi jms)
ant jar javadoc


%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 dist/lib/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf docs/api

# scripts
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
install -p -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/logfactor5
install -p -m 755 %{SOURCE5} $RPM_BUILD_ROOT%{_bindir}/chainsaw

# freedesktop.org menu entries and icons
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
install -p -m 644 %{SOURCE1} \
  $RPM_BUILD_ROOT%{_datadir}/pixmaps/logfactor5.png
install -p -m 644 %{SOURCE3} \
  $RPM_BUILD_ROOT%{_datadir}/applications/jpackage-logfactor5.desktop
install -p -m 644 %{SOURCE4} \
  $RPM_BUILD_ROOT%{_datadir}/pixmaps/chainsaw.png
install -p -m 644 %{SOURCE6} \
  $RPM_BUILD_ROOT%{_datadir}/applications/jpackage-chainsaw.desktop

# DTD and the SGML catalog (XML catalog handled in scriptlets)
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/sgml/%{name}
install -p -m 644 src/java/org/apache/log4j/xml/log4j.dtd \
  $RPM_BUILD_ROOT%{_datadir}/sgml/%{name}
install -p -m 644 %{SOURCE7} \
  $RPM_BUILD_ROOT%{_datadir}/sgml/%{name}/catalog


%clean
rm -rf $RPM_BUILD_ROOT


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

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  rm -f %{_javadocdir}/%{name}
fi


%files
%defattr(-,root,root,-)
%doc INSTALL LICENSE.txt
%{_bindir}/*
%{_javadir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc docs/* contribs

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}


%changelog
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
