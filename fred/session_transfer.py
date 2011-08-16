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
import socket, re
from cgi import escape as escape_html
import eppdoc_client
import client_socket
from session_base import *
from translate import encoding, options

try:
    # This module mustn't be included in release!
    # It is used for internal test only.
    import fred_debug
except ImportError:
    pass

"""
Class ManagerTransfer is a part of the one Manager instance what provides
about input and output. It is descentant of the ManageBase what care about
config and validation process.
On the one side is object Lorry with socket handle and function to manage it.
On the oterr side is function to build output string for display.
Next descendant is in session_command,py
"""
# Tags for scripted outputs:
d_tag = {
    'html': ('<pre class="fred_messages">','</pre>'),
    'php': ('<?php ','?>'),
}
BEGIN,END = range(2)

class ManagerTransfer(ManagerBase):
    """EPP client support.
    This class take care about sending and receiving messages from/to server.
    Function process_answer() must be implemented by derived class.
    """

    def __init__(self, cwd=None):
        self._cwd = cwd
        ManagerBase.__init__(self, cwd=self._cwd)
        self._epp_cmd = eppdoc_client.Message(self)
        self._epp_response = eppdoc_client.Message(self)
        self.defs[objURI] = self._epp_cmd.get_objURI()
        self.defs[extURI] = self._epp_cmd.get_extURI()
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        # Type of the answer. Here manager remembers what command sent
        # and along to this value sorted returned variables.
        self._command_sent = '' # the name of the last sent command
        self._raw_cmd = '' # XML EPP command sent to the server
        self._raw_answer = '' # XML EPP server answer
        self._dct_answer = {} # API response
        #... readline variables ...............
        self.readline = None
        self.readline_prefix = None
        self.readline_words = []
        self._startup_hook = '' # text what will be put in prompt
        #......................................
        self.reset_src()
        #test_init_client() # TEST ONLY

    def get_command_names(self):
        return self._available_commands

    def reset_src(self):
        'Reset buffers of sources.'
        self._raw_answer = '' # XML EPP server answer
        self._dict_answer = '' # dictionnary created from XML EPP server answer
        self._dct_answer = {'code':0,'command':'',  'reason':'', 'errors':[], 'data':{}} # API response
        # Set output SORT BY and VEROBOSE names:
        if self._session[TRANSLATE_ANSWER_COLUMN_NAMES] and not len(self._session[SORT_BY_COLUMNS]):
            # Default is 1 (display column names). Zero is used for TEST (display column keys).
            self._session[SORT_BY_COLUMNS] = self._epp_cmd.get_sort_by_names(self._command_sent)

    def reset_round(self):
        'Prepare for next round. Reset internal dict with communication values.'
        self._errors = []
        self._notes = []
        self._notes_afrer_errors = []
        self._epp_cmd.reset()
        self._epp_response.reset()
        self._command_sent = '' # name of the last command sent to the server
        self._session[SORT_BY_COLUMNS] = [] # used to sort output values

    def get_command_line(self):
        'Returns example of command built from parameters.'
        return self._epp_cmd.get_command_line(self._session[NULL_VALUE])

    #---------------------------------
    # function for set session
    #---------------------------------
    def __check_is_connected__(self):
        "Control if you are still connected."
        if self._lorry:
            if not self._lorry.is_connected():
                # broken connection
                if self._session[ONLINE] and self._session[VERBOSE] > 1:
                    self.append_error(_T('Connection to %s interrupted.')%self._session[HOST])
                self.close()
        else:
            self.close()

    def grab_command_name_from_xml(self, message):
        "Save EPP command type for recognize server answer."
        # The Manager remember the type of the command and it is used
        # for method how to interpret received variables.
        # The type of the command must be grab directly from XML because
        # it is possible to send any XML from any unknown source or application.
        epp_xml = eppdoc_client.Message(self)
        epp_xml.parse_xml(message)
        err = epp_xml.fetch_errors()
        command_name = epp_xml.get_epp_command_name()
        if len(err):
            self._errors.append(err)
        else: 
            match = re.match('(\w+):check',command_name) # domain:check
            if match:
                names = epp_xml.get_check_names(match.group(1))
                if len(names):
                    # makte struct (key, verbose, description)
                    self._session[SORT_BY_COLUMNS] = map(lambda s: (s,1,s), names)
        return command_name

    #==================================================
    #
    #    Transfer functions
    #    for communication with socket
    #
    #==================================================
    def set_data_connect(self, dc):
        """Set data needed to connection:
        dict with strings: {key: str, ....}
        Used by GUI interface.

        'host':         'epp.server.cz'
        'port':         '700'
        'ssl_key':      '/etc/cert/pkey.pem'
        'ssl_cert':     '/etc/cert/cert.pem'
        'timeout':      '10.0'
        'socket':       'IPv6'
        'username':     'username'
        'password':     'passw'
        """
        section = self.config_get_section_connect()
        for key in ('host','port','ssl_key','ssl_cert','timeout','socket'):
            if dc.has_key(key): self._conf.set(section,key,dc[key])
        if dc.has_key('username'): self._conf.set(section,'username',dc['username'])
        if dc.has_key('password'): self._conf.set(section,'password',dc['password'])
    
    def get_connect_defaults(self):
        'Get connect defaults from config'
        if not self._conf: self.load_config() # load config, if was not been yet
        section = self.config_get_section_connect()
        # OMIT_ERROR are used bycause these values can be set at the command line,
        # so we will not display error messages when any value missing.
        data = [self.get_config_value(section,'host',OMIT_ERROR),
                self.get_config_value(section,'port',OMIT_ERROR),
                self.get_config_value(section,'ssl_key',OMIT_ERROR),
                self.get_config_value(section,'ssl_cert',OMIT_ERROR),
                self.get_config_value(section,'timeout',OMIT_ERROR),
                self.get_config_value(section,'socket',OMIT_ERROR),
                self.get_config_value(self._section_epp_login, 'username',OMIT_ERROR),
                self.get_config_value(self._section_epp_login, 'password',OMIT_ERROR),
                ]
        # overwrite username+password by command line
        if self._epp_cmd._dct.has_key('username'): data[6] = self._epp_cmd._dct['username'][0]
        if self._epp_cmd._dct.has_key('password'): data[7] = self._epp_cmd._dct['password'][0]

        # add prefix if ssl_key or/and ssl_cert paths are relative
        ssl_key, ssl_cert = data[2], data[3]
        if ssl_key and not os.path.isabs(ssl_key) and self.get_cwd():
            data[2] = os.path.normpath(os.path.join(self.get_cwd(), ssl_key))
        if ssl_cert and not os.path.isabs(ssl_cert) and self.get_cwd():
            data[3] = os.path.normpath(os.path.join(self.get_cwd(), ssl_cert))

        # command options
        self._session[HOST] = data[0] # for prompt info
        return data

    def check_port(self, sport):
        "Check if value can be used as server port. '' - yes (no errors), '...' - no (any error occured)"
        error = ''
        try:
            port = int(sport)
        except ValueError, msg:
            error = _T("Invalid port value: '%s'.")%sport
        else:
            if not (port > 0 and port <= 65535):
                error = _T('Port is out of range: %d.')%port
        return error
        
    def check_connect_data(self, data, omit_username=0):
        'Check data for connnect. 1 - valid, 0 - invalid'
        # Check if all values are present:
        missing = []
        if not data[0]: missing.append(_T('Hostname missing'))
        if not data[1]:
            missing.append(_T('Server port number missing'))
        else:
            error = self.check_port(data[1])
            if error: missing.append(error)
        if not omit_username:
            if not data[6]: missing.append(_T('Username missing'))
            if not data[7]: missing.append(_T('Password missing'))
        if not data[3]:
            missing.append(_T('SSL certificate name missing'))
        else:
            if not os.path.isfile(data[3]): missing.append(_T('SSL certificate file not found'))
        if not data[2]:
            missing.append(_T('SSL private key name missing'))
        else:
            if not os.path.isfile(data[2]): missing.append(_T('SSL private key file not found'))
        if len(missing):
            self.append_error(_T("Can't connect to server"))
            map(self.append_error, missing)
            return 0
        return 1
        
    def connect(self):
        "Connect transfer socket. data=(host,port,ssl_key,ssl_cert,timeout,socket,username,password)"
        if self.is_connected():
            return 1 # connection is established already
        self._lorry = client_socket.Lorry(self)
        self._lorry.handler_message = self.process_answer
        data = self.get_connect_defaults()
        if not self.check_connect_data(data, 1): 
            return 0 # 1 - omit username + password

        success = self._lorry.connect(data, self._session[VERBOSE])
        if not success and self._lorry.try_again_with_timeout_zero:
            # Try again with timeout zero. Possible python2.4 + Windows SSL timeout bug
            self.display()
            data[4] = '0.0'
            self._notes.append(_T('Now I try again to connect with the zero timeout...'))
            success = self._lorry.connect(data, self._session[VERBOSE])
            if success:
                self._notes.append(_T('Attempt at connection with the zero timeout has been successful.'))
                self._notes.append(_T('Change timeout value to the zero in your configuration file.'))
            else:
                self._errors.append(_T('Attempt at connection again with the zero timeout, but this process failed.'))
        
        if success:
            epp_greeting = self._lorry.receive() # receive greeting
            self.__check_is_connected__()
            if epp_greeting:
                self.process_answer(epp_greeting)
                if self._session[VERBOSE] > 1:
                    # display server fingerprint (svID)
                    data = self._dct_answer.get('data',{})
                    for key,verbose,label in self._epp_cmd.get_sort_by_names('hello'):
                        if verbose > 1: continue # display only items in 1 verbose mode
                        value = data.get(key,u'')
                        if value not in ('',[]):
                            __append_into_report__(self._notes,key,value,label,self._ljust,'')
                return 1
            else:
                self.append_error(_T("Server didn't return Greeting message. Contact server administrator."))
        return 0

    def close(self):
        "Close connection with server."
        if self._lorry:
            self._lorry.close()
            self._lorry = None
        # Messages will be dispalyed after data from server.
        if self._session[ONLINE] == 1:
            self._notes_afrer_errors.append('%s %s'%(_T('Ending session at'),self._session[HOST]))
            self._notes_afrer_errors.append(_T('Disconnected.'))
        # if the connection has been broken we are not online already
        self._session[ONLINE] = 0
        self._session[USERNAME] = '' # for prompt info
        self._session[HOST] = '' # for prompt info
        # remove notes 'Ending session at ...' and 'Disconnected.'
        self.remove_notes_from_no_text_ouptut()

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
                # If XML doc has been sent, manager saves the name of this command.
                # This is essensial for resolve how type the server answer is.
                self._command_sent = self.grab_command_name_from_xml(message)
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    def send_logout(self, no_outoupt=None):
        'Send EPP logout command.'
        if not self._session[ONLINE]: return # session has not been login
        self.reset_round()
        self._epp_cmd.assemble_logout(self.__next_clTRID__())
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            self.append_note(_T('Logout command sent to server'))
            self.send(epp_doc)          # send document to the server
            answer = self.receive()     # receiving answer
            self.process_answer(answer) # process answer
            if not no_outoupt:
                self.display() # display errors or notes
                self.print_answer() # 2. departure from the rule to print answers
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

    #==================================================
    #
    #    PARSE RESPONSE
    #    functions for parse and display response
    #
    #==================================================
        
    def process_answer(self, epp_server_answer):
        "This function MUST override derived class."
        self.append_error('Internal Error: Function process_answer() must be overriden!')

    def print_answer(self, dct=None):
        "Returns str of dict object."
        if not dct: dct = self._dct_answer
        if dct.get('command'):
            # Here is exception from the verbose rule:
            # In verbose 0: Displays only raw XML server answer.
            # Print in only any command was sent.
            fnc = getattr(self,'get_answer_%s'%self._session[OUTPUT_TYPE], self.get_answer)
            print fnc(dct)
        
        
    def get_keys_sort_by_columns(self):
        'Returns list of keys what will be used to sorting output values.'
        return self.__get_column_items__(self._dct_answer['command'], self._dct_answer['data'])

    def __get_column_items__(self, command_name, dct_data):
        'Returns struct of key names for sorting output values lines.'
        if self._session[SORT_BY_COLUMNS]:
            sorted_columns = self._session[SORT_BY_COLUMNS] # sorted output (included in create command part)
        else:
            sorted_columns = map(lambda n:(n,1,''), dct_data.keys()) # default (unsorted)
        return sorted_columns
                
    def get_answer_udata(self, sep='\n'):
        'Special for GUI output. Returns unicode.'
        body=[]
        report = body.append
        dct_data = self._dct_answer['data']
        self.reduce_info_status(self._dct_answer['command'], dct_data) # join status key and description together
        for key,verbose,explain in self.__get_column_items__(self._dct_answer['command'], dct_data):
            value = dct_data.get(key,u'')
            if value not in ('',[]): __append_into_report__(body,key,value,explain,self._ljust,'',1) # '' - indent; 1 - no terminal tags
        return sep.join(body).decode(encoding)

    def reduce_info_status(self, command, dct_data):
        """Join status key and description together.
        For example:
            'contact:status.s': [u'ok', u'linked'], 
            'contact:status': [u'Contact is OK', u'Contact is admin or tech']
        command has value like 'contact:info'
        so we reduce elements 'contact:status.s' and 'contact:status'
        """
        match = re.match('(contact|nsset|domain):info', command)
        if match:
            # only for info commands
            key1 = '%s:status.s'%match.group(1)
            key2 = '%s:status'%match.group(1)
            if dct_data.has_key(key1) and dct_data.has_key(key2):
                if type(dct_data[key1]) in (list,tuple):
                    dct_data[key1] = map(lambda p:'%s - %s'%p, zip(dct_data[key1], dct_data[key2]))
                else:
                    dct_data[key1] = '%s - %s'%(dct_data[key1], dct_data[key2])
                dct_data.pop(key2)

    def __append_to_body__(self, body, dct):
        'Internal support for get_answer()'
        data_indent = ''
        data = []
        in_higher_verbose = 0
        used = []
        dct_data = dct['data']
        is_check = re.match('\w+:check',dct['command']) and 1 or 0 # object:check
        is_list = dct['command'] == 'fred:getresults' or self._loop_status == LOOP_INSIDE
        column_verbose = {} # dict of keys and their verbose level
        self.reduce_info_status(dct['command'], dct_data)

        for key,verbose,explain in self.__get_column_items__(dct['command'], dct_data):
            key = key.strip() # client normaly trim whitespaces, but if you use sender, you can send everything...
            if verbose > self._session[VERBOSE]:
                in_higher_verbose += 1
                used.append(key)
                continue
            value = dct_data.get(key,u'')
            if value is None:
                value = u''
            
            if type(value) not in (list, tuple):
                # split text into lines
                if type(value) is int:
                    value = str(value)
                else:
                    lines = re.split('[\r\n]+', value)
                    if len(lines) > 1:
                        value = lines
                    
            if value not in ('',[]):
                if is_check:
                    # Check response returns code and reason. Code is used to insert status into message.
                    # join is done in function __answer_response_check__() in module session_receiver.py
                    # pref:key 0
                    # pref:key:reason 'message'
                    value = dct_data.get(key+':reason',u'')
                __append_into_report__(data, key, value, explain, 
                        self._ljust, data_indent, 0,  # 2 - use HTML pattern;
                        is_list)
                
            used.append(key)
        if len(data):
            if len(body) and body[-1] != '': body.append('') # empty line
            body.extend(data)
        if globals().has_key('fred_debug') :
            # ONLY FOR INTERNAL USE
            fred_debug.check_missing_names(body, self._session[SORT_BY_COLUMNS],  self._session[VERBOSE], is_check, dct_data, used, column_verbose)

    def __modify__reason_message__(self, code, key, dct):
        """Modify reason message from standard answer to more fit message.
        READ HERE! These keys must be declared in function get_answer() a few lines above
        on the line 433: elif code not in (1000,1500) or key in (... HERE...).
        If they not, in the verbose level 1 is displayed nothing.
        """
        if code == 1000:
            if key == 'update':
                dct['reason'] = u'%s %s.'%(self._epp_cmd.get_object_handle(), _T('updated').decode(encoding))
            elif key == 'delete':
                dct['reason'] = u'%s %s.'%(self._epp_cmd.get_object_handle(), _T('deleted').decode(encoding))
            elif key == 'transfer':
                dct['reason'] = u'%s %s.'%(self._epp_cmd.get_object_handle(), _T('successfully transfered').decode(encoding))
            elif key == 'sendauthinfo':
                dct['reason'] = u'%s %s.'%(self._epp_cmd.get_object_handle(), _T('request for send authorisation info transmited').decode(encoding))
            elif key == 'technical_test':
                dct['reason'] = _T('The Request for technical test was successfully submitted.').decode(encoding)
            elif key == 'poll':
                dct['reason'] = _T('The message has been removed from the queue.').decode(encoding)
        
    def get_answer(self, dct=None, sep='\n'):
        'Show values parsed from the server answer.'
        body=[]
        report = body.append
        if not dct: dct = self._dct_answer
        if self._session[VERBOSE] > 0:
            #... code and reason .............................
            code = dct['code']
            match = re.match('\w+:(\w+)',dct['command'])
            if match:
                key = match.group(1)
            else:
                key = dct['command']
            self.__modify__reason_message__(code, key, dct)
            if self._session[VERBOSE] < 2:
                # brief output mode
                # exception on the command login and hello:
                if dct['command'] in ('login','hello'):
                    pass # omit reason block body.pop() # remove previous empty line
                else:
                    if code >= 2000:
                        dct['errors'].insert(0,dct['reason'])
                    elif code not in (1000,1500) or key in ('update','delete','transfer','sendauthinfo','technical_test', 'poll'):
                        # 1000 - success,  1500 - success logout
                        report(get_ltext(colored_output.render('${%s}%s${NORMAL}'%(code==1000 and 'GREEN' or 'NORMAL', dct['reason']))))
            else:
                # full
                if code:
                    label_code = (u'%s:'%get_unicode(_T('Return code'))).ljust(self._ljust+1) # +1 space between key and value
                    report(colored_output.render('${BOLD}%s${NORMAL}%d'%(get_ltext(label_code),code)))
                if dct.get('reason'):
                    label_reason = (u'%s:'%get_unicode(_T('Reason'))).ljust(self._ljust+1)
                    report(colored_output.render('${BOLD}%s${%s}%s${NORMAL}'%(get_ltext(label_reason), code==1000 and 'GREEN' or 'NORMAL', get_ltext(dct['reason']))))
            #... errors .............................
            if len(dct['errors']):
                if len(body) and body[-1] != '': report('') # empty line
                dct['errors'][-1] += colored_output.render('${NORMAL}')
                report(get_ltext('%s%s: %s'%(colored_output.render('${BOLD}${RED}'),_T('ERROR'),dct['errors'][0])))
                for error in dct['errors'][1:]:
                    report(get_ltext(error))
            #... data .............................
            self.__append_to_body__(body, dct)
            
        else:
            # Zero verbose level
            report(human_readable(self._raw_answer))
        #... third verbose level .............................
        for n in range(len(body)):
            if type(body[n]) == unicode: body[n] = body[n].encode(encoding)
        if self._session[VERBOSE] == 3 and self._loop_status == LOOP_NONE:
            if len(body) and body[-1] != '': report('') # empty line
            report(colored_output.render('${BOLD}COMMAND:${NORMAL}${GREEN} %s'%get_ltext(self._command_sent)))
            report(human_readable(self._raw_cmd))
            report(colored_output.render('${NORMAL}${BOLD}ANSWER:${NORMAL}${GREEN}'))
            report(human_readable(self._raw_answer))
            report(colored_output.render('${NORMAL}'))
        return sep.join(body)

    def get_answer_html(self, dct=None):
        """Returns data in HTML format. Used syles:
        CSS:
        .fred_client       - main div of HTML output
        .fred_code         - div part of message (code + reason)
        .fred_errors       - ul li with errors
        .fred_data         - table with data
        .fred_source       - pre with XML sources
        .command_success    - reason with code 1000
        .command_done       - other readons
        .even               - every even row in data table
        """
        body=[]
        report = body.append
        if not dct: dct = self._dct_answer
        #... code and reason .............................
        code = dct['code']
        reason_css_class = code==1000 and 'command_success' or 'command_done'
        if self._session[VERBOSE] > 0:
            if code != 1000:
                # full
                tbl_reason=['<table class="fred_data">']
                tbl_reason.append('<tr>\n\t<th>%s</th>\n\t<td>%d</td>\n</tr>'%(_T('Return code'),code))
                #tbl_reason.append('<tr>\n\t<th>command</th>\n\t<td>%s</td>\n</tr>'%get_ltext(dct['command']))
                tbl_reason.append('<tr>\n\t<th>%s</th>\n\t<td><span class="%s">%s</span></td>\n</tr>'%(_T('Reason'), reason_css_class,get_ltext(dct['reason'])))
                tbl_reason.append('</table>')
                report('\n'.join(tbl_reason))
            #... errors .............................
            if len(dct['errors']):
                report('<div class="fred_errors">\n<strong>errors:</strong><ul>')
                for error in dct['errors']:
                    report('<li>%s</li>'%get_ltext(error))
                report('</ul></div>')
            #... data .............................
            is_check = re.match('\w+:check',dct['command']) and 1 or 0 # object:check
            data_indent = ''
            data = []
            dct_data = dct['data']
            self.reduce_info_status(dct['command'], dct_data) # join status key and description together
            is_list = dct['command'] == 'fred:getresults' or self._loop_status == LOOP_INSIDE
            for key,verbose,explain in self.__get_column_items__(dct['command'], dct_data):
                if verbose > self._session[VERBOSE]: continue
                key = key.strip() # client normaly trim whitespaces, but if you use sender, you can send everything...
                value = dct_data.get(key,u'')
                if value not in ('',[]):
                    if is_check:
                        # Tighten check response by code.
                        value = dct_data.get(key+':reason',u'')
                    __append_into_report__(data, key, value, explain, 
                            self._ljust, '', 2,  # 2 - use HTML pattern;
                            is_list)
            
            if len(data):
                if self._loop_status == LOOP_NONE or self._loop_status == LOOP_FIRST_STEP:
                    report('<table class="fred_data">')
                body.extend(data)
                if self._loop_status == LOOP_NONE or self._loop_status == LOOP_LAST_STEP:
                    report('</table>')
            elif self._loop_status == LOOP_LAST_STEP:
                report('</table>')
                    
            # encode to 8bit local
            for n in range(len(body)):
                if type(body[n]) == unicode: body[n] = body[n].encode(encoding)
        else:
            # Zero verbose level
            report(escape_html(human_readable(self._raw_answer)))
        #... third verbose level .............................
        if self._session[VERBOSE] == 3 and self._loop_status == LOOP_NONE:
            report('<pre class="fred_source">')
            report('<strong>COMMAND:</strong>')
            report(escape_html(human_readable(self._raw_cmd)))
            report('<strong>ANSWER:</strong>')
            report(escape_html(human_readable(self._raw_answer)))
            report('</pre>')
        # ..............
        return '\n'.join(body)

    def get_empty_php_code(self):
        'Returns empty PHP code when create command fails.'
        return """
$fred_encoding = %s;           // used encoding
$fred_command = '';            // command sent to the server
$fred_code = 0;                // code returned from server
$fred_reason = '';             // reason returned from server (description of the code)
$fred_reason_errors = array(); // errors described details that caused invalid code
$fred_labels = array();        // descriptions of the data columns
$fred_data = array();          // data returned by server
$fred_source_command = '';     // source code (XML) of the command prepared to display
$fred_source_answer = '';      // source code (XML) of the answer prepared to display
"""%php_string(encoding)

    def get_formated_message(self, message, type):
        'Returns formated outout for text/php/html type: 0 - note, 1 - ERROR'
        if self._session[OUTPUT_TYPE] == 'php':
            msg = '$fred_client_%s[] = %s;'%(type == 1 and 'errors' or 'notes', php_string(message))
        elif self._session[OUTPUT_TYPE] == 'html':
            msg = '<div class="fred_%s">%s<div>'%(type == 1 and 'errors' or 'notes', message)
        elif self._session[OUTPUT_TYPE] == 'xml':
            tags = type == 1 and ('errors','error') or ('notes', 'note')
            msg = '<?xml version="1.0" encoding="%s"?>\n<%s>\n\t<%s>%s</%s>\n</%s>'%(encoding, tags[0], tags[1], message, tags[1], tags[0])
        else: # text
            msg = message
        return msg

    def get_answer_xml(self, dct=None):
        'Returns raw XML'
        if self._loop_status == LOOP_NONE:
            return self._raw_answer
        else:
            # exception for loop list functions
            tag_name = 'fred:resultsList'
            
            if self._loop_status == LOOP_FIRST_STEP:
                info_response = 'fred:infoResponse'
                patt = '</%s>'%info_response
                begin, self._xml_loop_end = self._raw_answer.split(patt)
                result_list = '\n<%s%s>'%(tag_name, re.search('<%s([^>]*)>'%info_response, begin).group(1))
                body = '%s%s%s'%(begin, patt, result_list)
            elif self._loop_status == LOOP_LAST_STEP:
                body = '%s\n%s'%('</%s>'%tag_name, self._xml_loop_end)
            else:
                body = '\n'.join(re.findall('<fred:item>.+</fred:item>',self._raw_answer))
        return body
        
        
    def get_answer_php(self, dct=None):
        """Returns data as a PHP code:
        $fred_encoding      string
        $fred_code           int
        $fred_command        string
        $fred_reason         string
        $fred_labels         array
        $fred_data           array
        $fred_reason_errors  array
        $fred_source_command string (third level)
        $fred_source_answer  string (third level)
        """
        if not dct: dct = self._dct_answer
        body=[]
        report = body.append
        if self._session[VERBOSE] > 0:
            if self._loop_status == LOOP_NONE or self._loop_status == LOOP_FIRST_STEP:
                report("$fred_encoding = %s; // used encoding"%php_string(encoding))
                #... code and reason .............................
                code = dct['code']
                report("$fred_command = %s; // command sent to the server"%php_string(dct['command']))
                report('$fred_code = %d; // code returned from server'%code)
                report("$fred_reason = %s; // reason returned from server (description of the code)"%php_string(dct['reason']))
                #... errors .............................
                errors = []
                for error in dct['errors']:
                    errors.append(php_string(error))
                report('$fred_reason_errors = array(%s); // errors described details that caused invalid code'%', '.join(errors))
                #... data .............................
                report('$fred_labels = array(); // descriptions of the data columns')
                report('$fred_data = array(); // data returned by server')
                report('$fred_data_attrib = array(); // data attributes returned by server')
            dct_data = dct['data']
            is_check = re.match('\w+:check',dct['command']) and 1 or 0 # object:check
            
            # some veriables must be always array type
            for key in ('domain:status', 'domain:status.s'):
                if not dct_data.has_key(key):
                    continue
                if type(dct_data[key]) is unicode:
                    dct_data[key] = [dct_data[key]] # make array from string
            
            for key,verbose,explain in self.__get_column_items__(dct['command'], dct_data):
                if verbose > self._session[VERBOSE]: continue
                key = key.strip() # client normaly trim whitespaces, but if you use sender, you can send everything...
                if not explain: explain = key
                value = dct_data.get(key,u'')
                if value not in ('',[]):
                    if is_check:
                        # Check response returns code and reason. Code is used to insert status into message.
                        # join is done in function __answer_response_check__() in module session_receiver.py
                        # pref:key 0
                        # pref:key:reason 'message'
                        value = dct_data.get(key)
                        if value is not None:
                            report("$fred_data_attrib[%s]['avail'] = %s;"%(php_string(key),php_string(value)))
                        value = dct_data.get(key+':reason',u'')
                    if type(value) in (list,tuple):
                        if self._loop_status == LOOP_NONE or self._loop_status == LOOP_FIRST_STEP:
                            report('$fred_labels[%s] = %s;'%(php_string(key),php_string(explain)))
                            report('$fred_data[%s] = array();'%php_string(key))
                        php_key = php_string(key)
                        for v in value:
                            report('$fred_data[%s][] = %s;'%(php_key,php_string(v)))
                    else:
                        report('$fred_labels[%s] = %s;'%(php_string(key),php_string(explain)))
                        report('$fred_data[%s] = %s;'%(php_string(key),php_string(value)))
        else:
            # Zero verbose level:
            report('$fred_source_answer = %s;'%php_string(human_readable(self._raw_answer)))
        #... third verbose level .............................
        if self._loop_status == LOOP_NONE:
            if self._session[VERBOSE] == 3:
                report('$fred_source_command = %s;'%php_string(human_readable(self._raw_cmd)))
                report('$fred_source_answer = %s;'%php_string(human_readable(self._raw_answer)))
            else:
                report("$fred_source_command = '';")
                report("$fred_source_answer = '';")
        # ..............
        return  '\n'.join(body)

    def print_tag(self, pos):
        'Prints tag for HTML or PHP mode at the position (0-beginig,1-end)'
        tag = d_tag.get(self._session[OUTPUT_TYPE],('',''))[pos]
        if tag: print tag
        if self._session[OUTPUT_TYPE]=='php' and pos==0:
            # init variables for notes and errros
            print self.get_init_php()
        
    def save_history(self, readline):
        'Save history of command line.'
        if self._is_history:
            eppdoc_client.eppdoc_assemble.save_history(readline)

    def restore_history(self, readline):
        'Restore history of command line.'
        if self._is_history:
            eppdoc_client.eppdoc_assemble.restore_history(readline)

    def remove_from_history(self, readline, count=1):
        'Remove count last commands from history.'
        if self._is_history:
            eppdoc_client.eppdoc_assemble.remove_from_history(readline, count)

    #-------------------------------------
    # readline part
    #-------------------------------------
    def init_readline(self, readline):
        'Init modul readline'
        if readline:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            readline.set_startup_hook(self.readline_startup_hook)
            self.readline = readline
            self._epp_cmd.readline = readline
            self._epp_response.readline = readline

    def __get_readline_words__(self, buffer):
        'Find set of words to choose in the prompt help'
        #writelog("BUFFER=%s"%buffer)
        m = re.match('\w+',buffer)
        if m:
            command_name = m.group(0)
        else:
            command_name = None
        if command_name is not None and command_name in self._available_commands:
            #writelog("\tCOMMAND IS %s"%command_name)
            dct, errors = self._epp_cmd.readline_parse_prompt(command_name, buffer)
            #writelog("DICT %s\nERRORS: %s"%(dct,errors))
            words = self._epp_cmd.readline_find_words(command_name, dct, writelog is None and (lambda s: s) or writelog)
        else:
            words = self._available_commands # default offer
        writelog('\tOFFER WORDS = %s'%str(words))
        return words

    def complete_with_params(self, prefix, index):
        'Function for readline.complete manages reaction on the TAB key press.'
        if index == 0:
            self.readline_words = [w for w in self.__get_readline_words__(self.readline.get_line_buffer()) if w.startswith(prefix)]
            #try: # FOR TEST ONLY
            #    self.readline_words = []
            #    words = self.__get_readline_words__(self.readline.get_line_buffer())
            #    self.readline_words = [w for w in words if w.startswith(prefix)]
            #except Exception, msg:
            #    writelog('*** EXCEPTION ***: %s'%str(msg))
        try:
            word = self.readline_words[index]+' '
        except IndexError:
            word = None
        #writelog("complete(%s, %d) WORD='%s';"%(prefix,index,word))
        #writelog('word = %s'%str(self.readline_words))
        return word

    def complete(self, prefix, index):
        'Function for readline.complete manages reaction on the TAB key press.'
        if prefix != self.readline_prefix:
            self.readline_prefix = prefix
            buffer = self.readline.get_line_buffer().strip()
            match = re.match('\w+',buffer)
            command = match and match.group() or buffer # remove command parameters
            if re.match('\?|h(elp)?$',command):
                # exception for command help whitch after display list command
                match = re.match('(\?\s*|\w+\s+)(\w+)',buffer)
                command = match and match.group(2) or ''
            if command in self.readline_words:
                if prefix == command:
                    self.matching_words = [command] # space at the end missing
                else:
                    self.matching_words = [] # command is already typed
            else:
                # find all words that start with this prefix
                self.matching_words = [w for w in self.readline_words if w.startswith(prefix)]
        try:
            word = self.matching_words[index]+' '
        except IndexError:
            word = None
        #writelog("complete(%s, %d) WORD='%s'"%(prefix,index,word))
        return word

    def readline_startup_hook(self):
        """It is called with no arguments just before readline prints the first prompt.
        This function is used for display result from command fetch_from_info.
        """
        if len(self._startup_hook):
            self.readline.insert_text(self._startup_hook)
            self._startup_hook = ''
    #-------------------------------------

        
