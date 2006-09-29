# -*- coding: utf8 -*-
#!/usr/bin/env python
import os
import socket
import threading
import time
import re
import struct
from translate import _T, encoding

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._conn_ssl = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._body_length = 0 # velikost EPP zprávy, která se má přijmout
        self._timeout = 10.0 # Windows bug! In MS-Win MUST be zero.

    def is_error(self):
        return len(self._errors)

    def is_connected(self):
        return self._conn and self._conn_ssl

    def connect(self, DATA, verbose=1):
        "DATA = ('host', PORT, 'file.key', 'file.crt', timeout, 'socket_family')"
        family = {}
        family[socket.AF_INET] = 'IPv4'
        if getattr(socket,'AF_INET6',None):
            family[socket.AF_INET6] = 'IPv6'
        elif verbose > 1:
            self._notes.append(_T('Socket type IPv6 (AF_INET6) is not present in socket module.'))
        family_rev = {}
        for k,v in family.items():
            family_rev[v.lower()] = k
        ok = 0
        self._conn = None
        try:
            self._timeout = float(DATA[4])
        except ValueError:
            pass
        if DATA[5]:
            socket_family = family_rev.get(DATA[5].lower(),socket.AF_INET)
        else:
            try:
                tc = socket.getaddrinfo(DATA[0], DATA[1])
                socket_family = tc[0][0]
            except socket.error, (no,msg):
                self._errors.append('getaddrinfo() socket.error [%d] %s'%(no,msg))
                socket_family = socket.AF_INET
        if verbose > 1: self._notes.append('%s: ${BOLD}%s${NORMAL}.'%(_T('Used socket type'),family[socket_family]))
        try:
            self._conn = socket.socket(socket_family, socket.SOCK_STREAM)
            ok = 1
        except socket.error, (no,msg):
            self._errors.append('Create socket.error [%d] %s'%(no,msg))
            # WinXP IPv6: [10047] Address family not supported
        except TypeError, msg:
            self._errors.append('Create socket.error (socket.getaddrinfo): %s'%msg)
        if self._conn is None: return 0
        if self._timeout:
            self._notes.append('Socket timeout: ${BOLD}%.1f${NORMAL} sec.'%self._timeout)
            self._conn.settimeout(self._timeout)
        try:
            self._conn.connect((DATA[0], DATA[1]))
            self._notes.append('%s ${BOLD}%s${NORMAL}, port %d'%(_T('Opened connection to'), DATA[0], DATA[1]))
        except socket.error, tmsg:
            self._errors.append('Connection socket.error: %s (%s:%s)'%(str(tmsg),DATA[0],DATA[1]))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupted by user'))
        if not ok: return ok
        if verbose > 1: self._notes.append(_T('SSL connection initiated'))
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
                self._notes.append(_T('Certificates missing. Trying to connect without SSL!'))
                self._conn_ssl = socket.ssl(self._conn)
            ssl_ok = 1
        except socket.sslerror, msg:
            self._errors.append('socket.sslerror: %s (%s:%s)'%(str(msg),DATA[0],DATA[1]))
            if type(msg) not in (str,unicode):
                err_note = {
                    1:_T('Certificate not signed by verified certificate authority.'),
                    2:'%s\n%s'%(_T('Server configuration is not valid. Contact administrator.'),
                      _T('If this client runs under MS Windows and timeout is not zero, it is probably SLL bug! Set timeout back to zero.')),
                }
                try:
                    text = err_note.get(msg[0],None)
                    if text: self._errors.append(text)
                except (TypeError, IndexError):
                    pass
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupted by user'))
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
        except socket.error, tmsg:
            self._errors.append('READ HEADER socket.error: %s'%str(tmsg))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupted by user'))
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
                while(len(data) < self._body_length):
                    part = self._conn_ssl.read(self._body_length)
                    if not len(part):
                        self._errors.append('READ empty part')
                        break
                    data += part
                ok = len(data) == self._body_length
            except socket.timeout, msg:
                self._errors.append('READ socket.timeout: %s'%msg)
            except socket.sslerror, msg:
                self._errors.append('READ socket.sslerror: %s'%str(msg))
            except socket.error, tmsg:
                self._errors.append('READ socket.error: %s'%str(tmsg))
            except MemoryError, msg:
                self._errors.append('READ socket.receive MemoryError: %s'%msg)
            except (KeyboardInterrupt,EOFError):
                self._errors.append(_T('Interrupted by user'))
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
        except socket.error, tmsg:
            self._errors.append('SEND socket.error: %s'%str(tmsg))
        except (KeyboardInterrupt,EOFError):
            self._errors.append(_T('Interrupted by user'))
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
                self._errors.append(_T('Interrupted by user'))
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

