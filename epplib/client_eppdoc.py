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
import re
from gettext import gettext as _T
import ConfigParser
import eppdoc
import cmd_parser

UNBOUNDED = None

# Text k helpu
examples = {}
examples['create-nsset'] = '\n'.join((
    'create-nsset exampleNsset passw',
     'create-nsset exampleNsset passw ((ns1.domain.net (127.1.0.1 127.1.0.2)),(ns2.domain.net (127.2.0.1 127.2.0.2)),(ns3.domain.net (127.3.0.1 127.3.0.2))) tech-contact',
    ))
examples['update-nsset'] = '\n'.join((
    'update-nsset nic.cz',
    'update-nsset nsset-ID (((nsset1.name.cz 127.0.0.1),(nsset2.name.cz (127.0.2.1 127.0.2.2)),) tech-add-contact ok) ("My Name",("Tech contact 1","Tech contact 2"),(clientDeleteProhibited ok)) (password extension)',
    ))
    

notice = {'check':_T("""
   The EPP "check" command is used to determine if an object can be
   provisioned within a repository.  It provides a hint that allows a
   client to anticipate the success or failure of provisioning an object
   using the "create" command as object provisioning requirements are
   ultimately a matter of server policy.
"""),
    'info':_T("""
   The EPP "info" command is used to retrieve information associated
   with an existing object. The elements needed to identify an object
   and the type of information associated with an object are both
   object-specific, so the child elements of the <info> command are
   specified using the EPP extension framework.
"""),
    'transfer':_T("""
   The EPP "transfer" command provides a query operation that allows a
   client to determine real-time status of pending and completed
   transfer requests.
   The EPP "transfer" command is used to manage changes in client
   sponsorship of an existing object.  Clients can initiate a transfer
   request, cancel a transfer request, approve a transfer request, and
   reject a transfer request using the "op" command attribute.
"""),
   'create':_T("""
   The EPP "create" command is used to create an instance of an object.
   An object can be created for an indefinite period of time, or an
   object can be created for a specific validity period.
"""),
   'delete':_T("""The EPP "delete" command is used to remove an instance of an existing object."""),
   'renew':_T("""The EPP "renew" command is used to extend validity of an existing object."""),
   'update':_T("""The EPP "update" command is used to update an instance of an existing object.""")
}

