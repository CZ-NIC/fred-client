# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
import eppdoc_assemble
import translate
_T = translate._T

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
   'update':_T("""The EPP "update" command is used to update an instance of an existing object.""")
}

class Message(eppdoc_assemble.Message):
    "Client EPP commands."
    # transfer op attribute allowed values:
    transfer_op = ('request','approve','cancel','query','reject')
    update_status = ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok', 'serverDeleteProhibited', 'serverTransferProhibited', 'serverUpdateProhibited')
    # format:
    # command-name: (param-name, (min,max), (list of required), 'help', (list of children)
    command_params = {
        'hello': (0, (('',(0,0),(),'',()),), _T('The EPP "hello" request a "greeting" response message from an EPP server at any time.'),()),
        'logout': (0, (('',(0,0),(),'',()),), _T('The EPP "logout" command is used to end a session with an EPP server.'),()),
        #----------------------------------------------------
        'login': (2,(
            ('username',(1,1),(),_T('your login name'),()),
            ('password',(1,1),(),_T('your password'),()),
            ('new-password',(0,1),(),_T('new password'),()),
        ),_T("""
   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session."""),('login john mypass "my new pass!"',)),
        #----------------------------------------------------
        'info_contact': (1,(
            ('name',(1,1),(),_T('contact name'),()),
        ),notice['info'],('info-contact contact-ID',)),
        'info_domain': (1,(
            ('name',(1,1),(),_T('domain name'),()),
        ),notice['info'],('info-domain my-domain.cz',)),
        'info_nsset': (1,(
            ('name',(1,1),(),_T('nsset name'),()),
        ),notice['info'],('info-nsset NSSET_ID',)),
        #----------------------------------------------------
        'check_contact': (1,(
            ('name',(1,UNBOUNDED),(),_T('contact name'),()),
        ),notice['check'],('check-contact my-contact1 my-contact2',)),
        'check_domain': (1,(
            ('name',(1,UNBOUNDED),(),_T('domain name'),()),
        ),notice['check'],('check-domain domain1.cz domain2.cz',)),
        'check_nsset': (1,(
            ('name',(1,UNBOUNDED),(),_T('nsset name'),()),
        ),notice['check'],('check-nsset nsset1 nsset2',)),
        #----------------------------------------------------
        'poll': (1,(
            ('op',(1,1),('req','ack'),_T('query type'),()),
        ),_T('The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients.'),('poll req','poll ack',)),
        #----------------------------------------------------
        'transfer_domain': (3,(
            ('name',(1,1),(),_T('domain name'),()),
            ('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),()),
        ),notice['transfer'],('transfer-domain name-domain request password',)),
        #----------------------------------------------------
        'transfer_nsset': (3,(
            ('name',(1,1),(),_T('nsset name'),()),
            ('op',(1,1),transfer_op,_T('query type'),()),
            ('passw',(1,1),(),_T('password'),()),
        ),notice['transfer'],('transfer-nsset name-nsset request password',)),
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
            ('notify_email',(0,1),(),_T('notify email'),()),
            ),notice['create'],('create-contact reg-id "John Doe" jon@mail.com "New York" US "Example Inc." ("Yellow harbor" "Blueberry hill") VA 20166-6503 +1.7035555555 +1.7035555556 (0 d-name "d org." "Street number City" +21321313 +734321 my@mail.com) vat-test ssn-test notify@here.net',)),
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
            ),notice['create'],('create-domain domain.cz password (3 m) nsset.name.cz registr-name ("My address","My next contact")',)),
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
            ('val_ex_date',(0,1),(),_T('valExDate'),()),
            ),notice['create'],('create-domain-enum domain.cz password (3 m) nsset.name.cz registr-name ("My address","My next contact") 2006-06-08',)),
        #----------------------------------------------------
        'create_nsset': (2,(
            ('id',(1,1),(),_T('nsset ID'),()),
            ('pw',(1,1),(),_T('password'),()),
            ('ns',(0,9),(),_T('LIST of nssets'),(
                ('name',(1,1),(),_T('nsset name'),()),
                ('addr',(0,UNBOUNDED),(),_T('nsset address'),()),
            )),
            ('tech',(0,UNBOUNDED),(),_T('tech contact'),()),

            ),notice['create'],(
                'create-nsset exampleNsset passw',
                'create-nsset exampleNsset passw ((ns1.domain.net (127.1.0.1 127.1.0.2)),(ns2.domain.net (127.2.0.1 127.2.0.2)),(ns3.domain.net (127.3.0.1 127.3.0.2))) tech-contact',
            )),
        #----------------------------------------------------
        'delete_contact': (1,(
             ('id',(1,1),(),_T('contact ID'),()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'delete_domain': (1,(
            ('name',(1,1),(),_T('domain name'),()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'delete_nsset': (1,(
            ('id',(1,1),(),_T('nsset ID'),()),
            ),notice['delete'],()),
        #----------------------------------------------------
        'renew_domain': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('cur_exp_date',(1,1),(),_T('current expiration date'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ),notice['renew'],('renew-domain nic.cz 2023-06-02 (6 y)',)),
        #----------------------------------------------------
        'renew_domain_enum': (2,(
            ('name',(1,1),(),_T('domain name'),()),
            ('cur_exp_date',(1,1),(),_T('current expiration date'),()),
            ('period',(0,1),(),_T('period'),(
                ('num',(1,1),(),_T('number of months or years'),()),
                ('unit',(1,1),('y','m'),_T('period unit (y year(default), m month)'),()),
            )),
            ('valExDate',(0,1),(),_T('valExDate'),()),
            ),notice['renew'],('renew-domain-enum nic.cz 2023-06-02 () 2006-08-09')),
        #----------------------------------------------------
        'update_contact': (1,(
            ('contact-id',(1,1),(),_T('your contact ID'),()),
            ('add',(0,5),(),_T('add status'),()),
            ('rem',(0,5),(),_T('remove status'),()),
            ('chg',(0,1),(),_T('change status'),(
                ('postal_info',(0,1),(),_T('postal informations'),(
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
                ('notify_email',(0,1),(),_T('notify email'),()),
            )),
            ),notice['update'],(
                    'update-contact id-contact clientDeleteProhibited',
                    'update-contact id-contact (clientDeleteProhibited linked ok)',
                    'update-contact id-contact (linked ok) (clientDeleteProhibited clientUpdateProhibited) (("John Doe" "Doe Company" "Down street, New York") +00123456789 +00123456456 john@doe.com (1 John John-Comp "Street and City" +01231321 +01234654 john@john.com) my-vat my-ssn notify@here.net',
            )),
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
            ),notice['update'],(
                'update-domain nic.cz',
                'update-domain nic.cz (linked add-contact) ((ok linked) rem-contact) (nsset registrant (password extensions))',
            )),
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
                ('auth_info',(0,1),(),_T('authInfo'),(
                    ('pw',(0,1),(),_T('password'),()),
                    ('ext',(0,1),(),_T('ext'),()),
                )),
            )),
            ('val_ex_date',(0,1),(),_T('valExDate'),()),
            ),notice['update'],('update-domain-enum 1.1.1.1.1.arpa64.net (linked add-contact) ((ok linked) rem-contact) (nsset registrant (password extensions)) 2006-06-08',)),
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
                #('ext',(0,1),(),_T('ext'),()),
            )),
            ),notice['update'],(
                'update-nsset nic.cz',
                'update-nsset nsset-ID (((nsset1.name.cz 127.0.0.1),(nsset2.name.cz (127.0.2.1 127.0.2.2)),) tech-add-contact ok) ("My Name",("Tech contact 1","Tech contact 2"),(clientDeleteProhibited ok)) (password extension)',
            )),
    }

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
        errors = epp.parse_cmd(cmd_name, cmd, manag._conf)
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
        command_line,command_help,notice, examples = epp.get_help(command_name)
        print colored_output.render(command_line)
        print colored_output.render(command_help)
        print colored_output.render(notice)
        print '\nExamples:'
        print '\n'.join(examples)
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
##    test(('update_contact id-contact',))
    test(commands1)
    test(commands2)
    test(commands3)
    test(commands4)
    test(commands6)
    test_help(('login','update_nsset',))
