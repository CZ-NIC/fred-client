# -*- coding: utf8 -*-
#!/usr/bin/env python
from cgi import escape as escape_html
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
            self._session[SORT_BY_COLUMNS] = self._epp_cmd.get_sort_by_names(self._command_sent)

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
            if self._session[ONLINE]:
                self.append_note(_T('ERROR: Connection to %s interrupted.')%self._session[HOST])
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
        data = [self.get_config_value(section,'host',OMMIT_ERROR),
                self.get_config_value(section,'port',OMMIT_ERROR,'int'),
                self.get_config_value(section,'ssl_key',OMMIT_ERROR),
                self.get_config_value(section,'ssl_cert',OMMIT_ERROR),
                self.get_config_value(section,'timeout',OMMIT_ERROR),
                self.get_config_value(section,'socket',OMMIT_ERROR),
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

    def process_answer(self, epp_server_answer):
        "This function MUST override derived class."
        self.append_error('Internal Error: Function process_answer() must be overriden!')

    def print_answer(self, dct=None):
        "Returns str of dict object."
        if not dct: dct = self._dct_answer
        if self._session[VERBOSE] and dct.get('command'):
            # Print in only any command was sent.
            if self._session[OUTPUT_TYPE] == 'html':
                print self.get_answer_html(dct) # verbose is not 0
            else:
                print self.get_answer(dct) # verbose is not 0

    def get_keys_sort_by_columns(self):
        'Returns list of keys what will be used to sorting output values.'
        return self.__get_column_items__(self._dct_answer['command'], self._dct_answer['data'])
        
    def __get_column_items__(self, command_name, dct_data):
        'Returns struct of key names for sorting output values lines.'
        if self._session[SORT_BY_COLUMNS]:
            sorted_columns = self._session[SORT_BY_COLUMNS] # sorted output (included in create command part)
        elif re.match('\w+:check',command_name):
            # exeption for all check commands
            keys = dct_data.keys()
            keys.sort()
            sorted_columns = map(lambda n:(n,1,''), keys) # sorted by keys
        else:
            sorted_columns = map(lambda n:(n,1,''), dct_data.keys()) # default (unsorted)
        return sorted_columns
                
    def get_answer_udata(self, sep='\n'):
        'Special for GUI output. Returns unicode.'
        body=[]
        report = body.append
        dct_data = self._dct_answer['data']
        for key,verbose,explain in self.__get_column_items__(self._dct_answer['command'], dct_data):
            value = dct_data.get(key,u'')
            if value not in ('',[]): __append_into_report__(body,key,value,explain,'',1) # '' - indent; 1 - no terminal tags
        return sep.join(body).decode(encoding)

    def get_answer(self, dct=None, sep='\n'):
        'Show values parsed from the server answer.'
        body=[]
        report = body.append
        if not dct: dct = self._dct_answer
        report('')
        #... code and reason .............................
        code = dct['code']
        if self._session[VERBOSE] < 2:
            # brief output mode
            # exception on the command login and hello:
            if dct['command'] in ('login','hello'):
                body.pop() # remove previous empty line
            else:
                report(get_ltext(colored_output.render('${%s}%s${NORMAL}'%({False:'NORMAL',True:'GREEN'}[code==1000],dct['reason']))))
        else:
            # full
            report(colored_output.render('${BOLD}code:${NORMAL} %d'%code))
            report(colored_output.render('${BOLD}command:${NORMAL} %s'%dct['command']))
            report('%s%s'%(
                colored_output.render('${BOLD}reason:${NORMAL} '),
                get_ltext(colored_output.render('${%s}%s${NORMAL}'%({False:'NORMAL',True:'GREEN'}[code==1000],dct['reason']))))
                )
        #... errors .............................
        if len(dct['errors']):
            report(colored_output.render('${BOLD}errors:${NORMAL}'))
            report(colored_output.render('${BOLD}${RED}'))
            for error in dct['errors']:
                report(get_ltext('  %s'%error))
            report(colored_output.render('${NORMAL}'))
        #... data .............................
        data_indent = ''
        data = []
        in_higher_verbose = 0
        used = []
        dct_data = dct['data']
        for key,verbose,explain in self.__get_column_items__(dct['command'], dct_data):
            if verbose > self._session[VERBOSE]:
                in_higher_verbose += 1
                used.append(key)
                continue
            value = dct_data.get(key,u'')
            if value not in ('',[]): __append_into_report__(data,key,value,explain,data_indent)
            used.append(key)
        if len(data):
            body.append('')
            if self._session[VERBOSE] > 1:
                body.append(colored_output.render('${BOLD}data:${NORMAL}'))
            body.extend(data)
        #if in_higher_verbose:
        #    report(colored_output.render('   ${WHITE}(${YELLOW}${BOLD}%d${NORMAL} ${WHITE}%s)${NORMAL}'%(in_higher_verbose,_TP('not displayed value','not displayed values',in_higher_verbose))))
        #--- INTERNAL USE ----
        # POZOR!!! V ostré verzi musí být deaktivováno!!!
        if self._session[SORT_BY_COLUMNS]:
            # in mode SORT_BY_COLUMNS check if all names was used
            missing = [k for k in dct_data.keys() if k not in used and dct_data[k][0] >= self._session[VERBOSE]]
            if len(missing):
                report(colored_output.render('\n${BOLD}${RED}Here needs FIX code: %s${NORMAL}'%'(%s)'%', '.join(missing)))
        #---------------------
        #... third verbose level .............................
        report('') # empty row
        for n in range(len(body)):
            if type(body[n]) == unicode: body[n] = body[n].encode(encoding)
        if self._session[VERBOSE] == 3:
            report(colored_output.render('${BOLD}COMMAND:${NORMAL}${GREEN}'))
            report(human_readable(self._raw_cmd))
            report(colored_output.render('${NORMAL}${BOLD}ANSWER:${NORMAL}${GREEN}'))
            report(human_readable(self._raw_answer))
            report(colored_output.render('${NORMAL}'))
            report('')
        return sep.join(body)

    def get_answer_html(self, dct=None):
        """Returns data in HTML format. Used syles:
        .ccreg_client       - main div of HTML output
        .ccreg_code         - div part of message (code + reason)
        .ccreg_errors       - ul li with errors
        .ccreg_data         - table with data
        .ccreg_source       - pre with XML sources
        .command_success    - reason with code 1000
        .command_done       - other readons
        .even               - every even row in data table
        """
        body=[]
        report = body.append
        if not dct: dct = self._dct_answer
        report('<div class="ccreg_client">')
        #... code and reason .............................
        report('<div class="ccreg_code">')
        code = dct['code']
        reason_css_class = {False:'command_done',True:'command_success'}[code==1000]
        if self._session[VERBOSE] < 2:
            # brief output mode
            report('<table class="ccreg_reason">')
            report('\t<tr>\n\t<td><span class="%s">%s</span></td>\n</tr>'%(reason_css_class,get_ltext(dct['reason'])))
            report('</table>')
        else:
            # full
            tbl_reason=['<table class="ccreg_reason">']
            tbl_reason.append('<tr>\n\t<th>code</th>\n\t<td>%d</td>\n</tr>'%code)
            tbl_reason.append('<tr>\n\t<th>command</th>\n\t<td>%s</td>\n</tr>'%get_ltext(dct['command']))
            tbl_reason.append('<tr>\n\t<th>reason</th>\n\t<td><span class="%s">%s</span></td>\n</tr>'%(reason_css_class,get_ltext(dct['reason'])))
            tbl_reason.append('</table>')
            report('\n'.join(tbl_reason))
        report('</div>')
        #... errors .............................
        if len(dct['errors']):
            report('<div class="ccreg_errors">\n<strong>errors:</strong><ul>')
            for error in dct['errors']:
                report('<li>%s</li>'%get_ltext(error))
            report('</ul></div>')
        #... data .............................
        data_indent = ''
        data = []
        dct_data = dct['data']
        for key,verbose,explain in self.__get_column_items__(dct['command'], dct_data):
            if verbose > self._session[VERBOSE]: continue
            value = dct_data.get(key,u'')
            if value not in ('',[]): __append_into_report__(data,key,value,explain,'',2) # 2 - use HTML pattern;
        if len(data):
            report('<table class="ccreg_data">')
            body.extend(data)
            report('</table>')
        for n in range(len(body)):
            if type(body[n]) == unicode: body[n] = body[n].encode(encoding)
        #... third verbose level .............................
        if self._session[VERBOSE] == 3:
            report('<pre class="ccreg_source">')
            report('<strong>COMMAND:</strong>')
            report(escape_html(human_readable(self._raw_cmd)))
            report('<strong>ANSWER:</strong>')
            report(escape_html(human_readable(self._raw_answer)))
            report('</pre>')
        # ..............
        report('</div>')
        return '\n'.join(body)
        
    def save_history(self):
        'Save history of command line.'
        eppdoc_client.eppdoc_assemble.save_history()

    def restore_history(self):
        'Restore history of command line.'
        eppdoc_client.eppdoc_assemble.restore_history()

    def remove_from_history(self, count=1):
        'Remove count last commands from history.'
        eppdoc_client.eppdoc_assemble.remove_from_history(count)
        
def __append_into_report__(body,k,v,explain, indent = '', no_terminal_tags=0):
    'Append value type(unicode|list|tuple) into report body.'
    # odd - lichý, even - sudý
    patt = (
        ('%s${BOLD}%s${NORMAL} %s','%s${BOLD}%s${NORMAL}','%s%s'),
        ('%s%s %s','%s%s','%s%s'),
        ('%s<tr>\n\t<th>%s</th>\n\t<td>%s</td>\n</tr>','%s<tr>\n\t<th>%s</th>\n\t<td>&nbsp;</td>\n</tr>','%s<tr>\n\t<th>&nbsp;</th>\n\t<td>%s</td>\n</tr>'),
    )[no_terminal_tags]
    escape = {False:lambda s: s, True:escape_html}[no_terminal_tags == 2]
    if explain: k = explain # overwrite key by explain message
    if type(k) is str: k = k.decode(encoding)
    if type(v) is str: v = v.decode(encoding)
    space = 23 # indent between names and values
    if no_terminal_tags == 2:
        # html
        key = k
        ljustify = ''
    else:
        # text
        key = (k+':').ljust(space)
        ljustify = ''.ljust(space+len(indent)+1)
    if type(v) in (list,tuple):
        if len(v):
            body.append(get_ltext(colored_output.render(patt[0]%(indent,key,escape(str_lists(v[0]))))))
            for text in v[1:]:
                body.append(get_ltext(patt[2]%(ljustify,escape(str_lists(text)))))
        else:
            body.append(get_ltext(colored_output.render(patt[1]%(indent,key))))
    else:
        body.append(get_ltext(colored_output.render(patt[0]%(indent,key, v))))

def str_lists(text):
    """Prepare list or tuples for display. Same as str() but ommit u'...' symbols
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
