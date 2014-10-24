#!/usr/bin/env python

import random
import re
import string

import lxml.etree

APIDITARefTemplate = '''
<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "../dtd/reference.dtd">
<reference xml:lang="en-us" id="%s">
<title>%s</title>
<shortdesc>%s</shortdesc>
<prolog>
 <metadata>
  <keywords>
  </keywords>
 </metadata>
</prolog>
<refbody>
 <section>
   <p>For information see <xref href="XREF"></xref>.</p>
 </section>
 <section id="syntax"><title>Syntax</title>
  <codeblock>
  </codeblock></section>
 <section id="example"><title>Example</title>
  <codeblock>
  </codeblock>
 </section>
</refbody>
</reference>
'''

#   index.html
#      namespaces.html
#          classlist.html
#       		class1.html
#       			class1ctor.html
#         			class1methods.html
#          			class1props.html
#         			class1events.html
#       		class2.html
#       			class2ctor.html
#         			class2methods.html
#          			class2props.html
#         			class2events.html

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

def findItem (name, itemList):
	if name in [item.title for item in itemList]:
		return item

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

class Bind(object):
	def __init__(self, path, converter=None, first=False):
		'''
		path -- xpath to select elements
		converter -- run result through converter
		first -- return only first element instead of a list of elements
		'''
		self.path = path
		if converter is None:
			converter = lambda x: x
		self.converter = converter
		self.first = first

	def __get__(self, instance, owner=None):
		res = instance._elem.xpath(self.path)
		if self.first:
			return self.converter(res[0])
		return [self.converter(r) for r in res]

class Data(object):
	def __init__(self, elem):
		self._elem = elem

class APIDocEntity(Data):
	#use xpath text() to get text
	title = Bind('@name')
	#get text via converter
	summary = Bind('summary', converter=lambda x: x.text,  first=True)
	prop = Bind('param/text()', first=True)
	prop_name = Bind('param/@name', first=True)
	returns = Bind('returns', first=True)
	exception = Bind('exception', first=True)

class APIdoxydb(Data):
	#bind result to custom class which is itself a mapping
	members = Bind('//member', APIDocEntity)

class APINamespace():
	def __init__(self, name):
		self.name = name
		self.id = randomword(16)
		self.classes = []

	def addClass(self, classobj):
		self.classes.append(classobj)

	def getid(self):
		return self.id

	def getClasses(self):
		return self.classes

	def getClass(self, name):
		return findItem (name, self.classes)

class APIClass():
	def __init__(self, name, ns, super):
		self.name = name
		self.id = randomword(16)
		self.summary = ''
		self.ctor = []		#constructor
		self.methods = []
		self.props = []
		self.enumtypes = []
		self.subclasses = []
		self.namespace = ns
		self.superclass = super

	def addSummary(self, summary):
		self.summary = summary

	def addMethod(self, method):
		self.methods.append(method)

	def addSubClass(self, subclass):
		self.subclasses.append(subclass)

	def addctor(self, name, desc):
		self.ctor.append([name, desc])

	def addProp(self, enum):
		self.props.append(enum)

	def addenumType(self, enumType):
		self.enumtypes.append(enumType)

	def getid(self):
		return self.id

	def getName(self):
		return self.name

	def getNamespace(self):
		return self.namespace

	def getProp(self, name):
		return findItem (name, self.params)

	def getenumType(self, name):
		return findItem (name, self.enumtypes)

	def getSubClasses(self):
		return self.subclasses

	def getSubClass(self, name):
		return findItem (name, self.subclasses)

	def getSuperClass(self):
		return self.superclass

	def writeDITA (self):
		fp = open('out/' + self.name + '.dita', 'w')
		fp.write(APIDITARefTemplate % (self.id, self.name, self.summary))
		fp.close()

class APIProp():
	def __init__(self, name, desc):
		self.name = name
		self.id = randomword(16)
		self.desc = desc

	def getid(self):
		return self.id

class APIEnumType():
	def __init__(self, name):
		self.name = ''
		self.id = randomword(16)
		self.desc = desc
		self.enumvals = []

	def addVal(self, val, desc):
		self.enumvals.append([val,desc])

XML = 'TestT.xml'	  # change this

doxydb = APIdoxydb(lxml.etree.parse(XML))

# clean up input before transformation
for member in doxydb.members:
	try:
		member.summary
	except:
		print 'WARNING: No summary for ' + member.title[0]
		member.summary = 'SUMMARY'

