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
        except socket.error, (errno,msg):
            print 'socket.error: [%d] %s'%(errno,msg)
            return
        self._socket.listen(1)
        print "EPP server listening at port %d (stop ^C)..."%port
        try:
            self._conn, self._addr = self._socket.accept()
        except KeyboardInterrupt:
            print 'Stopped listening by user.'
        else:
            self._conn.settimeout(1.0)
            print 'Connected by', self._addr
        return self._addr

            
        
def test(host, port):
    transport = Dock()
    if transport.listen(host, port):
        print transport.fetch_notes()
        # spustí se thread s příjmem
        transport.start_receive_thread()
    else:
        print transport.fetch_errors()
        return
    print 'Run forever... (break ^C)'
    while transport.isAlive():
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'): break
        if not transport.send(command):
            print transport.fetch_errors()
            break
    transport.close()
    print transport.fetch_notes()
    print "[END TEST]"

    
if __name__ == '__main__':
    test('',700)
