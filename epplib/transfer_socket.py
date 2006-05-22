# -*- coding: utf8 -*-
#!/usr/bin/env python
# Testování spojení: 
# python transfer_socket.py cli curlew 700
#
# Odpověď serveru: 0x00(nul),0x00,0x02(stx)<?xml ...
# ... epp ...
# 0x00,0x00,0x00,0x04 (CTRL-D|eot)
#
import re
import time
import socket
import threading

EOT = '\4'
END = '\0\0\0\4' #!!!
run = 0
timeout = 3.0 # sec. doba čekání na příchozí paket
lock = threading.Lock()
listen_thread = None # naslouchací thread
conn, conn_ssl = None,None # konexe soketů

INIT=['','localhost',700,''] # type, host, port, i - interactive server

def stop(val=0):
    global run, lock
    lock.acquire()
    run = val
    lock.release()

set_run = lambda : stop(1)

def close():
    global conn, conn_ssl
    if conn:
##        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        conn,conn_ssl = None,None
        print '[conn CLOSE]'

def connect(verbose=None):
    global conn,conn_ssl
    conn, conn_ssl = None,None # konexe soketů
    HP = tuple(INIT[1:3])
    if verbose: print '[create socket]'
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(timeout)
    except socket.error, (no,msg):
        print 'CREATE socket.error: [%d] %s'%(no,msg)
        close()
        return 0
    if verbose: print "Try to connect to %s, port %d"%HP
    try:
        conn.connect(HP)
        if verbose: print "Connected to host %s, port %d"%HP
    except socket.error, (no,msg):
        print 'CONNECT socket.error: [%d] %s'%(no,msg)
        close()
        return 0
    if INIT[0]=='cli-ssl':
        if verbose: print 'Init SSL connection'
        conn_ssl = socket.ssl(conn)
    if 1:
        print 'getpeername()',conn.getpeername() # vzdálený ('host', port)
        print 'getsockname()',conn.getsockname() # vlastní ('host', port)
    return conn

def parse_white_chars(text):
    chars=[]
    for c in text:
        chars.append(c)
        if ord(c) < 0x20:
            chars.append('(0x%02x)'%ord(c))
    return ''.join(chars)

def parse_from_server(msg):
    print 'server says:',parse_white_chars(msg)

def parse_from_client(msg):
    print 'client says:',msg
    send("jak myslíš, nechám to na tobě")
    if INIT[0] == 'servnot':
##        send(EOT) # klientovi se pošle zakončovací kód
        stop() # po každé odpovědi se spojení přeruší
    
def listen_loop(verbose):
    if not conn:
        if not connect(verbose): return
##    print '[START LOOP listen]'
    while run:
##        print "--[STEP listen]--"
        try:
            if conn_ssl:
                data = conn_ssl.read()
            else:
                data = conn.recv(1024)
        except socket.timeout, msg:
            continue # nic se neděje, pustí se další naslouchání
        except socket.sslerror, msg:
            print 'socket.sslerror: %s'%msg
            break
        except socket.error, (no, msg):
            print 'socket.error: [%d] %s'%(no, msg)
            break
        msg = data.strip()
        if msg=='':
        # při neočekávaném přesušení
##            print "Empty:",parse_white_chars(data)
            break
        parse_incomming_message(msg)
        if EOT in msg:
            print '[EOT occured]'
            break
    stop()
##    print "[STOP LOOP listen]"
    close()

def send(msg):
    ok=None
    if not conn:
        if not connect(): return 0
    try:
        if conn_ssl:
            conn_ssl.write(msg)
        else:
            conn.send(msg)
        ok=1
    except socket.timeout, msg:
        print 'socket.timeout',msg
    except socket.sslerror, msg:
        print 'socket.sslerror: %s'%msg
    except socket.error, (no, msg):
        print 'socket.error: [%d] %s'%(no, msg)
    return ok

def parse(text):
    # simulace více řádek
    return re.sub('\\\\n','\n',text)

