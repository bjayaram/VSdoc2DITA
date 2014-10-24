#!/usr/bin/env python

#import untangle
import random
import re
import string
import os

import lxml.etree

from ditatemplates import *

#
# sectionTemplate = '''
#  <section id = "%s">
#   <title>%s</title>
#    %s
#  </section>
# '''
#
# sectiondivTemplate = '''
#  <sectiondiv id = "%s">
#    %s
#  </sectiondiv>
# '''
#
# APIDITARefTemplate = '''
# <!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "../dtd/reference.dtd">
# <reference xml:lang="en-us" id="%s">
# <title>%s</title>
# <shortdesc></shortdesc>
# <prolog>
#  <metadata>
#   <keywords>
#   </keywords>
#  </metadata>
# </prolog>
# <refbody>
# <!-- Summary -->
# %s
# <!-- Methods -->
# %s
# <!-- Properties -->
# %s
# <!-- Constructors -->
# %s
# <!-- Fields -->
# %s
# </refbody>
# </reference>
# '''
#
# #   index.html
# #      namespaces.html
# #          classlist.html
# #       		class1.html
# #       		class2.html
#
#
# API_topDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual">
# <topicref href="index.dita" navtitle="My Project"></topicref>
# <mapref href="namespaces.ditamap">
# </mapref>
# </map>
# '''
#
# API_NSDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual - Namespaces">
# <topicref href="nsindex.dita" navtitle="Namespaces">
# </topicref>
# </map>
# '''
# API_NSDITATemplate = '''
# <!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "../dtd/topic.dtd">
# <topic xml:lang="en-us" id="%s">
# <title>API Reference Manual - Namespaces</title>
# <shortdesc>This is a list of namespaces</shortdesc>
# <body>
# <ul>
# </ul>
# </body>
# </topic>
# '''
#
# API_classesDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual - Class %s">
# <topicref href="%s_clist.dita" navtitle="%s"></topicref>
# </map>
# '''
#
# API_classDITATemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="%s">
# </map>
# '''
#
# API_classctorDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual Class Constructor">
# </map>
# '''
#
# API_methodsDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual Class Members">
# </map>
# '''
#
# API_propertiesDITAmapTemplate = '''
# <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
# <map xml:lang="en-us" title="API Reference Manual Class Properties">
# </map>
# '''

def findItem (name, itemList):
    if name in [item.title for item in itemList]:
        return item

def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

# process summary element and return valid DITA fragment
def summary2DITA(summary):

    # replace first <code> element by <codeblock>, if found
    code = summary.find('code')
    if code is not None:
        # remove <br> elements within <code>, if found
        brlist = code.findall('br')
        for br in brlist:
            br.getparent().remove(br)
        code.tag = 'codeblock'

    # replace subsequent <code> elements by <codeph>, if found
    codel = summary.findall('code')
    if codel is not None:
        for code in codel:
            code.tag = 'codeph'

    # replace <br> elements by <p>, if found
    brlist = summary.findall('br')
    if brlist is not None:
        for br in brlist:
            br.tag = 'lines'

    # create Summary section
    summary = lxml.etree.tostring(summary).replace('<code>', '<codeph>').replace('</code>', '</codeph>')

    summary = summary.replace('<summary>', '<p>').replace('</summary>', '</p>')
    return summary

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
        if self.first and res[0] is not None:
            return self.converter(res[0])
        return [self.converter(r) for r in res]

class Data(object):
    def __init__(self, elem):
        self._elem = elem

class APIDocEntity(Data):
    #use xpath text() to get text
    title = Bind('@name')
    text = Bind('text()')
    #get text via converter
    summary = Bind('summary', first=False)
    params = Bind('param', first=False)
    returns = Bind('returns', first=False)
    exceptn = Bind('exception', first=False)

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
        return findItem(name, self.classes)

