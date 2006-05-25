# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import epplib.server_session

def test(server):
    # zde se spustí naslouchací smyčka:
    while server.listen():
        server.run_listen_loop()
        server.wait_to_listen() # čeká se na ukončení naslouchání
    server.close()
    print server.fetch_errors()
    print server.fetch_notes()
    print "[END SERVER TEST]"

if __name__ == '__main__':
    DATA=('',700,'') # host, port, keep-connection
    server = epplib.server_session.Manager()
    if server.bind(DATA):
        test(server)
    else:
        print server.fetch_errors()
        print server.fetch_notes()
