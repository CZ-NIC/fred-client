#!/usr/bin/env python
#
#This file is part of FredClient.
#
#    FredClient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    FredClient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FredClient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import os, sys
import socket
import threading
import time
import re
import struct
from translate import encoding

try:
    # python 2.6
    import ssl
except ImportError:
    # python 2.5
    ssl = None

"""Module client_socket manage connection handler. Create socket, open and close
connection. Collect the errors and notes for displaying. Method of communication
is described in RFC3734.txt - Transport Over TCP (4.  Data Unit Format) and
RFC3730.txt  (2. Protocol Description).
Class Lorry is managed by ManagerTransfer in session_transfer.py.
"""

if not getattr(socket, 'ssl', None):
    # Protect to missing SSL support
    print _T("This version of Python doesn't support SSL. Reinstall it with SLL support.")
    sys.exit(-1)

class Lorry:
    "Socket transfer."
    def __init__(self, parent):
        self._conn = None
        self._conn_ssl = None
        self._parent = parent # keep parent object for notes and error messages
        self._body_length = 0 # size of the EPP document what will be received
        self._timeout = 10.0 # Windows bug! In MS-Win MUST be zero.

    def is_error(self):
        return self._parent.is_error()
    
    def append_error(self, msg):
        'Join error message to the message list.'
        self._parent.append_error(msg)

    def append_note(self, msg):
        'Join note to the message list.'
        self._parent.append_note(msg)
        
    def is_connected(self):
        return self._conn and self._conn_ssl

    def connect(self, DATA, verbose=1):
        "DATA = ('host', PORT, 'file.key', 'file.crt', timeout, 'socket_family')"
        self.try_again_with_timeout_zero = False # false - no, true - yes
        # this values has been checked before already...
        if len(DATA) < 4:
            self.append_error(_T('Certificate names not set.'))
        if len(DATA) > 2 and not os.path.isfile(DATA[2]):
            self.append_error('%s %s'%(DATA[2],_T('Private key file not found.')))
            DATA[2] = None
        if len(DATA) > 3 and not os.path.isfile(DATA[3]):
            self.append_error('%s %s'%(DATA[3],_T('Certificate key file not found.')))
            DATA[3] = None
        try:
            port = int(DATA[1]) # port has been checked in previous code, but for safety...
        except ValueError, msg:
            self.append_error('%s: %s'%(_T('Invalid port value'),str(DATA[1])))
        else:
            DATA[1] = port
        if self._parent.is_error():
            return 0 # if any errors occured there's no point in
        
        family = {}
        family[socket.AF_INET] = 'IPv4'
        if getattr(socket,'AF_INET6',None):
            family[socket.AF_INET6] = 'IPv6'
        elif verbose > 1:
            self.append_note(_T('Socket type IPv6 (AF_INET6) is not present in socket module.'))
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
                self.append_error('getaddrinfo() socket.error [%d] %s'%(no,msg))
                socket_family = socket.AF_INET
        if verbose > 1: self.append_note('%s: ${BOLD}%s${NORMAL}.'%(_T('Used socket type'),family[socket_family]))
        try:
            self._conn = socket.socket(socket_family, socket.SOCK_STREAM)
            ok = 1
        except socket.error, (no,msg):
            self.append_error('Create socket.error [%d] %s'%(no,msg))
            # WinXP IPv6: [10047] Address family not supported
        except TypeError, msg:
            self.append_error('Create socket.error (socket.getaddrinfo): %s'%msg)
        if self._conn is None:
            return 0
            
        if self._timeout:
            if verbose > 1: self.append_note('Socket timeout: ${BOLD}%.1f${NORMAL} sec.'%self._timeout)
            self._conn.settimeout(self._timeout)
        #self.append_note('%s ${BOLD}%s${NORMAL}, port %d ...'%(_T('Connecting to'), DATA[0], DATA[1]))
        self.append_note('%s %s, port %d ...'%(_T('Connecting to'), DATA[0], DATA[1]))
        try:
            self._conn.connect((DATA[0], DATA[1]))
        except socket.error, tmsg:
            self.append_error('%s %s.\n'%(_T('I cannot connect to the server'),DATA[0]))
            self.append_error('Connection socket.error: %s (%s:%s)'%(str(tmsg),DATA[0],DATA[1]))
        except (KeyboardInterrupt,EOFError):
            self.append_error(_T('Interrupted by user'))
        if not ok:
            return ok
            
        if verbose > 1:
            self.append_note(_T('Connection established.'))
            self.append_note(_T('Try to open SSL layer...'))
        if self._parent.is_error():
            return 0 # if any errors occured there's no point in
            
        ssl_ok = 0
        try:
            if len(DATA) > 3 and DATA[2] and DATA[3]:
                if ssl:
                    # python 2.6
                    self._conn_ssl = ssl.wrap_socket(self._conn, 
                                             keyfile=DATA[2], certfile=DATA[3])
                else:
                    # python 2.5
                    self._conn_ssl = socket.ssl(self._conn, DATA[2], DATA[3])
            else:
                self.append_note(_T('Certificates missing. Trying to connect without SSL!'))
                self._conn_ssl = socket.ssl(self._conn)
            ssl_ok = 1
        except socket.sslerror, msg:
            self.append_error('socket.sslerror: %s (%s:%s)'%(str(msg),DATA[0],DATA[1]))
            if type(msg) not in (str,unicode):
                err_note = {
                    1:_T('Certificate not signed by verified certificate authority.'),
                    2:'%s\n%s'%(_T('Server configuration is not valid. Contact administrator.'),
                      _T('If this client runs under MS Windows and timeout is not zero, it is probably SLL bug! Set timeout back to zero.')),
                }
                try:
                    text = err_note.get(msg[0],None)
                    if text: self.append_error(text)
                except (TypeError, IndexError):
                    pass
                self.try_again_with_timeout_zero = msg[0] == 2 # false - no, true - yes
        except (KeyboardInterrupt,EOFError):
            self.append_error(_T('Interrupted by user'))
        if ssl_ok:
            if verbose > 1: self.append_note(_T('SSL layer opened.'))
        else:
            self._conn.close()
            self._conn = None
            ok = 0
        return ok

    def receive(self):
        "Receive answer from EPP server."
        message = ''
        if self._conn_ssl and self.__receive_header__():
            message = self.__receive__()
        return message

    def __receive_header__(self):
        "Header part of receiving process."
        self._body_length = 0
        ok = 0
        try:
            header = self._conn_ssl.read(4)
            ok = 1
        except socket.timeout, msg:
            self.append_error('READ HEADER socket.timeout: %s'%msg)
        except socket.sslerror, msg:
            self.append_error('READ HEADER socket.sslerror: %s'%str(msg))
        except socket.error, tmsg:
            self.append_error('READ HEADER socket.error: %s'%str(tmsg))
        except (KeyboardInterrupt,EOFError):
            self.append_error(_T('Interrupted by user'))
        else:
            # message header
            try:
                self._body_length = struct.unpack('!i',header)[0] - 4
            except struct.error, msg:
                self.append_error('ERROR HEADER: %s'%msg)
                ok = 0
        if not ok: self.close()
        return ok
        
    def __receive__(self):
        "Body part of receiving process."
        data = ''
        ok = 0
        if self._body_length:
            try:
                while(len(data) < self._body_length):
                    part = self._conn_ssl.read(self._body_length)
                    if not len(part):
                        self.append_error('READ empty part')
                        break
                    data += part
                ok = len(data) == self._body_length
            except socket.timeout, msg:
                self.append_error('READ socket.timeout: %s'%msg)
            except socket.sslerror, msg:
                self.append_error('READ socket.sslerror: %s'%str(msg))
            except socket.error, tmsg:
                self.append_error('READ socket.error: %s'%str(tmsg))
            except MemoryError, msg:
                self.append_error('READ socket.receive MemoryError: %s'%msg)
            except (KeyboardInterrupt,EOFError):
                self.append_error(_T('Interrupted by user'))
        else:
            # the answer cannot be zero length
            self.append_error(_T("Server returned an empty message."))
        if not ok: self.close()
        return data.strip()

    def fetch_errors(self, sep='\n'):
        return self._parent.fetch_errors(sep)

    def fetch_notes(self, sep='\n'):
        return self._parent.fetch_notes(sep)

    def handler_message(self, msg):
        'Handler of incomming message'
        # function for precess message
        print 'SERVER ANSWER:\n',msg
        
    def send(self,msg):
        "Send message to server."
        # Here can be automatic connection, be casue we need use session Manager
        ok=0
        try:
            self._conn_ssl.write('%s%s'%(struct.pack('!i',len(msg)+4),msg))
            ok=1
        except socket.timeout, msg:
            self.append_error('SEND socket.timeout: %s'%msg)
        except socket.sslerror, msg:
            self.append_error('SEND socket.sslerror: %s'%str(msg))
        except socket.error, tmsg:
            self.append_error('SEND socket.error: %s'%str(tmsg))
        except (KeyboardInterrupt,EOFError):
            self.append_error(_T('Interrupted by user'))
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
                self.append_error(_T('Interrupted by user'))
        self._conn = None
        self._conn_ssl = None


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 3:
        DATA = [sys.argv[1],700,sys.argv[2],sys.argv[3],'10.0','']
        class TestParent:
            def __init__(self):
                self.reset()
            def reset(self):
                self._errors = []
                self._notes = []
            def append_error(self, msg):
                self._errors.append(msg)
            def append_note(self, msg):
                self._notes.append(msg)
            def fetch_notes(self, sep='\n'):
                report = sep.join(self._errors)
                self._notes = []
                return report
            def fetch_errors(self, sep='\n'):
                report = sep.join(self._notes)
                self._errors = []
                return report
            def is_error(self):
                return len(self._errors)
            def display(self, sep='\n'):
                sys.stderr.write('%s\n'%sep.join(self._errors))
                sys.stderr.write('%s\n'%sep.join(self._notes))
                self.reset()
        manager = TestParent()
        client = Lorry(manager)
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
                manager.display()
            manager.display()
            print "[STOP LOOP prompt]"
        print client.fetch_errors()
        print client.fetch_notes()
        client.close()
    else:
        print "usage:",os.path.basename(__file__)," host client.key client.crt"

