# -*- coding: utf-8 -*-
from qt import *
from qttable import *
from create_domain import dialog

class panel(dialog):
    'Create domain dialog.'

    def __init__(self,parent = None,name = None,fl = 0):
        dialog.__init__(self,parent,name,fl)
        self.admin.horizontalHeader().setLabel(0, 'admin', 320)
        self._admin_item = None

    def admin_value_changed(self,r,c):
        w = self.admin
        qs = w.text(r,c).stripWhiteSpace()
        if qs.isEmpty():
            if w.numRows() > 1:
                w.removeRow(r)
        else:
            if self._admin_item:
                if self._admin_item.isEmpty() or w.numRows() < 2:
                    w.insertRows(w.numRows())
            else:
                w.insertRows(w.numRows())

    def admin_current_changed(self,r,c):
        self._admin_item = self.admin.text(r,c).stripWhiteSpace()


if __name__ == '__main__':
    app = QApplication([])
    form = panel()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()
