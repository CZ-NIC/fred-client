# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
"""Přenos zpráv přes TCP/IP.
Použití viz funkce test()
"""
import socket
import threading
import time
import re
from gettext import gettext as _T

class Lorry:
    "Socket transfer."
    def __init__(self):
        self._conn = None
        self._notes = [] # hlášení o stavu
        self._errors = [] # chybová hlášení
        self._cargo = ''
        self.run=0        # run receive thread
        self._thr_receive = threading.Thread(target = self.run_receive)
        self._thr_lock = threading.Lock()
        self._timeout = 5 # pokus se do timeoutu nic nepřijme, tak se pošle PING
        self._last_receive = None # čas posledního příjmu zprávy
        self._fnc = None # funkce pro zpracování zprávy

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

    def join(self):
        if self._thr_receive.isAlive(): self._thr_receive.join()
        
    def set_run(self,value):
        self._thr_lock.acquire()
        self.run = value
        self._thr_lock.release()

    def close(self):
        self.set_run(0) # Zastavit thread naslouchání
        self.join() # počkat, až se ukončí naslouchání
##        if self._thr_receive.isAlive(): self._thr_receive.join()
        if self._conn:
            self._conn.close()
            self._conn = None
            self._notes.append(_T('Disconnected.'))

    def connect(self, host, port):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._conn.connect((host, port))
            self._conn.settimeout(1.0)
            self._notes.append(_T('Connected at server OK.'))
        except socket.error, (errno,msg):
            self._errors.append('socket.error: [%d] %s'%(errno,msg))
            self._conn = None
        return self._conn

    def send(self, message):
        try:
            self._conn.send(message)
        except socket.error, msg:
            self.set_run(0)
##            self._errors.append('socket.error: [%d] %s'%(errno,msg))
            self._errors.append('socket.error: %s'%str(msg))
        return self.run
        
    def receive(self):
        self._cargo=''
        valid=0
        try:
            self._cargo = self._conn.recv(1024)
            valid=1
            if(self._cargo.strip()):
                # pokud něco přišlo, tak je spojení pořád živé
                self._last_receive = time.time()
        except socket.timeout:
            valid=1 # přerušení příjmu, aby se mohl zastavit thread
        except socket.error, (errno,msg):
            self._errors.append('socket.error: [%d] %s'%(errno,msg))
        except AttributeError:
            pass # došlo ke zrušení objektu
        return valid

    def check_timeout(self):
        "Control if timeout occurs"
        if (time.time() - self._last_receive) > self._timeout:
            # pokud byl překročen timeout, tak se spojení pingne
            self.send('PING')

    def get_clear_cargo(self):
        "Return messages. (Ommit PING & PONG)"
        cargo = self.get_cargo().strip()
        if cargo:
            if re.match('P(I|O)NG.*',cargo):
                if re.match('PING.*',cargo): self.send('PONG')
                cargo='' # PING, PONG nezobrazovat
        return cargo
            
            
    def run_receive(self):
        "Run into own thread."
        self._last_receive = time.time()
        while self.run:
            if not self.receive():
                self.set_run(0)
                print self.fetch_errors()
                break
            cargo = self.get_clear_cargo()
            if cargo:
                # pokud je nějaká zpráva přijata
                if self._fnc:
                    self._fnc(cargo) # funkce pro zpracování zprávy
                else:
                    print cargo # jen test
            self.check_timeout()
        print '[Receive process stopped]'
            
    def start_receive_thread(self, fnc=None):
        "Start receiving thread."
        self._fnc = fnc # funkce pro zpracování zprávy
        self.set_run(1)
        self._thr_receive.start()
        return self._thr_receive.isAlive()

    def isAlive(self):
        ret = None
        if self._thr_receive:
            ret = self._thr_receive.isAlive()
        return ret
        
def test(host, port):
    transport = Lorry()
    if transport.connect(host, port):
        print transport.fetch_notes()
        # spustí se thread s příjmem
        transport.start_receive_thread()
    else:
        print transport.fetch_errors()
        return
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
    test('localhost',700)
