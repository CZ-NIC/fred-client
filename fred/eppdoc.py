#!/usr/bin/env python
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# This module owns functions and values needed for build EPP document.
"""Eppdoc module owns base class of the EPP XML Message.
This class shares function needed for create XML document.
There is also defined XMLNS constants and schema version.

This class is parent for classes what manage XML commands
and XML server's answers.

Second class is Data what build XML elements to the python
discitionary.
"""
import os, re
import xml.dom.minidom
try:
    from xml.dom.ext import PrettyPrint
except ImportError:
    PrettyPrint = None
from xml.dom import Node
import StringIO

#========================================================
# Namespaces for  EPP
# shared for all templates
# Defaults - can overwrite by values from config or command line option
#========================================================
SCHEMA_PREFIX = 'http://www.nic.cz/xml/epp/'
VERSION_CONTACT  = '1.6'
VERSION_DOMAIN   = '1.4'
VERSION_NSSET    = '1.2'
VERSION_KEYSET   = '1.3'
VERSION_ENUMVAL  = '1.2'
VERSION_FRED     = '1.5'
VERSION_VERSION  = '1.0'

obj_uri = "urn:ietf:params:xml:ns:"
xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance"
default_encoding = 'utf-8' # default document output encoding
#========================================================

class Message:
    'Struct maintaining DOM object and process errors.'

    def __init__(self, manager):
        self.manager = manager
        self.dom = None         # DOM object
        self.errors = []        # [(code, value, reason), ...]
        self.encoding = default_encoding
        self._cr = '\n' # new line
        self._dct = {}  # parsed parameters from command line
        self._command_params = {} # struct of command parameters
        self._verbose = 1  # verbose interactive params input
        self.server_disclose_policy = 1 # Data collection policy: Access; default: 1 - disclosed
        self._handle_ID = '' # keep object handle (ID)
        self.schema_version = {
            'contact': VERSION_CONTACT, 
            'nsset':   VERSION_NSSET, 
            'keyset':  VERSION_KEYSET, 
            'domain':  VERSION_DOMAIN, 
            'enum':    VERSION_ENUMVAL, 
            'fred':    VERSION_FRED, 
            'epp':     VERSION_VERSION,
        }
        self.set_schema_version('epp', VERSION_VERSION)
        self.getresults_loop = 0 # indicate if client starts messages loop
        self.readline = None

    def get_schema_names(self):
        return self.schema_version.keys()

    def set_schema_version(self, key, value):
        'Set schema version'
        self.schema_version[key] = value
        if key == 'epp':
            self.xmlns = "%sepp-%s"%(obj_uri, value)
            self.xsi_schemaLocation = "%s epp-%s.xsd"%(self.xmlns, value)

    def get_objURI(self):
        'Returns the list of the objURI namesapces.'
        return ['%s%s-%s'%(SCHEMA_PREFIX, name, self.schema_version[name]) 
                    for name in ('contact','nsset','domain', 'keyset')]


    def get_extURI(self):
        'Returns the list of the extURI namesapces.'
        return ['%senumval-%s'%(SCHEMA_PREFIX, self.schema_version['enum'])]


    def reset(self):
        self.__reset_dom__()
        self.errors = []
        self._handle_ID = ''
        self._dct = {}  # parsed parameters from command line
        self.getresults_loop = 0

    def get_params(self):
        'Returns dict of the command params.'
        return self._dct
    def set_params(self, params):
        'Put dict of the command params.'
        self._dct = params

    def __reset_dom__(self):
        #if self.dom:
        #    print "type:",type(self.dom)
        #    print self.dom.toxml()
        #    self.dom.unlink()
        self.dom = None

    def get_xml(self):
        'Build XML form DOM.'
        xml=''
        if self.dom:
            self.dom.normalize()
            #if PrettyPrint:
            # (PrettyPrint is disabled be cause of wrong result: "&lt;value>")
            if 0: 
                f = StringIO.StringIO()
                PrettyPrint(self.dom, f, self.encoding)
                f.seek(0,0)
                xml = f.read()
            else:
                # Kdyz chybi funkce PrettyPrint()
                #xml = self.dom.toprettyxml('', '', self.encoding)
                xml = self.dom.toxml(self.encoding)
        # hook parametru standalone
        return re.sub('(<?xml .+?)\?>','\\1 standalone="no"?>',xml, re.I)

    def join_errors(self, errors):
        self.errors.extend(errors)

    def is_error(self):
        return len(self.errors)

    def fetch_errors(self, sep=None):
        ret = self.get_errors(sep)
        self.errors=[]
        return ret

    def get_errors(self, sep=None):
        if sep==None: sep=self._cr
        errors=['[%d] (%s) %s'%(code,str(value),reason) for code,value,reason in self.errors]
        return sep.join(errors)

    def get_results(self, sep=None):
        #errors,xml_epp
        if sep==None: sep=self._cr
        return self.get_errors(sep), self.get_xml()

    def append_attribNS(self, node, attribs, ns=''):
        """Append attributes into top node.
        IN: attribs ((name,value), (name,value), ....)
        """
        for n,v in attribs:
            node.setAttributeNS(ns,n,v)

    def load_xml_doc(self, filepath):
        'Load XML file. Used for EPP templates.'
        try:
            xml_doc = open(filepath).read()
        except IOError, (no,msg):
            # when template missing
            self.errors.append((2000, filepath, 'IOError: %d, %s'%(no,msg)))
            xml_doc = None
        return xml_doc

    def parse_xml(self, xml_doc):
        'Parse XML into DOM object.'
        self.__reset_dom__()
        try:
            self.dom = xml.dom.minidom.parseString(xml_doc)
            self.dom.normalize()
        except xml.parsers.expat.ExpatError, msg:
            # when XML is invalid
            self.errors.append((2001, None, _T('Invalid XML document. ExpatError: %s'%msg)))
        except LookupError, msg:
            # invalid or unknown encoding
            self.errors.append((2001, None, _T('Document has wrong encoding. LookupError: %s'%msg)))

    def join_top_attribs(self):
        ns=(
            ('xmlns',self.xmlns),
            ('xmlns:xsi',xmlns_xsi),
            ('xsi:schemaLocation',self.xsi_schemaLocation),
        )
        self.append_attribNS(self.dom.documentElement, ns)

    def create(self, top_name='epp'):
        'Create empty EPP DOM.'
        self.__reset_dom__()
        # Lasta parameter (0) define DTD and if it is 0 than document has not DTD.
        # ("jmeny_prostor","korenovy-element",0)
        self.dom = xml.dom.getDOMImplementation().createDocument('',top_name,0)
        self.join_top_attribs()

    def new_node_by_name(self, master_name, name, value=None, attribs=None):
        "Create new node by Tag Name and attach to the Master Node. attribs=((name,value), (name,value), ....)"
        master = self.dom.getElementsByTagName(master_name)
        if type(master) == xml.dom.minicompat.NodeList:
            # If valus is list, than take always last node.
            if len(master): master = master[-1]
        if master:
            node=self.new_node(master, name, value, attribs)
        else:
            # if upper node doesn't exist, sahll we stop it?
            self.errors.append((2001, None, _T("Internal error: Master node '%s' doesn't exist."%master_name)))
            raise "Internal Error: Master node '%s' doesn't exist."%master_name # TODO ????
            node=None # TODO ????
        return node
        
    def new_node(self, master, name, value=None, attribs=None):
        "Create new node and attach to the master node. attribs=((name,value), (name,value), ....)"
        if not master:
            raise "ERROR: new_node(%s) Master missing!"%name # TODO ????
        node = self.dom.createElement(name)
        if type(master) == xml.dom.minicompat.NodeList:
            master[0].appendChild(node)
        else:
            master.appendChild(node)
        if value:
            # strip backslashes before ' and " and \\
            value = value.replace(r"\'", "'").replace(r'\"', '"').replace(r'\\ '[:-1], r'\ '[:-1])
            try:
                node.appendChild(self.dom.createTextNode(value))
            except TypeError, msg:
                print "FredClient Internal Error: ",name,type(value),value
                raise 'TypeError:',msg
        if attribs:
            self.append_attribNS(node, attribs)
        return node

    def get_element_node(self, node):
        'Return first node of type Node.ELEMENT_NODE or None.'
        ret=None
        for n in node.childNodes:
            if n.nodeType == Node.ELEMENT_NODE:
                ret=n
                break
        return ret

    def get_epp_command_name(self):
        """Returns top EPP command name. 
        Level 1: epp.greeting
        Level 1: epp.command 
        Level 2:     info, check, create, ....
        Level 3:        contact:create
        Level 4:        fred:sendauthinfo, fred:creditinfo, fred:test
        """
        name = ''
        if self.dom:
            # Level 1.
            node = self.get_element_node(self.dom.documentElement)
            if not node: return name
            name = node.nodeName.lower()
            if name in ('command','extension'):
                # Level 2.
                node = self.get_element_node(node)
                if not node: return name
                name = node.nodeName.lower()
                if name not in ('login','logout','poll'):
                    # Level 3.
                    node = self.get_element_node(node)
                    if not node: return name
                    name = node.nodeName.lower()
                    if name == 'fred:sendauthinfo':
                        # Level 4.
                        node = self.get_element_node(node)
                        if not node: return name
                        name = node.nodeName.lower()
                    elif name == 'fred:creditinfo':
                        name = 'credit_info'
                    elif name == 'fred:test':
                        name = 'technical_test'
        return name

    def get_check_names(self, type):
        'Returs list of names from object:check commands. It can be used for sorting.'
        names=[]
        if not self.dom: return names
        node_name = type == 'domain' and 'domain:name' or '%s:id'%type
        # <command> <check> <domain:check> <domain:name>
        for node in self.dom.getElementsByTagName(node_name):
            if node.nodeType == Node.ELEMENT_NODE and len(node.childNodes):
                names.append(node.childNodes[0].nodeValue)
        return names
        
    #====================================
    # Parse to Dict / Data class
    #====================================
    def __create_data__(self, el, current_obj, is_class):
        "Create class object represents DOM struct of EPP document."
        # 1. buid node names and count them
        # 2. create node or list along by number
        # 3. Walk recursively all nodes and append values
        # 4. appends help
        #....................................
        # attr
        #....................................
        attr=[]
        for a in el.attributes.values():
            attr.append((a.name, a.value)) # <xml.dom.minidom.Attr instance>
        if len(attr):
            if is_class:
                current_obj._attr = attr
            else:
                append_to_dict(current_obj,'attr',attr)
        #....................................
        # data
        #....................................
        for e in el.childNodes:
            if e.nodeType != Node.ELEMENT_NODE:
                if e.nodeValue:
                    val = e.nodeValue.strip()
                    if val:
                        if is_class:
                            current_obj._data += val
                        else:
                            append_to_dict(current_obj,'data',val)
        #....................................
        # next nodes
        #....................................
        # *** 1. ***
        nodes = [e.nodeName.encode('ascii') for e in el.childNodes if e.nodeType == Node.ELEMENT_NODE]
        # *** 2. ***
        for name, count in [(name, nodes.count(name))for name in set(nodes)]:
            if count > 1:
                if is_class:
                    current_obj.__dict__[name] = [None]*count
                else:
                    current_obj[name] = [None]*count
            else:
                if is_class:
                    current_obj.__dict__[name] = Data(current_obj)
                    current_obj.__dict__[name].__doc__ = name
                else:
                    current_obj[name] = {}
        # *** 3. ***
        for e in el.childNodes:
            if e.nodeType == Node.ELEMENT_NODE:
                name = e.nodeName.encode('ascii')
                if is_class:
                    child_obj = current_obj.__dict__[name]
                else:
                    child_obj = current_obj[name]
                if type(child_obj) == list:
                    pos = child_obj.index(None)
                    if is_class:
                        child_obj[pos] = Data(current_obj)
                        child_obj[pos].__doc__ = name
                    else:
                        child_obj[pos] = {}
                    child_obj = child_obj[pos]
                self.__create_data__(e, child_obj, is_class)

    def create_data(self, is_class=None):
        "Create object representing DOM data"
        if not self.dom: return None
        if is_class:
            root = Data(None)
            root.__doc__ = 'epp'
        else:
            root = {}
        self.__create_data__(self.dom.documentElement, root, is_class)
        if is_class: root.__make_data_help__()
        return root


