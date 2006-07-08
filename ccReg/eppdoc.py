#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Tento modul obsahuje funkce a data, která jsou potřebná
# na sestavení EPP dokumentu.
# Funkce i data jsou společná jak pro klienta, tak pro server:
#
#       dom - stromová struktura XML
#       errors - pole s chybovými hlášeními
#       encoding - výstupní kódování
#
import os, re
import xml.dom.minidom
try:
    from xml.dom.ext import PrettyPrint
except ImportError:
    PrettyPrint = None
from xml.dom import Node
import StringIO
from gettext import gettext as _T

#========================================================
# Jmenné prostory EPP
# společné pro všechny šablony
#========================================================
xmlns="urn:ietf:params:xml:ns:epp-1.0"
xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi_schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd"
default_encoding = 'utf-8' # default document output encoding
nic_cz_xml_epp_path = 'http://www.nic.cz/xml/epp/'
nic_cz_version = '1.0'
#========================================================

class Message:
    'Struct maintaining DOM object and process errors.'

    def __init__(self):
        self.dom = None         # DOM object
        self.errors = []        # [(code, value, reason), ...]
        self.encoding = default_encoding
        self._cr = '\n' # new line
        self._dct = {}  # parsed parameters from command line
        self._command_params = {} # struct of command parameters
        
    def reset(self):
        self.__reset_dom__()
        self.errors = []

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
            if PrettyPrint:
                f = StringIO.StringIO()
                PrettyPrint(self.dom, f, self.encoding)
                f.seek(0,0)
                xml = f.read()
            else:
                # Kdyz chybi funkce PrettyPrint()
                xml = self.dom.toprettyxml('', '', self.encoding)
        # hook parametru standalone
        return re.sub('(<?xml .+?)\?>','\\1 standalone="no"?>',xml, re.I)
        return xml

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

    def parse_xml(self, xml_doc):
        'Parse XML into DOM object.'
        self.__reset_dom__()
        try:
            self.dom = xml.dom.minidom.parseString(xml_doc)
            self.dom.normalize()
        except xml.parsers.expat.ExpatError, msg:
            # když je zprasené XML
            self.errors.append((2001, None, _T('Invalid XML document. ExpatError: %s'%msg)))
        except LookupError, msg:
            # chybné nebo neznámé kódování
            self.errors.append((2001, None, _T('Document has wrong encoding. LookupError: %s'%msg)))

    def join_top_attribs(self):
        ns=(
            ('xmlns',xmlns),
            ('xmlns:xsi',xmlns_xsi),
            ('xsi:schemaLocation',xsi_schemaLocation),
        )
        self.append_attribNS(self.dom.documentElement, ns)

    def create(self, top_name='epp'):
        'Create empty EPP DOM.'
        self.__reset_dom__()
        # Posledni parametr (0) urcuje DTD, a pokud je 0 tak dokument zadne DTD nema.
        # ("jmeny_prostor","korenovy-element",0)
        self.dom = xml.dom.getDOMImplementation().createDocument('',top_name,0)
        self.join_top_attribs()

    def new_node_by_name(self, master_name, name, value=None, attribs=None):
        "Create new node by Tag Name and attach to the Master Node. attribs=((name,value), (name,value), ....)"
        master = self.dom.getElementsByTagName(master_name)
        if type(master) == xml.dom.minicompat.NodeList:
            # Pokud je to pole, tak se bere vždy poslední uzel.
            if len(master): master = master[-1]
        if master:
            node=self.new_node(master, name, value, attribs)
        else:
            # pokud nadřazený uzel neexistuje, tak by se to celé mělo zastavit?
            self.errors.append((2001, None, _T("Internal Error: Master node '%s' doesn't exist."%master_name)))
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
            node.appendChild(self.dom.createTextNode(value))
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
        """
        name = ''
        if self.dom:
            # Level 1.
            node = self.get_element_node(self.dom.documentElement)
            if not node: return name
            name = node.nodeName.lower()
            if name == 'command':
                # Level 2.
                node = self.get_element_node(node)
                if not node: return name
                name = node.nodeName.lower()
                if name not in ('login','logout','poll'):
                    # Level 3.
                    node = self.get_element_node(node)
                    if not node: return name
                    name = node.nodeName.lower()
        return name

    #====================================
    # Parse to Dict / Data class
    #====================================
    def __create_data__(self, el, current_obj, is_class):
        "Create class object represents DOM struct of EPP document."
        # 1. sestaví jména uzlů a jejich počet
        # 2. vytvoří uzel nebo pole podle počtu
        # 3. prochází rekurzivně všechny uzly a přidá hodnoty
        # 4. připojí help
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
        # POROR! Žádný uzel se nesmí jmenovat attr a data.
        self._parent = parent
        self._attr = []
        self._data = ''
    def __getattr__(self, key):
        # Avoid AttributeError
        if key in ('attr','data'):
            # class members
            ret = self.__dict__['_%s'%key]
        # ........................................
        # Zde se může zrušit vypnutí exception AttributeError 
        # a tím se vrátí normální chování.
##        else:
##            ret = super.__getattr__(key)
        # ........................................
        # Zde je možnost vypnutí exception AttributeError 
        # (musí se zakomentovat předchozí dva řádky: else a ret = ...)
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
        if self._data: self.__doc__ += '*' # indikátor, že položka má data
        if self._attr: self.__doc__ += '^' # indikátor, že položka má atributy
        for key in self.__dict__:
            if key[0] == '_': continue
            member = self.__dict__[key]
            if type(member)==list:
                subname = '%s[%d]'%(key,len(member))
                subdoc=[]
                for item in member:
                    subitem = item.__make_data_help__()
                    if subitem != key: subdoc.append(subitem) # element, který je prázdný se nemusí přidávat
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
        if type(d[key]) == str:
            d[key] += val
        else:
            d[key].extend(val)
    else:
        d[key] = val

def get_dct_attr(dict_data, names, attr_name, sep='\n'):
    "Returns attribute value of the key name in names list."
    return get_dct_value(dict_data, names, sep, attr_name)

def getd(dct, names):
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
    ret=[]
    if type(names) not in (tuple,list):
        names = (names,)
    if len(names):
        for i in range(len(names)):
            name = names[i]
            if name in ('data','attr'): continue
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
                vals = dict_data.get('attr','')
                if vals:
                    for k,v in vals:
                        if k==attr_name:
                            if v: ret.append(v)
                            break
            else:
                vals = dict_data.get('data','')
                if vals: ret.append(vals)
        else:
            ret.append(dict_data)
    return ret

def get_dct_value(dict_data, names, sep='\n', attr_name=''):
    "Returns value of the key name in names list."
    return sep.join(get_dct_values(dict_data, names, attr_name))

def __pfd__(dict_data,color=0,indent=0):
    "Prepare dictionary data for display."
    if color:
        patt=('${BOLD}%s:${NORMAL} %s','[${YELLOW}${BOLD}ATTR:${NORMAL} %s]','%s[${GREEN}${BOLD}%s${NORMAL}]:','%s[${GREEN}${BOLD}%s${NORMAL}]: %s')
    else:
        patt=('%s: %s','[ATTR: %s]','%s[%s]:','%s[%s]: %s')
    body=[]
    if type(dict_data) in (list,tuple):
        for d in dict_data:
            rows = __pfd__(d,color,indent)
            if len(rows): body.extend(rows)
    else:
        if indent and dict_data.has_key('attr'):
            # attributy, ale ne ty z rootu
            attr=[]
            for k,v in dict_data['attr']:
                attr.append(patt[0]%(k,v))
            body.append(patt[1]%'; '.join(attr))
        # data
        if dict_data.has_key('data'): body.append(dict_data['data'])
        # other children nodes    
        ind = ' '*indent
        for key in dict_data.keys():
            # podřízené uzly
            if key in ('attr','data'): continue
            rows = __pfd__(dict_data[key],color,indent+4)
            if len(rows):
                if len(rows)>1:
                    # více řádků [klíč]: a na další řádky hodnoty
                    body.append(patt[2]%(ind,key))
                    for r in rows:
                        body.append('%s%s'%(ind,r))
                else:
                    # jeden řádek - [klíč]: hodnota
                    body.append(patt[3]%(ind,key,rows[0]))

    return body

def prepare_display(dict_data,color=0):
    "Prepare dictionary data for display."
    # Druhá verze prepare_for_dispaly(), která je kompaktnější a 
    # kde jednořádkové hodnoty jsou na řádku s klíčem.
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
            patt = ('%s[${YELLOW}${BOLD}ATTR${NORMAL}: %s]','%s[${GREEN}${BOLD}%s${NORMAL}]:\n%s','${BOLD}%s:${NORMAL} %s')
        else:
            patt = ('%s[ATTR: %s]','%s[%s]:\n%s','%s: %s')
        for key in dict_values.keys():
            ind = ' '*indent
            if key == 'attr':
                if not indent: continue # attributy uzlu, ale ne ty z rootu
                attr = []
                for k,v in dict_values[key]:
                    v = v.strip()
                    if v: attr.append(patt[2]%(k,v))
                body.append(patt[0]%(ind,', '.join(attr)))
            elif key == 'data':
                # data uzlu
                v = dict_values[key].strip()
                if v: body.append('%s%s'%(ind,v))
            else:
                # podřízené uzly
                if type(dict_values[key]) == dict:
                    data = prepare_for_display(dict_values[key],color,indent+4)
                    if data: body.append(patt[1]%(ind,key,data))
                else:
                    body.append(patt[1]%(ind,key,dict_values[key]))
    return '\n'.join(body)
    
def test_display():
    exampe1 = {'attr': [(u'xmlns:xsi', u'http://www.w3.org/2001/XMLSchema-instance'),
          ('xmlns', u'urn:ietf:params:xml:ns:epp-1.0'),
          (u'xsi:schemaLocation',
           u'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd')],
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
        ('xmlns', u'urn:ietf:params:xml:ns:epp-1.0'), 
        (u'xsi:schemaLocation', u'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd')], 
    'response': {'trID': 
    {'clTRID': {'data': u'jzqq002#06-07-07at14:08:37'}, 
     'svTRID': {'data': u'ccReg-0000010021'}}, 
    'result': {'msg': {'data': u'P\u0159\xedkaz \xfasp\u011b\u0161n\u011b proveden', 
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

def correct_unbound_prefix(xml):
    'Input missing prefix definitions.'
    # TODO: Tohle zanikne...
    names = []
    for token in re.findall('<([\w-]+):',xml):
        if token not in names: names.append(token)
    if len(names):
        return re.sub(r'<([^\?][^>]+)>', '<\\1 %s>'%' '.join(['xmlns:%s="urn:ietf:params:xml:ns:epp-1.0"'%n for n in names]), xml, 1)
    else:
        return xml

def test_parse():
    m = Message()
    m.parse_xml(xml)
    print m.fetch_errors()
    print m.get_xml()
    
if __name__ == '__main__':
    "Testování zpracování XML dokumentu a mapování XML.DOM do python dict/class."
    test_display()
    test_parse()
##    ret = {'reason': u'Authentication error; server closing connection', 'code': 2501, 'data': {"h1":"ano"}, 'errors': []}
##    print getd(ret, ('data','xh1'))
