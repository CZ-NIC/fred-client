#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
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
#========================================================

class Message:
    'Struct maintaining DOM object and process errors.'

    def __init__(self):
        self.dom = None         # DOM object
        self.errors = []        # [(code, value, reason), ...]
        self.encoding = default_encoding
        
    def reset(self):
        self.__reset_dom__()
        self.errors = []

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
                xml = self.dom.toprettyxml('  ','\n',self.encoding)
        return xml

    def join_errors(self, errors):
        self.errors.extend(errors)
    
    def get_errors(self, sep='\n'):
        errors=['[%d] (%s) %s'%(code,str(value),reason) for code,value,reason in self.errors]
        return sep.join(errors)

    def get_results(self, sep='\n'):
        #errors,xml_epp
        return self.get_errors(sep), self.get_xml()

    def append_attribNS(self, node, attribs, ns=''):
        """Append attributes into top node.
        IN: attribs ((name,value), (name,value), ....)
        """
        for n,v in attribs:
            node.setAttributeNS(ns,n,v)

    def make_template_path(self):
        # Make absolute path on the name epplib
        names = re.split('[\\\\/]',os.getcwd())
        try:
            pos = names.index('epplib')
            names = names[:pos]
        except ValueError:
            pass
        names.extend(('epplib','templates'))
        return '/'.join(names)

    def load_xml_doc(self, name, path=''):
        'Load XML file. Used for EPP templates.'
        if path=='': path = self.make_template_path()
        try:
            xml_doc = open('%s/%s.xml'%(path,name)).read()
        except IOError, (no,msg):
            # když šablona chybí
            self.errors.append((2000, '%s.xml'%name, _T('IOError: %d, %s'%(no,msg))))
            xml_doc = None
        return xml_doc

    def parse_xml(self, xml_doc):
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

    def load_EPP_template(self, name, path=''):
        xml_doc = self.load_xml_doc(name, path)
        if xml_doc:
            self.parse_xml(xml_doc)
        if self.dom:
            self.join_top_attribs()

    def create(self):
        'Create empty EPP DOM.'
        self.__reset_dom__()
        # Posledni parametr (0) urcuje DTD, a pokud je 0 tak dokument zadne DTD nema.
        # ("jmeny_prostor","korenovy-element",0)
        self.dom = xml.dom.getDOMImplementation().createDocument('','epp',0)
        self.join_top_attribs()

    def new_node_by_name(self, master_name, name, value=None, attribs=None):
        "Create new node by Tag Name and attach to the Master Node."
        master = self.dom.getElementsByTagName(master_name)
        if master:
            node=self.new_node(master, name, value, attribs)
        else:
            # pokud nadřazený uzel neexistuje, tak by se to celé mělo zastavit?
            self.errors.append((2001, None, _T("Internal Error: Master node '%s' doesn't exist."%master_name)))
            raise "Internal Error: Master node '%s' doesn't exist."%master_name # TODO ????
            node=None # TODO ????
        return node
        
    def new_node(self, master, name, value=None, attribs=None):
        "Create new node and attach to the master node."
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

    def put_value(self, name, value, master_name=''):
        node = self.dom.getElementsByTagName(name)
        if not node and master_name:
            # když uzel neexistuje a je zadán master, tak se pod ním uzel vytvoří
            self.new_node_by_name(master_name, name, value)
        else:
            # když uzel existuje
            if node:
                # když uzel existuje
                if node.item(0).firstChild:
                    # když hodnota uzlu existuje, tak se přepíše
                    node.item(0).firstChild.data=value
                else:
                    # pokud hodnota uzlu neexistuje, tak se vytvoří
                    node.item(0).appendChild(self.dom.createTextNode(value))
            else:
                # pokud uzel neexistuje, tak je to chyba
                self.errors.append((2001, None, _T("Internal Error: Node %s doesn't exist."%name)))

    def check_node(self, name):
        "Check if node exists and if has any value."
        node = self.dom.getElementsByTagName(name)
        if node:
            # když uzel existuje
            if node.item(0).firstChild:
                # když hodnota uzlu existuje, tak nesmí být prázdná
                if node.item(0).firstChild.data.strip()=='':
                    self.errors.append((2001, name, _T("Node is empty")))
            else:
                # pokud hodnota uzlu neexistuje, tak je to chyba
                self.errors.append((2001, name, _T("Node haven't entry")))
        else:
            # pokud uzel neexistuje, tak je to chyba
            self.errors.append((2001, name, _T("Node missing")))

    def remove_node(self, name):
        node = self.dom.getElementsByTagName(name)
        if node:
            # pokud uzel existuje, tak se odstraní
            parent = node[0].parentNode
            parent.removeChild(node[0])

    def is_element_node(self, node):
        return node.nodeType == Node.ELEMENT_NODE

    def get_element_node(self, node):
        'Return first node of type Node.ELEMENT_NODE or None.'
        ret=None
        for n in node.childNodes:
            # if node.nodeType == Node.ELEMENT_NODE:
            if self.is_element_node(n):
                ret=n
                break
        return ret


#------------------------------------
# Testování chybných XML
#------------------------------------

def test_template(name, path=''):
    "Test if template si valid."
    epp = Message()
    epp.load_EPP_template(name, path)
    errors,xml_epp = epp.get_results()
    if errors: print 'ERRORS:',errors
    if xml_epp: print 'XML_EPP:',xml_epp
    print '-'*60
    

if __name__ == '__main__':
    # Pokus o načtení neexistující šablony.
    test_template('soubor-neexistuje','epplib/testy')
    # Nesprávně formátované XML.
    test_template('chybny-format','epplib/testy')
    # Dokument je uložen v jiném kódování, než je definováno v hlavičce.
    test_template('kodovani-neodpovida','epplib/testy')
    # V dokumentu je definován neznámý typ kódování.
    test_template('nezname-kodovani','epplib/testy')
    # V dokumentu se nachází neznámá entita.
    test_template('neznama-entita','epplib/testy')
    # Správné načtení šablony v jiném kódování, než utf8
    test_template('kodovani-cp1250','epplib/testy')
    # Správné načtení standardní šablony.
    test_template('hello')