def __append_into_report__(body, k, v, explain, ljust, indent = '', no_terminal_tags=0, is_list_type=0):
    'Append value type(unicode|list|tuple) into report body.'
    if is_list_type:
        indent = k = explain = ''
    patt = (
        ['%s${BOLD}%s${NORMAL} %s','%s${BOLD}%s${NORMAL}','%s%s'],
        ['%s%s %s','%s%s','%s%s'],
        ['%s<tr>\n\t<th>%s</th>\n\t<td>%s</td>\n</tr>',
         '%s<tr>\n\t<th>%s</th>\n\t<td>&nbsp;</td>\n</tr>',
         '%s<tr>\n\t<th>&nbsp;</th>\n\t<td>%s</td>\n</tr>'],
    )[no_terminal_tags]
    escape = no_terminal_tags == 2 and escape_html or (lambda s: s)
    if explain: k = explain # overwrite key by explain message
    if type(k) is str: k = k.decode(encoding)
    if type(v) is str: v = v.decode(encoding)
    if no_terminal_tags == 2:
        # html
        key = escape(k)
        ljustify = ''
    else:
        # text
        key = (escape(k)+':').ljust(ljust)
        ljustify = ''.ljust(ljust+len(indent)+1)
    if is_list_type:
        key = ljustify = ''
        patt[0] = patt[0].replace(' ', '')
    
    key = get_ltext(key)
    if type(v) in (list,tuple):

        if no_terminal_tags == 2:
            # html only
            value = escape(get_ltext(str_lists(v)))
            body.append(get_ltext(colored_output.render(patt[0]%(indent, key, value))))
        else:
            # other output (text, php)
            if len(v):
                # more lines: first is prefixed by column name
                body.append(colored_output.render(patt[0]%(indent, key, escape(get_ltext(str_lists(v[0]))))))
                # others are indented only
                for text in v[1:]:
                    body.append(patt[2]%(ljustify, escape(get_ltext(str_lists(text)))))
            else:
                # one line only
                body.append(colored_output.render(patt[1]%(indent, key)))
    else:
        # value is not array
        body.append(colored_output.render(patt[0]%(indent, key, escape(get_ltext(v)))))

