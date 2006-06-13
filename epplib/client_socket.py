# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import os
import socket
import threading
import time
import re
import struct
from gettext import gettext as _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        "keys=('private.pem','public.pem')"
        self._conn = None
        self._conn_ssl = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._body_length = 0 # velikost EPP zprávy, která se má přijmout
        self._timeout = 3.0   # počet vteřin, po kterých se čeká na odpověď serveru

    def is_error(self):
        return len(self._errors)

    def is_connected(self):
        return self._conn and self._conn_ssl

    def connect(self, DATA):
        "DATA = ('host', PORT, ('file.key','file.crt'))"
        self._conn = None
        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, (no,msg):
            self._errors.append('Create socket.error [%d] %s'%(no,msg))
            return 0
        try:
            self._conn.connect((DATA[0], DATA[1]))
            self._notes.append('Connected to host %s, port %d'%tuple(DATA[:2]))
            self._conn.settimeout(self._timeout)
        except socket.error, (no,msg):
            self._errors.append('Connection socket.error [%d] %s'%(no,msg))
            return 0
        self._notes.append(_T('Init SSL connection'))
        if DATA[2]:
            if not os.path.isfile(DATA[2][0]):
                self._errors.append('%s %s'%(DATA[2][0],_T('Private key file not found.')))
            if not os.path.isfile(DATA[2][1]):
                self._errors.append('%s %s'%(DATA[2][1],_T('Certificate key file not found.')))
        try:
            if DATA[2]:
                self._conn_ssl = socket.ssl(self._conn, DATA[2][0], DATA[2][1])
            else:
                self._conn_ssl = socket.ssl(self._conn)
        except socket.sslerror, msg:
            if type(msg) is not str:
                self._errors.append(str(msg))
            else:
                self._errors.append(msg)
            self._conn.close()
            self._conn = None
        return self._conn

    def receive(self):
        "Receive answer from EPP server."
        if self.__receive_header__():
            return self.__receive__()
        return ''

    def __receive_header__(self):
        "Header part of receiving process."
        self._body_length = 0
        try:
            header = self._conn_ssl.read()
        except socket.timeout, msg:
            self._errors.append('READ HEADER socket.timeout: %s'%msg)
        except socket.sslerror, (no, msg):
            self._errors.append('READ HEADER socket.sslerror: [%d] %s'%(no, msg))
        except socket.error, (no, msg):
            self._errors.append('READ HEADER socket.error: [%d] %s'%(no, msg))
        else:
            # hlavička zprávy
            try:
                self._body_length = struct.unpack('!i',header)[0] - 4
            except struct.error, msg:
                self._errors.append('Error HEADER: %s'%msg)
        if len(self._errors): self.close()
        return self._body_length
        
    def __receive__(self):
        "Body part of receiving process."
        data = ''
        while self._body_length and len(data) < self._body_length:
            try:
                part = self._conn_ssl.read()
            except socket.timeout, msg:
                self._errors.append('READ socket.timeout: %s'%msg)
                break
            except socket.sslerror, msg:
                self._errors.append('READ socket.sslerror: %s'%msg)
                break
            except socket.error, (no, msg):
                self._errors.append('READ socket.error: [%d] %s'%(no, msg))
                break
            data += part
        if len(self._errors): self.close()
        return data.strip()

    def fetch_errors(self, sep='\n'):
        msg = sep.join(self._errors)
        self._errors = []
        return msg
    def fetch_notes(self, sep='\n'):
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    def handler_message(self, msg):
        'Handler of incomming message'
        # funkce pro zpracování zprávy
        print 'SERVER ANSWER:\n',msg
        
    def send(self,msg):
        "Send message to server."
        # tady nemůže být automatické navázání konexe, protože to se musí
        # navázat ze session Managera
        ok=0
        try:
            self._conn_ssl.write('%s%s'%(struct.pack('!i',len(msg)+4),msg))
            ok=1
        except socket.timeout, msg:
            self._errors.append('SEND socket.timeout: %s'%msg)
        except socket.sslerror, (no, msg):
            self._errors.append('SEND socket.sslerror: [%d] %s'%(no, msg))
        except socket.error, (no, msg):
            self._errors.append('SEND socket.error: [%d] %s'%(no, msg))
        return ok

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._errors.append(_T('Connection closed'))

if __name__ == '__main__':
    import sys
    DATA = ['curlew',700, ('certificate_private.pem','certificate_public.pem')]
    if len(sys.argv)>1: DATA[0] = sys.argv[1]
    if len(sys.argv)>2: DATA[1] = int(sys.argv[2])
    client = Lorry()
    if client.connect(DATA):
        print client.fetch_notes()
        print "[START LOOP prompt]"
        while 1:
            q = raw_input("> q (quit) ")
            if q.strip()=='': continue
            if q in ('q','quit','exit','konec'): break
            if not client.send(q): break
            print client.receive()
            if client.is_error(): break
        print "[STOP LOOP prompt]"
    print client.fetch_errors()
    print client.fetch_notes()
    client.close()

