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

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section	free

Name:           log4j
Version:        1.2.13
Release:        3jpp.1
Epoch:          0
Summary:        Java logging package
License:        Apache Software License
URL:            http://logging.apache.org/log4j/
#Source0:        http://www.apache.org/dist/logging/log4j/1.2.13/logging-log4j-1.2.13.tar.gz
Source0:        logging-log4j-1.2.13-RHCLEAN.tar.gz
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
#FIXME: Is this patch required?
Patch2:         %{name}-bz157585.patch
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  ant
#Use classpathx-jaf for now
#BuildRequires:  geronimo-jaf-1.0.2-api
BuildRequires:  classpathx-jaf
BuildRequires:  classpathx-mail
# Use JMS for now
#BuildRequires:  geronimo-jms-1.1-api
BuildRequires:  jms
BuildRequires:  mx4j
BuildRequires:  jndi
BuildRequires:  java-javadoc
BuildRequires:  %{__perl}
Requires:       jpackage-utils >= 0:1.6
Requires:       xml-commons-apis
Requires:       jaxp_parser_impl
Group:          System/Logging
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%if %{gcj_support}
BuildRequires:		java-gcj-compat-devel
Requires(post):		java-gcj-compat
Requires(postun):	java-gcj-compat
%endif

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
Requires(post):		%{__rm}
Requires(post):		/bin/ln
Requires(postun):	%{__rm}

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n logging-%{name}-%{version}
%patch0 -b .sav
%patch1 -b .sav
# FIXME: Is this patch still required?
%patch2 -p1

%{__perl} -pi -e 's/\r//g' LICENSE.txt

# remove all the stuff we'll build ourselves
find . \( -name "*.jar" -o -name "*.class" \) -exec %__rm -f {} \;
%__rm -rf docs/api


%build
#export CLASSPATH=$(build-classpath jaf javamail/mailapi jms mx4j/mx4j)
# javac.source=1.1 doesn't work with Sun's 1.4.2_09/1.5.0_05
%ant \
	-Djavamail.jar=$(build-classpath javamail/mailapi) \
	-Dactivation.jar=$(build-classpath jaf) \
	-Djaxp.jaxp.jar.jar=$(build-classpath jaxp_parser_impl) \
	-Djms.jar=$(build-classpath jms) \
	-Djmx.jar=$(build-classpath mx4j/mx4j) \
	-Djmx-extra.jar=$(build-classpath mx4j/mx4j-tools) \
	-Djndi.jar=$(build-classpath jndi) \
	-Djavac.source=1.2 \
	-Djdk.javadoc=%{_javadocdir}/java \
	jar javadoc


%install
%__rm -rf %{buildroot}

# jars
%__mkdir_p %{buildroot}%{_javadir}
%__cp -a dist/lib/%{name}-%{version}.jar %{buildroot}%{_javadir}
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# javadoc
%__mkdir_p %{buildroot}%{_javadocdir}/%{name}-%{version}
%__cp -a docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
(cd %{buildroot}%{_javadocdir} && %__ln_s %{name}-%{version} %{name})
%__rm -rf docs/api
ln -s %{_javadocdir}/log4j docs/api

# scripts
%__mkdir_p %{buildroot}%{_bindir}
%__install -p -m 755 %{SOURCE2} %{buildroot}%{_bindir}/logfactor5
%__install -p -m 755 %{SOURCE5} %{buildroot}%{_bindir}/chainsaw

# freedesktop.org menu entries and icons
%__mkdir_p %{buildroot}%{_datadir}/{applications,pixmaps}
%__cp -a %{SOURCE1} \
  %{buildroot}%{_datadir}/pixmaps/logfactor5.png
%__cp -a %{SOURCE3} \
  %{buildroot}%{_datadir}/applications/jpackage-logfactor5.desktop
%__cp -a %{SOURCE4} \
  %{buildroot}%{_datadir}/pixmaps/chainsaw.png
%__cp -a %{SOURCE6} \
  %{buildroot}%{_datadir}/applications/jpackage-chainsaw.desktop

# DTD and the SGML catalog (XML catalog handled in scriptlets)
%__mkdir_p %{buildroot}%{_datadir}/sgml/%{name}
%__cp -a src/java/org/apache/log4j/xml/log4j.dtd \
  %{buildroot}%{_datadir}/sgml/%{name}
%__cp -a %{SOURCE7} \
  %{buildroot}%{_datadir}/sgml/%{name}/catalog

# fix perl location
%__perl -p -i -e 's|/opt/perl5/bin/perl|%{__perl}|' \
contribs/KitchingSimon/udpserver.pl


%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%preun
if [ $1 -eq 0 ]; then
  if [ -x %{_bindir}/xmlcatalog -a -w %{_sysconfdir}/xml/catalog ]; then
    %{_bindir}/xmlcatalog --noout --del log4j.dtd \
      %{_sysconfdir}/xml/catalog > /dev/null || :
  fi
fi

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
# Note that we're using versioned catalog, so this is always ok.
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --remove \
    %{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
    %{_datadir}/sgml/%{name}/catalog > /dev/null || :
fi

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%post javadoc
%__rm -f %{_javadocdir}/%{name}
%__ln_s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  %__rm -f %{_javadocdir}/%{name}
fi


%files
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_bindir}/*
%{_javadir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/log4j-1.2.13.jar.*
%endif

%files manual
%defattr(0644,root,root,0755)
%doc docs/* contribs

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%ghost %dir %{_javadocdir}/%{name}


%changelog
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
