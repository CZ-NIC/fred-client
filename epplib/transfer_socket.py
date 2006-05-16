# -*- coding: utf8 -*-
#!/usr/bin/env python
# Testování spojení: 
# python transfer_socket.py cli curlew 700
#
import re
import time
import socket
import threading

run = 0
lock = threading.Lock()

def stop(val=0):
    global run, lock
    lock.acquire()
    run = val
    lock.release()

def listen_loop(conn,conn_ssl):
    print "[START LOOP listen]"
    while run:
        try:
            if conn_ssl:
                data = conn_ssl.read()
            else:
                data = conn.recv(1024)
        except socket.error, msg:
            print msg
            stop()
        msg = data.strip()
        if msg=='':
            send(conn,conn_ssl) # oznámí konec spojení
            break
        print 'server:',msg
    print "[STOP LOOP listen]"

def send(conn,conn_ssl,msg='\n'):
    try:
        if conn_ssl:
            conn_ssl.write(msg)
        else:
            conn.send(msg)
        ok=1
    except socket.error, msg:
        print msg
        ok=None
    return ok

def parse(text):
    # simulace více řádek
    return re.sub('\\\\n','\n',text)

def main(conn, conn_ssl=None):
    stop(1)
    tr = threading.Thread(target=listen_loop, args=(conn,conn_ssl))
    tr.start()
    time.sleep(0.5)
    print "[START LOOP prompt]"
    while tr.isAlive():
        q = raw_input("> q (quit) ")
        if q.strip()=='': continue
        if q in ('q','quit','exit','konec'):
            stop()
            send(conn,conn_ssl) # inform end of session
            if tr.isAlive():
                print "[END->WAITING for listen loop]"
                tr.join()
            break
        print "you:",q
        msg = parse(q)
        if not send(conn,conn_ssl,msg):
            stop()
    print "[STOP LOOP prompt]"
    stop()

def main_server(port):
    print "Run as SERVER"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
    except socket.error, msg:
        print msg
        return
    sock.listen(1)
    print "Listen at port %d. (^C to break listening)"%(port,)
    conn=None
    try:
        conn, addr = sock.accept()
        print "Connected from",addr
    except socket.error, msg:
        print msg
    except KeyboardInterrupt:
        print 'Stoped by user'
    if conn: main(conn)

def main_client(host, port, type):
    print "Run as CLIENT"
    conn,conn_ssl = None,None
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print msg
        return
    print "Try to connect to %s, port %d"%(host, port)
    try:
        conn.connect((host, port))
        print "Connected to host %s, port %d"%(host, port)
    except socket.error, msg:
        print msg
        return
    if type=='sslc':
        print 'Init SSL connection'
        conn_ssl = socket.ssl(conn)
    if conn: main(conn,conn_ssl)
    
if __name__ == '__main__':
    import sys
    param = None
    host = 'localhost'
    port = 700
    if len(sys.argv) > 1:
        if sys.argv[1] in ('cli','serv','sslc'):
            param = sys.argv[1]
    print "INIT: type=%s; host='%s'; port=%d;"%(param,host,port)
    if param:
        if param in ('cli','sslc'):
            if len(sys.argv) > 2:
                host = sys.argv[2]
            if len(sys.argv) > 3:
                port = int(sys.argv[3])
            main_client(host,port,param)
        elif param=='serv':
            if len(sys.argv) > 2:
                port = int(sys.argv[2])
            main_server(port)
        else:
            print "unknown type"
        print '[END]'
    else:
        n=sys.argv[0]
        print """usage:
%s cli  [host [port]] # run as client
%s serv [port]        # run as server
%s sslc [host [port]] # run as SSL client
"""%(n,n,n)
