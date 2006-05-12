# -*- coding: utf8 -*-

    ======================
    Struktura EPP klienta, Zdeněk Böhm, 11.5.2006
    ======================

    Veřejná část                                       .         Interní část
    ------------                                       .         ------------
    Jednotlivé typy klientů:                           .
    Klienti zobrazují data stanoveným způsobem.        .
    Data předávají/získávají od objektu Manager()      .
    v modulu client_session z knihovny epplib          .
                                                       .
    +---------------------+                            .   +------------------------+
 +--| epp_batch.py        | zpracovává dávkový soubor  .   | run_test_epp_server.py |
 |  +---------------------+                            .   +------------------------+
 |                                                     .     Testování serveru
 |  +---------------------+                            .
 +--| epp_console.py      | interaktivní konzole       .
 |  +---------------------+                            .
 |                                                     .
 |  +---------------------+                            .
 +--| epp_windows.py      | GUI okna na Tkinteru       .                  CORBA
 |  +---------------------+                            .                    ^
 |                                                     .                    |
====[ knihovna epplib ]=================================================================
 |                                                     .                    |
 |   +--------------------+ stará se o session         .          +--------------------+
 +-->| client_session.py  | řídí EPP dokumenty         .          | server_session.py  |
     | class Manager()    | udržuje spojení            .          | class Manager()    |
	 +--------------------+ vlastní help               .          +--------------------+
         |     |                                       .                    |
         |     |   +--------------------+              .          +--------------------+
         |     +-->| client_socket.py   | <---------------------->| server_socket.py   |
         |         +--------------------+              .          +--------------------+
         |         provádí SSL spojení se servrem      .                    |
         |                                             .                    |
         |   +--------------------+                    .          +--------------------+
         +-->| client_eppdoc.py   | sestavuje EPP      .          | server_eppdoc.py   |
             | class Message()    | dokumenty          .          | class Message()    |
             +--------------------+                    .          +--------------------+
                       |                               .                    |
                       |     funkce pro tvorbu XML EPP .                    |
                       |        +--------------------+ .                    |
                       +------->| eppdoc.py          |<---------------------+
                                | class Message()    | .
                                +--------------------+ .
                                         |             .
                                +--------------------+ .
                 chybové hlášky | responses.py       | .
                                +--------------------+ .
                                         |             .
                                +--------------------+ .
                                | templates/         | .
                                +--------------------+ .
                                šablony EPP dokumentů  .
                                                       .
=========================================================================================
Způsob použití knihovny epplib:                   client.send(epp_doc)
                                                  epp_server_answer = client.receive()
import epplib                                     print client.digest(epp_server_answer)
client = epplib.client_session.Manager()               
notes, errors, epp_doc = client.get_result("hello")    
print 'NOTES:',notes                                
print 'ERRORS:',error                               
print 'XMLEPP:',epp_doc                             
