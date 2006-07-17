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
import re, sys
import ConfigParser
import eppdoc
import cmd_parser
import session_base
from translate import _T

UNBOUNDED = None

class Message(eppdoc.Message):
    "Client EPP commands."

    def __get_help_scope__(self, params, deep=1):
        'Support for get_help(). IN: params, deep'
        msg=[]
        indent = '    '*deep
        for row in params:
            name,min_max,allowed,help,children = row
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
                max_size = _T('list with max %d items.')%max
            else:
                max_size = ''
            if max_size:
                text = '%s%s%s'%(text,('\t','\t\t')[len(text)<42],max_size)
            if len(allowed):
                txt = ','.join(allowed)
                if len(txt)>37: txt = txt[:37]+'...' # shorter too long text
                text = '%s ${WHITE}%s: ${CYAN}(%s)${NORMAL}'%(text,_T('accept only values'),txt)
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
            command_line = ['${BOLD}%s${NORMAL}'%command_name.replace('_','-')]
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
        section = 'epp_%s'%columns[0][0]
        if not config or not config.has_section(section): return errors
        for key,value in config.items(section):
            # go throught dict and create keys if missing:
            cmd_parser.insert_on_key(errors, dct, columns, key, value, 1)
        return errors
        
        
    def __check_required__(self, columns, dct_values, scopes=[]):
        'Check parsed values for required and allowed values.'
        errors = []
        if len(scopes) and not len(dct_values): return errors # if descendant is empty - not check
        if type(dct_values) != dict: return ('%s (%s)'%(_T('Invalid input format.'),[c[0] for c in columns]),)
        for row in columns:
            name,min_max,allowed,msg_help,children = row
            scopes.append(name)
            scope_name = '.'.join(scopes)
            if dct_values.has_key(name):
                if min_max[1] != UNBOUNDED and len(dct_values[name]) > min_max[1]:
                    errors.append('%s: %s %d. %s'%(scope_name,_T('list of values overflow. Maximum is'),min_max[1],str(dct_values[name])))
                if allowed:
                    # check allowed values
                    for value in dct_values[name]:
                        if value not in allowed:
                            errors.append('%s: %s %s'%(scope_name,_T('Value "%s" is not allowed here. Valid:')%value,str(allowed)))
                # walk throught descendants:
                if children:
                    for dct in dct_values[name]:
                        err = self.__check_required__(children, dct, scopes)
                        if err: errors.extend(err)
            else:
                if min_max[0] > 0: errors.append('%s %s.'%(scope_name,_T('missing')))
            scopes.pop()
        return errors

    def __interactive_params__(self, command_name, columns, dct, parents=[]):
        'Runs LOOP of interactive input of the command params.'
        errors = []
        param = ''
        is_child = len(parents)>0
        min = 0
        for row in columns:
            if len(param) and param[0] == '!': break
            if is_child and param == '' and min:
                break
            name,min_max,allowed,msg_help,children = row
            min,max = min_max
            parents.append([name,0,max])
            if len(children):
                print_info_listmax(max) # (Value can be a list of max %d values.)
                dct[name] = []
                idc=0
                while max is UNBOUNDED or idc < max:
                    dct[name].append({})
                    parents[-1][1] = idc
                    err, param = self.__interactive_params__(command_name, children, dct[name][-1], parents)
                    if err: errors.extend(err)
                    if len(param) and param[0] == '!':
                        if max is None or max > 1: 
                            param = param[1:]
                        break
                    idc+=1
                parents.pop()
                continue
            if name =='':
                parents.pop()
                continue
            is_child = len(parents)>1
            color = ('GREEN','YELLOW')[is_child]
            req = (_T('optional'),'${BOLD}${%s}%s${NORMAL}'%(color,_T('required')))[min]
            print_info_listmax(max) # (Value can be a list of max %d values.)
            if len(allowed):
                session_base.print_unicode('%s: (${BOLD}%s${NORMAL})'%(_T('Param MUST be a value from this list'),', '.join(allowed)))
            cr = 0
            while max is UNBOUNDED or cr < max:
                parents[-1][1] = cr
                prompt = '${BOLD}${GREEN}!${NORMAL}%s:${BOLD}%s${NORMAL} (%s) > '%(command_name,__scope_to_string__(parents),req)
                param = raw_input(session_base.colored_output.render(prompt)).strip()
                if param == '': break
                if param[0] == '!': break
                if re.search('\s',param) and not re.search(r'[\(\)]',param): param = '"%s"'%param
                err = cmd_parser.parse(dct, ((name,min_max,allowed,'',()),), param)
                if err: errors.extend(err)
                cr+=1
            parents.pop()
        if len(param) and param[0] == '!': param = param[1:]
        return errors,param

    def parse_cmd(self, command_name, cmd, config, interactive):
        "Parse command line. Returns errors. Save parsed values to self._dct."
        self._dct = dct = {}
        error=[]
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
        columns = [(command_name,(1,1),(),'',())]
        columns.extend(self._command_params[command_name][1])
        if interactive:
            session_base.print_unicode(_T('${BOLD}${YELLOW}Start interactive input of params. To break type: ${NORMAL}${BOLD}!${NORMAL}[!!...] (one ${BOLD}!${NORMAL} for scope)'))
            self._dct[command_name] = [command_name]
            errors,param = self.__interactive_params__(command_name, vals[1], self._dct)
        else:
            errors = cmd_parser.parse(dct, columns, cmd)
        if errors: error.extend(errors)
        # TODO: display command line
        self.__fill_empy_from_config__(config, dct, columns) # fill missing values from config
        errors = self.__check_required__(columns, dct) # check list and allowed values
        if errors: error.extend(errors)
        if len(dct) < vals[0]+1: # počet parametrů plus název příkazu
            # build command_line example
            error.append('%s %d.'%(_T('Missing values. Required minimum is'),vals[0]))
            error.append('%s: %s'%(_T('Type'),self.get_help(command_name)[0]))
            error.append('(%s: ${BOLD}help %s${NORMAL})'%(_T('For more type'),command_name.replace('_','-')))
        return error

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:].replace('_','-') for name in dir(self.__class__) if name[:9]=='assemble_']

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
        cols=('check','contact','id')
        key = name of key pointed to vlaue in parameters dictionary
        params must have ('clTRID',('name',['name','name',]))
        """
        data=[('epp', 'command'),
            ('command', cols[0]),
            (cols[0],'%s:%s'%(cols[1],cols[0]),None,(
            ('xmlns:%s'%cols[1],'%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,cols[1],eppdoc.nic_cz_version)),
            ('xsi:schemaLocation','%s%s-1.0 %s-%s.xsd'%(eppdoc.nic_cz_xml_epp_path,cols[1],cols[1],eppdoc.nic_cz_version))
            ))
            ]
        col1 = '%s:%s'%(cols[1],cols[0])
        col2 = '%s:%s'%(cols[1],cols[2])
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

    def assemble_poll(self, *params):
        attr = [('op',self._dct['op'][0])]
        if self._dct.get('msg_id',None): attr.append(('msgID',self._dct['msg_id'][0]))
        ('op',self._dct['op'][0])
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
            ('command', 'transfer', '', (('op',self._dct['op'][0]),)),
            ('transfer', '%s:transfer'%names[0], '', attr),
            ('%s:transfer'%names[0], '%s:%s'%names, self._dct['name'][0]),
            ('%s:transfer'%names[0], '%s:authInfo'%names[0]),
            ('%s:authInfo'%names[0], '%s:pw'%names[0], self._dct['passw'][0]),
            ('command', 'clTRID', params[0])
        ))

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
            ('contact:create','contact:id', dct['contact-id'][0]),
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
        # --- BEGIN disclose ------
        if __has_key_dict__(dct,'disclose'):
            disclose = dct['disclose'][0]
            data.append(('contact:create','contact:disclose','',(('flag',disclose['flag'][0]),)))
            for key in ('name','org','addr','voice','fax','email'):
                if __has_key__(disclose,key): data.append(('contact:disclose','contact:%s'%key,disclose[key][0]))
        # --- END disclose ------
        if __has_key__(dct,'vat'): data.append(('contact:create','contact:vat', dct['vat'][0]))
        if __has_key__(dct,'ssn'): data.append(('contact:create','contact:ssn', dct['ssn'][0]))
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
        self.__append_values__(data, dct, 'contact', 'domain:create', 'domain:contact')
        data.extend((
            ('domain:create','domain:authInfo'),
            ('domain:authInfo','domain:pw', dct['pw'][0])
        ))
        if len(params)>1 and params[1]=='extensions': self.__enum_extensions__('create',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_create_domain_enum(self, *params):
        'Extensions for enum.'
        self.assemble_create_domain(params[0], 'extensions')

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
        if len(params)>1 and params[1]=='extensions': self.__enum_extensions__('renew',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_renew_domain_enum(self, *params):
        "Assemble XML EPP command"
        self.assemble_renew_domain(params[0], 'extensions')

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
            ('contact:update','contact:id', dct['contact-id'][0]),
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
                poin = chg['postal_info'][0]
                data.append(('contact:chg','contact:postalInfo'))
                for key in ('name','org'):
                    if __has_key__(poin,key): data.append(('contact:postalInfo','contact:%s'%key, poin[key][0]))
                if __has_key_dict__(poin,'addr'):
                    addr = poin['addr'][0]
                    data.append(('contact:postalInfo','contact:addr'))
                    for key in ('street','city','sp','pc','cc'):
                        if __has_key__(addr,key): data.append(('contact:addr','contact:%s'%key, addr[key][0]))
                for key in ('voice','fax','email'):
                    if __has_key__(chg,key): data.append(('contact:chg','contact:%s'%key, chg[key][0]))
                if __has_key_dict__(chg,'disclose'):
                    # --- BEGIN disclose ------
                    disclose = chg['disclose'][0]
                    data.append(('contact:chg','contact:disclose','',(('flag',disclose['flag'][0]),)))
                    for key in ('name','org','addr','voice','fax','email'):
                        if __has_key__(disclose,key): data.append(('contact:disclose','contact:%s'%key,disclose[key][0]))
                # --- END disclose ------
        for key in ('vat','ssn'):
            if __has_key__(dct,key): data.append(('contact:chg','contact:%s'%key, dct[key][0]))
        if __has_key__(dct,'notify_email'): data.append(('contact:chg','contact:notifyEmail', dct['notify_email'][0]))
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
                for name in ('status','contact'):
                    if __has_key__(dct_key,name):
                        self.__append_values__(data, dct_key, name, 'domain:%s'%key, 'domain:%s'%name)
        if __has_key_dict__(dct,'chg'):
            chg = dct['chg'][0]
            data.append(('domain:update', 'domain:chg'))
            if __has_key__(chg,'nsset'): data.append(('domain:chg','domain:nsset', chg['nsset'][0]))
            if __has_key__(chg,'registrant'): data.append(('domain:chg','domain:registrant', chg['registrant'][0]))
            if __has_key_dict__(chg,'auth_info'):
                data.append(('domain:chg','domain:authInfo'))
                authInfo = chg['auth_info'][0]
                if __has_key__(authInfo,'pw'): data.append(('domain:authInfo','domain:pw', authInfo['pw'][0]))
                if __has_key__(authInfo,'ext'): data.append(('domain:authInfo','domain:ext', authInfo['ext'][0]))
        if len(params)>1 and params[1]=='extensions': self.__enum_extensions__('update',data, params,'chg')
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_domain_enum(self, *params):
        "Assemble XML EPP command"
        self.assemble_update_domain(params[0], 'extensions')

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
            if __has_key__(dct_chg, 'ext'): data.append(('nsset:authInfo','nsset:ext',dct_chg['ext'][0]))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    #===========================================

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

def print_info_listmax(max):
    if max > 1:
        session_base.print_unicode(_T('(Value can be a list of max %d values.)')%max)
    elif max is UNBOUNDED:
        session_base.print_unicode(_T('(Value can be an unbouded list of values.)'))