class APIClass():
    def __init__(self, name, ns, supclass):
        self.name = name
        self.id = randomword(16)
        self.summary = ''
        self.ctors = []		#constructors
        self.methods = []
        self.props = []
        self.enumtypes = []
        self.subclasses = []
        self.namespace = ns
        self.superclass = supclass

    def addSummary(self, summary):
        self.summary = summary

    def addMethod(self, method):
        self.methods.append(method)

    def addSubClass(self, subclass):
        self.subclasses.append(subclass)

    def addCtor(self, ctor):
        self.ctors.append(ctor)

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
        return findItem(name, self.params)

    def getenumType(self, name):
        return findItem(name, self.enumtypes)

    def getSubClasses(self):
        return self.subclasses

    def getSubClass(self, name):
        return findItem(name, self.subclasses)

    def getSuperClass(self):
        return self.superclass

    def writeDITA(self):

        fname = self.name + '.dita'
        if '.' in self.name:
            fname = self.name.rsplit('.', 1)[1] + '.dita'

        fp = open('out/' + fname, 'w')

        print 'Writing DITA file ' + '\'' + fname + '\''

        summarysec = sectionTemplate % (randomword(5), 'Summary', summary2DITA(self.summary[0]))

        # create Methods section
        methodsec = ''
        for meth in self.methods:
            methodsec += meth.getDITA()

        # create Properties section
        propsec = ''

        # create Constructor section
        ctorsec = ''
        for ctor in self.ctors:
            ctorsec += ctor.getDITA()

        # create Fields section
        fieldsec = ''

        fp.write(APIDITARefTemplate % (self.id, self.name, summarysec, methodsec, propsec, ctorsec, fieldsec))
        fp.close()


# process param elements and return valid DITA fragment
def params2DITA(params):

    paramsec = '<dl>'
    for param in params:
        # replace first <code> element by <codeph>, if found
        code = param.find('code')
        if code is not None:
            code.tag = 'codeph'

        # replace <br> elements by <p>, if found
        brlist = param.findall('br')
        if brlist is not None:
            for br in brlist:
                br.tag = 'p'
        # create parameter entry
        paramsec += paramentry % (param.attrib['name'], param.text)

    paramsec += '</dl>'
    return paramsec

# process exception element and return valid DITA fragment
def exc2DITA(exceptn):

    excepdl = '<b>Exception</b>'
    excepdl += '<dl>'
    cref = exceptn[0].attrib['cref'].split('.', 1)[1]
    # create parameter entry
    excepdl += paramentry % (cref, exceptn[0].text)
    excepdl += '</dl>'
    return excepdl

class APICtor():
    def __init__(self, classobj, call, summary, params, exceptn):
        self.classobj = classobj    # string
        self.call = call    # string
        self.id = randomword(5) # string
        # summary is a XML fragment
        self.summary = summary
        # params is a dict with name and associated text
        self.params = params
        # exception is a XML fragment
        self.exception = exceptn

    def getid(self):
        return self.id

    def getDITA(self):

        secdivs = sectiondivTemplate % (randomword(5), summary2DITA(self.summary[0]))
        secdivs += sectiondivTemplate % (randomword(5), params2DITA(self.params))
        if self.exception:
            secdivs += sectiondivTemplate % (randomword(5), exc2DITA(self.exception))

        return sectionTemplate % (randomword(5), self.call, secdivs)

class APIMethod():
    def __init__(self, name, argstr, summary, params, returns, exception):
        self.name = name    # string
        self.args = argstr    # string
        self.id = randomword(5) # string
        # summary is a XML fragment
        self.summary = summary
        # params is a dict with name and associated text
        self.params = params
        # returns is a XML fragment
        self.returns = returns
        # exception is a XML fragment
        self.exception = exception

    def getid(self):
        return self.id

    def getSummary(self):
        return self.summary

    def getparams(self):
        return self.params

    def getDITA(self):

        secdivs = sectiondivTemplate % (randomword(5), summary2DITA(self.summary[0]))
        if self.params:
            secdivs += sectiondivTemplate % (randomword(5), params2DITA(self.params))

        return sectionTemplate % (randomword(10), self.name, secdivs)

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
        self.enumvals.append([val, desc])