def run_listen_loop(verbose=None):
    global listen_thread
    if listen_thread and listen_thread.isAlive():
        # když proces naslouchání stále běží, 
        # tak není třeba jej znova spouštět
        return
##    print '[Init listen THREAD]'
    set_run() # nastavení příznaku běhu
    listen_thread = threading.Thread(target=listen_loop, args=(verbose,))
    listen_thread.start()
    time.sleep(0.5)
    
def main():
    run_listen_loop('display connection notes') # spustí se naslouchání
##    print "[START LOOP prompt]"
    while 1: 
        # vkládací smyčka běží, dokud ji uživatel neukončí
        q = raw_input("> q (quit) ")
        if q.strip()=='': continue
        if q in ('q','quit','exit','konec'):
##            send(END)
            break
        print "you:",q
        msg = parse(q)
        if not send(msg): break
        run_listen_loop()
##    print "[STOP LOOP prompt]"
    stop() # stop listening
    if listen_thread.isAlive():
        # Pokud běží naslouchání, tak se počká na jeho ukončení.
        print "[END->WAITING for listen loop]"
        listen_thread.join()
    close()

def main_client():
    global parse_incomming_message
    parse_incomming_message = parse_from_server
    print "Run as CLIENT"
    main()
        
def main_server():
    global conn, parse_incomming_message
    parse_incomming_message = parse_from_client
    print "Run as SERVER type",('KEEP connection','NOT KEEP connection')[INIT[0]=='servnot']
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(('', INIT[2]))
    except socket.error, (no,msg):
        print 'SERVER BIND socket.error: [%d] %s'%(no,msg)
        return
    server_sock.listen(1)
    print "Listen at port %d..."%INIT[2]
    while 1:
        print '--[WAITING to next client]-- (CTRL+C to close)'
        conn=None
        try:
            conn, addr = server_sock.accept()
            print "Connected from",addr
            conn.settimeout(timeout)
        except socket.error, (no,msg):
            print 'SERVER ACCEPT socket.error: [%d] %s'%(no,msg)
        except KeyboardInterrupt:
            print 'Shutdown by user'
            break
        if conn:
            run_listen_loop('display connection notes') # spustí se naslouchání
            if INIT[3]=='i' and INIT[0] != 'servnot':
                # interactive server
                print '[SERVER RUN prompt loop]'
                while 1:
                    q = raw_input("> q (quit) ")
                    if q.strip()=='': continue
                    if q in ('q','quit','exit','konec','shut','shutdown'):
                        break
                    if not send(q): break
                    run_listen_loop()
                if q in ('shut','shutdown'):
                    print '[SERVER SHUTDOWN]'
                    stop()
                    break
            listen_thread.join() # čeká se na ukončení naslouchání
            close()
    listen_thread.join() # čeká se na ukončení naslouchání
    close()
    server_sock.close()
    print '[SERVER closed]'

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] in ('cli','cli-ssl','serv','servnot'):
            INIT[0] = sys.argv[1]
    if INIT[0]:
        if INIT[0] in ('cli','cli-ssl'):
            if len(sys.argv) > 2:
                INIT[1] = sys.argv[2]
            if len(sys.argv) > 3:
                INIT[2] = int(sys.argv[3])
            print "CLIENT INIT: type=%s; host='%s'; port=%d; interactive='%s';"%tuple(INIT)
            main_client()
        elif INIT[0] in ('serv','servnot'):
            if len(sys.argv) > 2:
                INIT[2] = int(sys.argv[2]) # port
            if len(sys.argv) > 3:
                INIT[3] = sys.argv[3] # ineractive
            print "SERVER INIT: type=%s; host='%s'; port=%d; interactive='%s';"%tuple(INIT)
            main_server()
        else:
            print "unknown type"
        print '[END]'
    else:
        n=sys.argv[0]
        print """usage:
%s cli     [host [port]] # run as client
%s cli-ssl [host [port]] # run as SSL client
%s serv    [port [i]]    # run as server keeping connection (interactive)
%s servnot [port [i]]    # run as server NOT keeping connection (interactive)
"""%(n,n,n,n)
