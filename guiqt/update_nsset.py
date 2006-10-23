# -*- coding: utf-8 -*-

from qt import *
from shared_fnc import *
import _update_nsset
import dns


class FredWindow(_update_nsset.FredWindow):

    def __init__(self,parent = None,name = None,fl = 0):
        _update_nsset.FredWindow.__init__(self,parent,name,fl)
        self.add_tech.horizontalHeader().resizeSection(0,320)
        self._add_tech_item = None
        self.rem_name.horizontalHeader().resizeSection(0,320)
        self._rem_name_item = None
        self.rem_tech.horizontalHeader().resizeSection(0,320)
        self._rem_tech_item = None
        self.dns_sets = []
        self.panel_add_dns = add_dns_sets(self.dns_sets, self.frame_add_dns, dns, 'dns')

    def add_tech_current_changed(self,r,c):
        self._add_tech_item = table_current_changed(self.add_tech, r, c)
    def add_tech_value_changed(self,r,c):
        table_value_changed(self.add_tech, self._add_tech_item, r, c)

    def rem_dns_name_current_changed(self,r,c):
        self._rem_name_item = table_current_changed(self.rem_name, r, c)
    def rem_dns_name_value_changed(self,r,c):
        table_value_changed(self.rem_name, self._rem_name_item, r, c, 9)

    def rem_tech_current_changed(self,r,c):
        self._rem_tech_item = table_current_changed(self.rem_tech, r, c)
    def rem_tech_value_changed(self,r,c):
        table_value_changed(self.rem_tech, self._rem_tech_item, r, c)


if __name__ == '__main__':
    app = QApplication([])
    form = FredWindow()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()
