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
""")
}

class Message(eppdoc.Message):
    "Client EPP commands."
    # transfer op attribute allowed values:
    transfer_op = ('request','approve','cancel','query','reject')
    # format:
    # command-name: (required, (param-name, parameter-help [,(param-list,max)[, param-values]]), command-help )
    cmd_params = {
        'hello': (0,None, _T('The EPP "hello" request a "greeting" response message from an EPP server at any time.')),
        'logout': (0,None, _T('The EPP "logout" command is used to end a session with an EPP server.')),
        #----------------------------------------------------
        'login': (2,(
             ('username',_T('your login name'))
            ,('password',_T('your password'))
            ,('new-password',_T('new password'))
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
             ('name',_T('domain name'))
            ,('op',_T('query type'),None,transfer_op)
            ,('passw',_T('password'))
        ),notice['transfer']),
        #----------------------------------------------------
        'transfer_nsset': (3,(
             ('name',_T('nsset name'))
            ,('op',_T('query type'),None,transfer_op)
            ,('passw',_T('password'))
        ),notice['transfer']),
        #----------------------------------------------------
        'create_contact': (5,(
             ('contact-id',_T('your contact ID'))
            ,('name',_T('your name'))
            ,('email',_T('your email'))
            ,('city',_T('your city'))
            ,('cc',_T('country code')) # required end
            ,('org',_T('organisation name'))
            ,('street',_T('street'),(LIST,3))
            ,('sp',_T('sp'))
            ,('pc',_T('postal code'))
            ,('voice',_T('voice (phone number)'))
            ,('fax',_T('fax number'))
            ,('disclose',_T('disclose flag'),None,('0','1'))
            ,('disclose-name',_T('disclose name'))
            ,('disclose-org',_T('disclose organisation name'))
            ,('disclose-addr',_T('disclose address'))
            ,('disclose-voice',_T('disclose voice (phone)'))
            ,('disclose-fax',_T('disclose fax'))
            ,('disclose-email',_T('disclose email'))
            ,('vat',_T('VAT'))
            ,('ssn',_T('SSN'))
            ,('notifyEmail',_T('notify email'))
            ),notice['create'])
        }

    def __get_help_note__(self, help, params, pos):
        'Support for get_help().'
        sep=('\t','\t\t')[len(params[pos][0])<8]
        note=[]
        if len(params[pos])>2 and params[pos][2] and params[pos][2][0]==LIST:
            note.append(_T('Can be LIST of values, max %d items: (%s)')%(params[pos][2][1],' '.join(['item']*params[pos][2][1])))
        if len(params[pos])>3:
            note.append('%s: (%s)'%(_T('MUST be one of'),', '.join(params[pos][3])))
        help.append('\t%s%s(%s) %s'%(params[pos][0],sep,params[pos][1],' '.join(note)))

    def get_help(self, command_name):
        "Returns help for selected command: (command_line, complete help)."
        command_line = []
        help=[]
        notice=''
        display_cmd = command_name
        # v příkazu zrušit spojovníky
        m = re.match('(\S+)(.*)',command_name)
        if m:
            display_cmd = m.group(1)
            command_name = '%s%s'%(m.group(1).replace('-','_'), m.group(2))
        if Message.cmd_params.has_key(command_name):
            # příkaz existuje
            required,params,notice = Message.cmd_params[command_name]
            command_line = ['${BOLD}%s${NORMAL}'%display_cmd]
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
            return error
        if not vals[1]: return error # bez parametrů
        command_line,command_help,notice = self.get_help(command_name)
        cols = [command_name]
        check = {command_name:[None,None]}
        for c in vals[1]:
            name = c[0] # sestaví se jména parametrů
            cols.append(name)
            check[name] = [None,None] # a povolené typy hodnot
            if len(c)>2: check[name][0]=c[2] # (type,max)
            if len(c)>3: check[name][1]=c[3] # (allowed-val,)
        ers = data_parser.fill_dict(dct, cols, cmd)
        if ers: error.extend(ers)
        if len(dct) < vals[0]+1: # počet parametrů plus název příkazu
            error.append('%s %d.'%(_T('Missing values. Required minimum is'),vals[0]))
            error.append('%s: %s'%(_T('Type'),command_line))
        # check list and allowed values
        for key in dct.keys():
            if not check.get(key,None): continue # pokud se název neneachází v požadovaných jménech, tak se ignoruje.
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
                show_allowed=0
                for value in vals:
                    if value not in check[key][1]:
                        show_allowed=1
                        error.append("%s: %s='%s'."%(_T('This value is not allowed'),key,value))
                if show_allowed:
                    error.append('%s: %s=(%s)'%(_T('You can use'),key,', '.join(check[key][1])))
        return error

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:].replace('_','-') for name in dir(self.__class__) if name[:9]=='assemble_']

    #===========================================
    #
    # Process commands
    #
    #===========================================
    def __assemble_cmd__(self, data):
        'Support for assemble_...() functions.'
        self.create()
        for v in data:
            value, attr = None,None
            parent_name, name = v[0:2]
            if len(v)>2: value = v[2]
            if len(v)>3: attr  = v[3]
            self.new_node_by_name(parent_name, name, value, attr)

    def __asseble_command__(self, cols, params):
        """Internal fnc for assembly commands info, check. 
        cols=('check','contact','id')
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
        names = self._dct['name']
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
        self.__asseble_command__(('check','contact','id'), params)
        
    def assemble_check_domain(self, *params):
        self.__asseble_command__(('check','domain','name'), params)
        
    def assemble_check_nsset(self, *params):
        self.__asseble_command__(('check','nsset','id'), params)

    def assemble_info_contact(self, *params):
        self.__asseble_command__(('info','contact','id'), params)

    def assemble_info_domain(self, *params):
        self.__asseble_command__(('info','domain','name'), params)

    def assemble_info_nsset(self, *params):
        self.__asseble_command__(('info','nsset','id'), params)

    def assemble_poll(self, *params):
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'poll', '', (('op',self._dct['op']),) ),
            ('command', 'clTRID', params[0])
        ))

    def __assemble_transfer__(self, names, params):
        "params must have ('clTRID',('name','op','heslo'))"
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
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
    def assemble_create_contact(self, *params):
        "Assemble XML EPP command."
        dct = self._dct
        names = ('contact',)
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
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
        if dct.has_key('street'):
            if type(dct['street']) == list:
                for street in dct['street']:
                    data.append(('contact:addr','contact:street',street))
            else:
                data.append(('contact:addr','contact:street',dct['street']))
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

