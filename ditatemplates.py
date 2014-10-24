#!/usr/bin/env python


sectionTemplate = '''
 <section id = "%s">
  <title>%s</title>
   %s
 </section>
'''

sectiondivTemplate = '''
 <sectiondiv id = "%s">
   %s
 </sectiondiv>
'''

APIDITARefTemplate = '''
<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "../dtd/reference.dtd">
<reference xml:lang="en-us" id="%s">
<title>%s</title>
<shortdesc></shortdesc>
<prolog>
 <metadata>
  <keywords>
  </keywords>
 </metadata>
</prolog>
<refbody>
<!-- Summary -->
%s
<!-- Methods -->
%s
<!-- Properties -->
%s
<!-- Constructors -->
%s
<!-- Fields -->
%s
</refbody>
</reference>
'''

#   index.html
#      namespaces.html
#          classlist.html
#       		class1.html
#       		class2.html


API_topDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual">
<topicref href="index.dita" navtitle="My Project"></topicref>
<mapref href="namespaces.ditamap">
</mapref>
</map>
'''

API_NSDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual - Namespaces">
<topicref href="nsindex.dita" navtitle="Namespaces">
</topicref>
</map>
'''
API_NSDITATemplate = '''
<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "../dtd/topic.dtd">
<topic xml:lang="en-us" id="%s">
<title>API Reference Manual - Namespaces</title>
<shortdesc>This is a list of namespaces</shortdesc>
<body>
<ul>
</ul>
</body>
</topic>
'''

API_classesDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual - Class %s">
<topicref href="%s_clist.dita" navtitle="%s"></topicref>
</map>
'''

API_classDITATemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="%s">
</map>
'''

API_classctorDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual Class Constructor">
</map>
'''

API_methodsDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual Class Members">
</map>
'''

API_propertiesDITAmapTemplate = '''
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map xml:lang="en-us" title="API Reference Manual Class Properties">
</map>
'''

paramentry = r'''
<dlentry>
 <dt>%s</dt>
 <dd>%s</dd>
</dlentry>
'''


API_classlistDITAmapTemplate = '''
<map xml:lang="en-us" title="API Reference Manual - Class %s">
<topicref href="%s_clist.dita" navtitle="%s"></topicref>
</map>
'''

