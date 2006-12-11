#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module shared functions used by PyQt4 for mainulate with widgets.
"""
from PyQt4 import QtCore, QtGui

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

def add_dns_sets(parent_frame, FredWindowDNS, num_required=0):
    'Add scrolled view window.'
    dns_sets = []
    scroll = QtGui.QScrollArea(parent_frame)
    g = parent_frame.geometry()
    scroll.setGeometry(0,0,g.width(),g.height())
    layout = QtGui.QVBoxLayout()
    max = 9
    for n in range(max):
        wnd = FredWindowDNS((n+1,max), n < num_required)
        dns_sets.append(wnd)
        layout.addWidget(wnd)
    panel = QtGui.QFrame(scroll)
    panel.setLayout(layout)
    scroll.setWidget(panel)
    return dns_sets