class Message(eppdoc.Message):
    "Client EPP commands."
    # transfer op attribute allowed values:
    transfer_op = ('request','approve','cancel','query','reject')
    update_status = ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok', 'serverDeleteProhibited', 'serverTransferProhibited', 'serverUpdateProhibited')
    # format:
    # command-name: (param-name, (min,max), (list of required), 'help', (list of children)
    command_params = {
        'hello': (0, (('',(0,0),(),'',()),), _T('The EPP "hello" request a "greeting" response message from an EPP server at any time.')),
        'logout': (0, (('',(0,0),(),'',()),), _T('The EPP "logout" command is used to end a session with an EPP server.')),
        #----------------------------------------------------
        'login': (2,(
            ('username',(1,1),(),_T('your login name'),()),
            ('password',(1,1),(),_T('your password'),()),
            ('new-password',(0,1),(),_T('new password'),()),
        ),_T("""
   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session.""")),
        #----------------------------------------------------
        'info_contact': (1,(
            ('name',(1,1),(),_T('contact name'),()),
        ),notice['info']),
        'info_domain': (1,(
            ('name',(1,1),(),_T('domain name'),()),
        ),notice['info']),
        'info_nsset': (1,(
            ('name',(1,1),(),_T('nsset name'),()),
        ),notice['info']),
        #----------------------------------------------------
        'check_contact': (1,(
            ('name',(1,UNBOUNDED),(),_T('contact name'),()),
        ),notice['check']),
        'check_domain': (1,(
            ('name',(1,UNBOUNDED),(),_T('domain name'),()),
        ),notice['check']),
        'check_nsset': (1,(
            ('name',(1,UNBOUNDED),(),_T('nsset name'),()),
        ),notice['check']),
        #----------------------------------------------------
        'poll': (1,(
            ('op',(1,1),('req','ack'),_T('query type'),()),
        ),_T('The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients.')),
        #----------------------------------------------------
        'transfer_domain': (3,(
            ('name',(1,1),(),_T('domain name'),()),
            ('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),()),
        ),notice['transfer']),
        #----------------------------------------------------
        'transfer_nsset': (3,(
            ('name',(1,1),(),_T('nsset name'),()),
            ('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),()),
        ),notice['transfer']),
        #----------------------------------------------------
        'create_contact': (5,(
            ('contact-id',(1,1),(),_T('your contact ID'),()),
            ('name',(1,1),(),_T('your name'),()), # odtud shoda s update contact
            ('email',(1,1),(),_T('your email'),()),
            ('city',(1,1),(),_T('your city'),()),
            ('cc',(1,1),(),_T('country code'),()), # required end
            ('org',(0,1),(),_T('organisation name'),()),
            ('street',(0,3),(),_T('street'),()),
            ('sp',(0,1),(),_T('sp'),()),
            ('pc',(0,1),(),_T('postal code'),()),
            ('voice',(0,1),(),_T('voice (phone number)'),()),
            ('fax',(0,1),(),_T('fax number'),()),
            ('disclose',(0,1),(),_T('disclose part'),(
                ('flag',(1,1),('0','1'),_T('disclose flag'),()),
                ('name',(0,1),(),_T('disclose name'),()),
                ('org',(0,1),(),_T('disclose organisation name'),()),
                ('addr',(0,1),(),_T('disclose address'),()),
                ('voice',(0,1),(),_T('disclose voice (phone)'),()),
                ('fax',(0,1),(),_T('disclose fax'),()),
                ('email',(0,1),(),_T('disclose email'),()),
            )),
            ('vat',(0,1),(),_T('VAT'),()),
            ('ssn',(0,1),(),_T('SSN'),()),
            ('notifyEmail',(0,1),(),_T('notify email'),()),
            ),notice['create']),
        #----------------------------------------------------
        'create_domain': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('pw',(1,1),(),_T('password'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ('nsset',(0,1),(),_T('nsset'),()),
            ('registrant',(0,1),(),_T('registrant'),()),
            ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            ),notice['create']),
        #----------------------------------------------------
        'create_domain_enum': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('pw',(1,1),(),_T('password'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ('nsset',(0,1),(),_T('nsset'),()),
            ('registrant',(0,1),(),_T('registrant'),()),
            ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            ('valExDate',(0,1),(),_T('valExDate'),()),
            ),notice['create']),
        #----------------------------------------------------
        'create_nsset': (2,(
            ('id',(1,1),(),_T('nsset ID'),()),
            ('pw',(1,1),(),_T('password'),()),
            ('ns',(0,9),(),_T('LIST of nssets'),(
                ('name',(1,1),(),_T('nsset name'),()),
                ('addr',(0,UNBOUNDED),(),_T('nsset address'),()),
            )),
            ('tech',(0,UNBOUNDED),(),_T('tech contact'),()),

            ),'%s\n${BOLD}%s:${NORMAL}\n%s'%(notice['create'],_T('Examples'),examples['create-nsset'])),
        #----------------------------------------------------
        'delete_contact': (1,(
             ('id',(1,1),(),_T('contact ID'),()),
            ),notice['delete']),
        #----------------------------------------------------
        'delete_domain': (1,(
            ('name',(1,1),(),_T('domain name'),()),
            ),notice['delete']),
        #----------------------------------------------------
        'delete_nsset': (1,(
            ('id',(1,1),(),_T('nsset ID'),()),
            ),notice['delete']),
        #----------------------------------------------------
        'renew_domain': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('curExpDate',(1,1),(),_T('current expiration date'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ),notice['renew']),
        #----------------------------------------------------
        'renew_domain_enum': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('curExpDate',(1,1),(),_T('current expiration date'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ('valExDate',(0,1),(),_T('valExDate'),()),
            ),notice['renew']),
        #----------------------------------------------------
        'update_contact': (1,(
            ('contact-id',(1,1),(),_T('your contact ID'),()),
            ('add',(0,5),(),_T('add status'),()),
            ('rem',(0,5),(),_T('remove status'),()),
            ('chg',(0,1),(),_T('change status'),(
                ('postalInfo',(0,1),(),_T('postal informations'),(
                    ('name',(0,1),(),_T('name'),()),
                    ('org',(0,1),(),_T('organisation name'),()),
                    ('addr',(0,1),(),_T('address'),()),
                )),
                ('voice',(0,1),(),_T('voice (phone number)'),()),
                ('fax',(0,1),(),_T('fax number'),()),
                ('email',(0,1),(),_T('your email'),()),
                ('disclose',(0,1),(),_T('disclose part'),(
                    ('flag',(1,1),('0','1'),_T('disclose flag'),()),
                    ('name',(0,1),(),_T('disclose name'),()),
                    ('org',(0,1),(),_T('disclose organisation name'),()),
                    ('addr',(0,1),(),_T('disclose address'),()),
                    ('voice',(0,1),(),_T('disclose voice (phone)'),()),
                    ('fax',(0,1),(),_T('disclose fax'),()),
                    ('email',(0,1),(),_T('disclose email'),()),
                )),
                ('vat',(0,1),(),_T('VAT'),()),
                ('ssn',(0,1),(),_T('SSN'),()),
                ('notifyEmail',(0,1),(),_T('notify email'),()),
            )),
            ),notice['update']),
        #----------------------------------------------------
        'update_domain': (1,(
            ('name',(1,1),(),_T('domain name'),()),
            ('add',(0,1),(),_T('add status'),(
                ('status',(0,8),update_status,_T('status'),()),
                ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            )),
            ('rem',(0,1),(),_T('remove status'),(
                ('status',(0,8),update_status,_T('status'),()),
                ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            )),
            ('chg',(0,1),(),_T('change status'),(
                ('nsset',(0,1),(),_T('nsset'),()),
                ('registrant',(0,1),(),_T('registrant'),()),
                ('authInfo',(0,1),(),_T('authInfo'),(
                    ('pw',(0,1),(),_T('password'),()),
                    ('ext',(0,1),(),_T('ext'),()),
                )),
            )),
            ),notice['update']),
        #----------------------------------------------------
        'update_domain_enum': (1,(
            ('name',(1,1),(),_T('domain name'),()),
            ('add',(0,1),(),_T('add status'),(
                ('status',(0,8),update_status,_T('status'),()),
                ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            )),
            ('rem',(0,1),(),_T('remove status'),(
                ('status',(0,8),update_status,_T('status'),()),
                ('contact',(0,UNBOUNDED),(),_T('contact'),()),
            )),
            ('chg',(0,1),(),_T('change status'),(
                ('nsset',(0,1),(),_T('nsset'),()),
                ('registrant',(0,1),(),_T('registrant'),()),
                ('authInfo',(0,1),(),_T('authInfo'),(
                    ('pw',(0,1),(),_T('password'),()),
                    ('ext',(0,1),(),_T('ext'),()),
                )),
            )),
            ('valExDate',(0,1),(),_T('valExDate'),()),
            ),notice['update']),
        #----------------------------------------------------
        'update_nsset': (1,(
            ('id',(1,1),(),_T('nsset ID'),()),
            ('add',(0,1),(),_T('add part'),(
                ('ns',(0,9),(),_T('list of nssets'),(
                    ('name',(1,1),(),_T('nsset name'),()),
                    ('addr',(0,UNBOUNDED),(),_T('IP address'),()),
                )),
                ('tech',(0,UNBOUNDED),(),_T('technical contact'),()),
                ('status',(0,6),update_status,_T('status'),()),
            )),
            ('rem',(0,1),(),_T('remove part'),(
                ('name',(0,9),(),_T('name'),()),
                ('tech',(0,UNBOUNDED),(),_T('technical contact'),()),
                ('status',(0,6),update_status,_T('status'),()),
            )),
            ('chg',(0,1),(),_T('change part'),(
                ('pw',(0,1),(),_T('password'),()),
                ('ext',(0,1),(),_T('ext'),()),
            )),
            ),'%s\n${BOLD}%s:${NORMAL}\n%s'%(notice['update'],_T('Examples'),examples['update-nsset'])),
    }

    def __get_help_scope__(self, params, deep=1):
        'Support for get_help(). IN: params, deep'
        msg=[]
        indent = '    '*deep
        for row in params:
            name,min_max,allowed,help,children = row
            min,max = min_max
            if min > 0:
                color = ('YELLOW','GREEN')[deep==1]
                required = '${%s}${BOLD}(%s)${NORMAL}'%(color,_T('required'))
            else:
                required = '${WHITE}(%s)${NORMAL}'%_T('optional')
            text = '%s%s %s'%(indent,name,required)
            if max == None:
                max_size = _T('unbounded list')
            elif max > 1:
                max_size = _T('list with max %d items.')%max
            else:
                max_size = ''
            if max_size:
                text = '%s%s%s'%(text,('\t','\t\t')[len(text)<42],max_size)
            if len(allowed):
                text = '%s ${WHITE}%s: ${YELLOW}(%s)${NORMAL}'%(text,_T('accept only values'),','.join(allowed))
            msg.append(text)
            if len(children):
                msg.extend(self.__get_help_scope__(children, deep+1))
        return msg

    def get_help(self, command_name):
        "Returns help for selected command: (command_line, complete help)."
        command_line = []
        help=[]
        notice=''
        # v příkazu zrušit spojovníky
        m = re.match('(\S+)(.*)',command_name)
        if m: command_name = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if Message.command_params.has_key(command_name):
            # příkaz existuje
            required,params,notice = Message.command_params[command_name]
            command_line = ['${BOLD}%s${NORMAL}'%command_name.replace('_','-')]
            if required:
                help.append('%s:'%_T('Required parameters'))
            if params:
                for pos in range(required):
                    command_line.append(params[pos][0])
            help = self.__get_help_scope__(params)
        else:
            # neznámý příkaz
            help.append(_T('Unknown EPP command. Select one from EPP commands list (Type help).'))
            self.help_check_name(help,command_name)
        return ' '.join(command_line), '\n'.join(help), notice
            
    def help_check_name(self,help,command_name):
        'Join extended help if possible (for some commands).'
        if command_name in ('create','check','info','transfer'):
            help.append('%s: %s'%(_T('Try'),' '.join(['%s-%s'%(command_name,n) for n in ('contact','domain','nsset')])))

    def __fillup_from_config__(self, config, dct, columns):
        'Dopnění parametrů EPP přikazu z configu.'
        errors = []
        section = 'epp_%s'%columns[0][0]
        if not config or not config.has_section(section): return errors
        for key_val in config.items(section):
            cmd = '-%s %s'%key_val
            err = cmd_parser.parse(dct, columns, cmd)
            if errors: errors.extends(err)
        return errors

    def __check_required__(self, columns, dct_values, scopes=[]):
        'Check parsed values for required and allowed values.'
        errors = []
        if len(scopes) and not len(dct_values): return errors # if descendant is empty - not check
        if type(dct_values) != dict: return (_T('Invalid input format.'),)
        for row in columns:
            name,min_max,allowed,msg_help,children = row
            scopes.append(name)
            scope_name = '.'.join(scopes)
            if dct_values.has_key(name):
                if min_max[1] != None and len(dct_values[name]) > min_max[1]:
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

    def parse_cmd(self, command_name, cmd, config):
        "Parse command line. Returns errors. Save parsed values to self._dct."
        self._dct = dct = {}
        error=[]
        m = re.match('check_(\w+)\s+(.+)',cmd)
        if m:
            # úprava pro příkazy check_..., kde se jména seskupí do jednoho parametru name
            cmd = 'check_%s (%s)'%(m.group(1),m.group(2))
        vals = Message.command_params.get(command_name,None)
        if not vals:
            error.append("%s: '%s'"%(_T('Unknown command'),command_name))
            error.append('(%s: ${BOLD}help${NORMAL})'%(_T('For more type')))
            return error
        if not vals[1]: return error # bez parametrů
        columns = [(command_name,(1,1),(),'',())]
        columns.extend(Message.command_params[command_name][1])
        # nejdříve dojde k dopnění parametrů z configu
        self.__fillup_from_config__(config, dct, columns)
        errors = cmd_parser.parse(dct, columns, cmd)
        if errors: error.extend(errors)
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
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'poll', '', (('op',self._dct['op'][0]),) ),
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
        if not __has_key__(self._dct,'valExDate'): return
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
        data.append(('%s:%s'%names,'%s:valExDate'%names[0], self._dct['valExDate'][0]))

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
        if __has_key__(dct,'notifyEmail'): data.append(('contact:create','contact:notifyEmail', dct['notifyEmail'][0]))
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
        if len(params)>2 and params[2]=='extensions': self.__enum_extensions__('create',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_create_domain_enum(self, *params):
        'Extensions for enum.'
        self.assemble_create_domain(params[0], params[1], 'extensions')

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
        if __has_key__(dct,'ns'):
            for ns in dct['ns']:
                self.__append_nsset__('create', data, ns)
        data.extend((
            ('nsset:create','nsset:authInfo'),
            ('nsset:authInfo','nsset:pw', dct['pw'][0])
        ))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_renew_domain(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ('version', 'objURI', 'LANG') [,'extensions'])
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
            ('domain:renew','domain:curExpDate', dct['curExpDate'][0]),
            ]
        if __has_key_dict__(dct,'period'):
            period = dct['period'][0]
            if not __has_key__(period,'unit'): period['unit']=('y',)
            data.append(('domain:renew','domain:period',period['num'][0], (('unit',period['unit'][0]),)))
        if len(params)>2 and params[2]=='extensions': self.__enum_extensions__('renew',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_renew_domain_enum(self, *params):
        "Assemble XML EPP command"
        if len(params)<2: params = (params[0],None)
        self.assemble_renew_domain(params[0], params[1], 'extensions')

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
            if __has_key_dict__(chg,'postalInfo'):
                poin = chg['postalInfo'][0]
                data.append(('contact:chg','contact:postalInfo'))
                for key in ('name','org','addr'):
                    if __has_key__(poin,key): data.append(('contact:postalInfo','contact:%s'%key, poin[key][0]))
            for key in ('voice','fax','email'):
                if __has_key__(chg,key): data.append(('contact:chg','contact:%s'%key, chg[key][0]))
            if __has_key_dict__(chg,'disclose'):
                # --- BEGIN disclose ------
                disclose = chg['disclose'][0]
                data.append(('contact:update','contact:disclose','',(('flag',disclose['flag'][0]),)))
                for key in ('name','org','addr','voice','fax','email'):
                    if __has_key__(disclose,key): data.append(('contact:disclose','contact:%s'%key,disclose[key][0]))
                # --- END disclose ------
        for key in ('vat','ssn','notifyEmail'):
            if __has_key__(dct,key): data.append(('contact:chg','contact:%s'%key, dct[key][0]))
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
            if __has_key_dict__(chg,'authInfo'):
                data.append(('domain:chg','domain:authInfo'))
                authInfo = chg['authInfo'][0]
                if __has_key__(authInfo,'pw'): data.append(('domain:authInfo','domain:pw', authInfo['pw'][0]))
                if __has_key__(authInfo,'ext'): data.append(('domain:authInfo','domain:ext', authInfo['ext'][0]))
        if len(params)>2 and params[2]=='extensions': self.__enum_extensions__('update',data, params,'chg')
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_domain_enum(self, *params):
        "Assemble XML EPP command"
        if len(params)<2: params = (params[0],None)
        self.assemble_update_domain(params[0], params[1], 'extensions')

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
            if __has_key_dict__(dct_add,'ns'):
                for dct_ns in dct_add['ns']:
                    if not __has_key__(dct_ns, 'name'): continue
                    data.append(('nsset:add','nsset:ns'))
                    data.append(('nsset:ns','nsset:name',dct_ns['name'][0]))
                    self.__append_values__(data, dct_ns, 'addr', 'nsset:ns', 'nsset:addr')
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

def test_command(command, label):
    "Test if template si valid."
    epp = Message()
    cmd = command.split()
    fnc_name = "assemble_%s"%cmd[0]
    if hasattr(epp, fnc_name):
        getattr(epp, fnc_name)('clTRID',cmd[1:],('version', 'objURI', 'language'))
    else:
        print "Error: Command not found."
    errors, xmlepp = epp.get_results()
    print '%s:'%label
    print 'XMLEPP:',xmlepp
    print 'ERRORS:',errors
    print '-'*60

def test(commands):
    import pprint
    import client_session_base
    manag = client_session_base.ManagerBase()
    epp = Message()
    print "#"*60
    for cmd in commands:
        print "COMMAND:",cmd
        m = re.match('(\S+)',cmd)
        if not m: continue
        cmd_name = m.group(1)
        epp.reset()
        errors = epp.parse_cmd(cmd_name, cmd, None)
        if errors:
            print errors
        else:
            getattr(epp,'assemble_%s'%cmd_name)('llcc002#06-06-16at13:21:30',('1.0', ('objURI',), ('extURI',), 'LANG'))
            errors, xmlepp = epp.get_results()
            print errors, xmlepp
            if xmlepp:
                print manag.is_epp_valid(xmlepp)
        print '='*60

def test_help(command_names):
    import terminal_controler
    colored_output = terminal_controler.TerminalController()
    epp = Message()
    for command_name in command_names:
        command_line,command_help,notice = epp.get_help(command_name)
        print colored_output.render(command_line)
        print colored_output.render(command_help)
        print colored_output.render(notice)
        print '\n\n'
        
if __name__ == '__main__':
    # Test na jednotlivé příkazy
    commands1 = (
     'hello',
     'login john mypass "my new pass!"',
     'logout',
     'info_domain my-domain.cz',
     'info_contact my-contact',
     'check_domain nic.cz cin.cz',
     'check_contact my-contact1 my-contact2',
     'transfer_domain name-domain request password',
     'transfer_nsset name-nsset request password',
     'poll req',
    )
    commands2 = (
     'create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 (0 d-name "d org." "ulice číso město" +21321313 +734321 pepa@jojo.com) vat-test ssn-test notify@semka.net',
     'create_domain domain.cz password (3 m) nsset.name.cz registr-name ("My address","My next contact")',
     'create_domain_enum domain.cz password (3 m) nsset.name.cz registr-name ("My address","My next contact") 2006-06-08',
     'create_nsset exampleNsset passw ((ns1.domain.net (127.1.0.1 127.1.0.2)),(ns2.domain.net (127.2.0.1 127.2.0.2)),(ns3.domain.net (127.3.0.1 127.3.0.2))) tech-contact',
    )
    commands3 = (
     'delete_contact contact-id',
     'delete_domain domain.cz',
     'delete_nsset nsset-id',
    )
    commands4 = (
     'renew_domain nic.cz 2023-06-02 (6 y)',
     'renew_domain_enum nic.cz 2023-06-02 () 2006-08-09',
    )
    commands5 = (
     'update_contact id-contact clientDeleteProhibited',
     'update_contact id-contact (clientDeleteProhibited linked ok)',
     'update_contact id-contact (linked ok) (clientDeleteProhibited clientUpdateProhibited) (("John Doe" "Doe Company" "Down street, New York") +00123456789 +00123456456 john@doe.com (1 John John-Comp "Street and City" +01231321 +01234654 john@john.com) my-vat my-ssn notify@here.net',
     'update_domain nic.cz',
     'update_domain nic.cz (linked add-contact) ((ok linked) rem-contact) (nsset registrant (password extensions))',
     'update_domain_enum 1.1.1.1.1.arpa64.net (linked add-contact) ((ok linked) rem-contact) (nsset registrant (password extensions)) 2006-06-08',
)
    commands6 = (
    'update_nsset nic.cz',
    'update_nsset nsset-ID (((nsset1.name.cz 127.0.0.1),(nsset2.name.cz (127.0.2.1 127.0.2.2)),) tech-add-contact ok) ("My Name",("Tech contact 1","Tech contact 2"),(linked ok)) (password extension)',
    )
    test(commands1)
    test(commands2)
    test(commands3)
    test(commands4)
    test(commands6)
    test_help(('login','update_nsset',))
