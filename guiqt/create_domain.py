# -*- coding: utf-8 -*-
from qt import *
from shared_fnc import *
import _create_domain

class ccregWindow(_create_domain.ccregWindow):
    'Create domain frame.'

    def __init__(self,parent = None,name = None,fl = 0):
        _create_domain.ccregWindow.__init__(self,parent,name,fl)
        self.admin.horizontalHeader().resizeSection(0,320)
        self._admin_item = None

    def admin_value_changed(self,r,c):
        table_value_changed(self.admin, self._admin_item, r, c)

    def admin_current_changed(self,r,c):
        self._admin_item = table_current_changed(self.admin, r, c)


if __name__ == '__main__':
    app = QApplication([])
    form = ccregWindow()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()
