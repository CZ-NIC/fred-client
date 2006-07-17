# -*- coding: utf8 -*-
#!/usr/bin/env python
import os
import socket
import threading
import time
import re
import struct
from translate import _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._conn_ssl = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._body_length = 0 # velikost EPP zprávy, která se má přijmout
        self._timeout = 0.0 # Windows bug! MUST be zero.

    def is_error(self):
        return len(self._errors)

    def is_connected(self):
        return self._conn and self._conn_ssl

    def set_timeout(self, sec):
        self._timeout = sec
    def get_timeout(self):
        return self._timeout

    def connect(self, DATA):
        "DATA = ('host', PORT, 'file.key', 'file.crt', timeout)"
        ok = 0
        self._conn = None
        try:
            self._timeout = float(DATA[4])
        except ValueError:
            pass
        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ok = 1
        except socket.error, (no,msg):
            self._errors.append('Create socket.error [%d] %s'%(no,msg))
        try:
            self._conn.connect((DATA[0], DATA[1]))
            self._notes.append(_T('Connected to host ${GREEN}${BOLD}%s${NORMAL}, port %d')%tuple(DATA[:2]))
            if self._timeout:
                self._notes.append('Socket timeout: ${BOLD}%.1f${NORMAL} sec.'%self._timeout)
                self._conn.settimeout(self._timeout)
        except socket.error, (no,msg):
            self._errors.append('Connection socket.error [%d] %s'%(no,msg))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupt from user'))
        if not ok: return ok
        self._notes.append(_T('Init SSL connection'))
        if len(DATA) < 4:
            self._errors.append(_T('Certificate names not set.'))
        if len(DATA) > 2 and not os.path.isfile(DATA[2]):
            self._errors.append('%s %s'%(DATA[2],_T('Private key file not found.')))
            DATA[2] = None
        if len(DATA) > 3 and not os.path.isfile(DATA[3]):
            self._errors.append('%s %s'%(DATA[3],_T('Certificate key file not found.')))
            DATA[3] = None
        ssl_ok = 0
        try:
            if len(DATA) > 3 and DATA[2] and DATA[3]:
                self._conn_ssl = socket.ssl(self._conn, DATA[2], DATA[3])
            else:
                self._notes.append(_T('Certificates missing. Try connect without SSL!'))
                self._conn_ssl = socket.ssl(self._conn)
            ssl_ok = 1
        except socket.sslerror, msg:
            self._errors.append('socket.sslerror: %s'%str(msg))
            if type(msg) not in (str,unicode):
                err_note = {
                    1:_T('Used certificat is not signed by verified certificate authority.'),
                    2:'%s\n%s'%(_T('The server configuration is not valid. Contact the server administrator.'),
                      _T('If this script runs under MS Windows and timeout is not zero, it is probably SLL bug! Set timeout back to zero.')),
                }
                try:
                    text = err_note.get(msg[0],None)
                    if text: self._errors.append(text)
                except (TypeError, IndexError):
                    pass
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupt from user'))
        if not ssl_ok:
            self._conn.close()
            self._conn = None
            ok = 0
        return ok

    def receive(self):
        "Receive answer from EPP server."
        if self._conn_ssl and self.__receive_header__():
            return self.__receive__()
        return ''

    def __receive_header__(self):
        "Header part of receiving process."
        self._body_length = 0
        ok = 0
        try:
            header = self._conn_ssl.read(4)
            ok = 1
        except socket.timeout, msg:
            self._errors.append('READ HEADER socket.timeout: %s'%msg)
        except socket.sslerror, msg:
            self._errors.append('READ HEADER socket.sslerror: %s'%str(msg))
        except socket.error, (no, msg):
            self._errors.append('READ HEADER socket.error: [%d] %s'%(no, msg))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupt from user'))
        else:
            # hlavička zprávy
            try:
                self._body_length = struct.unpack('!i',header)[0] - 4
            except struct.error, msg:
                self._errors.append('Error HEADER: %s'%msg)
                ok = 0
        if not ok: self.close()
        return self._body_length
        
    def __receive__(self):
        "Body part of receiving process."
        data = ''
        if self._body_length:
            ok = 0
            try:
                data = self._conn_ssl.read(self._body_length)
                ok = 1
            except socket.timeout, msg:
                self._errors.append('READ socket.timeout: %s'%msg)
            except socket.sslerror, msg:
                self._errors.append('READ socket.sslerror: %s'%str(msg))
            except socket.error, (no, msg):
                self._errors.append('READ socket.error: [%d] %s'%(no, msg))
            except (KeyboardInterrupt,EOFError):
                self._errors.append(_T('Interrupt from user'))
            if not ok: self.close()
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
        except socket.sslerror, msg:
            self._errors.append('SEND socket.sslerror: %s'%str(msg))
        except socket.error, (no, msg):
            self._errors.append('SEND socket.error: [%d] %s'%(no, msg))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupt from user'))
        if not ok: self.close()
        return ok

    def close(self):
        "Close connection."
        if self._conn:
            try:
                self._conn.close()
                self._conn = None
                self._conn_ssl = None
            except (KeyboardInterrupt,EOFError):
                self._errors.append(_T('Interrupt from user'))
            self._errors.append(_T('Connection closed'))

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 3:
        DATA = [sys.argv[1],700,sys.argv[2],sys.argv[3]]
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
    else:
        print "usage:",os.path.basename(__file__)," host client.key client.crt"

