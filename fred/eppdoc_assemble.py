# -*- coding: utf8 -*-
#!/usr/bin/env python
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
from translate import encoding

try:
    import readline
    readline_is_present = 1
except ImportError:
    readline_is_present = 0

UNBOUNDED = None
# ''contact_disclose'' must be same format as eppdoc_client.update_status.
contact_disclose = map(lambda n: (n,), ('name','org','addr','voice','fax','email'))
history_filename = os.path.join(os.path.expanduser('~'),'.fred_history') # compatibility s MS Win

TAG_clTRID = 'cltrid' # Definition for --key-name = clTRID value.

class Message(eppdoc.Message):
    "Client EPP commands."

    param_reqired_type = (_T('optional'),_T('required'),_T('required only if part is set'))
    
    def __get_help_scope__(self, params, deep=1):
        'Support for get_help(). IN: params, deep'
        msg=[]
        indent = '    '*deep
        for row in params:
            name,min_max,allowed,help,example,pattern,children = row
            min,max = min_max
            if min > 0:
                color = deep==1 and 'GREEN' or 'YELLOW'
                required = '${%s}${BOLD}(%s)${NORMAL}'%(color,_T('required'))
                min_size = _TP('minimum is %d item','minimum are %d items',min)%min
            else:
                required = '${WHITE}(%s)${NORMAL}'%_T('optional')
                min_size = ''
            text = '%s${BOLD}%s${NORMAL} %s'%(indent,name,required)
            if max is UNBOUNDED:
                max_size = _T('unbounded list')
            elif max > 1:
                max_size = _TP('list with max %d item.','list with max %d items.',max)%max
            else:
                max_size = ''
            if max_size:
                text = '%s%s%s %s'%(text,('\t','\t\t')[len(text)<42],max_size,min_size)
            if len(allowed):
                txt = ','.join(self.__make_abrev_help__(allowed))
                if len(txt)>37: txt = txt[:37]+'...' # shorter too long text
                text = '%s ${WHITE}%s: ${CYAN}(%s)${NORMAL}'%(text,_T('accepts only values'),txt)
            if help:
                msg.append('%s %s'%(text,help))
            else:
                msg.append(_T('no options'))
            if len(children):
                msg.extend(self.__get_help_scope__(children, deep+1))
        return msg

    def __make_abrev_help__(self, allowed):
        'Join abreviations with main name.'
        allowed_abrev = []
        for n in allowed:
            allowed_abrev.append(n[0])
            if len(n)>1:
                allowed_abrev[-1]+= ' (%s)'%n[1]
        return allowed_abrev
        
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
            command_line = ['${BOLD}%s${NORMAL}'%command_name]
            if params:
                for pos in range(required):
                    command_line.append(params[pos][0])
                # Only hello has not cltrid optional parameter.
                if command_name != 'hello': command_line.append('[%s]'%_T('other_options'))
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
        if type(dct_values) != dict:
            # parameter is in invalid format
            keys = []
            vals = []
            for name,min_max,required,msg_help,example,pattern,children in columns:
                keys.append(name)
                if len(required):
                    vals.append(required[0][0])
                elif example:
                    vals.append(example)
                else:
                    vals.append(name)
            return ('%s: "%s". (%s: "%s")\n%s: (%s) %s: (%s)'%(
                _T('Invalid parameter'), '.'.join(scopes),
                _T('Corrupted value'),str(dct_values),
                _T('Correct format is'), ', '.join(keys), 
                _T('For example'), ', '.join(vals), 
                ) ,)
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            scopes.append(name)
            scope_name = '.'.join(scopes)
            if dct_values.has_key(name):
                if min_max[1] != UNBOUNDED and len(dct_values[name]) > min_max[1]:
                    errors.append('%s: %s %d. %s'%(scope_name,_T('list of values overflow. Maximum is'),min_max[1],str(dct_values[name])))
                if allowed:
                    # check allowed values
                    allowed_abrev=[]
                    map(allowed_abrev.extend, allowed)
                    for value in dct_values[name]:
                        if value not in allowed_abrev:
                            errors.append('%s: %s: (%s)'%(scope_name,_T('Value "%s" is not allowed. Valid is')%value.encode(encoding),', '.join(self.__make_abrev_help__(allowed))))
                # walk throught descendants:
                if children:
                    for dct in dct_values[name]:
                        err = self.__check_required__(children, dct, scopes)
                        if err: errors.extend(err)
            else:
                if min_max[0] > 0: errors.append('%s %s'%(scope_name,_T('missing')))
            scopes.pop()
        return errors

    def __ineractive_input_one_param__(self, name,min_max,allowed,example, null_value, prompt):
        'Loop raw_input while any value is set.'
        ret_value = null_value
        stop = 0
        autofill = 0
        allowed_abrev=[]
        map(allowed_abrev.extend, allowed)
        allowed_help = self.__make_abrev_help__(allowed)
        while 1:
            # param must not be NULL (except min == 0)
            try:
                param = raw_input(prompt.encode(encoding)).strip()
            except EOFError:
                # Ctrl+D - Finish
                if min_max[0]:
                    # If value is required Finish mode is rejected.
                    session_base.print_unicode('${BOLD}${RED}%s${NORMAL}'%_T('First fill required values and then press Ctrl+D to finish command. For abort press Ctrl+C.'))
                    param = null_value
                else:
                    stop = 1 # Finish
                    break
            except KeyboardInterrupt:
                # Ctrl+C - Abort (Cancel)
                session_base.print_unicode('\n${BOLD}%s${NORMAL}'%_T('Command has been aborted.'))
                stop = 2 # Abort (Cancel)
                break
            # autofill required missing values
            if autofill > 2 and param == '':
                session_base.print_unicode('\n${BOLD}${RED}%s${NORMAL}'%_T('Interactive mode has been aborted.'))
                stop = 2 # Abort (Cancel)
                break
            # Resolve NULL, STOP, min==0 / parse input
            if param == '':
                ret_value = null_value
            else:
                if param in ("''",'""'):
                    ret_value = '' # empty string
                else:
                    # parse input value
                    ret_value,err = text_to_unicode(param)
                    if err: session_base.print_unicode('${BOLD}${RED}%s${NORMAL}'%err)
                if allowed and ret_value not in allowed_abrev:
                    # not allowed value, go to input again
                    session_base.print_unicode('${BOLD}${RED}%s:${NORMAL} ${BOLD}${GREEN}(%s)${NORMAL}'%(_T('Value "%s" is not allowed. Valid is')%ret_value.encode(encoding),', '.join(allowed_help)))
                    continue
            #.. resolve if is need to continue loop ..........................
            if min_max[0] == 0:
                break # value not required
            elif ret_value == null_value:
                # need to continue
                session_base.print_unicode('${BOLD}${RED}%s${NORMAL}'%_T('Value is required. It MUST be set.'))
                autofill += 1
            else:
                break # value is set - stop input
        return ret_value, stop

    def __interactive_mode_children_values__(self,dct,command_name,parents,name,min,max,children,null_value):
        'Put children values (namespaces)'
        self.print_info_listmax(min,max) # (Value can be a list of max %d values.)
        dct[name] = []
        current_pos = already_done = 0
        while max is UNBOUNDED or current_pos < max:
            parents[-1][3] = current_pos # name, min, max, counter = current_pos
            dct_item = {}
            user_typed_null, stop = self.__interactive_mode__(command_name, children, dct_item, null_value, parents, already_done)
            if len(dct_item):
                dct[name].append(dct_item)
                user_typed_null = 0 # user typed at least one valid value
            already_done = (0,1)[len(dct[name]) >= min]
            if stop or (user_typed_null and already_done): break
            current_pos += 1
        if not len(dct[name]): dct.pop(name)
        return user_typed_null, stop

    def __interactive_mode_single_value__(self,dct,command_name,parents,name,min,max,allowed,msg_help,example,null_value,already_done,required_pos):
        'Put single value'
        # single value or list of values
        self.print_info_listmax(min,max) # (Value can be a list of max %d values.)
        if self._verbose > 1:
            if len(allowed):
                session_base.print_unicode('${WHITE}%s:${NORMAL} (%s)'%(_T('Parameter MUST be a value from following list'),', '.join(self.__make_abrev_help__(allowed))))
            if len(example):
                if type(example) == unicode: example = example.encode(encoding)
                session_base.print_unicode('%s ${WHITE}(%s)${NORMAL} %s: %s'%(__scope_to_string__(parents),msg_help,_T('Example'),example))
        current_pos = stop = 0
        while max is UNBOUNDED or current_pos < max:
            parents[-1][3] = current_pos # name, min, max, counter = current_pos
            if dct.has_key(name) and len(dct[name]) >= min: min = required_pos = 0 # all needed values has been set
            prompt = u'%s [%s]: '%(__scope_to_string__(parents), unicode(self.param_reqired_type[required_pos],encoding))
            param, stop = self.__ineractive_input_one_param__(name,(min,max),allowed,example, null_value, prompt)
            if stop: break
            current_pos += 1
            if param != null_value:
                if dct.has_key(name):
                    dct[name].append(param)
                else:
                    dct[name] = [param]
            elif min == 0: break
        return (dct.has_key(name) == False), stop
        
    def __interactive_mode__(self, command_name, columns, dct, null_value, parents=[], already_done=0):
        'Loop interactive input for all params of command.'
        stop = previous_value_is_set = 0
        previous_min = [n[1]for n in parents]
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            min,max = min_max
            utext,error = text_to_unicode(msg_help)
            parents.append([name,min,max,0,utext]) # name,min,max,counter
            # Když je hodnota povinná jen v této sekci, tak se req=1 nastaví na req=2
            # když je hodnota s req=2 zadána, tak se všechny ostatní req hodnoty nastaví na req=1
            if already_done:
                min = 0 # reset required values
            if min:
                required_pos = 1 # index of prompt message
                if not previous_value_is_set and len(parents) > 1 and 0 in previous_min:
                    required_pos = 2 # previous scope doesn't need this scope as required
                    min = 0 # reset required values
            else:
                required_pos = 0 # index of prompt message
            if len(children):
                # not value but list of children
                user_typed_null, stop = self.__interactive_mode_children_values__(dct,command_name,parents,name,min,max,children,null_value)
            else:
                user_typed_null, stop = self.__interactive_mode_single_value__(dct,command_name,parents,name,min,max,allowed,msg_help,example,null_value,already_done,required_pos)
            parents.pop()
            if user_typed_null and (already_done or required_pos == 2): break
            if stop: break # Handle ! or Ctrl+C, Ctrl+D
            if not user_typed_null: previous_value_is_set = 1
        return user_typed_null, stop

    def get_command_line(self, null_value):
        'Returns example of command built from parameters.'
        retval = ''
        if type(self._dct.get('command')) is list:
            command_name = self._dct['command'][0]
            columns = [(command_name,(1,1),(),'','','',())]
            columns.extend(self._command_params[command_name][1])
            retval = __build_command_example__(columns, self._dct, null_value)
        return retval.encode(encoding)

    def readline_parse_prompt(self, command_name, cmd):
        'Parse readline prompt'
        dct = {}
        columns = [(command_name,(1,1),(),'','','',())]
        columns.extend(self._command_params[command_name][1])
        dct['command'] = [command_name]
        errors = cmd_parser.parse(dct, columns, cmd)
        return dct, errors

    def readline_find_words(self, command_name, dct, fnc_debug_log=None):
        'Find words to offer in prompt last_token'
        # fnc_debug_log('readline_find_words("%s", len(DICT)=%d)'%(str(command_name), len(dct)))
        words = []
        columns = self._command_params[command_name][1]
        # Walk throught columns and check if values and blocks are filled.
        # Returns last empty column or block name and alternative value for choose.
        for key, min_max, required, help, example, pattern, children in columns:
            #fnc_debug_log('\t[%s] KEY: %s EXAMPLE: "%s" HAS-KEY: %s'%(time.strftime("%H:%I:%S"),key,local8bit(example),dct.has_key(key)))
            words = []
            if not dct.has_key(key):
                # case value is not allready in dict
                if len(children):
                    token = self.__readline_build_children__(children,min_max[0])
                else:
                    token = readline_build_token(key,example,required,min_max)
                if len(token): words = [token]
                break
        # fnc_debug_log('\tFOUND-WORDS: %s; last-key: %s;'%(str(words),key))
        return words

    def __readline_build_children__(self, columns, min):
        'Returns words of child element'
        tokens = []
        for key, min_max, required, help, example, pattern, children in columns:
            if len(children):
                token = '(%s)'%self.__readline_build_children__(children,min_max[0])
                if min_max[0] > 1: token = '(%s)'%(token*min_max[0])
                tokens.append(token)
            else:
                token = readline_build_token(key,example,required,min_max)
                if len(token): tokens.append(token)
        label  = '(%s)'%' '.join(tokens)
        if min > 1: label  = '(%s)'%(label*min)
        return label
        
    def parse_cmd(self, command_name, cmd, config, interactive, verbose, null_value):
        "Parse command line. Returns errors. Save parsed values to self._dct."
        # __interactive_mode__() -> 
        # 'Loop interactive input for all params of command.'
        #
        #    __interactive_mode_children_values__() -> __interactive_mode__()
        #    'Put children values (namespaces)'
        #
        #    __interactive_mode_single_value__() ->
        #    'Put single value'
        #
        #        __ineractive_input_one_param__()
        #        'Loop raw_input while any value is set.'
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
            dct[command_name] = [command_name]
            if len(vals[1]) > 1:
                session_base.print_unicode('${BOLD}%s${NORMAL}'%_T('Interactive input mode started. Press Ctrl+C to abort or Ctrl+D to finish command.'))
                history_length = get_history_length()
                user_typed_null, stop = self.__interactive_mode__(command_name, vals[1], dct, null_value)
                if stop: stop -= 1 # 0 - normal; 1 - Finish command => normal; 2 - Abort => break interact.m. but not whole application;
                if not stop: # user press ! or Ctrl+C or Ctrl+D
                    example = __build_command_example__(columns, dct, null_value)
                    # Note the interactive mode is closed.
                    try:
                        raw_input(session_base.colored_output.render('\n${BOLD}${YELLOW}%s${NORMAL}'%_T('End of interactive input. [press enter]')))
                    except (KeyboardInterrupt, EOFError):
                        pass
                remove_from_history(get_history_length() - history_length)
            else:
                session_base.print_unicode('${BOLD}${YELLOW}%s${NORMAL}'%_T('No parameters. Skip interactive mode.'))
            errors = []
        else:
            errors = cmd_parser.parse(dct, columns, cmd)
        if errors: error.extend(errors)
        dct = remove_empty_keys(dct, null_value) # remove empty for better recognition of missing values
        self.__fill_empy_from_config__(config, dct, columns) # fill missing values from config
        if not stop:
            # check list and allowed values if only 'stop' was not set
            errors = self.__check_required__(columns, dct)
            if errors:
                error.append(_TP('ERROR: Missing required value.','ERROR: Missing required values.',vals[0]))
                error.extend(errors)
                error.append('') # empty line
                error.append(_T("Type '%s' for more information.")%'help %s'%command_name.encode(encoding))
        self._dct = dct
        return error, example, stop

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:] for name in dir(self.__class__) if name[:9]=='assemble_']

        
    def __parse_status_abrev__(self, dct, key, allowed):
        'Replace abreviations to the full names'
        if not dct.has_key(key): return
        dabrv = {}
        for n in allowed:
            if len(n)>1:
                dabrv[n[1]] = n[0]
        names = []
        for name in dct[key]:
            if dabrv.has_key(name):
                names.append(dabrv[name])
            else:
                names.append(name)
        dct[key] = names
        
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
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
        cols.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
        self.__assemble_cmd__(cols)

    def assemble_logout(self, *params):
        "Assemble EPP command logount. *params: ('clTRID')"
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'logout'),
            ('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0])
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
            ('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0])
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
            ('%s:authInfo'%names[0], '%s:pw'%names[0], self._dct['auth_info'][0]),
            ('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0])
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
        explicit = [] # typed by user
        implicit = [] # others not mentioned
        flag = {'n':0,'y':1}.get(ds.get('flag',['n'])[0], 'n')
        disit = ds.get('data',[])
        if len(disit):
            for key in [n[0] for n in contact_disclose]:
                if key in disit:
                    explicit.append(key)
                else:
                    implicit.append(key)
            if self.server_disclose_policy: # 0/1 (disclose/hidden)
                disit = (explicit,implicit)[flag]
                flag = 0 # server default is disclose - send always list of hidden
            else:
                disit = (implicit,explicit)[flag]
                flag = 1 # server default is hidden - send always list of disclosed
        data.append(('contact:%s'%node_name,'contact:disclose','',(('flag',str(flag)),)))
        for key in disit:
            data.append(('contact:disclose','contact:%s'%key))

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
        if dct.has_key('auth_info'):
            # password required
            data.append(('contact:create','contact:authInfo'))
            data.append(('contact:authInfo','contact:pw',dct['auth_info'][0]))
        # --- BEGIN disclose ------
        if __has_key_dict__(dct,'disclose'):
            self.__append_disclose__(data, 'create', dct['disclose'][0])
        # --- END disclose ------
        if __has_key__(dct,'vat'): data.append(('contact:create','contact:vat', dct['vat'][0]))
        if __has_key_dict__(dct,'ssn'):
            ssn = dct['ssn'][0]
            data.append(('contact:create','contact:ssn', ssn['number'][0], (('type',ssn['type'][0]),)))
        if __has_key__(dct,'notify_email'): data.append(('contact:create','contact:notifyEmail', dct['notify_email'][0]))
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
        if dct.has_key('auth_info'):
            data.extend((
            ('domain:create','domain:authInfo'),
            ('domain:authInfo','domain:pw', dct['auth_info'][0])
        ))
        self.__enum_extensions__('create',data, params)
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
        if dct.has_key('auth_info'): 
            data.extend((
            ('nsset:create','nsset:authInfo'),
            ('nsset:authInfo','nsset:pw', dct['auth_info'][0])
        ))
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
            self.__parse_status_abrev__(dct,'add',self.update_status)
            self.__append_attr__(data, dct, 'add', 'contact:add', 'contact:status','s')
        if __has_key__(dct,'rem'):
            data.append(('contact:update', 'contact:rem'))
            self.__parse_status_abrev__(dct,'rem',self.update_status)
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
            if __has_key__(chg,'auth_info'):
                data.append(('contact:chg','contact:authInfo')) # required
                data.append(('contact:authInfo','contact:pw',chg['auth_info'][0])) # required
            # --- BEGIN disclose ------
            if __has_key_dict__(chg,'disclose'):
                self.__append_disclose__(data, 'chg', chg['disclose'][0])
            # --- END disclose ------
            if __has_key__(chg,'vat'): data.append(('contact:chg','contact:vat', chg['vat'][0]))
            if __has_key_dict__(chg,'ssn'):
                ssn = chg['ssn'][0]
                data.append(('contact:chg','contact:ssn', ssn['number'][0], (('type',ssn['type'][0]),)))
            if __has_key__(chg,'notify_email'): data.append(('contact:chg','contact:notifyEmail', chg['notify_email'][0]))
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
                self.__parse_status_abrev__(dct_key,'status',self.update_status)
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
                data.append(('domain:authInfo','domain:pw', chg['auth_info'][0]))
        self.__enum_extensions__('update',data, params,'chg')
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
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
            self.__parse_status_abrev__(dct_add,'status',self.update_status)
            self.__append_attr__(data, dct_add, 'status', 'nsset:add', 'nsset:status','s')

        if __has_key_dict__(dct,'rem'):
            data.append(('nsset:update','nsset:rem'))
            dct_rem = dct['rem'][0]
            self.__parse_status_abrev__(dct_rem,'status',self.update_status)
            self.__append_values__(data, dct_rem, 'name', 'nsset:rem', 'nsset:name')
            self.__append_values__(data, dct_rem, 'tech', 'nsset:rem', 'nsset:tech')
            self.__append_attr__(data, dct_rem, 'status', 'nsset:rem', 'nsset:status','s')

        if __has_key_dict__(dct,'chg'):
            data.append(('nsset:update','nsset:chg'))
            data.append(('nsset:chg','nsset:authInfo'))
            dct_chg = dct['chg'][0]
            if __has_key__(dct_chg, 'auth_info'): data.append(('nsset:authInfo','nsset:pw',dct_chg['auth_info'][0]))
            #if __has_key__(dct_chg, 'ext'): data.append(('nsset:authInfo','nsset:ext',dct_chg['ext'][0]))
        data.append(('command', 'clTRID', self._dct.get(TAG_clTRID,[params[0]])[0]))
        self.__assemble_cmd__(data)

    #===========================================

    def print_info_listmax(self,min,max):
        if self._verbose < 2: return # no display message in verbose mode 1
        msg = []
        if max > 1:
            msg.append(_TP('Value can be a list of max %d value.','Value can be a list of max %d values.',max)%max)
        elif max is UNBOUNDED:
            msg.append(_T('Value can be an unbouded list of values.'))
        if len(msg) and min:
            msg.append('%s %d.'%(_T('Minimum is'),min))
        if len(msg): session_base.print_unicode('(%s)'%(' '.join(msg)))
    
#-----------------------------------------------------
# Support of command line history
#-----------------------------------------------------
def save_history():
    'Save history of command line.'
    if readline_is_present:
        # Set maximum to 100 lines
        readline.set_history_length(100)
        try:
            readline.write_history_file(history_filename) # save history
        except IOError, msg:
            print 'IOError:',msg # some problem with history

def restore_history():
    'Restore history of command line.'
    if readline_is_present:
        try:
            readline.read_history_file(history_filename) # restore history (flush interactive params)
        except IOError, msg:
            pass # history doesn't exist, but no problem :-)

def remove_from_history(count=1):
    'Remove count last commands from history.'
    if readline_is_present:
        len = readline.get_current_history_length()
        if (len - count) >= 0:
            for pos in range(1,count+1):
                readline.remove_history_item(len-pos)
#-----------------------------------------------------

def get_history_length():
    return (0, readline.get_current_history_length())[readline_is_present]
            
def __has_key__(dct, key):
    'Check if key exists and if any value is set. (dct MUST be in format: dct[key] = [{...}, ...])'
    return dct.has_key(key) and len(dct[key])

def __has_key_dict__(dct, key):
    'Check if key exists and if any value is set. (dct MUST be in format: dct[key] = [{...}, ...])'
    return dct.has_key(key) and len(dct[key]) and len(dct[key][0])

def __scope_to_string__(scopes):
    'Assemble names into string. Scopes is in format: ((name, min, max, counter), ...)'
    tokens=[]
    for name,min,max,counter,label in scopes:
        if max is UNBOUNDED or max > 1:
            if max is UNBOUNDED:
                str_max = 'oo'
            else:
                str_max = str(max)
            tokens.append('%s[%d/%s]'%(label,counter+1,str_max))
        else:
            tokens.append(label)
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
    'Function append quotes if in text is any blank character and text is not in quotes.'
    if len(text) and text[0] not in '\'"' and re.search('\s',text):
        text = "'%s'"%escape(text)
    return text

def __build_command_example__(columns, dct_data, null_value):
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
                        text = __build_command_example__(children, dct_item, null_value)
                        if len(text): scopes.append('(%s)'%text)
                    text = ', '.join(scopes)
                else:
                    if len(dct_data[name]):
                        text = __build_command_example__(children, dct_data[name][0], null_value)
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
                text = (max is UNBOUNDED or max > 1) and '()' or null_value
                body.append(text)
    while len(body) and body[-1] in (null_value,'()'): body.pop()
    return ' '.join(body)

def remove_empty_keys(dct, null_value):
    'Remove empty keys. dct is in format {key: [str, {key: [str, str]} ,str]}'
    retd = {}
    for key in dct.keys():
        value = dct[key]
        if not (len(value)==1 and value[0]==null_value):
            scope = []
            for item in value:
                if type(item) is dict:
                    dcit = remove_empty_keys(item, null_value)
                    if len(dcit): scope.append(dcit)
                else:
                    if item != null_value: scope.append(item)
            if len(scope): retd[key] = scope
    return retd

def text_to_unicode(text):
    error=''
    if type(text) != unicode:
        try:
            text = unicode(text, encoding)
        except UnicodeDecodeError, msg:
            error='UnicodeDecodeError: %s'%msg
            text = unicode(repr(text), encoding)
    return text,error

def readline_build_token(key,example,required,min_max):
    'Returs token for readline prompt'
    if len(required):
        token = required[0][0]
    elif example:
        if re.search('\s',example): example = "'%s'"%example
        token = local8bit(example)
    else:
        token = key
    if min_max[1] is UNBOUNDED or min_max[1] > 1: token = '(%s)'%token
    if min_max[0]>1: token = '(%s)'%token
    return token

def local8bit(text):
    'Encode unicode to string in the local encoding.'
    if type(text) == unicode:
        try:
            text = text.encode(encoding)
        except UnicodeEncodeError, msg:
            text = repr(text)
    return text