#-------------------------------------------------
# Support for read XML.DOM nodes
#-------------------------------------------------
def get_node_values(nodes, name):
    'Returns all values of nodes. Retval is in format [{"data":"value"},...]'
    retval = []
    for node in nodes:
        for element in node.getElementsByTagName(name):
            for e in element.childNodes:
                if e.nodeType == Node.ELEMENT_NODE: continue
                retval.append({'data':e.nodeValue.strip()})
    return retval

def get_node_attributes(nodes, name):
    'Returns all attribudes of nodes. Retval is in format [{"attr":"value"},...]'
    retval = []
    for node in nodes:
        for e in node.attributes.values():
            retval.append((e.name, e.value.strip()))
    return {'attr':retval}
#-------------------------------------------------

        
class Data:
    """Data class. Have members along to a EPP DOM tree.
    Access to member values write member.data or member.attr.
    For example: 
        epp.svcMenu.data
        epp.svcMenu.attr
    
    Explain class struct you simply write object member name.
    For example member epp.svcMenu displays:
<CLASS:
    data:
    attr: []
    nodes: svcMenu (lang*, version*^)
>
    Member names have this decoration:
    * - member has data
    ^ - member has attributes
    """
    def __init__(self, parent):
        # ALERT! Names 'attr' and 'data' are reserved for internal use.
        self._parent = parent
        self._attr = []
        self._data = ''
    def __getattr__(self, key):
        # Avoid AttributeError
        if key in ('attr','data'):
            # class members
            ret = self.__dict__['_%s'%key]
        # ........................................
        # Here we can disable exception AttributeError and give back common behavior.
