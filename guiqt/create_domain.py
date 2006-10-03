# -*- coding: utf-8 -*-
from qt import *
from qttable import *
from create_domain import dialog
from shared_fnc import *

class panel(dialog):
    'Create domain dialog.'

    def __init__(self,parent = None,name = None,fl = 0):
        dialog.__init__(self,parent,name,fl)
        self.admin.horizontalHeader().resizeSection(0,320)
        self._admin_item = None

    def admin_value_changed(self,r,c):
        table_value_changed(self.admin, self._admin_item, r, c)

    def admin_current_changed(self,r,c):
        self._admin_item = table_current_changed(self.admin, r, c)


if __name__ == '__main__':
    app = QApplication([])
    form = panel()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()
