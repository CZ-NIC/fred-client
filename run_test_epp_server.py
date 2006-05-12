# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import epplib.server_session

def test(host, port):
    server = epplib.server_session.Manager()
    if not server.listen(host, port):
        return
    while 1:
        if not server.receive_from_client():
            print server.get_transfer_errors()
            break
        command = server.get_received_command()
        answer = server.answer(command)
        server.send_to_client(command)
        print '-'*60,'\nCLIENT COMMAND:\n',command
        print '-'*60,'\nSERVER ANSWER:\n',answer
    server.disconnect()
    print "[END SERVER TEST]"

        
if __name__ == '__main__':
    test('', 700)