##        else:
##            ret = super.__getattr__(key)
        # ........................................
        # Here we can disable exception AttributeError
        # (need make comment previous two lines: else a ret = ...)
        elif key[:2]=='__':
            # internal calls
            ret = super.__getattr__(key)
        else:
            # no AttributeError
            ret = self.__dict__.get(key, "[NOT EXISTS]")
        # ........................................
        return ret
    def __repr__(self):
        return '<CLASS:\n\tdata: %s\n\tattr: %s\n\tnodes: %s\n>'%(self._data, self._attr, self.__doc__)

    def __make_data_help__(self):
        "Make help in format 'name: (name, name: (name[3], name), name)'"
        doc = []
        if self._data: self.__doc__ += '*' # indicator item has got values
        if self._attr: self.__doc__ += '^' # indicator item had got attributtes
        for key in self.__dict__:
            if key[0] == '_': continue
            member = self.__dict__[key]
            if type(member)==list:
                subname = '%s[%d]'%(key,len(member))
                subdoc=[]
                for item in member:
                    subitem = item.__make_data_help__()
                    if subitem != key: subdoc.append(subitem) # element, what is empty doesn't need join
                if len(subdoc):
                    doc.append('%s: (%s)'%(subname,', '.join(subdoc)))
                else:
                    doc.append(subname)
            else:
                doc.append(member.__make_data_help__())
        if len(doc):
            self.__doc__ = '%s: (%s)'%(self.__doc__, ', '.join(doc))
        return self.__doc__