##    def assemble_delete(self, *params):
##        self.load_EPP_template('delete')
##    def assemble_renew(self, *params):
##        self.load_EPP_template('renew')
##    def assemble_update(self, *params):
##        self.load_EPP_template('update')

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
    epp = Message()
    for cmd in commands:
        print "COMMAND:",cmd
        m = re.match('(\S+)',cmd)
        if not m: continue
        cmd_name = m.group(1)
        errors = epp.parse_cmd(cmd_name, cmd)
        if errors:
            print errors
        else:
            getattr(epp,'assemble_%s'%cmd_name)('llcc002#06-06-16at13:21:30',('1.0', 'objURI', 'LANG'))
            errors, xmlepp = epp.get_results()
            print errors, xmlepp
        print '-'*60

if __name__ == '__main__':
    # Test na jednotlivé příkazy
    commands = (
     'create_contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 0 d-name "d org." "ulice číso město" +21321313 +734321 pepa@jojo.com vat-test ssn-test notify@semka.net',
     'transfer_domain name-domain request password',
     'transfer_nsset name-nsset request password',
     'poll req',
     'hello',
     'login john mypass "my new pass!"',
     'logout',
     'info_domain',
     'info_contact buzz-buzz "lorem ipsum"',
     'check_domain',
     'check_contact buzz-buzz "lorem ipsum"',
    )
    test(commands)