# Identify and save namespaces, classes, methods and properties

# dictionary of namespaces and contained classes as strings
namespacedict = {}
# dictionary of namespaces and namespace objects
nsdict = {}
# dictionary of classes and classobj objects
classdict = {}

for member in doxydb.members:
	print member.title[0]
	try:
		# expecting a string for member.title[0] such as, for e.g.:
		# T:DeviceInsightApi.InputData
		# M:DeviceInsightApi.InputData.GetCollectorPayloadField(System.String)
		# P:DeviceInsightApi.InputData.HttpHeaderMap
		# F:DeviceInsightApi.TrackingPreference.ENABLED

		title = re.split(":?", member.title[0], 1)
		if title[0] ==  'T': # class

			# split member name into strings
			hierstruct = re.split("\.",title[1])
			namespace = hierstruct[0]
			classl = hierstruct[1:len(hierstruct)]

			if namespace not in namespacedict:
				print 'Creating namespace object for ' + namespace
				namespacedict[namespace] = classl
				nsdict[namespace] = APINamespace(namespace)
			else:
				namespacedict[namespace].append(classl)

			if not classl[0] in classdict.keys():
				classobj = APIClass(classl[0], namespace, '')
				classdict[classl[0]] = classobj
			else:
				classobj = classdict[classl[0]]

			classobj.addSummary(member.summary)
			nsdict[namespace].addClass(classobj)

			parentclass = classobj
			for i in range(1,len(classl)):
				if not parentclass.getSubClass(classl[i]):
					parentclass.addSubClass(classl[i])
					parentclass = APIClass(classl[i], namespace, classl[i-1])

		elif title[0] == 'M': # method call

			# Methods usually have arguments - split into strings
			# as [methcall,args,ignore]
			[methcall,args,ignore] = re.split("\(|\)",title[1])

			# split method call to obtain class hierarchy
			classhier = re.split("\.",methcall)
			hierdepth = len(classhier)
			classobj = findItem(classhier(hierdepth-2))
			print classobj

		elif title[0] ==  'F': # enumval
			print member

		elif title[0] ==  'P': # property
			print member
		else:
			print 'WARNING: Unrecognized member ignored: ' + member.title[0]
	except:
		print 'WARNING: member has no title'
		member.title[0] = 'TITLE'

# Write out topic files	for all classes
for namespace in nsdict.keys():
	classobjs = nsdict[namespace].getClasses()
	for classobj in classobjs:
		classobj.writeDITA()

# Write out top level DITA topic file containing namespace list
map = lxml.etree.fromstring(API_NSDITATemplate)
ul = map.find('.//ul')
for namespace in nsdict.keys():
	item = lxml.etree.SubElement(ul,'li')
	item.text = namespace

fp = open('out/nsindex.dita', 'w')
lxml.etree.ElementTree(map).write(fp, pretty_print=True)
fp.close()

# Write out the top map file

for namespace in nsdict.keys():
	map = lxml.etree.fromstring(API_NSDITAmapTemplate)
	for classobj in classobjs:
		cname = classobj.getName()
		if classobj.getNamespace() == namespace and not classobj.getSuperClass():
			mr = lxml.etree.SubElement(map,'mapref')
			mr.attrib['href'] = cname + ".ditamap"
			tr.attrib['navtitle'] = cname

	fp = open('out/'+ namespace + '.ditamap', 'w')
	lxml.etree.ElementTree(map).write(fp, pretty_print=True)
	fp.close()


API_classlistDITAmapTemplate = '''
<map xml:lang="en-us" title="API Reference Manual - Class %s">
<topicref href="%s_clist.dita" navtitle="%s"></topicref>
</map>
'''

# Write out map file for each class

for namespace in nsdict.keys():
	classobjs = nsdict[namespace].getClasses()
	for classobj in classobjs:
		cname = classobj.getName()
		if not classobj.getSuperClass():
			map = lxml.etree.fromstring(API_classDITATemplate % classobj.getName())
			for subclass in classobj.getSubClasses():
				tr = lxml.etree.SubElement(map,'topicref')
				tr.attrib['href'] = subclass + ".dita"
				tr.attrib['navtitle'] = subclass
			fp = open('out/'+ cname + '.ditamap', 'w')
			lxml.etree.ElementTree(map).write(fp, pretty_print=True)