XML = 'TestM.xml'	  # change this

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
        if title[0] == 'T':  # class

            # split member name into strings
            hierstruct = re.split("\.", title[1])
            numlevels = len(hierstruct)

            # TODO: handle the case when class is in global scope (i.e., no namespace)
            # For now, ignore this case
            if numlevels == 1:
                continue

            classname = re.split("\.", title[1], 1)[1]

            namespace = hierstruct[0]
            if namespace not in namespacedict:
                print 'Creating namespace object for ' + namespace
                nsdict[namespace] = APINamespace(namespace)
                namespacedict[namespace] = [classname]
            else:
                namespacedict[namespace].append(classname)

            if classname in classdict.keys():
                print 'Duplicate entry for class ' + classname + ' - Ignored'
                continue
            else:
                supclass = ''
                if numlevels > 2:
                    supclass = classname.rsplit('.', 1)[0]
                classobj = APIClass(classname, namespace, supclass)
                classdict[classname] = classobj

            classobj.addSummary(member.summary)
            nsdict[namespace].addClass(classobj)

        elif title[0] == 'M':  # method call

            if '#ctor' in title[1]:

                # split into call and args to constructor
                [call, args, ignore] = re.split("\(|\)", title[1])
                call = call.rsplit('.#')[0]
                classname = call.split('.')[-1]
                classobj = classdict[classname]

                ctor = APICtor(classobj, call + '(' + args + ')', member.summary, member.params, member.exceptn)
                classobj.addCtor(ctor)

            else:

                # Methods usually have arguments - split into strings
                # as [methcall,args,ignore]
                try:
                    [methcall, args, ignore] = re.split("\(|\)", title[1])
                except ValueError:
                    methcall = title[1]

                methcall = re.split("\.", methcall, 1)[1]
                methname = methcall.rsplit('.')[-1]

                classname = methcall.replace('.' + methname, '')
                classobj = classdict[classname]

                # This is a hack to handle unhandled exception in Python
                if 'Traceback (most recent call last)' in member.exceptn:
                    member.exceptn = ''

                methobj = APIMethod(methname, args, member.summary, member.params, member.returns, member.exceptn)
                classobj.addMethod(methobj)

        elif title[0] == 'F':  # enumval
            print member

        elif title[0] == 'P':  # property
            print member
        else:
            print 'WARNING: Unrecognized member ignored: ' + member.title[0]
    except:
        print 'WARNING: member has no title'
        member.title[0] = 'TITLE'

if not os.path.exists('out'):
    os.mkdir('out')

# Write out topic files	for all classes
for namespace in nsdict.keys():
    classobjs = nsdict[namespace].getClasses()
    classobjs.sort(key=lambda x: x.name)
    for classobj in classobjs:
        classobj.writeDITA()

# Write out top level DITA topic file containing namespace list
map = lxml.etree.fromstring(API_NSDITATemplate % randomword(16))
ul = map.find('.//ul')
for namespace in nsdict.keys():
    item = lxml.etree.SubElement(ul, 'li')
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
            mr = lxml.etree.SubElement(map, 'mapref')
            mr.attrib['href'] = cname + ".ditamap"
            mr.attrib['navtitle'] = cname

    fp = open('out/' + namespace + '.ditamap', 'w')
    lxml.etree.ElementTree(map).write(fp, pretty_print=True)
    fp.close()

# Write out map file for each class

for namespace in nsdict.keys():
    classobjs = nsdict[namespace].getClasses()
    for classobj in classobjs:
        cname = classobj.getName()
        if '.' in cname:
            cname = cname.rsplit('.', 1)[1]
        map = lxml.etree.fromstring(API_classDITATemplate % classobj.getName())
        tr = lxml.etree.SubElement(map, 'topicref')
        tr.attrib['href'] = cname + ".dita"
        tr.attrib['navtitle'] = cname
        if classobj.getSuperClass():
            for subclass in classobj.getSubClasses():
                tr = lxml.etree.SubElement(map, 'topicref')
                tr.attrib['href'] = subclass + ".dita"
                tr.attrib['navtitle'] = subclass
        #else:

        print 'Writing DITAMAP file: ' + cname + '.ditamap'
        fp = open('out/' + cname + '.ditamap', 'w')
        lxml.etree.ElementTree(map).write(fp, pretty_print=True)
        fp.close()

#DITAdb = DITAtopicdb(lxml.etree.fromstring(APIDITARefTemplate))

# o = untangle.parse(XML)
#
# for member in o.doc.members.member:
#	  name = member['name']
#
#	  print '<topic id=%s>\n<title>%s</title>' % randomword(8), name
#
#	  summary = member.summary
#	  print '<shortdesc>%s</shortdesc>' % summary
