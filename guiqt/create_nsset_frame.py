# -*- coding: utf-8 -*-

from qt import *
from create_nsset import frame
from shared_fnc import *
import dns_frame


class panel(frame):

    def __init__(self,parent = None,name = None,fl = 0):
        frame.__init__(self,parent,name,fl)
        self.tech.horizontalHeader().resizeSection(0,320)
        self._tech_item = None
        self.dns_sets = []
        self.panel_dns = add_dns_sets(self.dns_sets, self.frame_dns, dns_frame, 'dns')

    def tech_current_changed(self,r,c):
        self._tech_item = table_current_changed(self.tech, r, c)

    def tech_value_changed(self,r,c):
        table_value_changed(self.tech, self._tech_item, r, c)

        
if __name__ == '__main__':
    app = QApplication([])
    form = panel()
    form.show()
    app.setMainWidget(form)
    app.exec_loop()
