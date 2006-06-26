# -*- coding: utf8 -*-
#!/usr/bin/env python
from gettext import gettext as _T
import client_eppdoc
import client_socket
from client_session_base import *

class ManagerTransfer(ManagerBase):
    """EPP client support.
    This class take care about sending and receiving messages from/to server.
    Function process_answer() must be implemented by derived class.
    """
    def __init__(self):
        ManagerBase.__init__(self)
        self._epp_cmd = client_eppdoc.Message()
        self._epp_response = client_eppdoc.Message()
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        # Typ očekávané odpovědi serveru. Zde si Manager pamatuje jaký příkaz
        # odeslal a podle toho pak zařadí návratové hodnoty.
        self._command_sent = ''
        self._raw_cmd = None # XML EPP příkaz odeslaný serveru

    def get_command_names(self):
        return self._available_commands

    #---------------------------------
    # funkce pro nastavení session
    #---------------------------------
    def __logout_session__(self):
        "Set internal session variables in the ID session."
        if self._session[ONLINE]:
            # odlogování
            self._session[ONLINE] = 0 # reset pořadí příkazů
            self._lorry.close() # zrušení konexe na server

    def __check_is_connected__(self):
        "Control if you are still connected."
        if self._lorry and not self._lorry.is_connected():
            # spojení spadlo
            if self._session[ONLINE]: self.append_note('--- %s ---'%_T('Connection broken'))
            self.__logout_session__()

            
    def __command_sent__(self, message):
        "Save EPP command type for recognize server answer."
        # manager si zapamatuje jakého typu příkaz byl a podle toho 
        # pak pracuje s hodnotami, které mu server vrátí
        # Tady se typ musí vytáhnout přímo z XML, jiná možnost není. 
        # Protože lze posílat i XML již vytvořené dříve nebo z jiného programu.
        epp_xml = client_eppdoc.Message()
        epp_xml.parse_xml(message)
        self._command_sent = epp_xml.get_epp_command_name()

    #==================================================
    #
    #    Transfer functions
    #    funkce pro komunikaci se socketem
    #
    #==================================================
    def connect(self, data=None):
        "Connect transfer socket. data=('host',port,'client-type')"
        if self.is_connected(): return 1 # spojení je již navázáno
        self._lorry = client_socket.Lorry()
        self._lorry._notes = self._notes
        self._lorry._errors = self._errors
        self._lorry.handler_message = self.process_answer
        if not data:
            section='conect'
            data = (self.__get_config__(section,'host'),
                    self.__get_config__(section,'port','int'),
                    self.__get_config__(section,'ssl_key'),
                    self.__get_config__(section,'ssl_cert'))
            if None in data:
                self.append_error('%s: %s'%(_T('Impossible create connection. Required config values missing'),str(data)))
                return 0
        if self._lorry.connect(data):
            epp_greeting = self._lorry.receive() # receive greeting
            self.__check_is_connected__()
            if epp_greeting:
                self.process_answer(epp_greeting)
                return 1
        return 0
        
    def close(self):
        "Close connection with server."
        if self._lorry:
            self._lorry.close()
            self._lorry = None
        # když se spojení zrušilo, tak o zalogování nemůže být ani řeči
        self._session[ONLINE] = 0

    def is_connected(self):
        "Check if the manager is connected."
        return self._lorry and self._lorry.is_connected()
        
    def send(self, message):
        "Send message to server."
        ret = 0
        self._raw_cmd = message
        if self._lorry:
            ret = self._lorry.send(message)
            if ret:
                # pokud se podařilo dokument odeslat, tak si manager zapamatuje
                # jakého typu příkaz byl a podle toho pak pracuje s hodnotami,
                # které mu server vrátí
                self.__command_sent__(message)
                self.append_note(_T('Command was sent to EPP server.'),('GREEN','BOLD'))
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    def send_logout(self):
        'Send EPP logout message.'
        if not self._session[ONLINE]: return # session zalogována nebyla
        self._epp_cmd.assemble_logout(self.__next_clTRID__())
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            self.append_note(_T('Send logout'))
            self.send(epp_doc)          # odeslání dokumentu na server
            answer = self.receive()     # příjem odpovědi
            self.process_answer(answer) # zpracování odpovědi
        else:
            self.append_error(self._epp_cmd.get_errors())
            
    def receive(self):
        "Receive message from server."
        ret = ''
        if self._lorry:
            ret = self._lorry.receive()
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    def process_answer(self, epp_server_answer):
        "This function MUST override derived class."
        self.append_error('Internal Error: Function process_answer() must be overriden!')
