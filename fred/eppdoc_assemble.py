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
#
"""This module include class with functions what provides services for main client Manager.
Class supports interactive input of the command line. Builds help for particular command.
Create example of the command line from the interactive input.
It contains set of the assemble functions what create XML document. They are not call directly
but from Message class interface.
"""
import re, sys, os
import random
import time
import ConfigParser
import cmd_parser
import session_base

from translate import encoding
from eppdoc import Message as MessageBase, SCHEMA_PREFIX


UNBOUNDED = None
MAXLIST = 9
# ''contact_disclose'' must be same format as eppdoc_client.update_status.
DISCLOSES = ('voice','fax','email', 'vat', 'ident', 'notify_email')
contact_disclose = map(lambda n: (n,), DISCLOSES)
history_filename = os.path.join(os.path.expanduser('~'),'.fred_history') # compatibility s MS Win

TAG_clTRID = 'cltrid' # Definition for --key-name = clTRID value.

# Pattern (re.search(pattern)) for resolve ENUM domain type:
ENUM_DOMAIN_TYPE_PATT = '\.e164\.arpa$'




class Message(MessageBase):
    "Client EPP commands."

    def __init__(self, manager):
        MessageBase.__init__(self, manager)
        self.make_param_required_types()

    def make_param_required_types(self):
        self.param_reqired_type = (_T('optional'),_T('required'),_T('required only if part is set'))

    def __get_help_scope__(self, params, deep=1):
        'Support for get_help(). IN: params, deep'
        msg=[]
        indent = ' '*(self._indent_left*deep)
        for row in params:
            name,min_max,allowed,description,example,pattern,children = row
            min,max = min_max
            attrib = []
            required = sattrib = ''
            reqlen = 0
            if min > 0:
                msg8bit = _T('required')
                color = deep==1 and 'GREEN' or 'YELLOW'
                required = '${%s}${BOLD}(%s)${NORMAL}'%(color,msg8bit)
                reqlen = len(msg8bit.decode(encoding))+2 # add brackets
                if min > 1:
                    attrib.append(_TP('minimum %d item','minimum %d items',min)%min)
            sep = ''.ljust(self._indent_notes-len(indent)-len(name)-reqlen)
            param_line = '%s${BOLD}%s${NORMAL} %s%s'%(indent,name,required,sep)
            if max is UNBOUNDED:
                attrib.append(_T('unbounded list'))
            elif max > 1:
                attrib.append(_TP('list with max %d item.','list with max %d items.',max)%max)

            if description:
                if len(attrib): sattrib = ' (%s)'%', '.join(attrib)
                msg.append('%s %s%s'%(param_line,description,sattrib))

            # display allowed values
            if len(allowed):
                msg.append('%s  ${CYAN}(%s)${NORMAL}'%(' '*self._indent_notes, 
                    ','.join(self.__make_abrev_help__(allowed)))
                )
                
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
        
    def get_help(self, command_name, indent_notes=30, indent_left=2):
        "Returns help for selected command: (command_line, complete help)."
        self._indent_notes = indent_notes # indent column with descriptions
        self._indent_left = indent_left   # indent from left border
        command_line = []
        help=[]
        notice=''
        examples = ()
        # remove hyphen in the command
        m = re.match('(\S+)(.*)',command_name)
        if m: command_name = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if self._command_params.has_key(command_name):
            # command exists
            required,params,notice,examples = self._command_params[command_name]
            command_line = ['${BOLD}%s${NORMAL}'%command_name]
            if params:
                for pos in range(required):
                    command_line.append(params[pos][0])
                # Only hello has not cltrid optional parameter.
                if command_name != 'hello': command_line.append('[%s]'%_T('other_options'))
            help = self.__get_help_scope__(params)
        else:
            # unknown command
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

    def __check_required__(self, command_name, columns, dct_values, null_value, scopes=[]):
        'Check parsed values for required and allowed values.'
        miss_req = 0
        errors = []
        if len(scopes) and not len(dct_values): return errors, miss_req # if descendant is empty - not check
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
            message = [_T('Invalid parameter value.')]
            if self._verbose > 1:
                message.append('%s: "%s". (%s: "%s")\n%s: (%s) %s: (%s)'%(
                _T('Invalid parameter'), local8bit(' / '.join(scopes)),
                _T('Corrupted value'),str(dct_values),
                _T('Correct format is'), ', '.join(keys), 
                _T('For example'), ', '.join(vals), 
                ))
            return '\n'.join(message), miss_req
        is_poll = command_name == 'poll' # compile boolean for more faster comparation
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            scopes.append(name)
            scope_name = local8bit(' / '.join(scopes))
            if dct_values.has_key(name):
                if is_poll and scope_name == 'msg_id' and dct_values.get('op',[''])[0] == 'req':
                    # exception for command 'poll req' what does't need msg_id value
                    # errors.append(_T("poll req doesn't have msg_id value. Type %s for continue with next parameter.")%null_value)
                    errors.append(_T("poll req doesn't have msg_id value"))
                else:
                    if min_max[1] != UNBOUNDED and len(dct_values[name]) > min_max[1]:
                        if command_name == 'hello':
                            errors.append(_T('Command does not have any parameters.'))
                        else:
                            errors.append('%s: %s %d. %s'%(scope_name,
                                _T('list of values overflow. Maximum is'),
                                min_max[1],
                                local8bit(join_arrays2unicode(dct_values[name])))
                                )
                    if allowed:
                        # check allowed values
                        allowed_abrev=[]
                        map(allowed_abrev.extend, allowed)
                        for value in dct_values[name]:
                            if value not in allowed_abrev:
                                errors.append('%s: %s: (%s)'%(scope_name,_T('Value "%s" is not allowed. Valid is')%local8bit(value),', '.join(self.__make_abrev_help__(allowed))))
                    # walk throught descendants:
                    if children:
                        for dct in dct_values[name]:
                            err, mr = self.__check_required__(command_name, children, dct, null_value, scopes)
                            if err:
                                if type(err) in (list,tuple):
                                    errors.extend(err)
                                else:
                                    errors.append(err)
                            miss_req += mr
            else:
                if is_poll and scope_name == 'msg_id' and dct_values.get('op',[''])[0] == 'req':
                    pass # exception for command 'poll req' what does't need msg_id value
                elif min_max[0] > 0:
                    errors.append('%s %s'%(scope_name,_T('missing')))
                    miss_req += 1
            scopes.pop()
        return errors, miss_req

    def __ineractive_input_one_param__(self, name, min_max, allowed, example, null_value, prompt):
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
                    session_base.print_unicode('\n${BOLD}${RED}%s${NORMAL}'%_T("Can't finish input, required values must be set. Press Ctrl+C to abort."))
                    param = null_value
                else:
                    stop = 1 # Finish
                    break
            except KeyboardInterrupt:
                # Ctrl+C - Abort (Cancel)
                session_base.print_unicode('\n${BOLD}%s${NORMAL}'%_T('Interactive input aborted.'))
                stop = 2 # Abort (Cancel)
                break
            # autofill required missing values
            if autofill > 2 and param == '':
                session_base.print_unicode('\n${BOLD}${RED}%s${NORMAL}'%_T('Interactive input aborted.'))
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
            message = []
            if len(allowed):
                message.append('${WHITE}%s:${NORMAL} (%s)'%(_T('Parameter MUST be a value from following list'),', '.join(self.__make_abrev_help__(allowed))))
            if len(example):
                message.append('${WHITE}%s:${NORMAL} %s'%(_T('Example'), local8bit(example)))
            if len(message): session_base.print_unicode(' '.join(message))
        current_pos = stop = 0

        # append allowed values (name, org, addr, voice, ...)
        prompt_allowed = '' # default empty
        if len(allowed):
            prompt_allowed = ' (%s)'%','.join([n[0] for n in allowed])
        
        while max is UNBOUNDED or current_pos < max:
            parents[-1][3] = current_pos # name, min, max, counter = current_pos
            if dct.has_key(name) and len(dct[name]) >= min: min = required_pos = 0 # all needed values has been set
            prompt = u'%s%s [%s]: '%(__scope_to_string__(parents), prompt_allowed, unicode(self.param_reqired_type[required_pos],encoding))
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
        is_poll = command_name == 'poll' # compile boolean for more faster comparation
        is_create_domain = command_name == 'create_domain'
        for row in columns:
            name,min_max,allowed,msg_help,example,pattern,children = row
            if is_poll and name == 'msg_id' and dct.get('op',[''])[0] == 'req':
                # exception on the 'poll req' type where msg_id is jumped
                continue
            min,max = min_max
            if is_create_domain and name == 'val_ex_date' and re.search(ENUM_DOMAIN_TYPE_PATT, dct.get('name',[''])[0], re.I):
                min = 1 # Parameter val_ex_date is required for ENUM domain type.
            utext,error = text_to_unicode(msg_help)
            parents.append([name,min,max,0,utext]) # name,min,max,counter
            # Mechanism for toggle section to required/optional:
            # When a value is required only in this section, then req=1 switchs to req=2
            # when a value with req=2 is put, then all others req values sets to req=1
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
        """Parse command line. Returns errors. Save parsed values to self._dct.
        Returns: 
            errors     list of errors
            example    string return command line after interactive mode
            stop       if user press stop/finish
        """
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
        match = re.match('check_(\w+)\s+(.+)',cmd)
        if match and len(match.group(2)) and match.group(2)[0] != '(':
            # hint for check_[object] commands, there must be a list
            cmd = 'check_%s (%s)'%(match.group(1),match.group(2))
        vals = self._command_params.get(command_name,None)
        if not vals:
            error.append("%s: '%s'"%(_T('Unknown command'),command_name))
            error.append('(%s: ${BOLD}help${NORMAL})'%(_T('For more type')))
            return error, example, stop
        if not vals[1]:
            # takes only command hello
            if interactive:
                error.append(_T('Command %s does not have any parameters, skipping interactive input mode.')%command_name)
            elif len(cmd.split(' ')) > 1:
                error.append(_T('Command %s does not have any parameters.')%local8bit(command_name))
            return error, example, stop # no parameters
        columns = [(command_name,(1,1),(),'','','',())]
        columns.extend(self._command_params[command_name][1])
        dct['command'] = [command_name]
        if interactive:
            dct[command_name] = [command_name]
            if command_name == 'hello':
                # only hello has not any parameter
                session_base.print_unicode('${BOLD}${YELLOW}%s${NORMAL}'%_T('Does not have any parameters, skipping interactive input mode.'))
            else:
                session_base.print_unicode('${BOLD}%s${NORMAL}'%_T('Interactive input mode started. Press Ctrl+C to abort or Ctrl+D to finish command.'))
                history_length = get_history_length(self.readline)
                user_typed_null, stop = self.__interactive_mode__(command_name, vals[1], dct, null_value)
                if stop: stop -= 1 # 0 - normal; 1 - Finish command => normal; 2 - Abort => break interact.m. but not whole application;
                if not stop: # user press ! or Ctrl+C or Ctrl+D
                    example = __build_command_example__(columns, dct, null_value)
                    # Note the interactive mode is closed.
                    try:
                        raw_input(session_base.colored_output.render('\n${BOLD}${YELLOW}%s${NORMAL}'%_T('Interactive input completed. [Press Enter]')))
                    except EOFError:
                        session_base.print_unicode(u'') # EOFError: Ctrl+D - Finish command
                    except KeyboardInterrupt:
                        stop = 1 # KeyboardInterrupt: Ctrl+C - Abort (Cancel)
                        example = ''
                        session_base.print_unicode('\n${BOLD}%s${NORMAL}'%_T('Command has been aborted.'))
                remove_from_history(self.readline, get_history_length(self.readline) - history_length)
            errors = []
        else:
            errors = cmd_parser.parse(dct, columns, cmd)
        if errors: error.extend(errors)
        dct = remove_empty_keys(dct, null_value) # remove empty for better recognition of missing values
        self.__fill_empy_from_config__(config, dct, columns) # fill missing values from config
        if not stop:
            # check list and allowed values if only 'stop' was not set
            errors, miss_req = self.__check_required__(command_name, columns, dct, null_value)
            if command_name == 'create_domain' and dct.has_key('name') and re.search(ENUM_DOMAIN_TYPE_PATT, dct['name'][0], re.I) and not dct.get('val_ex_date'):
                    # Exception for ENUM domain.
                    errors.append(_T('Parameter val_ex_date is required dor ENUM domain.'))
                    miss_req += 1
            if errors:
                if miss_req:
                    error.append(_TP('Missing required value.','Missing required values.',miss_req))
                error.extend(errors)
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
        'Support function for assemble_create_... functions.'
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


    def __append_cltrid__(self, data, default):
        "Append clTRID if it is not skipped"
        cltrid = self._dct.get(TAG_clTRID, [default])[0]
        if not self.manager.skip_element(cltrid):
            data.append(('command', 'clTRID', cltrid))


    def __asseble_command__(self, cols, key, params):
        """Internal fnc for assembly commands info, check. 
        cols=('check','contact','id' [,list])
        key = name of key pointed to vlaue in parameters dictionary
        params must have ('clTRID',('name',['name','name',]))
        """
        VERSION = self.schema_version[cols[1]]
        self._handle_ID = self._dct.has_key(key) and self._dct[key][0] or '' # keep object handle (ID)
        if len(cols) > 3:
            col1 = '%s:%s'%(cols[1],cols[3])
        else:
            col1 = '%s:%s'%(cols[1],cols[0])
        col2 = '%s:%s'%(cols[1],cols[2])
        data=[('epp', 'command'),
            ('command', cols[0]),
            (cols[0],col1,None,(
            ('xmlns:%s'%cols[1],'%s%s-%s'%(SCHEMA_PREFIX, cols[1], VERSION)),
            ('xsi:schemaLocation','%s%s-%s %s-%s.xsd'%(SCHEMA_PREFIX, cols[1], VERSION, cols[1], VERSION))
            ))
            ]
        if key:
            names = self._dct[key]
            if type(names) not in (list,tuple):
                names = (names,)
            for value in names:
                data.append((col1, col2, value))

        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def __asseble_extcommand__(self, cols, params, key=None, namespace='fred'):
        """Internal fnc for assembly extended commands - sendauthinfo
        cols=('sendAuthInfo','contact','id' [,list])
        key = name of key pointed to vlaue in parameters dictionary
        params must have ('clTRID',('name',['name','name',]))
        """
        self._handle_ID = self._dct.has_key(key) and self._dct[key][0] or '' # keep object handle (ID)
        NAMESPACE_VERSION = self.schema_version.get(namespace, self.schema_version['epp'])
        if len(cols) < 2:
            # for credit_info ------------------------------------------------
            data=[('epp', 'extension'),
            ('extension', '%s:extcommand'%namespace, None, (
                ('xmlns:%s'%namespace, '%s%s-%s'%(SCHEMA_PREFIX, namespace, NAMESPACE_VERSION)),
                ('xsi:schemaLocation','%s%s-%s %s-%s.xsd'%(SCHEMA_PREFIX, namespace, NAMESPACE_VERSION, namespace, NAMESPACE_VERSION)),
            )),
            ('%s:extcommand'%namespace, '%s:%s'%(namespace,cols[0]))
            ]
            if key:
                if type(key) not in (list,tuple): key = (key,)
                for key_name in key:
                    names = self._dct.get(key_name)
                    if names is None:
                        continue # jump over optional keys
                    nscol = '%s:%s'%(namespace, key_name)
                    if type(names) not in (list,tuple): names = (names,)
                    for value in names:
                        data.append(('%s:%s'%(namespace, cols[0]), nscol, value))
        else:
            # for auth_info ------------------------------------------------
            if len(cols) > 3:
                col1 = '%s:%s'%(cols[1],cols[3])
            else:
                col1 = '%s:%s'%(cols[1],cols[0])
            col2 = '%s:%s'%(cols[1],cols[2])
            VERSION = self.schema_version[cols[1]]
            data=[('epp', 'extension'),
                ('extension', '%s:extcommand'%namespace, None, (
                    ('xmlns:%s'%namespace, '%s%s-%s'%(SCHEMA_PREFIX, namespace, NAMESPACE_VERSION)),
                    ('xsi:schemaLocation','%s%s-%s %s-%s.xsd'%(SCHEMA_PREFIX, namespace, NAMESPACE_VERSION, namespace, NAMESPACE_VERSION)),
                )),
                ('%s:extcommand'%namespace, '%s:%s'%(namespace,cols[0])), 
                ('%s:%s'%(namespace,cols[0]),col1,None,(
                ('xmlns:%s'%cols[1],'%s%s-%s'%(SCHEMA_PREFIX, cols[1], VERSION)),
                ('xsi:schemaLocation','%s%s-%s %s-%s.xsd'%(SCHEMA_PREFIX, cols[1], VERSION, cols[1], VERSION))
                ))
                ]
            if key:
                if type(key) not in (list,tuple): key = (key,)
                for key_name in key:
                    names = self._dct.get(key_name)
                    if names is None:
                        continue # jump over optional keys
                    nscol = '%s:%s'%(cols[1],key_name)
                    if type(names) not in (list,tuple): names = (names,)
                    for value in names:
                        data.append((col1, nscol, value))
            # ------------------------------------------------
        cltrid = self._dct.get(TAG_clTRID, [params[0]])[0]
        if not self.manager.skip_element(cltrid):
            data.append(('%s:extcommand' % namespace, '%s:clTRID' % namespace, cltrid))
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
        if __has_key__(self._dct,'new_password'): cols.append(('login', 'newPW', self._dct['new_password'][0]))
        cols.extend([
            ('login', 'options'),
            ('options', 'version', params[1][0]), # The protocol version to be used for the command or ongoing server session.
            ('options', 'lang', params[1][3]),
            ('login', 'svcs'),
        ])
        if params[1][1]: # objURI
            ## <objURI>http://www.nic.cz/xml/epp/contact-1.0</objURI>
            ## <objURI>http://www.nic.cz/xml/epp/domain-1.0</objURI>
            ## <objURI>http://www.nic.cz/xml/epp/nsset-1.0</objURI>
            for uri in params[1][1]:
                cols.append(('svcs', 'objURI', uri))
        if params[1][2]: # extURI
            ## <extURI>http://www.nic.cz/xml/epp/enumval-1.0</extURI>
            cols.append(('svcs', 'svcExtension'))
            for uri in params[1][2]:
                cols.append(('svcExtension', 'extURI', uri))
        self.__append_cltrid__(cols, params[0])
        self.__assemble_cmd__(cols)

    def assemble_logout(self, *params):
        "Assemble EPP command logount. *params: ('clTRID')"
        dom = [
            ('epp', 'command'),
            ('command', 'logout'),
        ]
        cltrid = self._dct.get(TAG_clTRID, [params[0]])[0]
        if not self.manager.skip_element(cltrid):
            dom.append(('command', 'clTRID', cltrid))
        self.__assemble_cmd__(dom)

    #-------------------------------------------
    # Questions (query)
    #-------------------------------------------
    def assemble_check_contact(self, *params):
        self.__asseble_command__(('check','contact','id'), 'name', params)
        
    def assemble_check_domain(self, *params):
        self.__asseble_command__(('check','domain','name'), 'name', params)
        
    def assemble_check_nsset(self, *params):
        self.__asseble_command__(('check','nsset','id'), 'name', params)

    def assemble_check_keyset(self, *params):
        self.__asseble_command__(('check','keyset','id'), 'name', params)
        
    def assemble_info_contact(self, *params):
        self.__asseble_command__(('info','contact','id'), 'name', params)

    def assemble_info_domain(self, *params):
        self.__asseble_command__(('info','domain','name'), 'name', params)

    def assemble_info_nsset(self, *params):
        self.__asseble_command__(('info','nsset','id'), 'name', params)

    def assemble_info_keyset(self, *params):
        self.__asseble_command__(('info','keyset','id'), 'name', params)
        
    def assemble_list_contacts(self, *params):
        self.getresults_loop = 1 # run messages loop
        self.__asseble_extcommand__(('listContacts', ), params)
        
    def assemble_list_domains(self, *params):
        self.getresults_loop = 1 # run messages loop
        self.__asseble_extcommand__(('listDomains', ), params)
        
    def assemble_list_nssets(self, *params):
        self.getresults_loop = 1 # run messages loop
        self.__asseble_extcommand__(('listNssets', ), params)

    def assemble_list_keysets(self, *params):
        self.getresults_loop = 1 # run messages loop
        self.__asseble_extcommand__(('listKeysets', ), params)
    

    def assemble_poll(self, *params):
        op = self._dct.get('op',['req'])[0]
        msg_id = self._dct.get('msg_id',[None])[0]
        attr = [('op',op)]
        if msg_id:
            if type(msg_id) not in (unicode, str):
                msg_id = str(msg_id) # translate type int
            attr.append(('msgID',msg_id))
        dom = [
            ('epp', 'command'),
            ('command', 'poll', '', attr),
        ]
        cltrid = self._dct.get(TAG_clTRID, [params[0]])[0]
        if not self.manager.skip_element(cltrid):
            dom.append(('command', 'clTRID', cltrid))
        self.__assemble_cmd__(dom)

    #-------------------------------------------
    # Edit (query)
    #-------------------------------------------
    def assemble_delete_contact(self, *params):
        self.__asseble_command__(('delete','contact','id'), 'id', params)

    def assemble_delete_domain(self, *params):
        self.__asseble_command__(('delete','domain','name'), 'name', params)

    def assemble_delete_nsset(self, *params):
        self.__asseble_command__(('delete','nsset','id'), 'id', params)

    def assemble_delete_keyset(self, *params):
        self.__asseble_command__(('delete','keyset','id'), 'id', params)


    def __assemble_transfer__(self, names, params):
        "Assemble transfer XML EPP command."
        VERSION = self.schema_version[names[0]]
        self._handle_ID = self._dct['name'][0] # keep object handle (ID)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], VERSION)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns, names[0], VERSION)))
        dom = [
            ('epp', 'command'),
            ('command', 'transfer', '', (('op','request'),)), # self._dct['op'][0]
            ('transfer', '%s:transfer' % names[0], '', attr),
            ('%s:transfer' % names[0], '%s:%s' % names, self._dct['name'][0]),
            ('%s:transfer' % names[0], '%s:authInfo' % names[0], self._dct['auth_info'][0]),
        ]
        cltrid = self._dct.get(TAG_clTRID, [params[0]])[0]
        if not self.manager.skip_element(cltrid):
            dom.append(('command', 'clTRID', cltrid))
        self.__assemble_cmd__(dom)

    def assemble_transfer_contact(self, *params):
        self.__assemble_transfer__(('contact','id'),params)

    def assemble_transfer_domain(self, *params):
        self.__assemble_transfer__(('domain','name'),params)

    def assemble_transfer_nsset(self, *params):
        self.__assemble_transfer__(('nsset','id'),params)

    def assemble_transfer_keyset(self, *params):
        self.__assemble_transfer__(('keyset','id'),params)
        
    #-------------------------------------------
    # Executives
    #-------------------------------------------
    def __enum_extensions__(self, type, data, params, tag_name=''):
        'Enum extension for (create|renew)-domain commands.'
        if not (__has_key__(self._dct, 'val_ex_date') or
                __has_key__(self._dct, 'publish')):
                return
        names = ('enumval',type)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['enum'])
        attr = (('xmlns:%s'%names[0],ns),
            ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['enum'])))
        data.extend((
            ('command','extension'),
            ('extension','%s:%s'%names,'',attr)
        ))
        if tag_name:
            data.append(('%s:%s'%names,'%s:%s'%(names[0], tag_name))) # mezitag
            names = ('enumval',tag_name)
        if __has_key__(self._dct, 'val_ex_date'):
            data.append(('%s:%s'%names,'%s:valExDate'%names[0], self._dct['val_ex_date'][0]))
        if __has_key__(self._dct, 'publish'):
            value = self._dct['publish'][0] == 'y' and 'true' or 'false'
            data.append(('%s:%s'%names,'%s:publish'%names[0], value))


    def __append_disclose__(self, data, node_name, disclose):
        'Create disclose nodes'
        explicit = [] # typed by user
        implicit = [] # others not mentioned
        flag = {'n':0,'y':1}.get(disclose.get('flag',['n'])[0], 'n')
        disit = disclose.get('data',[])
        if len(disit):
            for key in DISCLOSES: ## [n[0] for n in contact_disclose]:
                if key in disit:
                    explicit.append(make_camell(key))
                else:
                    implicit.append(make_camell(key))
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
        self._handle_ID = dct['contact_id'][0] # keep object handle (ID)
        names = ('contact',)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['contact'])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['contact'])))
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
            data.append(('contact:create','contact:authInfo',dct['auth_info'][0]))
        # --- BEGIN disclose ------
        if __has_key_dict__(dct,'disclose'):
            self.__append_disclose__(data, 'create', dct['disclose'][0])
        # --- END disclose ------
        if __has_key__(dct,'vat'): data.append(('contact:create','contact:vat', dct['vat'][0]))
        if __has_key_dict__(dct,'ident'):
            ident = dct['ident'][0]
            data.append(('contact:create','contact:ident', ident['number'][0], (('type',ident['type'][0]),)))
        if __has_key__(dct,'notify_email'): data.append(('contact:create','contact:notifyEmail', dct['notify_email'][0]))
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def assemble_create_domain(self, *params):
        "Assemble XML EPP command."
        dct = self._dct
        self._handle_ID = dct['name'][0] # keep object handle (ID)
        names = ('domain',)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['domain'])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['domain'])))
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
        if __has_key__(dct,'keyset'): data.append(('domain:create','domain:keyset',dct['keyset'][0]))
        if __has_key__(dct,'registrant'): data.append(('domain:create','domain:registrant',dct['registrant'][0]))
        self.__append_values__(data, dct, 'admin', 'domain:create', 'domain:admin')
        if dct.has_key('auth_info'):
            data.append(('domain:create','domain:authInfo', dct['auth_info'][0]))
        self.__enum_extensions__('create',data, params)
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def __append_nsset__(self, tag_name, data, dct_ns):
        "ns:  {'name': ['ns3.domain.net'], 'addr': ['127.3.0.1', '127.3.0.2']}"
        if not __has_key__(dct_ns,'name'): return
        data.append(('nsset:%s'%tag_name, 'nsset:ns'))
        data.append(('nsset:ns', 'nsset:name',dct_ns['name'][0]))
        if dct_ns.has_key('addr'):
            for addr in dct_ns['addr']:
                data.append(('nsset:ns', 'nsset:addr',addr))

    def __append_schema_location__(self, tag_name, data, element, prefix, change_namespace):
        "Append namespace"
        if change_namespace:
            namespace = change_namespace
            ns = (
                ('xmlns:%s'%namespace, '%s%s-%s'%(
                        SCHEMA_PREFIX, namespace, self.schema_version[namespace])),
                ('xsi:schemaLocation','%s%s-%s %s-%s.xsd'%(
                        SCHEMA_PREFIX, namespace, self.schema_version[namespace], \
                        namespace, self.schema_version[namespace])),
            )
            data.append(('%s:%s'%(prefix, tag_name), element%prefix, None, ns))
            prefix = namespace
        else:
            data.append(('%s:%s'%(prefix, tag_name), element%prefix))

    def __append_anyset_fromfile__(self, tag_name, data, filename, prefix, name, parse_file, change_namespace=None):
        "Load anyset from filename"
        element = '%s:' + name
        parent_prefix = prefix
        self.__append_schema_location__(tag_name, data, element, prefix, change_namespace)
        dct = {}
        for key in parse_file(dct, filename):
            data.append((element%parent_prefix, '%s:%s'%(prefix, make_camell(key)), dct[key]))
        
    def __append_keyset_fromfile__(self, tag_name, data, filename, prefix, change_namespace=None):
        "Load ds from filename"
        self.__append_anyset_fromfile__(tag_name, data, filename, prefix, 'ds', self.parse_ds_file, change_namespace)

    def __append_dnskey__(self, tag_name, data, dct_ks, prefix, change_namespace=None):
        "Join ds elements for keyset"
        element = '%s:dnskey'
        parent_prefix = prefix
        self.__append_schema_location__(tag_name, data, element, prefix, change_namespace)
        for key in ('flags', 'protocol', 'alg', 'pub_key'):
            data.append((element%parent_prefix, '%s:%s'%(prefix, make_camell(key)), dct_ks[key][0]))

    def __append_dnskey_fromfile__(self, tag_name, data, filename, prefix, change_namespace=None):
        "Load dnskey from filename"
        self.__append_anyset_fromfile__(tag_name, data, filename, prefix, 'dnskey', self.parse_dnskey_file, change_namespace)


    def load_filename(self, filename):
        "Load file"
        # create absolute path
        if filename[0] != '/':
            filename = os.path.join(os.getcwd(), filename)
        # load certificate
        try:
            body = open(filename, 'rb').read()
        except IOError, e:
            self.errors.append((0, 'file', 'IOError: %s'%e))
            body =  ''
        return body.strip()
    
    def parse_dnskey_file(self, dct, filename):
        "Parse certificate file"
        # data format:
        # cz. IN DNSKEY 256 3 5 BASE64CODE BASE64CODE BASE64CODE...
        parts = re.split('\s+', self.load_filename(filename))
        if len(parts) < 7:
            self.errors.append((0, 'dnskey file', 'Invalid DNSKEY file format.'))
            return [] # invalid format
        if parts[1] != 'IN' and parts[2] != 'DNSKEY':
            self.errors.append((0, 'dnskey file', 'Invalid DNSKEY data format.'))
            return []
        # fill dict by data from file
        dct['flags'] = parts[3]
        dct['protocol'] = parts[4]
        dct['alg'] = parts[5]
        dct['pub_key'] = '\n'.join(parts[6:])
        return ('flags', 'protocol', 'alg', 'pub_key')

    def parse_ds_file(self, dct, filename):
        "Parse certificate file"
        # data format:
        # cz.	3600	IN	DS	20487 5 1 1ff4b01e82cd41f2edb65b925d3f4b2ab68a4467
        parts = re.split('\s+', self.load_filename(filename))
        if len(parts) != 8:
            self.errors.append((0, 'ds file', 'Invalid DS file format.'))
            return [] # invalid format
        if parts[2] != 'IN' and parts[3] != 'DS':
            self.errors.append((0, 'ds file', 'Invalid DS data format.'))
            return []
        # fill dict by data from file
        dct['key_tag'] = parts[4]
        dct['alg'] = parts[5]
        dct['digest_type'] = parts[6]
        dct['digest'] = parts[7]
        dct['max_sig_life'] = parts[1]
        return ('key_tag', 'alg', 'digest_type', 'digest', 'max_sig_life')
        
    
    def __assemble_create_anyset__(self, prefix, *params):
        "Assemble XML EPP command."
        dct = self._dct
        self._handle_ID = dct['id'][0] # keep object handle (ID)
        names = (prefix,)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version[prefix])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version[prefix])))
        data = [
            ('epp', 'command'),
            ('command', 'create'),
            ('create', '%s:create'%prefix, '', attr),
            ('%s:create'%prefix, '%s:id'%prefix, dct['id'][0])]
        # for nsset only
        nsset_type = False
        if __has_key__(dct,'dns'):
            nsset_type = True
            for dns in dct['dns']:
                self.__append_nsset__('create', data, dns)
        
        count_dnskey = 0
        if __has_key__(dct,'dnskey'):
            for ds in dct['dnskey']:
                self.__append_dnskey__('create', data, ds, prefix)
                count_dnskey += 1
        if __has_key__(dct,'dnskeyref'):
            for ds in dct['dnskeyref']:
                self.__append_dnskey_fromfile__('create', data, ds, prefix)
                count_dnskey += 1
        
        if not nsset_type:
            # check list limits only for keyset
            if count_dnskey > MAXLIST:
                self.errors.append((0, 'dnskey', _T('Limit of list is exceeded. The maximum is %d.') % MAXLIST))
        
        # for nsset only
        if __has_key__(dct,'tech'):
            self.__append_values__(data, dct, 'tech', '%s:create'%prefix, '%s:tech'%prefix)
        if dct.has_key('auth_info'): 
            data.append(('%s:create'%prefix,'%s:authInfo'%prefix, dct['auth_info'][0]))

        # for nsset only
        if dct.has_key('reportlevel'):
            data.append(('%s:create'%prefix,'%s:reportlevel'%prefix, dct['reportlevel'][0]))
        
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def assemble_create_nsset(self, *params):
        self.__assemble_create_anyset__('nsset', *params)

    def assemble_create_keyset(self, *params):
        self.__assemble_create_anyset__('keyset', *params)

        
    def assemble_renew_domain(self, *params):
        """Assemble XML EPP command. 
        """
        dct = self._dct
        self._handle_ID = dct['name'][0] # keep object handle (ID)
        names = ('domain',)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['domain'])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['domain'])))
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
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def assemble_update_contact(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        self._handle_ID = dct['contact_id'][0] # keep object handle (ID)
        names = ('contact',)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['contact'])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['contact'])))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'contact:update', '', attr),
            ('contact:update','contact:id', dct['contact_id'][0]),
            ]
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
                data.append(('contact:chg','contact:authInfo',chg['auth_info'][0]))
            # --- BEGIN disclose ------
            if __has_key_dict__(chg,'disclose'):
                self.__append_disclose__(data, 'chg', chg['disclose'][0])
            # --- END disclose ------
            if __has_key__(chg,'vat'): data.append(('contact:chg','contact:vat', chg['vat'][0]))
            if __has_key_dict__(chg,'ident'):
                ident = chg['ident'][0] # number is required
                # type is optional
                type = ident.get('type', [None])[0]
                type_data = type and (('type', type),) or None
                data.append(('contact:chg','contact:ident', ident['number'][0], type_data))
            if __has_key__(chg,'notify_email'): data.append(('contact:chg','contact:notifyEmail', chg['notify_email'][0]))
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def assemble_update_domain(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        self._handle_ID = dct['name'][0] # keep object handle (ID)
        names = ('domain',)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version['domain'])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0], self.schema_version['domain'])))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'domain:update', '', attr),
            ('domain:update','domain:name', dct['name'][0]),
            ]
        tag_rem_is_set = 0 # put REM(OVE) tag only one time
        for key in ('add','rem'):
            element_name = '%s_admin'%key
            if __has_key_dict__(dct, element_name):
                data.append(('domain:update', 'domain:%s'%key))
                self.__append_values__(data, dct, element_name, 'domain:%s'%key, 'domain:admin')
                if key == 'rem':
                    tag_rem_is_set = 1 # tag REM has been set
        # append temporary contacts
        for key in ('rem', ):
            element_name = '%s_tempc'%key
            if __has_key_dict__(dct, element_name):
                if not tag_rem_is_set:
                    data.append(('domain:update', 'domain:%s'%key))
                self.__append_values__(data, dct, element_name, 'domain:%s'%key, 'domain:tempcontact')
                
        if __has_key_dict__(dct,'chg'):
            chg = dct['chg'][0]
            data.append(('domain:update', 'domain:chg'))
            if __has_key__(chg,'nsset'): data.append(('domain:chg','domain:nsset', chg['nsset'][0]))
            if __has_key__(chg,'keyset'): data.append(('domain:chg','domain:keyset', chg['keyset'][0]))
            if __has_key__(chg,'registrant'): data.append(('domain:chg','domain:registrant', chg['registrant'][0]))
            if __has_key_dict__(chg,'auth_info'):
                data.append(('domain:chg','domain:authInfo', chg['auth_info'][0]))
        self.__enum_extensions__('update',data, params,'chg')
        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def __assemble_update_set__(self, prefix, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        """
        dct = self._dct
        self._handle_ID = dct['id'][0] # keep object handle (ID)
        names = (prefix,)
        ns = '%s%s-%s'%(SCHEMA_PREFIX, names[0], self.schema_version[prefix])
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns, names[0], self.schema_version[prefix])))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', '%s:update'%prefix, '', attr),
            ('%s:update'%prefix,'%s:id'%prefix, dct['id'][0]),
            ]
        if __has_key_dict__(dct,'add'):
            data.append(('%s:update'%prefix,'%s:add'%prefix))
            dct_add = dct['add'][0]
            
            # for nsset only
            if __has_key_dict__(dct_add,'dns'):
                for dct_dns in dct_add['dns']:
                    if not __has_key__(dct_dns, 'name'): continue
                    data.append(('%s:add'%prefix,'%s:ns'%prefix))
                    data.append(('%s:ns'%prefix,'%s:name'%prefix,dct_dns['name'][0]))
                    self.__append_values__(data, dct_dns, 'addr', '%s:ns'%prefix, '%s:addr'%prefix)
            
            # two list of dnskeys will be join together
            count_dnskey = 0
            if __has_key_dict__(dct_add, 'dnskey'):
                for ds in dct_add['dnskey']:
                    self.__append_dnskey__('add', data, ds, prefix)
                    count_dnskey += 1
            if __has_key_dict__(dct_add, 'dnskeyref'):
                for ds in dct_add['dnskeyref']:
                    self.__append_dnskey_fromfile__('add', data, ds, prefix)
                    count_dnskey += 1
            
            # check list limits
            if count_dnskey > MAXLIST:
                self.errors.append((0, 'dnskey', _T('Limit of list is exceeded. The maximum is %d.') % MAXLIST))
            
            self.__append_values__(data, dct_add, 'tech', '%s:add'%prefix, '%s:tech'%prefix)

        if __has_key_dict__(dct,'rem'):
            data.append(('%s:update'%prefix,'%s:rem'%prefix))
            dct_rem = dct['rem'][0]
            
            # two list of dnskeys will be join together
            count_dnskey = 0
            if __has_key_dict__(dct_rem, 'dnskey'):
                for ds in dct_rem['dnskey']:
                    self.__append_dnskey__('rem', data, ds, prefix)
                    count_dnskey += 1
            if __has_key_dict__(dct_rem, 'dnskeyref'):
                for ds in dct_rem['dnskeyref']:
                    self.__append_dnskey_fromfile__('rem', data, ds, prefix)
                    count_dnskey += 1
            
            # check list limits
            if count_dnskey > MAXLIST:
                self.errors.append((0, 'dnskey', _T('Limit of list is exceeded. The maximum is %d.') % MAXLIST))
            
            # for nsset only
            if __has_key_dict__(dct_rem, 'name'):
                self.__append_values__(data, dct_rem, 'name', '%s:rem'%prefix, '%s:name'%prefix)
            self.__append_values__(data, dct_rem, 'tech', '%s:rem'%prefix, '%s:tech'%prefix)

        if __has_key_dict__(dct,'auth_info') or __has_key_dict__(dct,'reportlevel'):
            data.append(('%s:update'%prefix,'%s:chg'%prefix))
            if dct.has_key('auth_info'): 
                data.append(('%s:chg'%prefix,'%s:authInfo'%prefix, dct['auth_info'][0]))
            if dct.has_key('reportlevel'): 
                data.append(('%s:chg'%prefix,'%s:reportlevel'%prefix, dct['reportlevel'][0]))

        self.__append_cltrid__(data, params[0])
        self.__assemble_cmd__(data)

    def assemble_update_nsset(self, *params):
        self.__assemble_update_set__('nsset', *params)

    def assemble_update_keyset(self, *params):
        self.__assemble_update_set__('keyset', *params)
        
    def assemble_sendauthinfo_contact(self, *params):
        self.__asseble_extcommand__(('sendAuthInfo','contact','id'), params, 'id')

    def assemble_sendauthinfo_domain(self, *params):
        self.__asseble_extcommand__(('sendAuthInfo','domain','name'), params, 'name')

    def assemble_sendauthinfo_nsset(self, *params):
        self.__asseble_extcommand__(('sendAuthInfo','nsset','id'), params, 'id')

    def assemble_sendauthinfo_keyset(self, *params):
        self.__asseble_extcommand__(('sendAuthInfo','keyset','id'), params, 'id')
        
    def assemble_credit_info(self, *params):
        self.__asseble_extcommand__(('creditInfo',), params)

    def assemble_technical_test(self, *params):
        'Create technical_test document'
        self.__asseble_extcommand__(('test','nsset','id'), params, ('id', 'level', 'name'))

    
    def assemble_prep_contacts(self, *params):
        'Create prepare_contacts document'
        self.__asseble_extcommand__(('listContacts', ), params)
        
    def assemble_prep_domains(self, *params):
        'Create prepare_domains document'
        self.__asseble_extcommand__(('listDomains', ), params)
        
    def assemble_prep_nssets(self, *params):
        'Create prepare_nssets document'
        self.__asseble_extcommand__(('listNssets', ), params)
        
    def assemble_prep_keysets(self, *params):
        'Create prepare_keysets document'
        self.__asseble_extcommand__(('listKeysets', ), params)



    def assemble_get_results(self, *params):
        'Create count_list_nssets document'
        self.__asseble_extcommand__(('getResults', ), params)

        
    def assemble_prep_domains_by_nsset(self, *params):
        'Create prep_domains_by_nsset document'
        self.__asseble_extcommand__(('domainsByNsset', ), params, 'id')

    def assemble_prep_domains_by_keyset(self, *params):
        'Create prep_domains_by_keyset document'
        self.__asseble_extcommand__(('domainsByKeyset', ), params, 'id')

    def assemble_prep_domains_by_contact(self, *params):
        'Create prep_domains_by_contact document'
        self.__asseble_extcommand__(('domainsByContact', ), params, 'id')
    
    def assemble_prep_nssets_by_contact(self, *params):
        'Create prep_nssets_by_contact document'
        self.__asseble_extcommand__(('nssetsByContact', ), params, 'id')

    def assemble_prep_keysets_by_contact(self, *params):
        'Create prep_keysets_by_contact document'
        self.__asseble_extcommand__(('keysetsByContact', ), params, 'id')

    def assemble_prep_nssets_by_ns(self, *params):
        'Create prep_nssets_by_ns document'
        self.__asseble_extcommand__(('nssetsByNs', ), params, 'name')
    

    #===========================================

    def fetch_from_info(self, command_type, info_type, answer, null_value):
        'Create command line from INFO data.'
        epp_command = '%s_%s'%(command_type, info_type)
        self._dct = {'command': [epp_command], epp_command: [epp_command] }
        dct = answer['data']
        for name, verbose, note in self.sort_by_names[answer['command']][1]:
            key =  '%s:%s'%(info_type, name)
            value = dct.get(key,None)
            if value is not None:
                if type(value) not in (list, tuple): value = [value]
                # replace all occurences like 'authInfo' from 'authInfo' to 'auth_info'
                self._dct[re.sub('([A-Z])','_\\1',name, re.I).lower()] = value
        self._dct = getattr(self, '__ffi_%s__'%epp_command, lambda d:d)(self._dct)
        return self.get_command_line(null_value)

    def __ffi_create_domain__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        # from exDate value count years
        if dct.has_key('ex_date'):
            try:
                year = int(dct['ex_date'][0][:4])
            except (ValueError, TypeError):
                pass
            else:
                period_num = year - time.localtime()[0]
                if period_num > 0:
                    dct['period'] = [{'unit':['y'], 'num': [str(period_num)]}]
        return dct

    def __ffi_update_domain__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        chg ={}
        for key in ('nsset','registrant','auth_info'):
            if dct.has_key(key): chg[key] = dct[key]
        if len(chg): dct['chg'] = [chg]
        if dct.has_key('admin'): dct['rem_admin'] = dct['admin']
        if dct.has_key('tempcontact'): dct['rem_tempc'] = dct['tempcontact']
        return dct

    def __ffi_create_nsset__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        dns = []
        for name, addr in dct.get('ns',[]):
            dns.append({'name':[name], 'addr':addr})
        if len(dns): dct['dns'] = dns
        return dct

    def __ffi_update_nsset__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        dct = self.__ffi_create_nsset__(dct)
        rem = {}
        if dct.has_key('dns'):
            names = []
            for dns in dct['dns']:
                names.append(dns['name'][0])
            rem['name']  = names
        if dct.has_key('tech'): rem['tech'] = dct['tech']
        if len(rem): dct['rem'] = [rem]
        return dct

    def __ffi_update_contact__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        dct = self.__ffi_create_contact__(dct)
        chg = {}
        for key in ('voice','fax','email','vat','auth_info','notify_email'):
            if dct.has_key(key): chg[key] = dct[key]
        if dct.has_key('ident'): chg['ident'] = dct['ident']
        if dct.has_key('disclose'): chg['disclose'] = dct['disclose']
        postal_info = {}
        for key in ('name','org'):
            if dct.has_key(key): postal_info[key] = dct[key]
        addr = {}
        for key in ('city','cc','street','sp','pc'):
            if dct.has_key(key): addr[key] = dct[key]
        if len(addr): postal_info['addr'] = [addr]
        if len(postal_info): chg['postal_info'] = [postal_info]
        if len(chg): dct['chg'] = [chg]
        return dct

    def __ffi_create_contact__(self, dct):
        """This is support of the fetch_from_info(). 
        Individual modification of the contact."""
        if dct.has_key('disclose'):
            flag = self.server_disclose_policy and 'y' or 'n'
            dct['disclose'] = [{'flag': [flag], 'data':dct['disclose']}]
        if dct.has_key('ident'):
            dct['ident'] = [{'number':dct['ident']}]
        if dct.has_key('ident.type'):
            ident_type = dct.pop('ident.type')
            dct['ident'][0]['type'] = ident_type
        dct['contact_id'] = dct.pop('id')
        return dct

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

    def get_object_handle(self):
        'Returns object handle ID.'
        return self._handle_ID

        
#-----------------------------------------------------
# Support of command line history
#-----------------------------------------------------
def save_history(readline):
    'Save history of command line.'
    if readline:
        # Set maximum to 100 lines
        readline.set_history_length(100)
        try:
            readline.write_history_file(history_filename) # save history
        except IOError, msg:
            print 'History IOError:',msg # some problem with history

def restore_history(readline):
    'Restore history of command line.'
    if readline:
        try:
            readline.read_history_file(history_filename) # restore history (flush interactive params)
        except IOError, msg:
            pass # history doesn't exist, but no problem :-)

def remove_from_history(readline, count=1):
    'Remove count last commands from history.'
    if readline:
        len = readline.get_current_history_length()
        if (len - count) >= 0:
            for pos in range(1,count+1):
                readline.remove_history_item(len-pos)
#-----------------------------------------------------

def get_history_length(readline):
    return readline and readline.get_current_history_length() or 0
            
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
    return ' / '.join(tokens)

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

def join_arrays2unicode(data, scope=[]):
    'Join all arrays to the string.'
    out = u''
    if type(data) in (tuple, list):
        tmp = []
        for value in data:
            tmp.append(join_arrays2unicode(value, scope))
        if len(tmp):
            if len(tmp) == 1:
                out = tmp[0]
            else:
                out = u'(%s)'%u', '.join(tmp)
    elif type(data) == dict:
        tmp = []
        for key,value in data.items():
            scope.append(key)
            if len(filter(lambda n:type(n) is dict, value)):
                # if any of the children is dict type
                # the key name will be shown with children key together (scope)
                tmp.append(join_arrays2unicode(value, scope))
            else:
                tmp.append(u'--%s = %s'%(u'.'.join(scope), join_arrays2unicode(value, scope)))
            scope.pop()
        if len(tmp):
            out = u' '.join(tmp)
    else:
        out = data
    return out

def make_camell(text):
    'Make camell name: any_name -> anyName'
    for s in re.findall('_.', text):
        text = re.sub(s, s[1].upper(), text)
    return text

