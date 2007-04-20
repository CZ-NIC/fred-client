#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import re
from PyQt4 import QtGui, QtCore

def trim_suffix_reasion_and_pop_others(data):
    """Remove suffix :reason from key names and pop others.
    IN:
    data = {u'name.cz:reason': 'Message...', u'test.cz:reason': 'Message...', ...}
    columns = [(u'test.cz', 1, u'test.cz'), (u'name.cz', 1, u'name.cz'),  ...]
    OUT:
    data = {u'test.cz': 'Message...', u'name.cz': 'Message...',  ...}
    """
    msg = {}
    patt_reason = re.compile('(.+):reason$')
    for key, value in data.items():
        match = patt_reason.search(key)
        if match:
            msg[match.group(1)] = value
    return msg

def get_str(qtstr, encoding):
    'Translate QString. Trip whitespaces at the begining and end. Returns string in local charset.'
    if type(qtstr) is QtCore.QString:
        text = unicode(qtstr.trimmed().toUtf8(),'utf8').encode(encoding)
    else:
        if type(qtstr) not in (str, unicode): qtstr = str(qtstr)
        if type(qtstr) is unicode:
            text = qtstr.encode(encoding)
        else:
            text = qtstr
    return text

def get_unicode(text, encoding):
    'Convert to unicode and catch problems with conversion.'
    if type(text) not in (str, unicode): text = str(text)
    if type(text) == str:
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = repr(text)
    return text

def append_key(dct, key, widget):
    'Append value if has been typed.'
    wt = type(widget)
    if wt == QtGui.QLineEdit:
        value = get_str(widget.text())
        if value: dct[key] = value
    elif wt == QtGui.QTextEdit:
        value = get_str(widget.toPlainText())
        if value: dct[key] = value
    elif wt in (QtGui.QRadioButton, QtGui.QCheckBox):
        dct[key] = widget.isChecked() and 1 or 0
    elif wt == QtGui.QDateEdit:
        dct[key] = '%s'%widget.date().toString(QtCore.Qt.ISODate) # QDate; Qt.ISODate='YYYY-MM-DD'
    elif wt == QtGui.QComboBox:
        dct[key] = widget.currentIndex()
    elif wt == QtGui.QTableWidget:
        data = []
        for r in range(widget.rowCount()):
            tbl_item = widget.item(r,0)
            if not tbl_item: continue
            value = get_str(tbl_item.text())
            if len(value): data.append(value)
        if len(data): dct[key] = data
    else:
        print "INTERNAL ERROR: Unknown type widget:",type(widget)
        
def count_data_rows(dct):
    size = 0
    for v in dct.values():
        if type(v) in (list,tuple):
            ln = len(v)
            size += ln
            if ln == 0: size += 1
        else:
            size += 1
    return size

def join_key_and_values(value):
    'Implode DNS list and IP address together into one string.'
    # [u'ns2.test.cz', [u'127.289.30.63',u'127.289.30.63',]]
    if type(value) in (list, tuple):
        if len(value) == 2 and type(value[0]) in (str, unicode):
            key, addr = value
            value = '%s %s'%(key, join_items(addr))
        else:
            value = join_items(value)
    return value

def join_items(value):
    'Join items into string'
    if type(value) in (list, tuple):
        items = []
        for item in value:
            text = join_items(item)
            if text: items.append(text)
        if len(items):
            if len(items) > 1:
                value = u'(%s)'%u', '.join(items) 
            else:
                value = items[0]
        else:
            value = u''
    return value

def ttytag2html(text):
    'Convert tty tags to the html tags.'
    # ${BOLD}, ${NORMAL}, ${COLOR}
    text = re.sub('\$\{BOLD\}(.*?)\$\{NORMAL\}','<b>\\1</b>',text)
    text = text.replace('${NORMAL}','</span>')
    text = re.sub('\$\{(\w+)\}','<span style="color:\\1">',text)
    return text

def get_exception():
    'Fetch excption for recording.'
    msg = ['Traceback (most recent call last):']
    ex = sys.exc_info()
    sys.exc_clear()
    for trace in traceback.extract_tb(ex[2]):
        msg.append(' File "%s", line %d, in %s'%(trace[0], trace[1], trace[2]))
        msg.append('    %s'%trace[3])
    msg.append('%s: %s'%(ex[0], ex[1]))
    return '\n'.join(msg)
