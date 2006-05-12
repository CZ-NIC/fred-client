# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import socket
from client_socket import Lorry

class Dock(Lorry):

    def __init__(self):
        Lorry.__init__(self)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._addr = None

    def listen(self,host, port):
        self._addr = None
        try:
            self._socket.bind((host, port))
        except socket.error, msg:
            print msg
        else:
            self._socket.listen(1)
            print "EPP server listening at...",host,port
            self._conn, self._addr = self._socket.accept()
            print 'Connected by', self._addr
        return self._addr

            
        
def test(host, port):
    transport = Dock()
    if not transport.listen(host, port):
        return
    while 1:
        if not transport.receive():
            print transport.fetch_errors()
            break
        print transport.get_cargo()
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'): break
        transport.send(command)
    transport.close()
    print transport.fetch_notes()
    print "[END TEST]"

if __name__ == '__main__':
    test('',700)
