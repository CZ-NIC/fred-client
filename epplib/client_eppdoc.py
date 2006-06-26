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
import eppdoc
import data_parser

SINGLE,LIST = range(2) # typ parametru v příkazu

# Text k helpu
examples = {}
cn=[]
cmd = '  create-nsset exampleNsset passw '
for p in ('ns1.domain.net',
     'ns1.domain.net',
     '(ns1.domain.net ns2.domain.net)',
     '(ns1.domain.net 194.23.54.1 194.23.54.2 ns2.domain.net 196.23.54.1 196.23.54.2)',):
     cn.append('%s%s'%(cmd,p))
examples['create-nsset'] = '\n'.join(cn)
cn=[]
cmd = '  update_nsset nic.cz '
for p in ('update_nsset nic.cz (ns-add1.nic.cz ns-add2.nic.cz) ns-rem1.nic.cz password',
    '((ns-add1.nic.cz ns-add2.nic.cz) tech-add ok) (ns-rem1.nic.cz ns-rem2.nic.cz) password',
    '((ns-add1.nic.cz 127.0.0.1 ns-add2.nic.cz 127.0.2.1) tech-add ok) ((ns-rem1.nic.cz, ns-rem2.nic.cz) tech-rem clientDeleteProhibited) password',
    '((ns-add1.nic.cz 127.0.0.1 127.0.0.2 ns-add2.nic.cz 127.0.2.1 127.0.2.2) tech-add ok) () password',
    '(((ns-add1.nic.cz 127.0.0.1 127.0.0.2)(ns-add2.nic.cz 127.0.2.1 127.0.2.2)) tech-add ok) () password',
    '(((ns-add1.nic.cz (127.0.0.1 127.0.0.2))(ns-add2.nic.cz (127.0.2.1 127.0.2.2))) ("first technical contact","second technical contact") ok) ((ns-rem1.nic.cz, ns-rem2.nic.cz) "remove technical contact" clientDeleteProhibited) password',):
     cn.append('%s%s'%(cmd,p))
examples['update-nsset'] = '\n'.join(cn)
    

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
   'renew':_T("""The EPP "delete" command is used to remove an instance of an existing object."""),
   'update':_T("""The EPP "update" command is used to update an instance of an existing object.""")
}

