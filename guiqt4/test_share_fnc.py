#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module is used for test shared functions in module shared_fnc.py
"""
from shared_fnc import *

class UnknownTypeWidget:
    pass

def test_str():
    print "fred.translate.encoding=",encoding
    for text in (u'TEST', u'řečiště',u'ŘEČITĚ',u'žluťoučký kůň příšerně úpěl ďábelské ódy'):
        var = get_str(QtCore.QString(text))
        print u'QString(%s):'%text, type(var), var

def test_widgets():
    app = QtGui.QApplication([])
    dct = {}

    key = 'QLineEdit'
    widget = QtGui.QLineEdit()
    widget.insert(key)
    append_key(dct, key, widget)

    key = 'QTextEdit'
    widget = QtGui.QTextEdit()
    widget.setText(key)
    append_key(dct, key, widget)

    key = 'QRadioButton'
    widget = QtGui.QRadioButton()
    widget.setChecked(True)
    append_key(dct, key, widget)

    key = 'QCheckBox'
    widget = QtGui.QCheckBox()
    widget.setChecked(True)
    append_key(dct, key, widget)

    key = 'QDateEdit'
    widget = QtGui.QDateEdit()
    append_key(dct, key, widget)

    key = 'QComboBox'
    widget = QtGui.QComboBox()
    append_key(dct, key, widget)

    key = 'QTableWidget'
    widget = QtGui.QTableWidget(2,1)
    widget.setItem(0, 0, QtGui.QTableWidgetItem('first cell stuff'))
    widget.setItem(1, 0, QtGui.QTableWidgetItem('second cell stuff'))
    append_key(dct, key, widget)

    key = 'unknown type'
    widget = UnknownTypeWidget()
    append_key(dct, key, widget)

    for k,v in dct.items():
        print '\t',k,':\t',v

if __name__ == "__main__":
    # TESTS
    import sys
    sys.path.insert(0,'../')
    from fred.translate import encoding
    init_encoding(encoding)
    test_str()
    test_widgets()
