# -*- coding: utf8 -*-
#!/usr/bin/env python
import eppdoc_client
import client_socket
from session_base import *
from translate import _T, _TP, encoding


class ManagerTransfer(ManagerBase):
    """EPP client support.
    This class take care about sending and receiving messages from/to server.
    Function process_answer() must be implemented by derived class.
    """
    def __init__(self):
        ManagerBase.__init__(self)
        self._epp_cmd = eppdoc_client.Message()
        self._epp_response = eppdoc_client.Message()
        self._available_commands = self._epp_cmd.get_client_commands()
        self._lorry = None
        # Typ očekávané odpovědi serveru. Zde si Manager pamatuje jaký příkaz
        # odeslal a podle toho pak zařadí návratové hodnoty.
        self._command_sent = '' # jméno posledního odeslaného příkazu
        self._raw_cmd = '' # XML EPP příkaz odeslaný serveru
        self._raw_answer = '' # XML EPP odpověd serveru
        self._dct_answer = {} # API response
        self.reset_src()

    def get_command_names(self):
        return self._available_commands

    def reset_src(self):
        'Reset buffers of sources.'
        self._raw_answer = '' # XML EPP odpověd serveru
        self._dict_answer = '' # dict - slovník vytvořený z XML EPP odpovědi
        self._dct_answer = {'code':0,'command':'',  'reason':'', 'errors':[], 'data':{}} # API response
        # Set output SORT BY and VEROBOSE names:
        if self._session[TRANSLATE_ANSWER_COLUMN_NAMES]:
            # Default is 1 (display column names). Zero is used for TEST (display column keys).
            cols = self._epp_cmd.get_sort_by_names(self._command_sent)
            if re.match('\w+:check',self._command_sent):
                pass # list of check names - don't touch!
            elif cols:
                self._session[SORT_BY_COLUMNS] = cols
            else:
                self._session[SORT_BY_COLUMNS] = []
                

    def reset_round(self):
        'Prepare for next round. Reset internal dict with communication values.'
        self._errors = []
        self._notes = []
        self._epp_cmd.reset()
        self._epp_response.reset()
        self._command_sent = '' # jméno posledního odeslaného příkazu
        self._session[SORT_BY_COLUMNS] = []

    def get_command_line(self):
        'Returns example of command built from parameters.'
        return self._epp_cmd.get_command_line(self._session[NULL_VALUE])

    #---------------------------------
    # funkce pro nastavení session
    #---------------------------------
    def __check_is_connected__(self):
        "Control if you are still connected."
        if self._lorry and not self._lorry.is_connected():
            # spojení spadlo
            if self._session[ONLINE]: self.append_note('--- %s ---'%_T('Connection broken'))
            self.close()

    def grab_command_name_from_xml(self, message):
        "Save EPP command type for recognize server answer."
        # manager si zapamatuje jakého typu příkaz byl a podle toho 
        # pak pracuje s hodnotami, které mu server vrátí
        # Tady se typ musí vytáhnout přímo z XML, jiná možnost není. 
        # Protože lze posílat i XML již vytvořené dříve nebo z jiného programu.
        epp_xml = eppdoc_client.Message()
        epp_xml.parse_xml(message)
        err = epp_xml.fetch_errors()
        if len(err): self._errors.append(err)
        return epp_xml.get_epp_command_name()

    #==================================================
    #
    #    Transfer functions
    #    funkce pro komunikaci se socketem
    #
    #==================================================
    def get_connect_defaults(self):
        'Get connect defaults from config'
        if not self._conf: self.load_config() # load config, if was not been yet
        section = self.config_get_section_connect()
        data = [self.get_config_value(section,'host'),
                self.get_config_value(section,'port',0,'int'),
                self.get_config_value(section,'ssl_key'),
                self.get_config_value(section,'ssl_cert'),
                self.get_config_value(section,'timeout'),
                self.get_config_value(section,'socket',1),
                ]
        # command options
        self._session[HOST] = data[0] # for prompt info
        return data

    def connect(self, data=None):
        "Connect transfer socket. data=('host',port,'client-type')"
        if self.is_connected(): return 1 # spojení je již navázáno
        self._lorry = client_socket.Lorry()
        self._lorry._notes = self._notes
        self._lorry._errors = self._errors
        self._lorry.handler_message = self.process_answer
        if not data:
            data = self.get_connect_defaults()
            if None in data[:5]:
                self.append_error('%s: %s'%(_T('Can not create connection. Missing values'),str(data)))
                return 0
        if self._lorry.connect(data, self._session[VERBOSE]):
            epp_greeting = self._lorry.receive() # receive greeting
            self.__check_is_connected__()
            if epp_greeting:
                self.process_answer(epp_greeting)
                return 1
            else:
                self.append_error(_T("Server didn't return Greeting message. Contact server administrator."))
        return 0
        
    def close(self):
        "Close connection with server."
        if self._lorry:
            self._lorry.close()
            self._lorry = None
        # když se spojení zrušilo, tak o zalogování nemůže být ani řeči
        self._session[ONLINE] = 0
        self._session[USERNAME] = '' # for prompt info
        self._session[HOST] = '' # for prompt info

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
                if self._session[VERBOSE] > 1: self.append_note(_T('Command sent to EPP server.'),'BOLD')
            self.__check_is_connected__()
        else:
            self.append_error(_T('You are not connected.'))
        return ret

    def send_logout(self, no_outoupt=None):
        'Send EPP logout message.'
        if not self._session[ONLINE]: return # session zalogována nebyla
        self.reset_round()
        self._epp_cmd.assemble_logout(self.__next_clTRID__())
        epp_doc = self._epp_cmd.get_xml()
        if epp_doc and self.is_connected():
            self.append_note(_T('Logout command sent to server'))
            self.send(epp_doc)          # odeslání dokumentu na server
            answer = self.receive()     # příjem odpovědi
            self.process_answer(answer) # zpracování odpovědi
            if not no_outoupt: self.print_answer() # 2. departure from the rule to print answers
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

    def print_answer(self, dct=None):
        "Returns str of dict object."
        if self._session[VERBOSE]:
            print self.get_answer(dct) # verbose is not 0

    def get_answer_udata(self, sep='\n'):
        'Special for GUI output. Returns unicode.'
        body=[]
        report = body.append
        dct = self._dct_answer
        if self._session[SORT_BY_COLUMNS]:
            keys = self._session[SORT_BY_COLUMNS] # sorted output (included in create command part)
        else:
            keys = map(lambda n:(n,1,''), dct['data'].keys()) # default (unsorted)
        for key,verbose,explain in keys:
            value = dct['data'].get(key,u'')
            if value not in ('',[]): __append_into_report__(body,key,value,explain,'',1) # '' - indent; 1 - no terminal tags
        return sep.join(body).decode(encoding)

            
    def get_answer(self, dct=None, sep='\n'):
        'Show values parsed from the server answer.'
        body=[]
        report = body.append
        if not dct: dct = self._dct_answer
        code = dct['code']
        if self._session[VERBOSE] < 2:
            # brief
            report(get_ltext(colored_output.render('${BOLD}%d${NORMAL}: ${%s}%s${NORMAL}'%(code,{False:'NORMAL',True:'GREEN'}[code==1000],dct['reason']))))
        else:
            # full
            report('-'*60)
            report(colored_output.render('${BOLD}code:${NORMAL} %d'%code))
            report(colored_output.render('${BOLD}command:${NORMAL} %s'%dct['command']))
            report('%s%s'%(
                colored_output.render('${BOLD}reason:${NORMAL} '),
                get_ltext(colored_output.render('${%s}%s${NORMAL}'%({False:'NORMAL',True:'GREEN'}[code==1000],dct['reason']))))
                )
            report(colored_output.render('${BOLD}errors:${NORMAL}'))
        if len(dct['errors']):
            report(colored_output.render('${BOLD}${RED}'))
            for error in dct['errors']:
                report(get_ltext('  %s'%error))
            report(colored_output.render('${NORMAL}'))
        if self._session[VERBOSE] > 1: report(colored_output.render('${BOLD}data:${NORMAL}'))
        if self._session[SORT_BY_COLUMNS]:
            keys = self._session[SORT_BY_COLUMNS] # sorted output (included in create command part)
        else:
            keys = map(lambda n:(n,1,''), dct['data'].keys()) # default (unsorted)
        in_higher_verbose = 0
        used = []
        for key,verbose,explain in keys:
            if verbose > self._session[VERBOSE]:
                in_higher_verbose += 1
                continue
            value = dct['data'].get(key,u'')
            if value not in ('',[]): __append_into_report__(body,key,value,explain)
            used.append(key)
        if in_higher_verbose:
            report(colored_output.render('   ${WHITE}(${YELLOW}${BOLD}%d${NORMAL} ${WHITE}%s)${NORMAL}'%(in_higher_verbose,_TP('not displayed value','not displayed values',in_higher_verbose))))
        #--- INTERNAL USE ----
        if self._session[SORT_BY_COLUMNS]:
            # in mode SORT_BY_COLUMNS check if all names was used
            missing = [n for n in dct['data'].keys() if n not in used]
            if len(missing):
                report(colored_output.render('\n${BOLD}${RED}%s: %s${NORMAL}'%(_T('Not used'),'(%s)'%', '.join(missing))))
        #---------------------
        report('-'*60)
        for n in range(len(body)):
            if type(body[n]) == unicode: body[n] = body[n].encode(encoding)
        if self._session[VERBOSE] == 3:
            report(colored_output.render('${BOLD}COMMAND:${NORMAL}${GREEN}'))
            report(human_readable(self._raw_cmd))
            report(colored_output.render('${NORMAL}${BOLD}ANSWER:${NORMAL}${GREEN}'))
            report(human_readable(self._raw_answer))
            report(colored_output.render('${NORMAL}'))
        return sep.join(body)

    def save_history(self):
        'Save history of command line.'
        eppdoc_client.eppdoc_assemble.save_history()

    def restore_history(self):
        'Restore history of command line.'
        eppdoc_client.eppdoc_assemble.restore_history()

    def remove_from_history(self, count=1):
        'Remove count last commands from history.'
        eppdoc_client.eppdoc_assemble.remove_from_history(count)
        
