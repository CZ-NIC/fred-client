# -*- coding: utf-8 -*-
"""
This module shared functions used by GUI modules.
"""
from PyQt4 import QtCore, QtGui

def table_value_changed(wndQTable, qstrPrevState, r, c, max=0):
    'Appends or remove cell'
    qs = wndQTable.item (r,c).text().trimmed()
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

