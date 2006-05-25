# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import socket
import threading
import time
import re
from gettext import gettext as _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._conn_ssl = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._thr_receive = threading.Thread(target = self.__listen_loop__) # thread pro příjem zpráv
        self._thr_lock = threading.Lock() # zámek pro možnost zastavení threadu
        self._run = 0                     # indikátor, že thread běží
        self._begin_listen = 0            # indikátor začátku přenosu

    def __connect__(self):
        self._conn = None
        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, (no,msg):
            self._errors.append('Create socket.error [%d] %s'%(no,msg))
            return 0
##        self._notes.append(_T("Try to connect to %s, port %d")%(self._host, self._port))
        try:
            self._conn.connect((self._host, self._port))
            self._notes.append(_T('Connected to host %s, port %d')%(self._host, self._port))
            self._conn.settimeout(3.0)
        except socket.error, (no,msg):
            self._errors.append('Connection socket.error [%d] %s'%(no,msg))
            return 0
        if self._is_ssl:
            self._notes.append(_T('Init SSL connection'))
            try:
                self._conn_ssl = socket.ssl(self._conn)
            except socket.sslerror, msg:
                self._errors.append(msg)
                self._conn.close()
                self._conn = None
        return self._conn

    def __close_socket__(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __parse_transmit_header__(self, t):
        if len(t)==4:
            # 4 bytes of message length
            # délka nás vpodstatě nezajímá
            #size = ord(t[0])<<32 | ord(t[1])<<16 | ord(t[2])<<8 | ord(t[3])
            #print "PART BEGINING: size=%d"%size
            t=''
        return t

    def __listen_loop__(self):
        if not self._conn:
            # když spojení neexistuje
            if not self.__connect__():
                # pokud se nepodařilo navázat
                self.stop_listening()
                return
        while self._run:
            try:
                if self._conn_ssl:
                    data = self._conn_ssl.read()
                else:
                    data = self._conn.recv(1024)
            except socket.timeout, msg:
                continue # nic se neděje, pustí se další naslouchání
            except socket.sslerror, msg:
                self._errors.append('READ socket.sslerror: %s'%msg)
                break
            except socket.error, (no, msg):
                self._errors.append('READ socket.error: [%d] %s'%(no, msg))
                break
            msg = data.strip()
            if msg=='':
                # při neočekávaném přesušení
                break
            if self._begin_listen:
                # při prvním přeneseném bloku:
                msg = self.__parse_transmit_header__(msg)
            self._begin_listen = 0 # první blok je za námi
            if msg: self.handler_message(msg)
        self.stop_listening()
        self.__close_socket__()

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
        print 'Client:',msg
        
    def stop_listening(self,val=''):
        self._thr_lock.acquire()
        self._run = val
        self._thr_lock.release()

    def run_listen_loop(self):
        'Run receiving thread again.'
        if not self._thr_receive.isAlive():
            self.stop_listening('RUN!') # Run listen thread
            self._begin_listen = 1 # indikátor začátku přenosu
            self._thr_receive = threading.Thread(target = self.__listen_loop__)
            self._thr_receive.start()
    
    def join(self):
        "Wait until listen process stops."
        if self._thr_receive.isAlive():
            # self._notes.append(_T('Wait to stop listen loop.'))
            self._thr_receive.join()

    def send(self,msg):
        if not self._conn:
            if not self.__connect__(): return 0
        ok=0
        try:
            if self._conn_ssl:
                self._conn_ssl.write(msg)
            else:
                self._conn.send(msg)
            ok=1
        except socket.timeout, msg:
            self._errors.append('SEND socket.timeout: %s'%msg)
        except socket.sslerror, msg:
            self._errors.append('SEND socket.sslerror: %s'%msg)
        except socket.error, (no, msg):
            self._errors.append('SEND socket.error: [%d] %s'%(no, msg))
        if not ok: self.__close_socket__()
        return ok

    def close(self):
        self.stop_listening() # Zastavit thread naslouchání
        self.join() # pokud běží, tak počkat až se ukončí
        self.__close_socket__()

    def connect(self, host, port, is_ssl=None):
        self._host = host
        self._port = port
        self._is_ssl = (0,1)[is_ssl=='ssl']
        return self.__connect__()



if __name__ == '__main__':
    import sys
##TEST    host, port, type = ('localhost',700,'cli')
    host, port, type = ('curlew',700,'ssl')
    if len(sys.argv)>1:
        host = sys.argv[1]
    cli = Lorry()
    if cli.connect(host,port,type):
        cli.run_listen_loop()
        print cli.fetch_notes()
        print "[START LOOP prompt]"
        while 1:
            q = raw_input("> q (quit) ")
            if q.strip()=='': continue
            if q in ('q','quit','exit','konec'): break
            if not cli.send(q): break
            cli.run_listen_loop()
        print "[STOP LOOP prompt]"
        print cli.fetch_notes()
        cli.close()
        print cli.fetch_errors()
        print cli.fetch_notes()
    else:
        print cli.fetch_errors()
        print cli.fetch_notes()

