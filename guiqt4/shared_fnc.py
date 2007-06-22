#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

def transl(text):
    return QtGui.QApplication.translate("FredWindow", text, None, QtGui.QApplication.UnicodeUTF8)