def append_to_dict(d,key,val):
    "Append or extend values along to insert type."
    if d.has_key(key):
        if type(d[key]) in (str,unicode):
            d[key] += val
        else:
            d[key].extend(val)
    else:
        d[key] = val

def get_dct_attr(dict_data, names, attr_name, sep=u'\n'):
    "Returns attribute value of the key name in names list."
    return get_dct_value(dict_data, names, sep, attr_name)

def get_value_from_dict(dct, names):
    """Returns safetly value form dict (treat missing keys).
        Parametr names can by str or list ro tuple.
    """
    scope = dct
    name = names
    if type(names) in (list, tuple) and len(names)>1:
        for name in names[:-1]:
            if scope.get(name,None):
                scope = scope[name]
            else:
                return None
        name = names[-1]
    return scope.get(name,None)
    
def get_dct_values(dict_data, names, attr_name=''):
    "Returns raw data or attribute from names queue."
    ret=[]
    if type(names) not in (tuple,list):
        names = (names,)
    if len(names):
        for i in range(len(names)):
            name = names[i]
            if name in ('data','attr'): continue
            if type(dict_data) is not dict:
                ret.append('%s %s'%(_T('Internal error: Value is not dict type:'),str(dict_data)))
                continue
            if not dict_data.get(name,None): continue
            inames = names[i+1:]
            if type(dict_data[name]) in (list,tuple):
                for item in dict_data[name]:
                    vals = get_dct_values(item, inames, attr_name)
                    if vals: ret.extend(vals)
            else:
                vals = get_dct_values(dict_data[name], inames, attr_name)
                if vals: ret.extend(vals)
    else:
        if type(dict_data) == dict:
            if attr_name:
                vals = dict_data.get('attr',u'')
                if vals:
                    for k,v in vals:
                        if k==attr_name:
                            if v: ret.append(v)
                            break
            else:
                vals = dict_data.get('data',u'')
                if vals: ret.append(vals)
        else:
            ret.append(dict_data)
    return ret