def __append_into_report__(body,k,v,explain, indent = '   ', no_terminal_tags=0):
    'Append value type(unicode|list|tuple) into report body.'
    patt = (
        ('%s${BOLD}%s${NORMAL} %s','%s${BOLD}%s${NORMAL}'),
        ('%s%s %s','%s%s')
    )[no_terminal_tags]
    if explain: k = explain # overwrite key by explain message
    if type(k) is str: k = k.decode(encoding)
    if type(v) is str: v = v.decode(encoding)
    space = 20 # indent between names and values
    key = (k+':').ljust(space)
    if type(v) in (list,tuple):
        if len(v):
            body.append(get_ltext(colored_output.render(patt[0]%(indent,key,str_lists(v[0])))))
            for text in v[1:]:
                body.append(get_ltext('%s%s'%(''.ljust(space+len(indent)+1),str_lists(text))))
        else:
            body.append(get_ltext(colored_output.render(patt[1]%(indent,key))))
    else:
        body.append(get_ltext(colored_output.render(patt[0]%(indent,key, v))))

def str_lists(text):
    """Prepare list or tuples for display. Same as str() but ommit u'...' symbols
    and put all values into brackets.
    """
    if type(text) in (list,tuple):
        body = []
        for item in text:
            body.append(str_lists(item))
        text = '(%s)'%', '.join(body)
    return text

def human_readable(body):
    'Resample to rows if they missing. This is hook while PrettyPrint missing.'
    if not re.search('</\w+>\n<',body):
        body = re.sub('(</[^>]+>)','\\1\n',body)
    return body