def str_lists(text):
    """Prepare list or tuples for display. Same as str() but omit u'...' symbols
    and put all values into brackets.
    """
    tmp = text
    if type(text) in (list,tuple):
        body = []
        for item in text:
            if item == '': continue
            str_item = str_lists(item)
            if str_item:
                if type(item) in (list,tuple):
                    str_item = '(%s)'%str_item
                body.append(str_item)
        if len(body):
            if len(body) > 1:
                text = ', '.join(body)
            else:
                text = body[0]
        else:
            text = ''
    return text

def human_readable(body):
    'Resample to rows if they missing. This is hook while PrettyPrint missing.'
    if not re.search('</\w+>\n<',body):
        body = re.sub('(</[^>]+>)','\\1\n',body)
    return body

#--------------------
# For test only
#--------------------
def writelog(msg):
    'for test only, debug readline'
    if debug_sock: debug_sock.send('%s\n'%msg)
def test_init_client():
    'for test only, debug readline'
    global debug_sock
    debug_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        debug_sock.connect((DEBUG_HOST, DEBUG_PORT))
    except socket.error, msg:
        debug_sock = None
def run_test_server():
    'for test only, debug readline'
    print "RUN TEST SERVER (for debug readline) AT PORT",DEBUG_PORT
    DEBUG_HOST = '' # Symbolic name meaning the local host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((DEBUG_HOST, DEBUG_PORT))
    s.listen(1)
    conn=None
    try:
        conn, addr = s.accept()
        print 'Connected by', addr
        while 1:
            data = conn.recv(1024)
            if not data: break
            print data
    except (KeyboardInterrupt, EOFError):
        pass
    if conn: conn.close()


DEBUG_HOST = 'localhost'
DEBUG_PORT = 50007
debug_sock = None
#--------------------
# TEST ONLY (enable this and test_init_client())
#--------------------
#if __name__ == '__main__':
#    if len(sys.argv) > 1 and sys.argv[1]=='server':
#        run_test_server()
