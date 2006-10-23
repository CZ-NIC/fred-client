# -*- coding: utf-8 -*-
from qt import *

def table_value_changed(wndQTable, qstrPrevState, r, c, max=0):
    'Appends or remove cell'
    qs = wndQTable.text(r,c).stripWhiteSpace()
    if qs.isEmpty():
        if wndQTable.numRows() > 1:
            wndQTable.removeRow(r)
    else:
        if qstrPrevState:
            if qstrPrevState.isEmpty() or wndQTable.numRows() < 2:
                if max == 0 or wndQTable.numRows() < max:
                    wndQTable.insertRows(wndQTable.numRows())
        else:
            if max == 0 or wndQTable.numRows() < max:
                wndQTable.insertRows(wndQTable.numRows())

def table_current_changed(wndQTable, r, c):
    'Returns text of selected cell.'
    return wndQTable.text(r,c).stripWhiteSpace()

def add_dns_sets(dns_sets, parent_frame, module, name):
    'Add scrolled view window. Module must have class FredWindow.'
    scroll = QScrollView(parent_frame, 'scroll_%s'%name)
    scroll.enableClipper(True)
    g = parent_frame.geometry()
    scroll.setGeometry(0,0,g.width(),g.height())
    frm = QWidget(scroll)
    layout = QVBoxLayout(frm)
    width = 0
    height = 0
    max = 9
    for i in range(max):
        wnd = module.FredWindow(frm,'dns%d'%i)
        label = u'%s (%d/%d)'%(wnd.label_dns_name.text(),i+1,max)
        if i == 0:
            label = u'<b>%s</b>'%label
            width = wnd.geometry().width()
        wnd.label_dns_name.setText(label)
        height += wnd.geometry().height()
        layout.addWidget(wnd)
        dns_sets.append(wnd)
    frm.setMinimumWidth(width)
    frm.setMinimumHeight(height)
    scroll.addChild(frm)
    frm.show()
    scroll.show()
    return wnd
