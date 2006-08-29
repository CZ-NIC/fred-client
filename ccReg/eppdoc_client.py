# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
import eppdoc_assemble
from translate import _T, options

UNBOUNDED = eppdoc_assemble.UNBOUNDED

# Help
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
   'update':_T("""The EPP "update" command is used to update an instance of an existing object."""),
   'disclose':_T('Names what are not included into disclose list are set to opposite value of the disclose flag value.'),
   'ssn':_T("""   SSN types can be: 
      op       number identity card
      rc       number of birth
      passport number of passport
      mpsv     number of Ministry of Labour and social affairs
      ico      number of company"""),
    'list':_T("""The EPP "list" command is used to list all ID of an existing object owning by registrant."""),
}

class Message(eppdoc_assemble.Message):
    "Client EPP commands."
    # transfer op attribute allowed values:
    # transfer_op = ('request','approve','cancel','query','reject')
    update_status = ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 
        'linked', 'ok', )
        #'serverDeleteProhibited', 'serverTransferProhibited', 'serverUpdateProhibited')
    # format:
    # command-name: (param-name, (min,max), (list of required), 'help', 'example', 'pattern', (list of children)
    command_params = {
        'hello': (0, (('',(0,0),(),'','','',()),), _T('The EPP "hello" request a "greeting" response message from an EPP server at any time.'),()),
        'logout': (0, (('',(0,0),(),'','','',()),), _T('The EPP "logout" command is used to end a session with an EPP server.'),()),
        #----------------------------------------------------
        'login': (2,(
            ('username',(1,1),(),_T('your login name'),'my_login_name','',()),
            ('password',(1,1),(),_T('your password'),'my_password','',()),
            ('new-password',(0,1),(),_T('new password'),'my_new_password','',()),
        ),_T("""
   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session."""),('login john mypass "my new pass!"',)),
        #----------------------------------------------------
        'info_contact': (1,(
            ('name',(1,1),(),_T('contact name'),'CID:ID01','',()),
        ),notice['info'],('info_contact contact-ID',)),
        'info_domain': (1,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
        ),notice['info'],('info_domain my-domain.cz',)),
        'info_nsset': (1,(
            ('name',(1,1),(),_T('nsset name'),'NSSET_ID','',()),
        ),notice['info'],('info_nsset NSSET_ID',)),
        #----------------------------------------------------
        'check_contact': (1,(
            ('name',(1,UNBOUNDED),(),_T('contact name'),'CID:ID01','',()),
        ),notice['check'],('check_contact my-contact1 my-contact2',)),
        'check_domain': (1,(
            ('name',(1,UNBOUNDED),(),_T('domain name'),'mydomain.cz','',()),
        ),notice['check'],('check_domain domain1.cz domain2.cz',)),
        'check_nsset': (1,(
            ('name',(1,UNBOUNDED),(),_T('nsset name'),'NSSET_ID','',()),
        ),notice['check'],('check_nsset nsset1 nsset2',)),
        #----------------------------------------------------
        'poll': (1,(
            ('op',(1,1),('req','ack'),_T('query type'),'','',()),
            ('msg_id',(0,1),(),_T('index of message, required with op=ack!'),'123','',()),
        ),_T('The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients.'),('poll req','poll ack 4',)),
        #----------------------------------------------------
        'transfer_contact': (2,(
            ('name',(1,1),(),_T('contact id'),'CID:ID01','',()),
            ('passw',(1,1),(),_T('password'),'mypassword','',()),
        ),notice['transfer'],('transfer_contact CID:ID01 password',)),
        #----------------------------------------------------
        'transfer_nsset': (2,(
            ('name',(1,1),(),_T('nsset name'),'NSSET_ID','',()),
            #('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),'mypassword','',()),
        ),notice['transfer'],('transfer_nsset name-nsset password',)),
        #----------------------------------------------------
        'transfer_domain': (2,(
            ('name',(1,1),(),_T('domain name'),'domain.cz','',()),
            #('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),'mypassword','',()),
        ),notice['transfer'],('transfer_domain name-domain password',)),
        #----------------------------------------------------
        'create_contact': (6,(
            ('contact_id',(1,1),(),_T('your contact ID'),'CID:ID01','',()),
            ('name',(1,1),(),_T('your name'),u'Jan Novák','',()), # odtud shoda s update contact
            ('email',(1,1),(),_T('your email'),'info@mymail.cz','',()),
            ('city',(1,1),(),_T('your city'),'Praha','',()),
            ('cc',(1,1),(),_T('country code'),'CZ',_T('country code'),()),
            ('pw',(1,1),(),_T('password'),'mypassword',_T('password'),()), # required end
            ('org',(0,1),(),_T('organisation name'),'Firma s.r.o.','',()),
            ('street',(0,3),(),_T('street'),u'Národní třída 1230/12','',()),
            ('sp',(0,1),(),_T('state or province'),_T('state or province'),'',()),
            ('pc',(0,1),(),_T('postal code'),'12000',_T('postal code'),()),
            ('voice',(0,1),(),_T('voice (phone number)'),'+420.222745111','',()),
            ('fax',(0,1),(),_T('fax number'),'+420.222745111','',()),
            ('disclose',(0,1),(),_T('disclose'),'','',(
                ('flag',(1,1),('y','n'),_T('disclose flag (default y)'),'','',()),
##                data pro které se nastaví příznak, data for with is set flag of value
                ('data',(0,len(eppdoc_assemble.contact_disclose)),eppdoc_assemble.contact_disclose,_T('data for with is set the flag value'),'','',()),
            )),
            ('vat',(0,1),(),_T('VAT (Value-added tax)'),'7035555556','',()), # daˇnový identifikátor
            ('ssn',(0,1),(),_T('SSN (Social security number)'),'','',( # mpsv: identifikátor Ministerstva práce a sociálních věcí
                ('type',(1,1),('op','rc','passport','mpsv','ico'),_T('SSN type'),'op','',()),
                ('number',(1,1),(),_T('SSN number'),'8888888856','',()),
            )),
            ('notify_email',(0,1),(),_T('notify email'),'info@mymail.cz','',()),
            ),'%s\n   %s\n%s'%(notice['create'],notice['disclose'],notice['ssn']),("create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword 'Firma s.r.o.' 'Narodni trida 1230/12' '' 12000 +420.222745111 +420.222745111 (y (org fax email)) 7035555556 (op 8888888856) info@mymail.cz",)),
        #----------------------------------------------------
        'create_domain': (2,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
            ('pw',(1,1),(),_T('password'),'mypassword','',()),
            ('nsset',(1,1),(),_T('nsset'),'NSSETID','',()),
            ('registrant',(1,1),(),_T('registrant'),'REGID','',()),
            ('period',(0,1),(),_T('period'),'','',(
                ('num',(1,1),(),_T('number of months or years'),'3','',()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),'','',()),
            )),
            ('admin',(0,UNBOUNDED),(),_T('admin'),'ADMIN_ID','',()),
            ('val_ex_date',(0,1),(),_T('valExDate'),'2008-12-03','',()),
            ),notice['create'],(
                'create_domain domain.cz password nsset1 reg-id (3 y) (handle1,handle2)',
                'create_domain 1.1.1.7.4.5.2.2.2.0.2.4.e164.arpa password nsset1 reg-id (3 y) (handle1,handle2) 2006-06-08'
            )),
        #----------------------------------------------------
        'create_nsset': (2,(
            ('id',(1,1),(),_T('nsset ID'),'NSSETID','',()),
            ('pw',(1,1),(),_T('password'),'mypassword','',()),
            ('dns',(1,9),(),_T('LIST of DNS'),'','',(
                ('name',(1,1),(),_T('nsset name'),'my.dns1.cz','',()),
                ('addr',(0,UNBOUNDED),(),_T('nsset address'),'217.31.207.130','',()),
            )),
            ('tech',(0,UNBOUNDED),(),_T('tech contact'),'CID:ID01','',()),

            ),notice['create'],(
                'create_nsset example passw',
                'create_nsset nsset1 passw ((ns1.domain.cz (217.31.207.130 217.31.207.129)),(ns2.domain.cz (217.31.206.130 217.31.206.129)),(ns3.domain.cz (217.31.205.130 217.31.205.129))) reg-id'
            )),
        #----------------------------------------------------
        'delete_contact': (1,(
             ('id',(1,1),(),_T('contact ID'),'CID:ID01','',()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'delete_domain': (1,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'delete_nsset': (1,(
            ('id',(1,1),(),_T('nsset ID'),'NSSET_ID','',()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'renew_domain': (2,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
            ('cur_exp_date',(1,1),(),_T('current expiration date'),'2006-12-03','',()),
            ('period',(0,1),(),_T('period'),'','',(
                ('num',(1,1),(),_T('number of months or years'),'3','',()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),'','',()),
            )),
            ),notice['renew'],('renew_domain nic.cz 2008-06-02 (6 y)',)),
        #----------------------------------------------------
        'renew_domain_enum': (2,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
            ('cur_exp_date',(1,1),(),_T('current expiration date'),'2006-12-03','',()),
            ('period',(0,1),(),_T('period'),'','',(
                ('num',(1,1),(),_T('number of months or years'),'3','',()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),'','',()),
            )),
            ('valExDate',(0,1),(),_T('valExDate'),'2008-12-03','',()),
            ),notice['renew'],('renew_domain_enum nic.cz 2023-06-02 () 2006-08-09',)),
        #----------------------------------------------------
        'update_contact': (1,(
            ('contact_id',(1,1),(),_T('your contact ID'),'CID:ID01','',()),
            ('add',(0,5),update_status,_T('add status'),'','',()),
            ('rem',(0,5),update_status,_T('remove status'),'','',()),
            ('chg',(0,1),(),_T('change status'),'','',(
                ('postal_info',(0,1),(),_T('postal informations'),'','',(
                    ('name',(0,1),(),_T('name'),u'Jan Novák','',()),
                    ('org',(0,1),(),_T('organisation name'),'Firma s.r.o.','',()),
                    ('addr',(0,1),(),_T('address'),'','',(
                        ('street',(0,3),(),_T('street'),u'Na národní 1234/14','',()),
                        ('city',(1,1),(),_T('city'),'Praha','',()),
                        ('sp',(0,1),(),_T('sp'),'','',()),
                        ('pc',(0,1),(),_T('pc'),'12000','',()),
                        ('cc',(1,1),(),_T('cc'),'CZ','',()),
                    )),
                )),
                ('voice',(0,1),(),_T('voice (phone number)'),'+420.222745111','',()),
                ('fax',(0,1),(),_T('fax number'),'+420.222745111','',()),
                ('email',(0,1),(),_T('your email'),'info@mymail.cz','',()),
                ('pw',(0,1),(),_T('password'),'mypassword','',()),
                ('disclose',(0,1),(),_T('disclose'),'','',(
                    ('flag',(1,1),('y','n'),_T('disclose flag (default y)'),'','',()),
                    ('data',(0,len(eppdoc_assemble.contact_disclose)),eppdoc_assemble.contact_disclose,_T('data for with is set the flag value'),'','',()),
                )),
                ('vat',(0,1),(),_T('VAT'),'7035555556','',()),
                ('ssn',(0,1),(),_T('SSN (Security social number)'),'','',(
                    ('type',(1,1),('op','rc','passport','mpsv','ico'),_T('SSN type'),'op','',()),
                    ('number',(1,1),(),_T('SSN number'),'8888888856','',()),
                )),
                ('notify_email',(0,1),(),_T('notify email'),'notify@mymail.cz','',()),
            )),
            ),'%s\n%s'%(notice['update'],notice['disclose']),(
                    'update_contact CID:ID01 clientDeleteProhibited',
                    'update_contact CID:ID01 (clientDeleteProhibited linked ok)',
                    "update_contact CID:ID01 clientTransferProhibited (clientDeleteProhibited, clientUpdateProhibited) (('Jan Nowak' 'Firma s.r.o.' (('Na narodni 1230/12', 'Americka 12') Praha Vinohrady 12000 CZ)) +420.222745111 +420.222745111 info@mymail.cz mypassword (y (org, voice, email)) 7035555556 (ico 8888888856) notify@mymail.cz)",
                    "update_contact CID:ID01 () () (() '' '' '' '' () '' () change.only@notify-mail.cz)",
            )),
        #----------------------------------------------------
        'update_domain': (1,(
            ('name',(1,1),(),_T('domain name'),'mydomain.cz','',()),
            ('add',(0,1),(),_T('add status'),'','',(
                ('admin',(0,UNBOUNDED),(),_T('admin'),'CID:ID01','',()),
                ('status',(0,8),update_status,_T('status'),'','',()),
            )),
            ('rem',(0,1),(),_T('remove status'),'','',(
                ('admin',(0,UNBOUNDED),(),_T('admin'),'CID:ID01','',()),
                ('status',(0,8),update_status,_T('status'),'','',()),
            )),
            ('chg',(0,1),(),_T('change status'),'','',(
                ('nsset',(0,1),(),_T('nsset'),'NSSET_ID','',()),
                ('registrant',(0,1),(),_T('registrant'),'CID:ID01','',()),
                ('auth_info',(0,1),(),_T('authInfo'),'','',(
                    ('pw',(0,1),(),_T('password'),'mypassword','',()),
                    #('ext',(0,1),(),_T('ext'),'','',()),
                )),
            )),
            ('val_ex_date',(0,1),(),_T('valExDate'),'2008-12-03','',()),
            ),notice['update'],(
                'update_domain mydomain.cz ((CID:ID01, CID:ID02) clientTransferProhibited) (CID:ID03 clientDeleteProhibited) (NSSID:NSSET01 CID:ID04 (mypass))',
                'update_domain 1.1.1.7.4.5.2.2.2.0.2.4.e164.arpa ((CID:ID01, CID:ID02) clientTransferProhibited) (CID:ID03 clientDeleteProhibited) (NSSID:NSSET01 CID:ID04 (mypass)) 2008-12-03',
            )),
        #----------------------------------------------------
        'update_nsset': (1,(
            ('id',(1,1),(),_T('nsset ID'),'NSSET_ID','',()),
            ('add',(0,1),(),_T('add part'),'','',(
                ('dns',(0,9),(),_T('list of DNS'),'','',(
                    ('name',(1,1),(),_T('nsset name'),'my.dns.cz','',()),
                    ('addr',(0,UNBOUNDED),(),_T('IP address'),'217.31.207.130','',()),
                )),
                ('tech',(0,UNBOUNDED),(),_T('technical contact'),'CID:ID01','',()),
                ('status',(0,6),update_status,_T('status'),'','',()),
            )),
            ('rem',(0,1),(),_T('remove part'),'','',(
                ('name',(0,9),(),_T('name'),'my.dns.cz','',()),
                ('tech',(0,UNBOUNDED),(),_T('technical contact'),'CID:ID01','',()),
                ('status',(0,6),update_status,_T('status'),'','',()),
            )),
            ('chg',(0,1),(),_T('change part'),'','',(
                ('pw',(0,1),(),_T('password'),'new_password','',()),
                #('ext',(0,1),(),_T('ext'),'','',()),
            )),
            ),notice['update'],(
                "update_nsset nsset1 (((ns1.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132)), (ns2.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132))) (tech1, tech2, tech3) (ok, clientTransferProhibited)) (((rem1.dns.cz, rem2.dns.cz) (tech-rem01, tech-rem02) serverUpdateProhibited)) (password)",
            )),
        #----------------------------------------------------
        'list_contact': (0,(('',(0,0),(),'','','',()),),notice['list'],()),
        'list_nsset': (0,(('',(0,0),(),'','','',()),),notice['list'],()),
        'list_domain': (0,(('',(0,0),(),'','','',()),),notice['list'],()),
        #----------------------------------------------------

    }
    #----------------------------------
    # OUTPUT SORTED BY NAMES
    #----------------------------------
    sort_by_names = {
    
      'info_contact': ('contact',(
        'id','roid',
        'crID','clID','upID',
        'crDate','trDate','upDate',
        'name','org','street','city','sp','pc','cc','pw',
        'voice','fax','email','notifyEmail',
        'status.s','disclose','hide',
        'vat','ssn.type','ssn',
        )),

      'info_domain': ('domain',(
        'name','roid',
        'crID','trID','clID','upID',
        'crDate','trDate','upDate','exDate','renew',
        'nsset','pw','status.s','registrant','admin',
        )),

      'info_nsset': ('nsset',(
        'id','roid',
        'crID','clID','upID',
        'crDate','trDate','upDate',
        'pw','status.s','tech','ns',
        )),
        
    }

    def get_sort_by_names(self, command_name):
        'Prepare column names for sorted output answer.'
        scope = Message.sort_by_names.get(command_name,None)
        if scope:
            names = map(lambda name: '%s:%s'%(scope[0],name),scope[1])
        else:
            names = []
        return names

    
    def __init__(self):
        eppdoc_assemble.Message.__init__(self)
        self._command_params = Message.command_params
    

def test(commands):
    import pprint
    import session_base
    manag = session_base.ManagerBase()
    epp = Message()
    manag.load_config()
    print "#"*60
    for cmd in commands:
        print "COMMAND:",cmd
        m = re.match('(\S+)',cmd)
        if not m: continue
        cmd_name = m.group(1)
        epp.reset()
        errors, example, stop = epp.parse_cmd(cmd_name, cmd, manag._conf, 0, 2)
        if stop == 2: break # User press Ctrl+C or Ctrl+D
        if errors:
            print "Errors:",errors
        else:
            getattr(epp,'assemble_%s'%cmd_name)('llcc002#06-06-16at13:21:30',('1.0', ('objURI',), ('extURI',), 'LANG'))
            errors, xmlepp = epp.get_results()
            print xmlepp
            if errors:
                print "Errors:",errors
            if xmlepp:
                print 'VALID?',manag.is_epp_valid(xmlepp)
        print "EXAMPLE:",epp.get_command_line()
        print '='*60

def test_help(command_names):
    import terminal_controler
    colored_output = terminal_controler.TerminalController()
    colored_output.set_mode(options['color'])
    epp = Message()
    for command_name in command_names:
        command_line,command_help,notice, examples = epp.get_help(command_name)
        print colored_output.render(command_line)
        print colored_output.render(command_help)
        print colored_output.render(notice)
        print '\nExamples:'
        print '\n'.join(examples)
        print '\n\n'

if __name__ == '__main__':
    # Test na jednotlivé příkazy
    test(("update_contact reg-id () () (('' '' ('' Město '' '' CZ)) '' '' '' (0) '' '' notify@mail.cz)",))