class Message(eppdoc.Message):
    "Client EPP commands."
    # transfer op attribute allowed values:
    transfer_op = ('request','approve','cancel','query','reject')
    update_status = ('clientDeleteProhibited', 'clientUpdateProhibited', 'linked', 'ok', 'serverDeleteProhibited', 'serverUpdateProhibited')
    # format:
    # command-name: (required, (param-name, parameter-help [,(param-list,max)[, param-values], dependence]), command-help )
    cmd_params = {
        'hello': (0,None, _T('The EPP "hello" request a "greeting" response message from an EPP server at any time.')),
        'logout': (0,None, _T('The EPP "logout" command is used to end a session with an EPP server.')),
        #----------------------------------------------------
        'login': (2,(
            ('username',_T('your login name')),
            ('password',_T('your password')),
            ('new-password',_T('new password')),
        ),_T("""
   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session.""")),
        #----------------------------------------------------
        'info_contact': (1,(
            ('name',_T('contact name')),
        ),notice['info']),
        'info_domain': (1,(
            ('name',_T('domain name')),
        ),notice['info']),
        'info_nsset': (1,(
            ('name',_T('nsset name')),
        ),notice['info']),
        #----------------------------------------------------
        'check_contact': (1,(
            ('name',_T('contact name'),(LIST,0)),
        ),notice['check']),
        'check_domain': (1,(
            ('name',_T('domain name'),(LIST,0)),
        ),notice['check']),
        'check_nsset': (1,(
            ('name',_T('nsset name'),(LIST,0)),
        ),notice['check']),
        #----------------------------------------------------
        'poll': (1,(
            ('op',_T('query type'),None,('req','ack')),
        ),_T('The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients.')),
        #----------------------------------------------------
        'transfer_domain': (3,(
            ('name',_T('domain name')),
            ('op',_T('query type'),None,transfer_op),
            ('passw',_T('password')),
        ),notice['transfer']),
        #----------------------------------------------------
        'transfer_nsset': (3,(
            ('name',_T('nsset name')),
            ('op',_T('query type'),None,transfer_op),
            ('passw',_T('password')),
        ),notice['transfer']),
        #----------------------------------------------------
        'create_contact': (5,(
            ('contact-id',_T('your contact ID')),
            ('name',_T('your name')), # odtud shoda s update contact
            ('email',_T('your email')),
            ('city',_T('your city')),
            ('cc',_T('country code')), # required end
            ('org',_T('organisation name')),
            ('street',_T('street'),(LIST,3)),
            ('sp',_T('sp')),
            ('pc',_T('postal code')),
            ('voice',_T('voice (phone number)')),
            ('fax',_T('fax number')),
            ('disclose',_T('disclose flag'),None,('0','1')),
            ('disclose-name',_T('disclose name'),None,None,'disclose'),
            ('disclose-org',_T('disclose organisation name'),None,None,'disclose'),
            ('disclose-addr',_T('disclose address'),None,None,'disclose'),
            ('disclose-voice',_T('disclose voice (phone)'),None,None,'disclose'),
            ('disclose-fax',_T('disclose fax'),None,None,'disclose'),
            ('disclose-email',_T('disclose email'),None,None,'disclose'),
            ('vat',_T('VAT')),
            ('ssn',_T('SSN')),
            ('notifyEmail',_T('notify email')),
            ),notice['create']),
        #----------------------------------------------------
        'create_domain': (2,(
            ('name',_T('domain name')),
            ('pw',_T('password')),
            ('period',_T('period')),
            ('period-unit',_T('period unit (y year(default), m month)'),None,('y','m'),'period'),
            ('nsset',_T('nsset')),
            ('registrant',_T('registrant')),
            ('contact',_T('contact'),(LIST,0)),
            ),notice['create']),
        #----------------------------------------------------
        'create_domain_enum': (2,(
            ('name',_T('domain name')),
            ('pw',_T('password')),
            ('period',_T('period')),
            ('period-unit',_T('period unit (y year(default), m month)'),None,('y','m'),'period'),
            ('nsset',_T('nsset')),
            ('registrant',_T('registrant')),
            ('contact',_T('contact'),(LIST,0)),
            ('valExDate',_T('valExDate')),
            ),notice['create']),
        #----------------------------------------------------
        'create_nsset': (2,(
            ('id',_T('nsset ID')),
            ('pw',_T('password')),
            ('name_and_addr',_T('nsset name and address inside quotes'),(LIST,9)),
            ('tech',_T('etch contact'),(LIST,0)),
            ),'%s\n${BOLD}%s:${NORMAL}\n%s'%(notice['create'],_T('Examples'),examples['create-nsset'])),
        #----------------------------------------------------
        'delete_contact': (1,(
             ('id',_T('contact ID')),
            ),notice['delete']),
        #----------------------------------------------------
        'delete_domain': (1,(
            ('name',_T('domain name')),
            ),notice['delete']),
        #----------------------------------------------------
        'delete_nsset': (1,(
            ('id',_T('nsset ID')),
            ),notice['delete']),
        #----------------------------------------------------
        'renew_domain': (2,(
            ('name',_T('domain name')),
            ('curExpDate',_T('current expiration date')),
            ('period',_T('period')),
            ('period-unit',_T('period unit (y year(default), m month)'),None,('y','m'),'period'),
            ),notice['renew']),
        #----------------------------------------------------
        'renew_domain_enum': (2,(
            ('name',_T('domain name')),
            ('curExpDate',_T('current expiration date')),
            ('period',_T('period')),
            ('period-unit',_T('period unit (y year(default), m month)'),None,('y','m'),'period'),
            ('valExDate',_T('valExDate')),
            ),notice['renew']),
        #----------------------------------------------------
        'update_contact': (1,(
            ('contact-id',_T('your contact ID')),
            ('add',_T('add status'),(LIST,5),update_status),
            ('rem',_T('remove status'),(LIST,5),update_status),
            ('name',_T('your name')), # odtud shoda s create contact
            ('email',_T('your email')),
            ('city',_T('your city')),
            ('cc',_T('country code')), # required end
            ('org',_T('organisation name')),
            ('street',_T('street'),(LIST,3)),
            ('sp',_T('sp')),
            ('pc',_T('postal code')),
            ('voice',_T('voice (phone number)')),
            ('fax',_T('fax number')),
            ('disclose',_T('disclose flag'),None,('0','1')),
            ('disclose-name',_T('disclose name'),None,None,'disclose'),
            ('disclose-org',_T('disclose organisation name'),None,None,'disclose'),
            ('disclose-addr',_T('disclose address'),None,None,'disclose'),
            ('disclose-voice',_T('disclose voice (phone)'),None,None,'disclose'),
            ('disclose-fax',_T('disclose fax'),None,None,'disclose'),
            ('disclose-email',_T('disclose email'),None,None,'disclose'),
            ('vat',_T('VAT')),
            ('ssn',_T('SSN')),
            ('notifyEmail',_T('notify email')),
            ),notice['update']),
        #----------------------------------------------------
        'update_domain': (1,(
            ('name',_T('domain name')),
            ('add',_T('add status'),(LIST,5),update_status),
            ('rem',_T('remove status'),(LIST,5),update_status),
            ('nsset',_T('nsset')),
            ('registrant',_T('registrant')),
            ('pw',_T('password')),
            ),notice['update']),
        #----------------------------------------------------
        'update_domain_enum': (1,(
            ('name',_T('domain name')),
            ('add',_T('add status'),(LIST,5),update_status),
            ('rem',_T('remove status'),(LIST,5),update_status),
            ('nsset',_T('nsset')),
            ('registrant',_T('registrant')),
            ('pw',_T('password')),
            ('valExDate',_T('valExDate')),
            ),notice['update']),
        #----------------------------------------------------
        'update_nsset': (1,(
            ('id',_T('nsset ID')),
            ('add',_T('nsset-names address tech status'),(LIST,0)),
            ('rem',_T('remove nsset-name tech status'),(LIST,0)),
            ('pw',_T('password')),
            ),'%s\n${BOLD}%s:${NORMAL}\n%s'%(notice['update'],_T('Examples'),examples['update-nsset'])),
    }
    
    def __get_help_note__(self, help, params, pos):
        'Support for get_help().'
        sep=('\t','\t\t')[len(params[pos][0])<8]
        note=[]
        if len(params[pos])>2 and params[pos][2] and params[pos][2][0]==LIST:
            if params[pos][2][1]:
                note.append(_T('Can be LIST of values (max %d items)')%(params[pos][2][1]))
            else:
                note.append(_T('Can be LIST of values (unbounded)'))
        if len(params[pos])>3 and params[pos][3]:
            note.append('%s: (%s)'%(_T('MUST be one of'),', '.join(params[pos][3])))
        if len(params[pos])>4 and params[pos][4]:
            note.append('%s %s'%(_T('depends on'),params[pos][4]))
        help.append('\t%s%s(%s) %s'%(params[pos][0],sep,params[pos][1],'; '.join(note)))

    def get_help(self, command_name):
        "Returns help for selected command: (command_line, complete help)."
        command_line = []
        help=[]
        notice=''
        # v příkazu zrušit spojovníky
        m = re.match('(\S+)(.*)',command_name)
        if m: command_name = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if Message.cmd_params.has_key(command_name):
            # příkaz existuje
            required,params,notice = Message.cmd_params[command_name]
            command_line = ['${BOLD}%s${NORMAL}'%command_name.replace('_','-')]
            if required:
                help.append('%s:'%_T('Required parameters'))
            if params:
                for pos in range(required):
                    self.__get_help_note__(help, params, pos)
                    command_line.append(params[pos][0])
                pos+=1
                if pos < len(params):
                    help.append('%s:'%_T('Optional parameters'))
                    for pos in range(pos,len(params)):
                        self.__get_help_note__(help, params, pos)
        else:
            # neznámý příkaz
            help.append(_T('Unknown EPP command. Select one from EPP commands list (Type help).'))
            self.help_check_name(help,command_name)
        return ' '.join(command_line), '\n'.join(help), notice

    def help_check_name(self,help,command_name):
        'Join extended help if possible (for some commands).'
        if command_name in ('create','check','info','transfer'):
            help.append('%s: %s'%(_T('Try'),' '.join(['%s-%s'%(command_name,n) for n in ('contact','domain','nsset')])))
    
    def parse_cmd(self, command_name, cmd):
        "Parse command line. Returns errors. Save parsed values to self._dct."
        self._dct = dct = {}
        error=[]
        m = re.match('check_(\w+)\s+(.+)',cmd)
        if m:
            # úprava pro příkazy check_..., kde se jména seskupí do jednoho parametru name
            cmd = 'check_%s (%s)'%(m.group(1),m.group(2))
        vals = Message.cmd_params.get(command_name,None)
        if not vals:
            error.append("%s: '%s'"%(_T('Unknown command'),command_name))
            error.append('(%s: ${BOLD}help${NORMAL})'%(_T('For more type')))
            return error
        if not vals[1]: return error # bez parametrů
        command_line,command_help,notice = self.get_help(command_name)
        cols = [command_name]
        check = {command_name:[None,None,None]}
        for c in vals[1]:
            name = c[0] # sestaví se jména parametrů
            cols.append(name)
            check[name] = [None,None,None] # a povolené typy hodnot
            if len(c)>2: check[name][0]=c[2] # (type,max)
            if len(c)>3: check[name][1]=c[3] # (allowed-val,)
            if len(c)>4: check[name][2]=c[4] # 'depends'
        ers = data_parser.fill_dict(dct, cols, cmd)
        if ers: error.extend(ers)
        if len(dct) < vals[0]+1: # počet parametrů plus název příkazu
            error.append('%s %d.'%(_T('Missing values. Required minimum is'),vals[0]))
            error.append('%s: %s'%(_T('Type'),command_line))
            error.append('(%s: ${BOLD}help %s${NORMAL})'%(_T('For more type'),command_name.replace('_','-')))
        # check list and allowed values
        for key in dct.keys():
            if not check.get(key,None): continue # pokud se název nenachází v požadovaných jménech, tak se ignoruje.
            if type(dct[key]) == list:
                # pokud je parametr typu list
                if check[key][0] and check[key][0][0] == LIST:
                    max = check[key][0][1]
                    # tak se provede kontrola na maximání počet
                    if max and len(dct[key]) > max:
                        error.append(_T("Parameter '%s' expected max %d items, but %d occured.")%(key,max,len(dct[key])))
                else:
                    # a není v této části povolen
                    error.append("%s: '%s'"%(_T('List type is not allowed in param name'),key))
                    if len(dct[key]): dct[key] = dct[key][0] # taxe vezme jen první položka
            if check[key][1]:
                # pokud jsou stanoveny povinné hodnoty, provede se kontrola
                if type(dct[key]) == list:
                    vals = dct[key]
                else:
                    vals = (dct[key],)
                show_allowed=0 # indikátor pro zobrazení hlášky "You can use: key=(...defs...)"
                for value in vals:
                    if value not in check[key][1]:
                        show_allowed=1
                        error.append("%s: %s='%s'."%(_T('This value is not allowed'),key,value))
                if show_allowed:
                    error.append('%s: %s=(%s)'%(_T('You can use'),key,', '.join(check[key][1])))
            if check[key][2]:
                # pokud jsou definovány závislosti
                if not dct.has_key(check[key][2]):
                    # Nelze zadat, musí se splint závislost.
                    error.append(_T("Impossible. Value '%s' depends on the value '%s' (MUST be set).")%(key, check[key][2]))
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
                ,('version', 'objURI', 'language'))
        """
        cols = [('epp', 'command')
            ,('command', 'login')
            ,('login', 'clID', self._dct['username'])
            ,('login', 'pw', self._dct['password'])
            ]
        if self._dct.has_key('new-password'): cols.append(('login', 'newPW', self._dct['new-password']))
        cols.extend([
             ('login', 'options')
            ,('options', 'version', params[1][0])
            ,('options', 'lang', params[1][2])
            ,('login', 'svcs')
            ,('svcs', 'objURI', params[1][1])
            ,('command', 'clTRID', params[0])
        ])
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
            ('command', 'poll', '', (('op',self._dct['op']),) ),
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
        "params must have ('clTRID',('name','op','heslo'))"
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'transfer', '', (('op',self._dct['op']),)),
            ('transfer', '%s:transfer'%names[0], '', attr),
            ('%s:transfer'%names[0], '%s:%s'%names, self._dct['name']),
            ('%s:transfer'%names[0], '%s:authInfo'%names[0]),
            ('%s:authInfo'%names[0], '%s:pw'%names[0], self._dct['passw']),
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
        if not self._dct.has_key('valExDate'): return
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
        data.append(('%s:%s'%names,'%s:valExDate'%names[0], self._dct['valExDate']))

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
            ('contact:create','contact:id', dct['contact-id']),
            ('contact:create','contact:postalInfo'),
            ('contact:postalInfo','contact:name', dct['name'])] # required
        if dct.has_key('org'): data.append(('contact:postalInfo','contact:org', dct['org']))
        # --- BEGIN addr ------
        data.append(('contact:postalInfo','contact:addr')) # required
        self.__append_values__(data, dct, 'street', 'contact:addr', 'contact:street')
        data.append(('contact:addr','contact:city', dct['city'])) # required
        if dct.has_key('sp'): data.append(('contact:addr','contact:sp', dct['sp']))
        if dct.has_key('pc'): data.append(('contact:addr','contact:pc', dct['pc']))
        data.append(('contact:addr','contact:cc', dct['cc'])) # required
        # --- END addr ------
        if dct.has_key('voice'): data.append(('contact:create','contact:voice', dct['voice']))
        if dct.has_key('fax'): data.append(('contact:create','contact:fax', dct['fax']))
        data.append(('contact:create','contact:email',dct['email'])) # required
        # --- BEGIN disclose ------
        if dct.has_key('disclose'):
            data.append(('contact:create','contact:disclose','',(('flag',dct['disclose']),)))
            for key in ('name','org','addr','voice','fax','email'):
                if dct.has_key('disclose-%s'%key): data.append(('contact:disclose','contact:%s'%key,dct['disclose-%s'%key]))
        # --- END disclose ------
        if dct.has_key('vat'): data.append(('contact:create','contact:vat', dct['vat']))
        if dct.has_key('ssn'): data.append(('contact:create','contact:ssn', dct['ssn']))
        if dct.has_key('notifyEmail'): data.append(('contact:create','contact:notifyEmail', dct['notifyEmail']))
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
            ('domain:create','domain:name', dct['name'])]
        if dct.has_key('period'):
            if not dct.has_key('period-unit'):dct['period-unit']='y'
            data.append(('domain:create','domain:period',dct['period'], (('unit',dct['period-unit']),)))
        if dct.has_key('nsset'):data.append(('domain:create','domain:nsset',dct['nsset']))
        if dct.has_key('registrant'):data.append(('domain:create','domain:registrant',dct['registrant']))
        self.__append_values__(data, dct, 'contact', 'domain:create', 'domain:contact')
        data.extend((
            ('domain:create','domain:authInfo'),
            ('domain:authInfo','domain:pw', dct['pw'])
        ))
        if len(params)>2 and params[2]=='extensions': self.__enum_extensions__('create',data, params)
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_create_domain_enum(self, *params):
        'Extensions for enum.'
        self.assemble_create_domain(params[0], params[1], 'extensions')

    def __append_nsset__(self, tag_name, data, ns):
        """Supporting function for assemble_create_nsset().
        param ns can be: ns / addr / [addr,addr,] / [ns [addr,addr,]]
        """
        if type(ns)==list:
            for n in ns:
                self.__append_nsset__(tag_name, data, n)
        else:
            if re.search('[a-z]',ns, re.I):
                data.append(('nsset:%s'%tag_name, 'nsset:ns'))
                data.append(('nsset:ns', 'nsset:name',ns))
            else:
                data.append(('nsset:ns', 'nsset:addr',ns))
        
    def assemble_create_nsset(self, *params):
        "Assemble XML EPP command."
        errors = []
        dct = self._dct
        names = ('nsset',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'create'),
            ('create', 'nsset:create', '', attr),
            ('nsset:create','nsset:id', dct['id'])]
        # ns records
        if dct.has_key('name_and_addr'):
            if type(dct['name_and_addr']) == list:
                for ns in dct['name_and_addr']:
                    if type(ns) == list:
                        for n in ns:
                            self.__append_nsset__('create', data, n) # ns / addr / [addr,addr,] / [ns [addr,addr,]]
                    else:
                        self.__append_nsset__('create', data, ns) # záznam ns ze seznamu
            else:
                self.__append_nsset__('create', data, dct['name_and_addr']) # jednoduchý ns záznam ns
        self.__append_values__(data, dct, 'tech', 'nsset:create', 'nsset:tech')
        data.extend((
            ('nsset:create','nsset:authInfo'),
            ('nsset:authInfo','nsset:pw', dct['pw'])
        ))
        data.append(('command', 'clTRID', params[0]))
        if errors:
            self.join_errors(errors)
        else:
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
            ('domain:renew','domain:name', dct['name']),
            ('domain:renew','domain:curExpDate', dct['curExpDate']),
            ]
        if dct.has_key('period'):
            if not dct.has_key('period-unit'):dct['period-unit']='y'
            data.append(('domain:renew','domain:period',dct['period'], (('unit',dct['period-unit']),)))
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
            ('contact:update','contact:id', dct['contact-id']),
            ]
        if dct.has_key('add'):
            data.append(('contact:update', 'contact:add'))
            self.__append_attr__(data, dct, 'add', 'contact:add', 'contact:status','s')
        if dct.has_key('rem'):
            data.append(('contact:update', 'contact:rem'))
            self.__append_attr__(data, dct, 'rem', 'contact:rem', 'contact:status','s')
        # --- BEGIN chg ------ (nemůže to být uděláno přes if len(dct) > 4: protože  --key = vlaue)
        for name in ('name','org','street','city','sp','pc','cc','voice','fax','email','disclose','vat','ssn','notifyEmail'):
            if dct.has_key(name):
                data.append(('contact:update','contact:chg'))
                break
        tag_postalInfo=0
        if dct.has_key('name') or dct.has_key('org'):
            tag_postalInfo=1
            data.append(('contact:chg','contact:postalInfo'))
            if dct.has_key('name'): data.append(('contact:postalInfo','contact:name', dct['name']))
            if dct.has_key('org'): data.append(('contact:postalInfo','contact:org', dct['org']))
        for name in ('street','city','sp','pc','cc'):
            if dct.has_key(name):
                if not tag_postalInfo: data.append(('contact:chg','contact:postalInfo'))
                data.append(('contact:postalInfo','contact:addr'))
                break
        # --- BEGIN addr ------
        self.__append_values__(data, dct, 'street', 'contact:addr', 'contact:street')
        if dct.has_key('city'): data.append(('contact:addr','contact:city', dct['city']))
        if dct.has_key('sp'): data.append(('contact:addr','contact:sp', dct['sp']))
        if dct.has_key('pc'): data.append(('contact:addr','contact:pc', dct['pc']))
        if dct.has_key('cc'): data.append(('contact:addr','contact:cc', dct['cc']))
        # --- END addr ------
        if dct.has_key('voice'): data.append(('contact:chg','contact:voice', dct['voice']))
        if dct.has_key('fax'): data.append(('contact:chg','contact:fax', dct['fax']))
        if dct.has_key('email'): data.append(('contact:chg','contact:email',dct['email']))
        # --- BEGIN disclose ------
        if dct.has_key('disclose'):
            data.append(('contact:chg','contact:disclose','',(('flag',dct['disclose']),)))
            for key in ('name','org','addr','voice','fax','email'):
                if dct.has_key('disclose-%s'%key): data.append(('contact:disclose','contact:%s'%key,dct['disclose-%s'%key]))
        # --- END disclose ------
        if dct.has_key('vat'): data.append(('contact:chg','contact:vat', dct['vat']))
        if dct.has_key('ssn'): data.append(('contact:chg','contact:ssn', dct['ssn']))
        if dct.has_key('notifyEmail'): data.append(('contact:chg','contact:notifyEmail', dct['notifyEmail']))
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
            ('domain:update','domain:name', dct['name']),
            ]
        if dct.has_key('add'):
            data.append(('domain:update', 'domain:add'))
            self.__append_attr__(data, dct, 'add', 'domain:add', 'domain:status','s')
        if dct.has_key('rem'):
            data.append(('domain:update', 'domain:rem'))
            self.__append_attr__(data, dct, 'rem', 'domain:rem', 'domain:status','s')
        # --- BEGIN chg ------ (nemůže to být uděláno přes if len(dct) > 4: protože  --key = vlaue)
        for name in ('nsset','registrant','pw','ext'):
            if dct.has_key(name):
                data.append(('domain:update','domain:chg'))
                break
        if dct.has_key('nsset'): data.append(('domain:chg','domain:nsset', dct['nsset']))
        if dct.has_key('registrant'): data.append(('domain:chg','domain:registrant', dct['registrant']))
        if dct.has_key('pw'):
            data.append(('domain:chg','domain:authInfo'))
            data.append(('domain:authInfo','domain:pw', dct['pw']))
        if len(params)>2 and params[2]=='extensions': self.__enum_extensions__('update',data, params,'chg')
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    def assemble_update_domain_enum(self, *params):
        "Assemble XML EPP command"
        if len(params)<2: params = (params[0],None)
        self.assemble_update_domain(params[0], params[1], 'extensions')

    def __update_nsset__(self, data, nsset, tech=None, stat=None):
        """Support of assemble_update_nsset()

        nsset value can acquired there value types:
        1.nsset: name
        2.nsset: (name, name)/(name addr)
        3.nsset: ((name addr),(name addr))
        4.nsset: ((name (addr)),(name (addr)))
        """
        # nsset: ns (addr,...)
        if type(nsset)==list:
            # (name, name) nebo ((name, addr), (name, addr))
            for ns_list in nsset:
                if type(ns_list)==list:
                    # (name, name) nebo ((name, addr), (name, addr))
                    for ns_addr in ns_list:
                        # name, addr
                        if type(ns_addr)==list:
                            for item in ns_addr:
                                self.__append_nsset__('add', data, item) # 4.
                        else:
                            self.__append_nsset__('add', data, ns_addr) # 3.
                else:
                    # 2. name or address
                    self.__append_nsset__('add', data, ns_list)
        else:
            # 1. simple name
            data.append(('nsset:add','nsset:ns'))
            data.append(('nsset:ns','nsset:name',nsset))
        if tech: self.__append_values__(data, {'tech':tech}, 'tech', 'nsset:add', 'nsset:tech')
        if stat: self.__append_attr__(data, {'stat':stat}, 'stat', 'nsset:add', 'nsset:status','s')

    def assemble_update_nsset(self, *params):
        """Assemble XML EPP command. 
        params = ('clTRID', ...)
        update-nsset id 
            (add 0-1
                (ns 0-9
                    name
                    (addr 0-9)
                )
                (tech 0-n)
                (status 0-6)
            )
            (rem 0-1
                (name 0-9)
                (tech 0-n)
                (status 0-6)
            )
            (chg 0-1 (pw 0-1))
        """
        print "="*30
        dct = self._dct
        names = ('nsset',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s-%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        data = [
            ('epp', 'command'),
            ('command', 'update'),
            ('update', 'nsset:update', '', attr),
            ('nsset:update','nsset:id', dct['id']),
            ]
        if dct.has_key('add'):
            # add: (nsset,...), tech, stat
            # nsset: ns (addr,...)
            data.append(('nsset:update','nsset:add'))
            if type(dct['add'])==list:
                # (nsset,...), tech, stat
                nssets = dct['add'][0]
                tech = stat = None
                if len(dct['add'])>1: tech = dct['add'][1]
                if len(dct['add'])>2: stat = dct['add'][2]
                self.__update_nsset__(data, nssets, tech, stat)
            else:
                # simple nsset name
                self.__update_nsset__(data, dct['add'])
        if dct.has_key('rem'):
            data.append(('nsset:update','nsset:rem'))
            # name, tech, status
            if type(dct['rem'])==list: # name
                self.__append_values__(data, {'name':dct['rem'][0]}, 'name', 'nsset:rem', 'nsset:name')
                if len(dct['rem'])>1: # tech
                    self.__append_values__(data, {'tech':dct['rem'][1]}, 'tech', 'nsset:rem', 'nsset:tech')
                if len(dct['rem'])>2: # status
                    self.__append_attr__(data, {'stat':dct['rem'][2]}, 'stat', 'nsset:rem', 'nsset:status','s')
            else:
                # name only
                data.append(('nsset:rem','nsset:name',dct['rem']))
        # --- BEGIN chg ------ (nemůže to být uděláno přes if len(dct) > 4: protože  --key = vlaue)
        if dct.has_key('pw'):
            data.append(('nsset:update','nsset:chg'))
            data.append(('nsset:chg','nsset:authInfo'))
            data.append(('nsset:authInfo','nsset:pw', dct['pw']))
        data.append(('command', 'clTRID', params[0]))
        self.__assemble_cmd__(data)

    #===========================================

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
        errors = epp.parse_cmd(cmd_name, cmd)
        if errors:
            print errors
        else:
            getattr(epp,'assemble_%s'%cmd_name)('llcc002#06-06-16at13:21:30',('1.0', 'objURI', 'LANG'))
            errors, xmlepp = epp.get_results()
            print errors, xmlepp
            if xmlepp:
                print manag.is_epp_valid(xmlepp)
        print '='*60

if __name__ == '__main__':
    # Test na jednotlivé příkazy
    commands1 = (
     'hello',
     'login john mypass "my new pass!"',
     'logout',
     'info_domain',
     'info_contact buzz-buzz "lorem ipsum"',
     'check_domain nic.cz cin.cz',
     'check_contact buzz-buzz "lorem ipsum"',
     'transfer_domain name-domain request password',
     'transfer_nsset name-nsset request password',
     'poll req',
    )
    commands2 = (
     'create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 0 d-name "d org." "ulice číso město" +21321313 +734321 pepa@jojo.com vat-test ssn-test notify@semka.net',
     'create_domain pokus.cz heslo 3 m nsset registr ("Na potůčku","U příhody")',
     'create_domain_enum pokus.cz heslo 3 m nsset registr ("Na potůčku","U příhody") 2006-06-08',
     'create_nsset exampleNsset passw ns1.domain.net',
     'create_nsset exampleNsset passw ns1.domain.net',
     'create_nsset exampleNsset passw (ns1.domain.net 194.23.54.1)',
     'create_nsset exampleNsset passw (ns1.domain.net ns2.domain.net)',
     'create_nsset exampleNsset passw ((ns1.domain.net 194.23.54.1) ns2.domain.net)',
     'create_nsset exampleNsset passw ((ns1.domain.net (194.23.54.1 194.23.54.2)) ns2.domain.net)',
     'create_nsset exampleNsset passw ((ns1.domain.net (194.23.54.1 194.23.54.2)) (ns2.domain.net (196.23.54.1 196.23.54.2))) tech-contact',
     'create_nsset exampleNsset passw (ns1.domain.net 194.23.54.1 194.23.54.2 ns2.domain.net 196.23.54.1 196.23.54.2) tech-contact',
    )
    commands3 = (
     'delete_contact pokus',
     'delete_domain pokus.cz',
     'delete_nsset pokus',
    )
    commands4 = (
     'renew_domain nic.cz 2023-06-02 6 y',
     'renew_domain_enum nic.cz 2023-06-02 6 y 2006-08-09',
    )
    commands5 = (
     'update_contact id-jouda clientDeleteProhibited',
     'update_contact id-jouda linked ok "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 0 d-name "d org." "ulice číso město" +21321313 +734321 pepa@jojo.com vat-test ssn-test notify@semka.net',
     'update_domain nic.cz',
     'update_domain nic.cz ok ok nsset registrant password',
     'update_domain_enum 1.1.1.1.1.arpa64.net () () nsset registrant password 2006-06-08',
     'update_domain_enum nic.cz',
)
    commands6 = (
    'update_nsset nic.cz ns1.nic.cz',
    'update_nsset nic.cz (ns-add1.nic.cz ns-add2.nic.cz) ns-rem1.nic.cz password',
    'update_nsset nic.cz ((ns-add1.nic.cz ns-add2.nic.cz) tech-add ok) (ns-rem1.nic.cz ns-rem2.nic.cz) password',
    'update_nsset nic.cz ((ns-add1.nic.cz 127.0.0.1 ns-add2.nic.cz 127.0.2.1) tech-add ok) ((ns-rem1.nic.cz, ns-rem2.nic.cz) tech-rem clientDeleteProhibited) password',
    'update_nsset nic.cz ((ns-add1.nic.cz 127.0.0.1 127.0.0.2 ns-add2.nic.cz 127.0.2.1 127.0.2.2) tech-add ok) () password',
    'update_nsset nic.cz (((ns-add1.nic.cz 127.0.0.1 127.0.0.2)(ns-add2.nic.cz 127.0.2.1 127.0.2.2)) tech-add ok) () password',
    'update_nsset nic.cz (((ns-add1.nic.cz (127.0.0.1 127.0.0.2))(ns-add2.nic.cz (127.0.2.1 127.0.2.2))) ("first tech cont","sec tech contact") ok) ((ns-rem1.nic.cz, ns-rem2.nic.cz) "rem tech contact" clientDeleteProhibited) password',
    )
##    test(commands1)
##    test(commands2)
##    test(commands3)
##    test(commands4)
    test(commands6)

