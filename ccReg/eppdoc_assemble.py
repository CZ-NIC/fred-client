# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
# Tento modul obsahuje funkce a data, která jsou potřebná
# na sestavení EPP dokumentu pro příkaz od klienta.
#
# Funkce s prefixem "assemble_" jsou jednotlivé EPP příkazy, které třída
# Message() umí sestavit. Seznam dostupných příkazů vrací funkce get_client_commands().
#
import re, sys, os
import random
import ConfigParser
import eppdoc
import cmd_parser
import session_base
from translate import _T, _TP, encoding

try:
    import readline
    history_write = readline.write_history_file
    history_read = readline.read_history_file
except ImportError:
    history_write = None
    history_read = None

UNBOUNDED = None
contact_disclose = ('name','org','addr','voice','fax','email')
history_filename = os.path.join(os.path.expanduser('~'),'.ccreg_history') # compatibility s MS Win

class Message(eppdoc.Message):
    "Client EPP commands."

    def __get_help_scope__(self, params, deep=1):
        'Support for get_help(). IN: params, deep'
        msg=[]
        indent = '    '*deep
        for row in params:
            name,min_max,allowed,help,example,pattern,children = row
            min,max = min_max
            if min > 0:
                color = {False:'YELLOW',True:'GREEN'}[deep==1]
                required = '${%s}${BOLD}(%s)${NORMAL}'%(color,_T('required'))
            else:
                required = '${WHITE}(%s)${NORMAL}'%_T('optional')
            text = '%s${BOLD}%s${NORMAL} %s'%(indent,name,required)
            if max is UNBOUNDED:
                max_size = _T('unbounded list')
            elif max > 1:
                max_size = _TP('list with max %d item.','list with max %d items.',max)%max
            else:
                max_size = ''
            if max_size:
                text = '%s%s%s'%(text,('\t','\t\t')[len(text)<42],max_size)
            if len(allowed):
                txt = ','.join(allowed)
                if len(txt)>37: txt = txt[:37]+'...' # shorter too long text
                text = '%s ${WHITE}%s: ${CYAN}(%s)${NORMAL}'%(text,_T('accepts only values'),txt)
            msg.append('%s %s'%(text,help))
            if len(children):
                msg.extend(self.__get_help_scope__(children, deep+1))
        return msg

    def get_help(self, command_name):
        "Returns help for selected command: (command_line, complete help)."
        command_line = []
        help=[]
        notice=''
        examples = ()
        # v příkazu zrušit spojovníky
        m = re.match('(\S+)(.*)',command_name)
        if m: command_name = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if self._command_params.has_key(command_name):
            # příkaz existuje
            required,params,notice,examples = self._command_params[command_name]
            command_line = ['${BOLD}%s${NORMAL}'%command_name] ## .replace('_','-')
            if params:
                for pos in range(required):
                    command_line.append(params[pos][0])
            help = self.__get_help_scope__(params)
        else:
            # neznámý příkaz
            help.append(_T('Unknown EPP command. Select one from EPP commands list (Type help).'))
            self.help_check_name(help,command_name)
        return ' '.join(command_line), '\n'.join(help), notice, examples
            
    def help_check_name(self,help,command_name):
        'Join extended help if possible (for some commands).'
        if command_name in ('create','check','info','transfer'):
            help.append('%s: %s'%(_T('Try'),' '.join(['%s-%s'%(command_name,n) for n in ('contact','domain','nsset')])))

    def __fill_empy_from_config__(self, config, dct, columns):
        'Fill missing values from config.'
        errors = []
        #DISABLED: function was disabled except login.
        if columns[0][0] == 'login':
            section = 'epp_%s'%columns[0][0]
            if not config or not config.has_section(section): return errors # silent, no errors
            for key,value in config.items(section):
                # go throught dict and create keys if missing:
                cmd_parser.insert_on_key(errors, dct, columns, key, value, 1)
        return errors

    def get_default_params_from_config(self, config, command_name):
        'Returns dict with default parameters from config.'
        dct = {}
        columns = [(command_name,(1,1),(),'','','',())]
        columns.extend(self._command_params[command_name][1])
        self.__fill_empy_from_config__(config, dct, columns)
        return dct
        
    def __check_required__(self, columns, dct_values, scopes=[]):
        'Check parsed values for required and allowed values.'
        errors = []
        if len(scopes) and not len(dct_values): return errors # if descendant is empty - not check
        if type(dct_values) != dict: return ('%s (%s)'%(_T('Invalid input format.'),[c[0] for c in columns]),)
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            scopes.append(name)
            scope_name = '.'.join(scopes)
            if dct_values.has_key(name):
                if min_max[1] != UNBOUNDED and len(dct_values[name]) > min_max[1]:
                    errors.append('%s: %s %d. %s'%(scope_name,_T('list of values overflow. Maximum is'),min_max[1],str(dct_values[name])))
                if allowed:
                    # check allowed values
                    for value in dct_values[name]:
                        if value not in allowed:
                            errors.append('%s: %s %s'%(scope_name,_T('Value "%s" is not allowed. Valid is:')%value.encode(encoding),str(allowed)))
                # walk throught descendants:
                if children:
                    for dct in dct_values[name]:
                        err = self.__check_required__(children, dct, scopes)
                        if err: errors.extend(err)
            else:
                if min_max[0] > 0: errors.append('%s: %s %s'%(_T('ERROR'),scope_name,_T('missing')))
            scopes.pop()
        return errors

    def __insist_on_required__(self, command_name, columns, dct, parents=[]):
        'Ask again for required values. Used by Interactive params mode.'
        errors = []
        param = ''
        stop=0
        used=[]
        for k,v in dct.items():
            if len(v[0]): used.append(k)
        if not len(used): return errors,param,stop # this scope was not set, so we dont neet required values
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            min,max = min_max
            if not min: continue
            if dct.has_key(name):
                for value in dct[name]:
                    if len(value): continue # one of values is set
            else:
                dct[name] = ['']
            parents.append([name,0,max])
            stop=0
            autofill=0
            while not len(dct[name][0]):
                prompt = u'!%s:%s (%s) > '%(command_name,__scope_to_string__(parents), unicode(_T('required'),encoding))
                try:
                    param = raw_input(prompt.encode(encoding)).strip()
                except (KeyboardInterrupt, EOFError):
                    stop=2
                    break
                if param in ('""',"''"): param = cmd_parser.SUBTITUTE_EMPTY
                if autofill > 2 and param == '':
                    param = example
                    if not param: param = 'example' # value MUST be set
                    if type(param) == unicode: param = param.encode(encoding)
                    session_base.print_unicode('${BOLD}${GREEN}%s, %s:${NORMAL} %s'%((_T("I'm fed up"),_T("It's boring"))[random.randint(0,1)],_T("example inserted"),param))
                    autofill=0
                if param == '':
                    session_base.print_unicode('${BOLD}${RED}%s${NORMAL}'%_T('Value is required. MUST be set:'))
                    autofill+=1
                    continue
                else:
                    if type(param) != unicode:
                        try:
                            param = unicode(param, encoding)
                        except UnicodeDecodeError, msg:
                            errors.append('UnicodeDecodeError: %s'%msg)
                            param = unicode(repr(param), encoding)
                    if param[0] == '!':
                        stop=1
                        break
                    if param[0] != '(': param = append_quotes(param)
                    req_dct = {}
                    err = cmd_parser.parse(req_dct, ((name,min_max,allowed,'','','',()),), param)
                    dct[name][0] = req_dct[name][0]
                    if err: errors.extend(err)
            parents.pop()
        if len(param) and param[0] == '!': param = param[1:]
        return errors,param,stop
        
    def __interactive_params__(self, command_name, columns, dct, parents=[]):
        'Runs LOOP of interactive input of the command params.'
        errors = []
        param = ''
        stop=0
        is_child = len(parents)>0
        min = 0
        param_reqired_type = (_T('optional'),_T('required'),_T('required only if part is set'))
        for row in columns:
            if len(param) and param[0] == '!': break
            if is_child and param == '' and min:
                break
            name,min_max,allowed,msg_help,example,pattern,children = row
            min,max = min_max
            parents.append([name,0,max])
            if len(children):
                print_info_listmax(max) # (Value can be a list of max %d values.)
                dct[name] = []
                idc=0
                while max is UNBOUNDED or idc < max:
                    dct[name].append({})
                    parents[-1][1] = idc
                    err, param, stop = self.__interactive_params__(command_name, children, dct[name][-1], parents)
                    if err: errors.extend(err)
                    if stop: break
                    err, param, stop = self.__insist_on_required__(command_name, children, dct[name][-1], parents)
                    if err: errors.extend(err)
                    if stop: break
                    if len(param) and param[0] == '!':
                        if max is None or max > 1: 
                            param = param[1:]
                        break
                    idc+=1
                parents.pop()
                if stop: break
                continue
            if name =='':
                parents.pop()
                continue
            is_child = len(parents)>1
            # Type of parameter:
            req = min
            if is_child and min: req = 2 # if param is child and required in this child part
            print_info_listmax(max) # (Value can be a list of max %d values.)
            if self._verbose > 1:
                if len(allowed):
                    session_base.print_unicode('${WHITE}%s:${NORMAL} (%s)'%(_T('Parameter MUST be a value from following list'),', '.join(allowed)))
                if len(example):
                    if type(example) == unicode: example = example.encode(encoding)
                    session_base.print_unicode('%s ${WHITE}(%s)${NORMAL} %s: %s'%(__scope_to_string__(parents),msg_help,_T('Example'),example))
            cr = 0
            stop=0
            autofill=0
            while max is UNBOUNDED or cr < max:
                parents[-1][1] = cr
                prompt = u'!%s:%s (%s) > '%(command_name,__scope_to_string__(parents), unicode(param_reqired_type[req],encoding))
                try:
                    param = raw_input(prompt.encode(encoding)).strip()
                except (KeyboardInterrupt, EOFError):
                    stop=2
                    break
                if param in ('""',"''"): param = cmd_parser.SUBTITUTE_EMPTY
                if autofill > 2 and param == '':
                    param = example
                    if not param: param = 'example' # value MUST be set
                    if type(param) == unicode: param = param.encode(encoding)
                    session_base.print_unicode('${BOLD}${GREEN}%s, %s:${NORMAL} %s'%((_T("I'm fed up"),_T("It's boring"))[random.randint(0,1)],_T("example inserted"),param))
                    autofill=0
                if param == '':
                    if req == 1: # require in first level only
                        session_base.print_unicode('${BOLD}${RED}%s${NORMAL}'%_T('Value is required. MUST be set:'))
                        autofill+=1
                        continue
                    if cr == 0:
                        # one item MUST be set at minimum
                        if dct.has_key(name):
                            dct[name].append('')
                        else:
                            dct[name] = ['']
                    break
                else:
                    if type(param) != unicode:
                        try:
                            param = unicode(param, encoding)
                        except UnicodeDecodeError, msg:
                            errors.append('UnicodeDecodeError: %s'%msg)
                            param = unicode(repr(param), encoding)
                    if param[0] == '!':
                        stop=1
                        break
                    if param[0] != '(': param = append_quotes(param)
                    err = cmd_parser.parse(dct, ((name,min_max,allowed,'','','',()),), param)
                    if err: errors.extend(err)
                cr+=1
            parents.pop()
            if stop: break
        if len(param) and param[0] == '!': param = param[1:]
        return errors,param,stop

    def get_command_line(self):
        'Returns example of command built from parameters.'
        retval = ''
        if type(self._dct.get('command')) is list:
            command_name = self._dct['command'][0]
            columns = [(command_name,(1,1),(),'','','',())]
            columns.extend(self._command_params[command_name][1])
            retval = __build_command_example__(columns, self._dct)
        return retval.encode(encoding)
    
    def parse_cmd(self, command_name, cmd, config, interactive, verbose):
        "Parse command line. Returns errors. Save parsed values to self._dct."
        dct = {}
        error=[]
        example = ''
        stop = 0
        self._verbose = verbose
        m = re.match('check_(\w+)\s+(.+)',cmd)
        if m:
            # úprava pro příkazy check_..., kde se jména seskupí do jednoho parametru name
            cmd = 'check_%s (%s)'%(m.group(1),m.group(2))
        vals = self._command_params.get(command_name,None)
        if not vals:
            error.append("%s: '%s'"%(_T('Unknown command'),command_name))
            error.append('(%s: ${BOLD}help${NORMAL})'%(_T('For more type')))
            return error
        if not vals[1]: return error # bez parametrů
        columns = [(command_name,(1,1),(),'','','',())]
        columns.extend(self._command_params[command_name][1])
        dct['command'] = [command_name]
        if interactive:
            session_base.print_unicode('${BOLD}${YELLOW}%s: ${NORMAL}${BOLD}!${NORMAL} %s'%(_T('Interactive input params mode. For BREAK type'),_T("If you don't fill item press ENTER.")))
            dct[command_name] = [command_name]
            self.save_history()
            errors, param, stop = self.__interactive_params__(command_name, vals[1], dct)
            if not errors:
                example = __build_command_example__(columns, dct)
            if stop != 2: # user press Ctrl+C or Ctrl+D
                # Note the interactive mode is closed.
                try:
                    raw_input(session_base.colored_output.render('${BOLD}${YELLOW}%s${NORMAL}'%_T('End of interactive input. [press enter]')))
                except (KeyboardInterrupt, EOFError):
                    pass
            self.restore_history()
        else:
            errors = cmd_parser.parse(dct, columns, cmd)
        if errors: error.extend(errors)
        dct = remove_empty_keys(dct) # remove empty for better recognition of missing values
        self.__fill_empy_from_config__(config, dct, columns) # fill missing values from config
        __subtitute_symbol_empty__(dct) # Replace SUBTITUTE_EMPTY to empty string
        errors = self.__check_required__(columns, dct) # check list and allowed values
        if errors: error.extend(errors)
        if len(dct) < vals[0]+1: # počet parametrů plus název příkazu
            # build command_line example
            error.append('%s %d.'%(_T('Missing values. Required minimum is'),vals[0]))
            error.append('%s: %s'%(_T('Type'),self.get_help(command_name)[0]))
            error.append('(%s: ${BOLD}help %s${NORMAL})'%(_T('For more type'),command_name.encode(encoding))) ## .replace('_','-')
        self._dct = dct
        return error, example, stop

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:] for name in dir(self.__class__) if name[:9]=='assemble_'] ## .replace('_','-')

    #===========================================
    #
    # Process commands
    #
    #===========================================
    def __append_attr__(self, data, dct, key, parent_node_name, node_name, attr_name):
        'Support function for assembel_create_... functions.'
        if dct.has_key(key):
            if type(dct[key]) == list:
                for item in dct[key]:
                    data.append((parent_node_name,node_name,'',((attr_name,item),)))
            else:
                data.append((parent_node_name,node_name,'',((attr_name,dct[key]),)))

    def __append_values__(self, data, dct, key, parent_node_name, node_name):
        'Support function for assembel_create_... functions.'
        if dct.has_key(key):
            if type(dct[key]) == list:
                for item in dct[key]:
                    data.append((parent_node_name,node_name,item))
            else:
                data.append((parent_node_name,node_name,dct[key]))

    def __assemble_cmd__(self, data):
        'Support for assemble_...() functions.'
        self.create()
        for v in data:
            value, attr = None,None
            parent_name, name = v[0:2]
            if len(v)>2: value = v[2]
            if len(v)>3: attr  = v[3]
            self.new_node_by_name(parent_name, name, value, attr)

    def __asseble_command__(self, cols, key, params):
        """Internal fnc for assembly commands info, check. 
        cols=('check','contact','id' [,list])
        key = name of key pointed to vlaue in parameters dictionary
        params must have ('clTRID',('name',['name','name',]))
        """
        if len(cols) > 3:
            col1 = '%s:%s'%(cols[1],cols[3])
        else:
            col1 = '%s:%s'%(cols[1],cols[0])
        col2 = '%s:%s'%(cols[1],cols[2])
        data=[('epp', 'command'),
            ('command', cols[0]),
            (cols[0],col1,None,(
            ('xmlns:%s'%cols[1],'%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,cols[1],eppdoc.nic_cz_version)),
            ('xsi:schemaLocation','%s%s-1.0 %s-%s.xsd'%(eppdoc.nic_cz_xml_epp_path,cols[1],cols[1],eppdoc.nic_cz_version))
            ))
            ]
        if key:
            names = self._dct[key]
            if type(names) not in (list,tuple):
                names = (names,)
            for value in names:
                data.append((col1, col2, value))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    #-------------------------------------------
    # Session management
    #-------------------------------------------
    def assemble_hello(self, *params):
        self.__assemble_cmd__((('epp', 'hello'),))

    def assemble_login(self, *params):
        """Client EPP command: login
        *params: ('clTRID'
                ,['username', 'password'[,'new-pass']]
                ,('version', ['objURI'] or None,['extURI'] or None, 'language'))
        """
        # protect to missing login values:
        for key in ('username','password'):
            if not (self._dct.has_key(key) and len(self._dct[key])):
                self.errors.append((0, key, 'missing'))
        if len(self.errors): return
        cols = [('epp', 'command'),
            ('command', 'login'),
            ('login', 'clID', self._dct['username'][0]),
            ('login', 'pw', self._dct['password'][0]),
            ]
        if __has_key__(self._dct,'new-password'): cols.append(('login', 'newPW', self._dct['new-password'][0]))
        cols.extend([
            ('login', 'options'),
            ('options', 'version', params[1][0]),
            ('options', 'lang', params[1][3]),
            ('login', 'svcs'),
        ])
        if params[1][1]:
            for uri in params[1][1]:
                cols.append(('svcs', 'objURI', uri))
        if params[1][2]:
            cols.append(('svcs', 'svcExtension'))
            for uri in params[1][2]:
                cols.append(('svcExtension', 'extURI', uri))
        cols.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(cols)

    def assemble_logout(self, *params):
        "Assemble EPP command logount. *params: ('clTRID')"
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'logout'),
            ('command', 'clTRID', params[0])
        ))

    #-------------------------------------------
    # Dotazovací (query)
    #-------------------------------------------
    def assemble_check_contact(self, *params):
        self.__asseble_command__(('check','contact','id'), 'name', params)
        
    def assemble_check_domain(self, *params):
        self.__asseble_command__(('check','domain','name'), 'name', params)
        
    def assemble_check_nsset(self, *params):
        self.__asseble_command__(('check','nsset','id'), 'name', params)

    def assemble_info_contact(self, *params):
        self.__asseble_command__(('info','contact','id'), 'name', params)

    def assemble_info_domain(self, *params):
        self.__asseble_command__(('info','domain','name'), 'name', params)

    def assemble_info_nsset(self, *params):
        self.__asseble_command__(('info','nsset','id'), 'name', params)

    def assemble_list_contact(self, *params):
        self.__asseble_command__(('info','contact','id','list'), '', params)
        
    def assemble_list_domain(self, *params):
        self.__asseble_command__(('info','domain','id','list'), '', params)
        
    def assemble_list_nsset(self, *params):
        self.__asseble_command__(('info','nsset','id','list'), '', params)

    def assemble_poll(self, *params):
        op = self._dct.get('op',['req'])[0]
        attr = [('op',op)]
        if self._dct.get('msg_id',None): attr.append(('msgID',self._dct['msg_id'][0]))
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'poll', '', attr),
            ('command', 'clTRID', params[0])
        ))

    #-------------------------------------------
    # Editační (query)
    #-------------------------------------------
    def assemble_delete_contact(self, *params):
        self.__asseble_command__(('delete','contact','id'), 'id', params)

    def assemble_delete_domain(self, *params):
        self.__asseble_command__(('delete','domain','name'), 'name', params)

    def assemble_delete_nsset(self, *params):
        self.__asseble_command__(('delete','nsset','id'), 'id', params)


    def __assemble_transfer__(self, names, params):
        "Assemble transfer XML EPP command."
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'transfer', '', (('op','request'),)), # self._dct['op'][0]
            ('transfer', '%s:transfer'%names[0], '', attr),
            ('%s:transfer'%names[0], '%s:%s'%names, self._dct['name'][0]),
            ('%s:transfer'%names[0], '%s:authInfo'%names[0]),
            ('%s:authInfo'%names[0], '%s:pw'%names[0], self._dct['passw'][0]),
            ('command', 'clTRID', params[0])
        ))

    def assemble_transfer_contact(self, *params):
        self.__assemble_transfer__(('contact','id'),params)

    def assemble_transfer_domain(self, *params):
        self.__assemble_transfer__(('domain','name'),params)

    def assemble_transfer_nsset(self, *params):
        self.__assemble_transfer__(('nsset','id'),params)

    #-------------------------------------------
    # Výkonné
    #-------------------------------------------
    def __enum_extensions__(self, type, data, params, tag_name=''):
        'Enum extension for (creste|renew)-domain commands.'
        if not __has_key__(self._dct,'val_ex_date'): return
        names = ('enumval',type)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
            ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data.extend((
            ('command','extension'),
            ('extension','%s:%s'%names,'',attr)
        ))
        if tag_name:
            data.append(('%s:%s'%names,'%s:%s'%(names[0],tag_name))) # mezitag
            names = ('enumval',tag_name)
        data.append(('%s:%s'%names,'%s:valExDate'%names[0], self._dct['val_ex_date'][0]))

    def __append_disclose__(self, data, node_name, ds):
        'Create disclose nodes'
        flag = {'n':0,'y':1}.get(ds.get('flag',['n'])[0], 'n')
        disit = ds.get('data',[])
        if len(disit):
            if flag:
                # 1 - list of disclosed -> invert other to hidden
                disit = [key for key in contact_disclose if key not in disit]
            else:
                # 0 - list of hidden -> sort only (and remove duplicity)
                disit = [key for key in contact_disclose if key in disit]
            data.append(('contact:%s'%node_name,'contact:disclose','',(('flag','0'),)))
            # create if only any set of names is to hide
            for key in disit:
                data.append(('contact:disclose','contact:%s'%key))
        else:
            data.append(('contact:%s'%node_name,'contact:disclose','',(('flag',str(flag)),)))

    def assemble_create_contact(self, *params):
        "Assemble XML EPP command."
        dct = self._dct
        names = ('contact',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'create'),
            ('create', 'contact:create', '', attr),
            ('contact:create','contact:id', dct['contact_id'][0]),
            ('contact:create','contact:postalInfo'),
            ('contact:postalInfo','contact:name', dct['name'][0])] # required
        if __has_key__(dct,'org'): data.append(('contact:postalInfo','contact:org', dct['org'][0]))
        # --- BEGIN addr ------
        data.append(('contact:postalInfo','contact:addr')) # required
        self.__append_values__(data, dct, 'street', 'contact:addr', 'contact:street')
        data.append(('contact:addr','contact:city', dct['city'][0])) # required
        if __has_key__(dct,'sp'): data.append(('contact:addr','contact:sp', dct['sp'][0]))
        if __has_key__(dct,'pc'): data.append(('contact:addr','contact:pc', dct['pc'][0]))
        data.append(('contact:addr','contact:cc', dct['cc'][0])) # required
        # --- END addr ------
        if __has_key__(dct,'voice'): data.append(('contact:create','contact:voice', dct['voice'][0]))
        if __has_key__(dct,'fax'): data.append(('contact:create','contact:fax', dct['fax'][0]))
        data.append(('contact:create','contact:email',dct['email'][0])) # required
        # password required
        data.append(('contact:create','contact:authInfo'))
        data.append(('contact:authInfo','contact:pw',dct['pw'][0]))
        # --- BEGIN disclose ------
        if __has_key_dict__(dct,'disclose'):
            self.__append_disclose__(data, 'create', dct['disclose'][0])
        # --- END disclose ------
        if __has_key__(dct,'vat'): data.append(('contact:create','contact:vat', dct['vat'][0]))
        if __has_key_dict__(dct,'ssn'):
            ssn = dct['ssn'][0]
            data.append(('contact:create','contact:ssn', ssn['number'][0], (('type',ssn['type'][0]),)))
        if __has_key__(dct,'notify_email'): data.append(('contact:create','contact:notifyEmail', dct['notify_email'][0]))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_create_domain(self, *params):
        "Assemble XML EPP command."
        dct = self._dct
        names = ('domain',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'create'),
            ('create', 'domain:create', '', attr),
            ('domain:create','domain:name', dct['name'][0])]
        if __has_key_dict__(dct,'period'):
            period = dct['period'][0]
            if not __has_key__(period,'unit'): period['unit']=('y',)
            data.append(('domain:create','domain:period',period['num'][0], (('unit',period['unit'][0]),)))
        if __has_key__(dct,'nsset'): data.append(('domain:create','domain:nsset',dct['nsset'][0]))
        if __has_key__(dct,'registrant'): data.append(('domain:create','domain:registrant',dct['registrant'][0]))
        self.__append_values__(data, dct, 'admin', 'domain:create', 'domain:admin')
        data.extend((
            ('domain:create','domain:authInfo'),
            ('domain:authInfo','domain:pw', dct['pw'][0])
        ))
        self.__enum_extensions__('create',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def __append_nsset__(self, tag_name, data, dct_ns):
        "ns:  {'name': ['ns3.domain.net'], 'addr': ['127.3.0.1', '127.3.0.2']}"
        if not __has_key__(dct_ns,'name'): return
        data.append(('nsset:%s'%tag_name, 'nsset:ns'))
        data.append(('nsset:ns', 'nsset:name',dct_ns['name'][0]))
        if dct_ns.has_key('addr'):
            for addr in dct_ns['addr']:
                data.append(('nsset:ns', 'nsset:addr',addr))
        
    def assemble_create_nsset(self, *params):
        "Assemble XML EPP command."
        dct = self._dct
        names = ('nsset',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'create'),
            ('create', 'nsset:create', '', attr),
            ('nsset:create','nsset:id', dct['id'][0])]
        # ns records
        if __has_key__(dct,'dns'):
            for dns in dct['dns']:
                self.__append_nsset__('create', data, dns)
        if __has_key__(dct,'tech'):
            self.__append_values__(data, dct, 'tech', 'nsset:create', 'nsset:tech')
        data.extend((
            ('nsset:create','nsset:authInfo'),
            ('nsset:authInfo','nsset:pw', dct['pw'][0])
        ))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_renew_domain(self, *params):
        """Assemble XML EPP command. 
        """
        dct = self._dct
        names = ('domain',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'renew'),
            ('renew', 'domain:renew', '', attr),
            ('domain:renew','domain:name', dct['name'][0]),
            ('domain:renew','domain:curExpDate', dct['cur_exp_date'][0]),
            ]
        if __has_key_dict__(dct,'period'):
            period = dct['period'][0]
            if not __has_key__(period,'unit'): period['unit']=('y',)
            data.append(('domain:renew','domain:period',period['num'][0], (('unit',period['unit'][0]),)))
        self.__enum_extensions__('renew',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_contact(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        names = ('contact',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'contact:update', '', attr),
            ('contact:update','contact:id', dct['contact_id'][0]),
            ]
        if __has_key__(dct,'add'):
            data.append(('contact:update', 'contact:add'))
            self.__append_attr__(data, dct, 'add', 'contact:add', 'contact:status','s')
        if __has_key__(dct,'rem'):
            data.append(('contact:update', 'contact:rem'))
            self.__append_attr__(data, dct, 'rem', 'contact:rem', 'contact:status','s')
        if __has_key_dict__(dct,'chg'):
            chg = dct['chg'][0]
            data.append(('contact:update','contact:chg'))
            if __has_key_dict__(chg,'postal_info'):
                # Part contact:postalInfo ------------------------
                poin = chg['postal_info'][0]
                data.append(('contact:chg','contact:postalInfo'))
                for key in ('name','org'):
                    if __has_key__(poin,key): data.append(('contact:postalInfo','contact:%s'%key, poin[key][0]))
                if __has_key_dict__(poin,'addr'):
                    addr = poin['addr'][0]
                    data.append(('contact:postalInfo','contact:addr'))
                    self.__append_values__(data, addr, 'street', 'contact:addr', 'contact:street')
                    for key in ('city','sp','pc','cc'):
                        if __has_key__(addr,key): data.append(('contact:addr','contact:%s'%key, addr[key][0]))
            for key in ('voice','fax','email'):
                if __has_key__(chg,key): data.append(('contact:chg','contact:%s'%key, chg[key][0]))
            # password
            if __has_key__(chg,'pw'):
                data.append(('contact:chg','contact:authInfo')) # required
                data.append(('contact:authInfo','contact:pw',chg['pw'][0])) # required
            # --- BEGIN disclose ------
            if __has_key_dict__(chg,'disclose'):
                self.__append_disclose__(data, 'chg', chg['disclose'][0])
            # --- END disclose ------
            if __has_key__(chg,'vat'): data.append(('contact:chg','contact:vat', chg['vat'][0]))
            if __has_key_dict__(chg,'ssn'):
                ssn = chg['ssn'][0]
                data.append(('contact:chg','contact:ssn', ssn['number'][0], (('type',ssn['type'][0]),)))
            if __has_key__(chg,'notify_email'): data.append(('contact:chg','contact:notifyEmail', chg['notify_email'][0]))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_domain(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        names = ('domain',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'domain:update', '', attr),
            ('domain:update','domain:name', dct['name'][0]),
            ]
        for key in ('add','rem'):
            if __has_key_dict__(dct,key):
                data.append(('domain:update', 'domain:%s'%key))
                dct_key = dct[key][0]
                if __has_key__(dct_key,'admin'):
                    self.__append_values__(data, dct_key, 'admin', 'domain:%s'%key, 'domain:admin')
                self.__append_attr__(data, dct_key, 'status', 'domain:%s'%key, 'domain:status','s')
        if __has_key_dict__(dct,'chg'):
            chg = dct['chg'][0]
            data.append(('domain:update', 'domain:chg'))
            if __has_key__(chg,'nsset'): data.append(('domain:chg','domain:nsset', chg['nsset'][0]))
            if __has_key__(chg,'registrant'): data.append(('domain:chg','domain:registrant', chg['registrant'][0]))
            if __has_key_dict__(chg,'auth_info'):
                data.append(('domain:chg','domain:authInfo'))
                authInfo = chg['auth_info'][0]
                if __has_key__(authInfo,'pw'): data.append(('domain:authInfo','domain:pw', authInfo['pw'][0]))
                #if __has_key__(authInfo,'ext'): data.append(('domain:authInfo','domain:ext', authInfo['ext'][0]))
        self.__enum_extensions__('update',data, params,'chg')
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_nsset(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        names = ('nsset',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'nsset:update', '', attr),
            ('nsset:update','nsset:id', dct['id'][0]),
            ]
        if __has_key_dict__(dct,'add'):
            data.append(('nsset:update','nsset:add'))
            dct_add = dct['add'][0]
            if __has_key_dict__(dct_add,'dns'):
                for dct_dns in dct_add['dns']:
                    if not __has_key__(dct_dns, 'name'): continue
                    data.append(('nsset:add','nsset:ns'))
                    data.append(('nsset:ns','nsset:name',dct_dns['name'][0]))
                    self.__append_values__(data, dct_dns, 'addr', 'nsset:ns', 'nsset:addr')
            self.__append_values__(data, dct_add, 'tech', 'nsset:add', 'nsset:tech')
            self.__append_attr__(data, dct_add, 'status', 'nsset:add', 'nsset:status','s')

        if __has_key_dict__(dct,'rem'):
            data.append(('nsset:update','nsset:rem'))
            dct_rem = dct['rem'][0]
            self.__append_values__(data, dct_rem, 'name', 'nsset:rem', 'nsset:name')
            self.__append_values__(data, dct_rem, 'tech', 'nsset:rem', 'nsset:tech')
            self.__append_attr__(data, dct_rem, 'status', 'nsset:rem', 'nsset:status','s')

        if __has_key_dict__(dct,'chg'):
            data.append(('nsset:update','nsset:chg'))
            data.append(('nsset:chg','nsset:authInfo'))
            dct_chg = dct['chg'][0]
            if __has_key__(dct_chg, 'pw'): data.append(('nsset:authInfo','nsset:pw',dct_chg['pw'][0]))
            #if __has_key__(dct_chg, 'ext'): data.append(('nsset:authInfo','nsset:ext',dct_chg['ext'][0]))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    #===========================================

    def save_history(self):
        'Save history of command line.'
        if history_write: history_write(history_filename) # save history
        
    def restore_history(self):
        'Restore history of command line.'
        if history_read: history_read(history_filename) # restore history (flush interactive params)


def __has_key__(dct, key):
    'Check if key exists and if any value is set. (dct MUST be in format: dct[key] = [{...}, ...])'
    return dct.has_key(key) and len(dct[key])

def __has_key_dict__(dct, key):
    'Check if key exists and if any value is set. (dct MUST be in format: dct[key] = [{...}, ...])'
    return dct.has_key(key) and len(dct[key]) and len(dct[key][0])

def __scope_to_string__(scopes):
    'Assemble names into string. Scopes is in format: ((name, cr, max), ...)'
    tokens=[]
    for name,cr,max in scopes:
        if max is UNBOUNDED or max > 1:
            if max is UNBOUNDED:
                str_max = 'oo'
            else:
                str_max = str(max)
            tokens.append('%s[%d/%s]'%(name,cr+1,str_max))
        else:
            tokens.append(name)
    return '.'.join(tokens)

def escape(text):
    'Escape quotes in text.'
    ret=[]
    for n in range(len(text)):
        c = text[n]
        if c in '\'"':
            num_of_backslash = 0
            o=n-1
            while o > 0 and text[o] == '\\':
                o-=1
                num_of_backslash+=1
            if not num_of_backslash%2:
                ret.append('\\')
        ret.append(c)
    return ''.join(ret)

def append_quotes(text):
    'Function append quotes if in text is any space and text is not in quotes.'
    if len(text) and text[0] not in '\'"' and re.search('\s',text):
        text = "'%s'"%escape(text)
    return text

def __build_command_example__(columns, dct_data):
    'Build command line from data (what was put in interactive mode).'
    body = []
    for row in columns:
        name,min_max,allowed,help,example,pattern,children = row
        min,max = min_max
        if len(children):
            text=''
            if dct_data.has_key(name):
                if max is UNBOUNDED or max > 1:
                    scopes = []
                    for dct_item in dct_data[name]:
                        text = __build_command_example__(children, dct_item)
                        if len(text): scopes.append('(%s)'%text)
                    text = ', '.join(scopes)
                else:
                    if len(dct_data[name]):
                        text = __build_command_example__(children, dct_data[name][0])
            body.append('(%s)'%text) # required bracket    
        else:
            values = dct_data.get(name,[])
            if len(values):
                if max is UNBOUNDED or max > 1:
                    # list
                    if len(values)>1:
                        vals = []
                        for value in values:
                            if value=='':
                                vals.append("''")
                            else:
                                vals.append(append_quotes(value))
                        body.append('(%s)'%', '.join(vals))
                    else:
                        # list, but only one item, bracket dont needed
                        value=values[0]
                        if value=='':
                            body.append("''")
                        else:
                            body.append(append_quotes(value))
                else:
                    # single value
                    value=values[0]
                    if value=='':
                        body.append("''")
                    else:
                        body.append(append_quotes(value))
            else:
                text = {False:"''",True:"()"}[max is UNBOUNDED or max > 1]
                body.append(text)
    while len(body) and body[-1] in ("''",'()'): body.pop()
    return ' '.join(body)
    
def print_info_listmax(max):
    if max > 1:
        session_base.print_unicode(_TP('(Value can be a list of max %d value.)','(Value can be a list of max %d values.)',max)%max)
    elif max is UNBOUNDED:
        session_base.print_unicode(_T('(Value can be an unbouded list of values.)'))

def remove_empty_keys(dct):
    'Remove empty keys. dct is in format {key: [str, {key: [str, str]} ,str]}'
    retd = {}
    for key in dct.keys():
        value = dct[key]
        if not (len(value)==1 and value[0]==''):
            scope = []
            for item in value:
                if type(item) is dict:
                    dcit = remove_empty_keys(item)
                    if len(dcit): scope.append(dcit)
                else:
                    scope.append(item)
            if len(scope): retd[key] = scope
    return retd

def __subtitute_symbol_empty__(dct):
    'Replace SUBTITUTE_EMPTY to empty string'
    for key, vals in dct.items():
        for i in range(len(vals)):
            if type(vals[i]) == dict:
                __subtitute_symbol_empty__(vals[i])
            else:
                if vals[i] == cmd_parser.SUBTITUTE_EMPTY: dct[key][i]=''
