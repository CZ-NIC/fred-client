# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import socket
import threading
import time
import re
import struct
from gettext import gettext as _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._conn_ssl = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
##        self._thr_receive = threading.Thread(target = self.__listen_loop__) # thread pro příjem zpráv
##        self._thr_lock = threading.Lock() # zámek pro možnost zastavení threadu
##        self._run = 0                     # indikátor, že thread běží
        self._body_length = 0 # velikost EPP zprávy, která se má přijmout
        self._timeout = 3.0   # počet vteřin, po kterých se čeká na odpověď serveru

    def is_error(self):
        return len(self._errors)
        
    def connect(self, DATA):
##        self._host = DATA[0]
##        self._port = DATA[1]
        self._conn = None
        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, (no,msg):
            self._errors.append('Create socket.error [%d] %s'%(no,msg))
            return 0
        try:
            self._conn.connect((DATA[0], DATA[1]))
            self._notes.append('Connected to host %s, port %d'%tuple(DATA))
            self._conn.settimeout(self._timeout)
        except socket.error, (no,msg):
            self._errors.append('Connection socket.error [%d] %s'%(no,msg))
            return 0
##        if self._is_ssl:
        self._notes.append(_T('Init SSL connection'))
        try:
            self._conn_ssl = socket.ssl(self._conn)
        except socket.sslerror, msg:
            self._errors.append(msg)
            self._conn.close()
            self._conn = None
        return self._conn

##    def __close_socket__(self):
##        if self._conn:
##            self._conn.close()
##            self._conn = None

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
##            if self._conn_ssl:
##                header = self._conn_ssl.read()
##            else:
##                header = self._conn.recv(4)
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
        return self._body_length
        
    def __receive__(self):
        "Body part of receiving process."
        data = ''
        while self._body_length and len(data) < self._body_length:
            try:
                part = self._conn_ssl.read()
##                if self._conn_ssl:
##                    part = self._conn_ssl.read()
##                else:
##                    part = self._conn.recv(1024)
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
        return data.strip()

##    def __listen_loop__(self):
##        if not self._conn:
##            # když spojení neexistuje
##            if not self.__connect__():
##                # pokud se nepodařilo navázat
##                self.stop_listening()
##                return
##        print "*** START ***" #!!!
##        self.__receive_header__()
####        while self._run:
##        while self._run and self._body_length and len(data) < self._body_length:
##            try:
##                if self._conn_ssl:
##                    data = self._conn_ssl.read()
##                else:
##                    data = self._conn.recv(1024)
##            except socket.timeout, msg:
##                continue # nic se neděje, pustí se další naslouchání
##            except socket.sslerror, msg:
##                self._errors.append('READ socket.sslerror: %s'%msg)
##                break
##            except socket.error, (no, msg):
##                self._errors.append('READ socket.error: [%d] %s'%(no, msg))
##                break
##            msg = data.strip()
####            if msg=='':
####                # při neočekávaném přesušení
####                break
##            if msg: self.handler_message(msg)
##        print "*** STOP ***" #!!!
##        print self.fetch_errors() #!!!
##        self.stop_listening()
##        self.__close_socket__()

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
        
##    def stop_listening(self,val=''):
##        self._thr_lock.acquire()
##        self._run = val
##        self._thr_lock.release()

##    def run_listen_loop(self):
##        'Run receiving thread again.'
##        if not self._thr_receive.isAlive():
##            self.stop_listening('RUN!') # Run listen thread
##            self._thr_receive = threading.Thread(target = self.__listen_loop__)
##            self._thr_receive.start()
    
##    def join(self):
##        "Wait until listen process stops."
##        if self._thr_receive.isAlive():
##            # self._notes.append(_T('Wait to stop listen loop.'))
##            self._thr_receive.join()

##    def __debug_message__(self,msg):
##        print '!!!SSL:',msg
##        print '-'*60
##        out=[]
##        for i in range(0,len(msg),2):
##            if i and not (i%16):
##                print ' '.join(out)
##                out=[]
##            out.append('%02x%02x'%(ord(msg[i]),ord(msg[i+1])))
##        print '-'*60
            
    def send(self,msg):
##        if not self._conn:
##            if not self.__connect__(): return 0
        ok=0
##        message = '%s%s'%(struct.pack('!i',len(msg)+4),msg)
        try:
            self._conn_ssl.write('%s%s'%(struct.pack('!i',len(msg)+4),msg))
##            if self._conn_ssl:
##                self._conn_ssl.write(message)
##            else:
##                self._conn.send(message)
            ok=1
        except socket.timeout, msg:
            self._errors.append('SEND socket.timeout: %s'%msg)
        except socket.sslerror, (no, msg):
            self._errors.append('SEND socket.sslerror: [%d] %s'%(no, msg))
        except socket.error, (no, msg):
            self._errors.append('SEND socket.error: [%d] %s'%(no, msg))
##        if not ok: self.__close_socket__()
        return ok

    def close(self):
##        self.stop_listening() # Zastavit thread naslouchání
##        self.join() # pokud běží, tak počkat až se ukončí
##        self.__close_socket__()
        if self._conn:
            self._conn.close()
            self._conn = None

##    def connect(self, DATA):
##        self._host = DATA[0]
##        self._port = DATA[1]
####        self._is_ssl = (0,1)[is_ssl=='ssl']
##        return self.__connect__()



if __name__ == '__main__':
    import sys
    DATA = ['curlew',700]
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

