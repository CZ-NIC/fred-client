#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module shared functions used by PyQt4 
for mainulate with widgets and functions to access them.
"""
from PyQt4 import QtCore, QtGui

# Default encoding MUST be set by actual encoding (throught init_encoding())
gui_encoding = encoding = ''

def table_value_changed(wndQTable, qstrPrevState, r, c, max=0):
    'Appends or remove cell'
    qs = wndQTable.item(r,c).text().trimmed()
    if qs.isEmpty():
        # if new text is empty (not typed or removed by user)
        if r < wndQTable.rowCount()-1:
            # not remove last cell
            wndQTable.removeRow(r) # cell is empty and has not been before
    else:
        # if any new text is typed
        if qstrPrevState.isEmpty() and (max == 0 or wndQTable.rowCount() < max):
            wndQTable.insertRow(wndQTable.rowCount()) # cell was filled
    return qs

def table_current_changed(wndQTable, r, c):
    'Returns text of selected cell.'
    table_item = wndQTable.item (r,c)
    return table_item and table_item.text().trimmed() or QtCore.QString()

def add_dns_sets(parent_frame, FredWindowDNS):
    'Add scrolled view window.'
    dns_sets = []
    scroll = QtGui.QScrollArea(parent_frame)
    g = parent_frame.geometry()
    scroll.setGeometry(0,0,g.width(),g.height())
    frm = QtGui.QWidget(scroll)
    layout = QtGui.QVBoxLayout(frm)
    width = 0
    height = 0
    max = 9
    for i in range(max):
        wnd = FredWindowDNS((i+1,max))
        layout.addWidget(wnd)
        if not i: width = wnd.geometry().width()
        height += wnd.geometry().height()
        dns_sets.append(wnd)
    frm.setMinimumWidth(width+5)
    frm.setMinimumHeight(height+20)
    # TODO: dodelat posuvniky
    return dns_sets

#
# Functions used for access widgets.
#

def init_encoding(type):
    'Init local encoding.'
    global encoding, gui_encoding
    encoding  = type
    # The encoding in MS Windows is different from GUI to console.
    gui_encoding = encoding == 'cp852' and 'cp1250' or encoding

def get_str(qtstr):
    'Translate QString. Trip whitespaces at the begining and end. Returns string in local charset.'
    if type(qtstr) is QtCore.QString:
        text = unicode(qtstr.trimmed().toUtf8(),'utf8').encode(encoding)
        if gui_encoding != encoding:
            text = text.decode(gui_encoding).encode(encoding)
    else:
        if type(qtstr) is unicode:
            text = qtstr.encode(encoding)
        else:
            text = qtstr
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