def get_dct_value(dict_data, names, sep=u'\n', attr_name='', defval=u''):
    "Returns value as a string from names queue."
    retvals = get_dct_values(dict_data, names, attr_name)
    if type(retvals) in (list,tuple): retvals = sep.join(retvals)
    if retvals == '': retvals = defval
    return retvals

def __pfd__(dict_data,color=0,indent=0):
    "Prepare dictionary data for display."
    if color:
        patt=('${BOLD}%s:${NORMAL} %s', '[%s]', '%s${GREEN}%s${NORMAL}:','%s${GREEN}%s${NORMAL}: %s')
    else:
        patt=('%s: %s', '[%s]', '%s%s:', '%s%s: %s')
    body=[]
    if type(dict_data) in (list,tuple):
        for d in dict_data:
            rows = __pfd__(d,color,indent)
            if len(rows): body.extend(rows)
    else:
        if indent and dict_data.has_key('attr'):
            # attributs, but not from root
            attr=[]
            for k,v in dict_data['attr']:
                attr.append(patt[0]%(k,v))
            body.append(patt[1]%'; '.join(attr))
        # data
        if dict_data is None:
            return body
        if dict_data.has_key('data'): body.append(dict_data['data'])
        # other children nodes    
        ind = ' '*indent
        for key in dict_data.keys():
            # descendents nodes
            if key in ('attr','data'): continue
            if dict_data[key] == {}:
                # display empty node
                body.append(patt[2]%(ind,remove_ns(key)))
            else:
                rows = __pfd__(dict_data[key],color,indent+4)
                if len(rows):
                    if len(rows)>1:
                        # more lines [key]: and next lines with values
                        body.append(patt[2]%(ind,remove_ns(key)))
                        for r in rows:
                            body.append('%s%s'%(ind,r))
                    else:
                        # one line - [key]: value
                        body.append(patt[3]%(ind,remove_ns(key),rows[0]))
    return body


def split_prexis_name(qname):
    "Split qualified name to prefix and local-name"
    try:
        retval = re.match('([^:]+):(.+)', qname).groups()
    except AttributeError:
        retval = '', qname # no any xmlns prefix
    return retval


def split_qattr_key(attr_name):
    """Split the attribute qualified name to (prefix, localname).
    Prefix is always required, localname is optional.
    """
    prefix, localname = split_prexis_name(attr_name)
    if prefix == '':
        localname, prefix = prefix, localname # localname missing
    return prefix, localname


def remove_ns(name):
    "remove namespace from xml element"
    return re.sub('.+:', '', name)

def prepare_display(dict_data,color=0):
    "Prepare dictionary data for display."
    # Second version of prepare_for_dispaly(), what is mode compact and
    # where onerow values are on the line with key.
    return '\n'.join(__pfd__(dict_data,color))

