# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
"""Přenos zpráv přes TCP/IP.

transport = Lorry()
transport.send(message)
if transport.receive():
    print transport.get_cargo()
else:
    print transport.fetch_errors()
transport.close()

"""
import socket
from gettext import gettext as _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._cargo = ''

    def fetch_errors(self, sep='\n'):
        msg = sep.join(self._errors)
        self._errors = []
        return msg
    def fetch_notes(self, sep='\n'):
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    def get_cargo(self):
        return self._cargo
        
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._notes.append(_T('Disconnected.'))

    def connect(self, host, port):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._conn.connect((host, port))
            self._notes.append(_T('Connected at server OK.'))
        except socket.error, (errno,msg):
            self._errors.append('socket.error: [%d] %s'%(errno,msg))
            self._conn = None
        return self._conn

    def send(self, message):
        self._conn.send(message)
        
    def receive(self):
        self._cargo=''
        try:
            self._cargo = self._conn.recv(1024)
            valid=1
        except socket.error, (errno,msg):
            self._errors.append('socket.error: [%d] %s'%(errno,msg))
            valid=0
        return valid
        

def test(host, port):
    transport = Lorry()
    run = transport.connect(host, port)
    if run:
        print transport.fetch_notes()
    else:
        print transport.fetch_errors()
    while run:
        command = raw_input("> (?-help, q-quit): ")
        if command in ('q','quit','exit','konec'): break
        transport.send(command)
        if not transport.receive():
            print transport.fetch_errors()
            break
        print transport.get_cargo()
    transport.close()
    print transport.fetch_notes()
    print "[END TEST]"

if __name__ == '__main__':
    test('localhost',700)
