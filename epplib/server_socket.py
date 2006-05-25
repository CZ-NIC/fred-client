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
        self._port = 0

    def bind(self, host, port):
        self._port = port
        try:
            self._socket.bind((host, port))
        except socket.error, (errno,msg):
            print 'socket.error: [%d] %s'%(errno,msg)
            return 0
        self._socket.listen(1)
        return self._socket
        
    def listen(self):
        self._addr = None
        print "EPP server listening at port %d (stop ^C)..."%self._port
        try:
            self._conn, self._addr = self._socket.accept()
        except KeyboardInterrupt:
            print 'Stopped listening by user.'
        else:
            self._conn.settimeout(1.0)
            print 'Connected by', self._addr
        return self._addr
            
def test(host, port):
    server = Dock()
    if not server.bind(host, port):
        return
    while server.listen():
        server.run_listen_loop()
        server.join() # čeká se na ukončení naslouchání
    server.close()
    print server.fetch_notes()
    print "[END TEST]"

if __name__ == '__main__':
    test('',700)