def prepare_for_display(dict_values,color=0,indent=0):
    "Prepare dictionary data for display."
    body=[]
    if type(dict_values) in (list,tuple):
        for d in dict_values:
            data = prepare_for_display(d,color,indent)
            if data: body.append(data)
    else:
        if color:
            patt = ('%s[${YELLOW}${BOLD}ATTR${NORMAL}: %s]','%s[${GREEN}%s${NORMAL}]:\n%s','${GREEN}%s:${NORMAL} %s')
        else:
            patt = ('%s[ATTR: %s]','%s[%s]:\n%s','%s: %s')
        for key in dict_values.keys():
            ind = ' '*indent
            if key == 'attr':
                if not indent: continue # node attributes, but not these from root
                attr = []
                for k,v in dict_values[key]:
                    v = v.strip()
                    if v: attr.append(patt[2]%(k,v))
                body.append(patt[0]%(ind,', '.join(attr)))
            elif key == 'data':
                # nodes data
                v = dict_values[key].strip()
                if v: body.append('%s%s'%(ind,v))
            else:
                # descendants nodes
                if type(dict_values[key]) == dict:
                    data = prepare_for_display(dict_values[key],color,indent+4)
                    if data: body.append(patt[1]%(ind,key,data))
                else:
                    body.append(patt[1]%(ind,key,dict_values[key]))
    return '\n'.join(body)


def test_display():
    exampe1 = {'attr': [(u'xmlns:xsi', u'http://www.w3.org/2001/XMLSchema-instance'),
          ('xmlns', xmlns),
          (u'xsi:schemaLocation', 'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd')],
 'greeting': {'dcp': {'access': {'all': {}},
                      'statement': {'purpose': {'admin': {}, 'prov': {}},
                                    'recipient': {'public': {}},
                                    'retention': {'stated': {}}}},
              'svDate': {'data': u'2006-05-13T07:44:37.0Z'},
              'svID': {'data': u'EPP server of cz.nic' },
              'svIDx': { 'attr':[('test','value'),('some','next value')], 'data': u'EPP server of cz.nic' },
              'svcMenu': {'lang': [{'data': u'en'},{'data': u'cz'}],
                          'version': {'data': u'1.0'}},
              'svcs': {'objURI': [{'data': u'http://www.nic.cz/xml/epp/contact-1.0'},
                                  {'data': u'http://www.nic.cz/xml/epp/domain-1.0'},
                                  {'data': u'http://www.nic.cz/xml/epp/nsset-1.0'}]}}}

    exampe2 = {'attr': [(u'xmlns:xsi', u'http://www.w3.org/2001/XMLSchema-instance'), 
        ('xmlns', xmlns), 
        (u'xsi:schemaLocation', 'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd')], 
    'response': {'trID': 
    {'clTRID': {'data': u'jzqq002#06-07-07at14:08:37'}, 
     'svTRID': {'data': u'fred-0000010021'}}, 
    'result': {'msg': {'data': 'Prikaz uspesne proveden', 
        'attr': [(u'lang', u'cs')]}, 
        'attr': [(u'code', u'1000')]
        }, 
        'resData': {'contact:chkData': 
            {'attr': [(u'xmlns:contact', u'http://www.nic.cz/xml/epp/contact-1.0'), 
            (u'xsi:schemaLocation', 
                u'http://www.nic.cz/xml/epp/contact-1.0 contact-1.0.xsd')],
        'contact:cd': [
            {'contact:id': {'data': u'handle2', 'attr': [(u'avail', u'1')]}}, 
            {'contact:id': {'data': u'handle1', 'attr': [(u'avail', u'0')]}}]}}}}
            
    print prepare_for_display(exampe2)
    print '='*60
    print prepare_display(exampe2)


def test_parse(filename):
    from session_base import ManagerBase
    manager = ManagerBase()
    m = Message(manager)
    xml = m.load_xml_doc(filename)
    errors = m.fetch_errors()
    if errors:
        print errors
        return
    m.parse_xml(xml)
    print m.fetch_errors()
    print m.get_xml()
    epp_dict = m.create_data()
    print prepare_display(epp_dict)

    

if __name__ == '__main__':
    "Test of parsing XML document and mapping XML.DOM into python dict/class."
    import sys
    _T = lambda s: s
    if len(sys.argv)>1:
        test_parse(sys.argv[1])
    else:
        print 'Usage: eppdoc.py eppfile.xml'
##    ret = {'reason': u'Authentication error; server closing connection', 'code': 2501, 'data': {"h1":"ano"}, 'errors': []}
##    print get_value_from_dict(ret, ('data','h1'))
