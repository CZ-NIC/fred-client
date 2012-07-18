# -*- coding: utf8 -*-
Tento dokument je uložen v kódování UTF-8


#################################################

    Popis knihovny fred

    Zdeněk Böhm
    13.7.2006

#################################################

    +----------------------------------+
 +--|  fred_console.py                 |
 |  |----------------------------------|
 |  | interaktivní konzole EPP klienta |
 |  +----------------------------------+
 |
 |
====[ knihovna fred ]===================================================================
 |
 |                                                   +---------------------------------+
 |-------------------------------------------------->| cmd_history.py                  |
 |                                                   |---------------------------------|
 |                                                   | ovládá historii příkazového     |
 |                                                   | řádku konzole                   |
 |                                                   +---------------------------------+
 |
 |   +======================================+        +=================================+
 |   | Client Session Manager               |<-------| __init__   * API * rozhraní pro |
 +-->|======================================|        |práci s knihovnou fred v pythonu |
     | ovládá všechny objekty tvorby EPP    |        +=================================+
     | dokumentů a komunikace se serverem   |
     |                                      |        +=================================+
     | je rozdělen do modulů:               |    +---| EPP document                    |
     |--------------------------------------|    |   |=================================|
     | session_receiver.py                  |<---+   | sestavuje XML dokument podle EPP|
     |                                      |    |   | schemat                         |
     | tato část má na starosti přijímání   |    |   |---------------------------------|
     | EPP zpráv od serveru, jejich         |    |   | eppdoc_client.py                |
     | interpretaci a zobrazení             |    |   |                                 |
     |                                      |    |   | zde jsou definice parametrů     |
     |--------------------------------------|    |   | jednotlivých EPP příkazů        |
     | session_command.py                   |<---+   |---------------------------------|
     |                                      |        | eppdoc_assemble.py              |
     | v této části se generují EPP příkazy |<---+   |                                 |
     | podle zadání z příkazové řádky nebo  |    |   | zde jsou funkce, které sestavují|
     | z funkcí API.                        |    |   | EPP dokumenty                   |
     |                                      |    |   |---------------------------------|
     |--------------------------------------|    |   | eppdoc.py                       |
     | session_transfer.py                  |<-+ |   |                                 |
     |                                      |  | |   | zde jsou obecné funkce pro      |
     | tato část komunikuje se sockety      |  | |   | podporu tvorby XML              |
     |                                      |  | |   +=================================+
     |--------------------------------------|  | |
     | session_base.py                      |  | |   +=================================+
     |                                      |  | +---| cmd_parser.py                   |
     | tato část se stará o chybová hlášení,|  |     |---------------------------------|
     | o validaci dokumentů a o config      |  |     | parsuje příkazovou řádku do dict|
     |                                      |  |     +=================================+
     +======================================+  |
              |       |      |      |          |     +=================================+
              |       |      |      |          +-----| client_socket.py                |
              |       |      |      |                |---------------------------------|
              |       |      |      |                | ovládá sockety komunikace       |
              |       |      |      |                +=================================+
              |       |      |      |
              |       |      |      |                +=================================+
              |       |      |      +--------------->| translate.py                    |
              |       |      |                       |---------------------------------|
              |       |      |                       | lokalizace - výběr předkladu    |
              |       |      |                       +=================================+
              |       |      +---------------------------------------------+
              |       +------------------------+                           |
              V                                V                           V
     +======================+     +=======================+     +======================+
     | default-config.txt   |     | terminal_controler.py |     | schemas              |
     |----------------------|     |-----------------------|     |----------------------|
     | hodnoty nastavení    |     | zobrazení barev       |     | adresář s xsd EPP    |
     | session (managera)   |     | na konzoli            |     | schematy pro validaci|
     +======================+     +=======================+     +======================+
