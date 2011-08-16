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
import re
import eppdoc_assemble
from translate import options, encoding
"""
This module described all EPP commands with their parameters and 
names of the returned values. Class Message is the top of the Message
classes in modules eppdoc_. This instance is used by client session Manager
object for manage with EPP commands and answers.
"""

UNBOUNDED = eppdoc_assemble.UNBOUNDED


def get_ident_names(keys=None, descr=None):
    "Get names"
    ident_names = (
        ('op',       _T('Number identity card')),
        ('passport', _T('Number of passport')),
        ('mpsv',     _T('Number of Ministry of Labour and social affairs')),
        ('ico',      _T('Number of company')), 
        ('birthday', _T('Birthday date')), 
    )
    if keys:
        # return keys only
        return [key for key, description in ident_names]
    if descr:
        # return description only 
        return [description for key, description in ident_names]
    return ident_names


def ident_type_list():
    "Ident types"
    return [(name, ) for name in get_ident_names(True)]


    
# Help
def get_shared_notice():
    'Returns notice for EPP commands'
    return {   
   'disclose':_T('Names what are not included into disclose list are set to opposite value of the disclose flag value.'),
    'ident': '%s\n%s'%(_T('Identificator type can be:'), 
    '\n'.join(['%#-10s %s' % (name, desc) for name, desc in get_ident_names()])
    ), 
}

def make_command_parameters():
    'Returns command parameters tuple'
    notice = get_shared_notice()
    # format:
    # command-name: (param-name, (min,max), (list of required), 'help', 'example', 'pattern', (list of children)
    # For include new command you need do this steps:
    #   1. add new item into command_params
    #   2. add function assemble_...() into eppdoc_assemble.Message
    #   3. [optional] add answer_response_...() in session_receiver.ManagerReceiver
    command_params = {
        'hello': (0, [], _T("""
Command 'hello' is used to obtain information from the server.
The server answer to 'hello' command is Greeting message. This message
is used usualy at the begining of the session for getting some variables
usefull for communication. Within Server version or ID you can got
available languages, Data Collection policy etc.
Command 'hello' you can call at any time."""),()),
        'logout': (0, [], _T("""
The EPP "logout" command is used to end a session with the server.
But client will be still running. For close client type 'quit' (see help).
Before quit the client send logout automaticly."""),()),
        #----------------------------------------------------
        'login': (2,[
            ('username',(1,1),(),_T('Username'),'username','',()),
            ('password',(1,1),(),_T('Password'),'password','',()),
            ('new_password',(0,1),(),_T('New password'),'new_password','',()),
            ('lang',(0,1),(),_T('Language version'),'en','',()),
        ],_T("""
The "login" command establishes an ongoing server session that preserves client identity
and authorization information during the duration of the session. Parametr "lang" set
session and client language together. Language is possible to set also by option on the
command line, or define it in configuration file or set by client command 'lang'.
Using parameter 'new_password' you can change password.
"""),('login john mypass "my new pass!"','login john mypass NULL cs')),
        #----------------------------------------------------
        'info_contact': (1,[
            ('name',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
        ],_T("""
The EPP 'info_contact' command is used to retrieve information associated
with an existing contact. The value 'Password for transfer' is shown only 
for privileged user."""),('info_contact cid:contact',)),
        'info_domain': (1,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
        ],_T("""
The EPP 'info_domain' command is used to retrieve information associated
with an existing domain. The value 'Password for transfer' is shown only
for privileged user. In addition for domain ENUM type the private values 
are also 'Registrant ID' and 'Administrative contact'."""),('info_domain my-domain.cz',)),
        'info_nsset': (1,[
            ('name',(1,1),(),_T('NSSET ID'),'NSSET_ID','',()),
        ],_T("""
The EPP 'info_nsset' command is used to retrieve information associated
with an existing NSSET. The value 'Password for transfer' is shown only 
for privileged user."""),('info_nsset nssid:nsid',)),
        'info_keyset': (1,[
            ('name',(1,1),(),_T('KEYSET ID'),'KEYSET_ID','',()),
        ],_T("""
The EPP 'info_keyset' command is used to retrieve information associated
with an existing KEYSET. The value 'Password for transfer' is shown only 
for privileged user."""),('info_keyset keysid:ksid',)),
        #----------------------------------------------------
        'check_contact': (1,[
            ('name',(1,UNBOUNDED),(),_T('Contact ID'),'CID:ID01','',()),
        ],_T("""
The EPP 'check_contact' command is used to determine if an contact can be
provisioned within a repository. It provides a hint that allows a
client to anticipate the success or failure of provisioning an contact
using the 'create_contact' command as contact provisioning requirements are
ultimately a matter of server policy."""),('check_contact cid:contact1 cid:contact2',)),
        'check_domain': (1,[
            ('name',(1,UNBOUNDED),(),_T('Domain name'),'mydomain.cz','',()),
        ],_T("""
The EPP 'check_domain' command is used to determine if an domain can be
provisioned within a repository.  It provides a hint that allows a
client to anticipate the success or failure of provisioning an domain
using the 'create_domain' command as domain provisioning requirements are
ultimately a matter of server policy."""),('check_domain domain1.cz domain2.cz',)),
        'check_nsset': (1,[
            ('name',(1,UNBOUNDED),(),_T('NSSET ID'),'NSSET_ID','',()),
        ],_T("""
The EPP 'check_nsset' command is used to determine if an NSSET can be
provisioned within a repository.  It provides a hint that allows a
client to anticipate the success or failure of provisioning an nsset
using the 'create_nsset' command as NSSET provisioning requirements are
ultimately a matter of server policy."""),('check_nsset nssid:id1 nssid:id2',)),
        'check_keyset': (1,[
            ('name',(1,UNBOUNDED),(),_T('KEYSET ID'),'KEYSET_ID','',()),
        ],_T("""
The EPP 'check_keyset' command is used to determine if an KEYSET can be
provisioned within a repository. It provides a hint that allows a
client to anticipate the success or failure of provisioning an nsset
using the 'create_nsset' command as KEYSET provisioning requirements are
ultimately a matter of server policy."""),('check_keyset keysid:id1 keysid:id2',)),
        #----------------------------------------------------
        'poll': (1,[
            ('op',(1,1),(('req',),('ack',)),_T('Query type'),'','',()),
            ('msg_id',(1,1),(),_T("Index of message (required only with op = 'ack')"),'123','',()),
        ],_T("""
Poll command is used to discover and retrieve service messages. They are saved
in the message queue. When you send poll with parameter op = req, 
you get only the last message from the queue. But this message
still remains on the queue. For remove message from the queue set
poll op = ack and ID of this message. So you needs to send two poll
commands for manage one message: 1. reading, 2. removing.
See help poll_autoack for client function that sends this commands together.
"""),('poll req','poll ack 4',)),
        #----------------------------------------------------
        'transfer_contact': (2,[
            ('name',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
            ('auth_info',(1,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
        ],_T("""
The EPP 'transfer_contact' command makes change in contact sponsorship 
of a designated registrar. New password for authorisation 
will be generated automaticly after succefull transfer."""),('transfer_contact CID:ID01 password',)),
        #----------------------------------------------------
        'transfer_nsset': (2,[
            ('name',(1,1),(),_T('NSSET ID'),'NSSET_ID','',()),
            #('op',(1,1),transfer_op,_T('query type'),()),
            ('auth_info',(1,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
        ],_T("""
The EPP 'transfer_nsset' command makes change in NSSET sponsorship 
of a designated registrar. New password for authorisation 
will be generated automaticly after succefull transfer."""),('transfer_nsset nssid:nsset password',)),
        #----------------------------------------------------
        'transfer_keyset': (2,[
            ('name',(1,1),(),_T('KEYSET ID'),'KEYSET_ID','',()),
            ('auth_info',(1,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
        ],_T("""
The EPP 'transfer_keyset' command makes change in KEYSET sponsorship 
of a designated registrar. New password for authorisation 
will be generated automaticly after succefull transfer."""),('transfer_keyset keysid:kset password',)),
        #----------------------------------------------------
        'transfer_domain': (2,[
            ('name',(1,1),(),_T('Domain name of domain to change sponsorship'),'domain.cz','',()),
            #('op',(1,1),transfer_op,_T('query type'),()),
            ('auth_info',(1,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
        ],_T("""
The EPP 'transfer_domain' command makes change in domain sponsorship 
of a designated registrar. New password for authorisation 
will be generated automaticly after succefull transfer."""),('transfer_domain domain.cz password',)),
        #----------------------------------------------------
        'create_contact': (5,[
            ('contact_id',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
            ('name',(1,1),(),_T('Name'), 'John Nowak','',()), # odtud shoda s update contact
            ('email',(1,1),(),_T('Email'),'info@mymail.cz','',()),
            ('street',(1,3),(),_T('Street'), 'Downing street 1230/12','',()),
            ('city',(1,1),(),_T('City'),'Praha','',()),
            ('pc',(1,1),(),_T('Postal code'),'12000',_T('postal code'),()),
            ('cc',(1,1),(),_T('Country code'),'CZ',_T('country code'),()),
            ('sp',(0,1),(),_T('State or province'),'Outlands','',()),
            ('org',(0,1),(),_T('Organisation'),'Firma s.r.o.','',()),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword',_T('password'),()), # authorization information for transfer
            ('voice',(0,1),(),_T('Phone'),'+420.222745111','',()),
            ('fax',(0,1),(),_T('Fax'),'+420.222745111','',()),
            ('disclose',(0,1),(),_T('Disclose'),'','',(
                ('flag',(1,1),(('y',),('n',)),_T('Disclose flag (default y)'),'n','',()),
                ('data',(0,len(eppdoc_assemble.contact_disclose)),eppdoc_assemble.contact_disclose,_T('Data for with is set the flag value'),'','',()),
            )),
            ('vat',(0,1),(),_T('VAT (Value-added tax)'),'7035555556','',()), # vat identificator
            ('ident',(0,1),(),_T('Identificator'),'','',( # mpsv: identifikator Ministerstva prace a socialnich veci
                ('number',(1,1),(),_T('Identificator number'),'8888888856','',()),
                ('type',(1,1), ident_type_list(), _T('Identificator type'),'op','',()),
            )),
            ('notify_email',(0,1),(),_T('Notification email'),'info@mymail.cz','',()),
            ],'%s\n\n%s\n\n%s'%(_T("""
The EPP 'create_contact' command is used to create an instance of the contact.
Contact can be used for values of the owner, registrant or technical contact."""),notice['disclose'],notice['ident']),(
            "create_contact CID:ID01 'Jan Novak' info@mymail.cz 'Narodni trida 1230/12' Praha 12000 CZ NULL 'Firma s.r.o.' mypassword  +420.222745111 +420.222745111 (y (fax email)) 7035555556 (8888888856 op) info@mymail.cz",
            "create_contact CID:ID02 'Jan Ban' info@mail.com Street Brno 123000 CZ"
            )),
        #----------------------------------------------------
        'create_domain': (2,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
            ('registrant',(1,1),(),_T('Registrant ID'),'CID:REGID','',()),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
            ('nsset',(0,1),(),_T('NSSET ID'),'NSSID:ID','',()),
            ('keyset',(0,1),(),_T('KEYSET ID'),'KEYSID:ID','',()),
            ('period',(0,1),(),_T('Period'),'','',(
                ('num',(1,1),(),_T('Number of months or years'),'3','',()),
                ('unit',(1,1),(('y',),('m',)),_T('Period unit (y year(default), m month)'),'','',()),
            )),
            ('admin',(0,UNBOUNDED),(),_T('Administrative contact ID'),'CID:ADMIN_ID','',()),
            ('val_ex_date',(0,1),(),_T('Validation expires at date. This value is required for ENUM domains.'),'2008-12-03','',()),
            ('publish', (0,1), (('y',), ('n',)), _T('Include ENUM domain into ENUM dictionary'), 'true', '', ()),
            ],_T("""
The EPP 'create_domain' command is used to create domain.
A domain can be created for an indefinite period of time, or 
a domain can be created for a specific validity period. Basicly
you can create two types of the domain: cz and ENUM.
The difference is in parameter val_ex_date. It is required 
for ENUM domains."""),(
                'create_domain domain.cz cid:regid password nssid:nsid NULL (3 y) (cid:admin1,cid:admin2)',
                'create_domain 1.1.1.7.4.5.2.2.2.0.2.4.e164.arpa cid:regid password nssid:nsid keysid:id (3 y) (cid:admin1,cid:admin2) 2006-06-08 y'
            )),
        #----------------------------------------------------
        'create_nsset': (3,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSID:ID','',()),
            ('dns',(2,9),(),_T('LIST of DNS'),'','',(
                ('name',(1,1),(),_T('Name server'),'my.dns1.cz','',()),
                ('addr',(0,UNBOUNDED),(),_T('Server address'),'217.31.207.130','',()),
            )),
            ('tech',(1,UNBOUNDED),(),_T('Technical contact'),'CID:ID01','',()),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
            ('reportlevel',(0,1),(),_T('Report range level (0 - 10; higher = more detailed)'),'1','',()),
            ],_T("""
The EPP 'create_nsset' command is used to create a record of the NSSET.

Report level sets depth level of the technical test. These tests are maintained 
in regular intervals and in case of the problem the technical contact is informed.
Report level is also applied on the test executed by the request throught EPP.
Every test has report level (number) and run just a parts what have equal or
lower level number. Valid range is from 0 to 10.
"""),(
                'create_nsset nssid:nsset1 ((ns1.domain.cz (217.31.207.130 217.31.207.129)),(ns2.domain.cz (217.31.206.130 217.31.206.129)),(ns3.domain.cz (217.31.205.130 217.31.205.129))) cid:regid passw',
            )),
        #----------------------------------------------------
        'create_keyset': (3,[
            ('id',(1,1),(),_T('KEYSET ID'),'KEYSID:ID','',()),
            ('dnskey',(0,9),(),_T('LIST of keys'),'','',(
                ('flags',(1,1),(),_T('Flags'),'257','',()),
                ('protocol',(1,1),(),_T('Protocol'),'3','',()),
                ('alg',(1,1),(),_T('Algorithm'),'5','',()),
                ('pub_key',(1,1),(),_T('Public key code'),'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8', '', ()),
            )),
            ('dnskeyref',(0,9),(),_T('LIST of filenames with dns keys'),'unittest/dnskey.pub','',()),
            ('tech',(1,UNBOUNDED),(),_T('Technical contact'),'CID:ID01','',()),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
            ],_T("""
The EPP 'create_keyset' command is used to create a record of the KEYSET.
"""),(
                'create_keyset KEYSID:01 ((257 3 5 AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8)) () CID:ID01 passw', 
                'create_keyset KEYSID:01 () (unittest/dnskey.pub) CID:ID01 passw', 
            )),
        #----------------------------------------------------
        'delete_contact': (1,[
             ('id',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
            ],_T("""The EPP 'delete_contact' command is used to remove a record of the contact."""),('delete_contact cid:id',)),
        #----------------------------------------------------
        'delete_domain': (1,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
            ],_T("""The EPP 'delete_domain' command is used to remove a record of the domain."""),('delete_domain domain.cz',)),
        #----------------------------------------------------
        'delete_nsset': (1,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSET_ID','',()),
            ],_T("""The EPP 'delete_nsset' command is used to remove a record of the nsset."""),('delete_nsset nssid:id',)),
        #----------------------------------------------------
        'delete_keyset': (1,[
            ('id',(1,1),(),_T('KEYSET ID'),'KEYSET_ID','',()),
            ],_T("""The EPP 'delete_keyset' command is used to remove a record of the keyset."""),('delete_keyset keysid:id',)),
        #----------------------------------------------------
        'renew_domain': (2,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
            ('cur_exp_date',(1,1),(),_T('Expiration date'),'2006-12-03','',()),
            ('period',(0,1),(),_T('Period'),'','',(
                ('num',(1,1),(),_T('Number of months or years'),'3','',()),
                ('unit',(1,1),(('y',),('m',)),_T('Period unit (y year(default), m month)'),'','',()),
            )),
            ('val_ex_date',(0,1),(),_T('Validation expires at'),'2008-12-03','',()),
            ],_T("""
A domain names have a specified validity period. The server
policy supports domain validity periods and the validity period
is defined when a domain is created. This validity can be extended 
by the EPP 'renew_domain' command.

Validity periods are measured in years or months with the appropriate
units specified using the 'unit' attribute.  Valid values for the
'unit' attribute are 'y' for years and 'm' for months.  The minimum
and maximum allowable period is defined in the Communication rules."""),('renew_domain nic.cz 2008-06-02 (6 y)',)), # The EPP renew_domain command is used to extend validity of an existing domain.
        #----------------------------------------------------
        'update_contact': (1,[
            ('contact_id',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
            ('chg',(0,1),(),_T('Change values'),'','',(
                ('postal_info',(0,1),(),_T('Postal informations'),'','',(
                    ('name',(0,1),(),_T('Name'),u'Jan Nowak','',()),
                    ('org',(0,1),(),_T('Organisation'),'Firma s.r.o.','',()),
                    ('addr',(0,1),(),_T('Address'),'','',(
                        ('street',(1,3),(),_T('Street'),u'Na narodni 1234/14','',()),
                        ('city',(1,1),(),_T('City'),'Praha','',()),
                        ('pc',(1,1),(),_T('Postal code'),'12000','',()),
                        ('cc',(1,1),(),_T('Country code'),'CZ','',()),
                        ('sp',(0,1),(),_T('State or province'),'','',()),
                    )),
                )),
                ('voice',(0,1),(),_T('Phone'),'+420.222745111','',()),
                ('fax',(0,1),(),_T('Fax'),'+420.222745111','',()),
                ('email',(0,1),(),_T('Email'),'info@mymail.cz','',()),
                ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
                ('disclose',(0,1),(),_T('Disclose'),'','',(
                    ('flag',(1,1),(('y',),('n',)),_T('Disclose flag (default y)'),'','',()),
                    ('data',(0,len(eppdoc_assemble.contact_disclose)),eppdoc_assemble.contact_disclose,_T('data for with is set the flag value'),'','',()),
                )),
                ('vat',(0,1),(),_T('VAT'),'7035555556','',()),
                ('ident',(0,1),(),_T('Identificator'),'','',(
                    ('number',(1,1),(),_T('Identificator number'),'8888888856','',()),
                    ('type',(0,1), ident_type_list(), _T('Identificator type'),'op','',()),
                )),
                ('notify_email',(0,1),(),_T('Notification email'),'notify@mymail.cz','',()),
            )),
            ],'%s\n\n%s\n\n%s'%(_T("""The EPP 'update_contact' command is used to update values in the contact."""),notice['disclose'],notice['ident']),
                (
                    "update_contact CID:ID01 (('Jan Nowak' 'Firma s.r.o.' (('Na narodni 1230/12', 'Americka 12') Praha 12000 CZ  Vinohrady )) +420.222745111 +420.222745111 info@mymail.cz mypassword (y (voice, email)) 7035555556 (8888888856 ico) notify@mymail.cz)",
                    "update_contact CID:ID01 (() NULL NULL NULL NULL () NULL () change.only@notify-mail.cz)",
            )),
        #----------------------------------------------------
        'update_domain': (1,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
            ('add_admin',(0,UNBOUNDED),(),_T('Add administrative contact ID'),'CID:ID01','',()),
            ('rem_admin',(0,UNBOUNDED),(),_T('Remove administrative contact ID'),'CID:ID01','',()),
            ('rem_tempc',(0,UNBOUNDED),(),_T('Remove temporary contact ID'),'CID:ID01','',()),
            ('chg',(0,1),(),_T('Change values'),'','',(
                ('nsset',(0,1),(),_T('NSSET ID'),'NSSET_ID','',()),
                ('keyset',(0,1),(),_T('KEYSET ID'),'KEYSET_ID','',()),
                ('registrant',(0,1),(),_T('Registrant ID'),'CID:ID01','',()),
                ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'mypassword','',()),
            )),
            ('val_ex_date',(0,1),(),_T('Validation expires at'),'2008-12-03','',()),
            ('publish', (0,1), (('y',), ('n',)), _T('Include ENUM domain into ENUM dictionary'), 'true', '', ()),
            ],_T("""The EPP 'update_domain' command is used to update values in the domain."""),(
                'update_domain mydomain.cz (CID:ID01, CID:ID02) CID:ID03 CID:TMP01 (NSSID:NSSET01 NULL CID:ID04 mypass)',
                'update_domain 1.1.1.7.4.5.2.2.2.0.2.4.e164.arpa (CID:ID01, CID:ID02) CID:ID03 CID:TMP01 (NSSID:NSSET01 KEYSID:KEYSET01 CID:ID04 mypass) 2008-12-03 y',
            )),
        #----------------------------------------------------
        'update_nsset': (1,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSET_ID','',()),
            ('add',(0,1),(),_T('Add values'),'','',(
                ('dns',(0,9),(),_T('List of DNS'),'','',(
                    ('name',(1,1),(),_T('Name server'),'my.dns.cz','',()),
                    ('addr',(0,UNBOUNDED),(),_T('Server address'),'217.31.207.130','',()),
                )),
                ('tech',(0,UNBOUNDED),(),_T('Technical contact ID'),'CID:ID01','',()),
            )),
            ('rem',(0,1),(),_T('Remove values'),'','',(
                ('name',(0,9),(),_T('Name server'),'my.dns.cz','',()),
                ('tech',(0,UNBOUNDED),(),_T('Technical contact ID'),'CID:ID01','',()),
            )),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'new_password','',()),
            ('reportlevel',(0,1),(),_T('Report range level (0 - 10; higher = more detailed)'),'1','',()),
            ],_T("""The EPP 'update_nsset' command is used to update values in the NSSET."""),(
                "update_nsset nssid:ns1 (((ns1.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132)), (ns2.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132))) (cid:tech1, cid:tech2, cid:tech3)) (((rem1.dns.cz, rem2.dns.cz) (cid:tech_rem01, cid:tech_rem02))) password",
            )),
        #----------------------------------------------------
        'update_keyset': (1,[
            ('id',(1,1),(),_T('KEYSET ID'),'KEYSET_ID','',()),
            ('add',(0,1),(),_T('Add values'),'','',(
                ('dnskey',(0,9),(),_T('LIST of keys'),'','',(
                    ('flags',(1,1),(),_T('Flags'),'257','',()),
                    ('protocol',(1,1),(),_T('Protocol'),'3','',()),
                    ('alg',(1,1),(),_T('Algorithm'),'5','',()),
                    ('pub_key',(1,1),(),_T('Public key code'),'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8', '', ()),
                )),
                ('dnskeyref',(0,9),(),_T('LIST of filenames with dns keys'),'unittest/dnskey.pub','',()),
                ('tech',(0,UNBOUNDED),(),_T('Technical contact ID'),'CID:ID01','',()),
            )),
            ('rem',(0,1),(),_T('Remove values'),'','',(
                ('dnskey',(0,9),(),_T('LIST of keys'),'','',(
                    ('flags',(1,1),(),_T('Flags'),'257','',()),
                    ('protocol',(1,1),(),_T('Protocol'),'3','',()),
                    ('alg',(1,1),(),_T('Algorithm'),'5','',()),
                    ('pub_key',(1,1),(),_T('Public key code'),'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8', '', ()),
                )),
                ('dnskeyref',(0,9),(),_T('LIST of filenames with dns keys'),'unittest/dnskey.pub','',()),
                ('tech',(0,UNBOUNDED),(),_T('Technical contact ID'),'CID:ID01','',()),
            )),
            ('auth_info',(0,1),(),_T('Password required by server to authorize the transfer'),'new_password','',()),
            ],_T("""The EPP 'update_keyset' command is used to update values in the KEYSET."""),(
            'update_keyset KEY01 (((256 3 5 AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8))) (() () () (CID:TECH1, CID:TECH2, CID:TECH3)) password', 
            'update_keyset KEY02 (() unittest/dnskey.pub) (() unittest/dnskey.pub)', 
            'update_keyset KEY03 () (() unittest/dnskey.pub)', 
            )),
        #----------------------------------------------------
        'sendauthinfo_contact': (1,[
             ('id',(1,1),(),_T('Contact ID'),'CID:ID01','',()),
            ],_T("""
The EPP 'sendauthinfo_contact' command transmit request for send password 
to contact email. This command is usefull during transfer 
when owner and new registrar needn't require previous registrar for password."""),('sendauthinfo_contact cid:id',)),
        #----------------------------------------------------
        'sendauthinfo_domain': (1,[
            ('name',(1,1),(),_T('Domain name'),'mydomain.cz','',()),
            ],_T("""
The EPP 'sendauthinfo_domain' command transmit request for send password 
to registrant email. This command is usefull during transfer 
when owner and new registrar needn't require previous registrar for password."""),('sendauthinfo_domain domain.cz',)),
        #----------------------------------------------------
        'sendauthinfo_nsset': (1,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSID:MYID','',()),
            ],_T("""
The EPP 'sendauthinfo_nsset' command transmit request for send password 
to technical contact email. This command is usefull during transfer 
when owner and new registrar needn't require previous registrar for password."""),('sendauthinfo_nsset nssid:id',)),
        #----------------------------------------------------
        'sendauthinfo_keyset': (1,[
            ('id',(1,1),(),_T('KEYSET ID'),'KEYSID:MYID','',()),
            ],_T("""
The EPP 'sendauthinfo_keyset' command transmit request for send password 
to technical contact email. This command is usefull during transfer 
when owner and new registrar needn't require previous registrar for password."""),('sendauthinfo_keyset keysid:id',)),
        #----------------------------------------------------
        'credit_info': (0,[],_T("""The EPP 'credit_info' command returns credit information."""),('credit_info',)),
        #----------------------------------------------------
        'technical_test': (2,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSID:MYID','',()),
            ('level',(0,1),(),_T('Report range level (0 - 10; higher = more detailed)'),'1','',()),
            ('name',(0,UNBOUNDED),(),_T('Domain name'),'mydomain.cz','',()),
            ],_T("""
The EPP 'technical_test' command transmit request for technical test 
for particular NSSET and domain. The result of the test will be saved 
into the message queue from where the registrant can fetch it 
by poll command. Every test has report level (number) and run just 
a parts what have equal or lower level number. Valid range 
is from 0 to 10. Set report level in the command create_nsset 
and update_nsset.
"""),('technical_test nssid:id 4 mydomain.cz',)),

        #----------------------------------------------------
        'prep_contacts': (0,[],_T("""
Prepare list of the contacts. This command fills server buffer by list 
of contacts and set pointer at the beginning of the list. The list 
is taken in sequence by calling command 'get_results' repeatedly 
until any data comming.
"""),('prep_contacts',)),
        #----------------------------------------------------
        'prep_domains': (0,[],_T("""
Prepare list of the domains. This command fills server buffer by list 
of domains and set pointer at the beginning of the list. The list is 
taken in sequence by calling command 'get_results' repeatedly until 
any data comming.
"""),('prep_domains',)),
        #----------------------------------------------------
        'prep_nssets': (0,[],_T("""
Prepare list of the NSSETs. This command fills server buffer by list 
of nssets and set pointer at the beginning of the list. The list 
is taken in sequence by calling command 'get_results' repeatedly 
until any data comming.
"""),('prep_nssets',)),
        #----------------------------------------------------
        'prep_keysets': (0,[],_T("""
Prepare list of the KEYSETs. This command fills server buffer by list 
of keysets and set pointer at the beginning of the list. The list 
is taken in sequence by calling command 'get_results' repeatedly 
until any data comming.
"""),('prep_nssets',)),

        #----------------------------------------------------
        'get_results': (0,[],_T("""
Returns a data chunk from the list of the records in the server buffer.
Pointer is moved to next part after every transmition. If no data received
the end of list has been reached.
New list is created by function (contacts_by_all, nssets_by_all, domains_by_all, ...)
or domains_by_contact, domains_by_nsset etc.
"""),('get_results',)),
        #----------------------------------------------------

        'list_contacts': (0,[],_T("""
Returns list of contacts using command contacts_by_all and runs a loop 
of get_results commands until whole list of contacts not received.
"""),('list_contacts',)),
        #----------------------------------------------------
        'list_domains': (0,[],_T("""
Returns list of domains using command domains_by_all and runs a loop 
of get_results commands until whole list of domain names not received.
"""),('list_domains',)),
        #----------------------------------------------------
        'list_nssets': (0,[],_T("""
Returns list of nssets using command nssets_by_all and runs a loop 
of get_results commands until whole list of nssets not received.
"""),('list_nssets',)),

        'list_keysets': (0,[],_T("""
Returns list of keysets using command nssets_by_all and runs a loop 
of get_results commands until whole list of keysets not received.
"""),('list_keysets',)),
        #----------------------------------------------------

        'prep_domains_by_nsset': (1,[
            ('id',(1,1),(),_T('NSSET ID'),'NSSID:VALID','',()),
        ],_T("""
Prepare domains by NSSET. This command fills server buffer by list 
of domains connected with defined nsset ID. The pointer is set 
at the beginning of the list. The list is taken in sequence 
by calling command 'get_results' repeatedly until any data comming.
"""),('prep_domains_by_nsset NSSID:VALID',)),
        #----------------------------------------------------
        'prep_domains_by_keyset': (1,[
            ('id',(1,1),(),_T('KEYSET ID'),'KEYSID:VALID','',()),
        ],_T("""
Prepare domains by KEYSET. This command fills server buffer by list 
of domains connected with defined keyset ID. The pointer is set 
at the beginning of the list. The list is taken in sequence 
by calling command 'get_results' repeatedly until any data comming.
"""),('prep_domains_by_keyset KEYSID:VALID',)),
        #----------------------------------------------------

        'prep_domains_by_contact': (1,[
            ('id',(1,1),(),_T('Contact ID'),'CID:TECH','',()),
        ],_T("""
Prepare domains by contact. This command fills server buffer by list 
of domains where occurs defined contact ID. It can be Registrant 
ID or Admin ID or Temporary ID. The pointer is set at the beginning 
of the list. The list is taken in sequence by calling command 
'get_results' repeatedly until any data comming.
"""),('prep_domains_by_contact CID:TECH',)),
        #----------------------------------------------------

        'prep_nssets_by_contact': (1,[
            ('id',(1,1),(),_T('Technical contact'),'CID:ADMIN','',()),
        ],_T("""
Prepare NSSETs by contact. This command fills server buffer by list 
of nssets connected with defined technical contact ID. The pointer 
is set at the beginning of the list. The list is taken in sequence 
by calling command 'get_results' repeatedly until any data comming.
"""),('prep_nssets_by_contact CID:ADMIN',)),

        'prep_keysets_by_contact': (1,[
            ('id',(1,1),(),_T('Technical contact'),'CID:ADMIN','',()),
        ],_T("""
Prepare KEYSETs by contact. This command fills server buffer by list 
of keysets connected with defined technical contact ID. The pointer 
is set at the beginning of the list. The list is taken in sequence 
by calling command 'get_results' repeatedly until any data comming.
"""),('prep_keysets_by_contact CID:ADMIN',)),
        #----------------------------------------------------

        'prep_nssets_by_ns': (1,[
            ('name',(1,1),(),_T('Name server'),'ns.mydns.cz','',()),
        ],_T("""
Prepare NSSETs by NS. This command fills server buffer by list of nssets 
connected with defined name server. The pointer is set at the beginning 
of the list. The list is taken in sequence by calling command 'get_results'
repeatedly until any data comming.
"""),('prep_nssets_by_ns mydomain.cz',)),

        #----------------------------------------------------
        
    }
    for k,v in command_params.items():
        if k == 'hello': continue
        v[1].append((eppdoc_assemble.TAG_clTRID,(0,1),(),_T('Client transaction ID'),'unique_transaction_id','',()))
    return command_params

def make_sort_by_names():
    'Returns tuple of names used for sorting received values'
    #----------------------------------
    #
    # OUTPUT SORTED BY NAMES
    # (key, verbose, description)
    # verbose 1: shown in verbose 1 and higher
    #         2: shown in verbose 2 and higher
    #         ...
    #----------------------------------
    sort_by_names = {
    
       'contact:info': ('contact',(
         ('id',          1,  _T('Contact ID')),
         ('roid',        1,  _T('Repository object ID')),
         ('crID',        1,  _T("Created by")),
         ('clID',        1,  _T("Designated registrar")),
         ('upID',        1,  _T("Updated by")),
         ('crDate',      1,  _T('Created on')),
         ('trDate',      1,  _T('Last transfer on')),
         ('upDate',      1,  _T('Last update on')),
         ('name',        1,  _T('Name')),
         ('org',         1,  _T('Organisation')),
         ('street',      1,  _T('Street')),
         ('city',        1,  _T('City')),
         ('sp',          1,  _T('State or province')),
         ('pc',          1,  _T('Postal code')),
         ('cc',          1,  _T('Country code')),
         ('authInfo',    1,  _T('Password for transfer')),
         ('voice',       1,  _T('Phone')),
         ('fax',         1,  'Fax'),
         ('email',       1,  'Email'),
         ('notifyEmail', 1,  _T('Notification email')),
         ('status.s',    1,  _T('Status')),
         ('status',      1,  _T('Status message')),
         ('disclose',    1,  _T('Disclose')),
         ('hide',        1,  _T('Hide')),
         ('vat',         1,  _T('VAT')),
         ('ident.type',  1,  _T('Identificator type')),
         ('ident',       1,  _T('Identificator')),
         )),

       'domain:info': ('domain',(
         ('name',        1,  _T('Domain name')),
         ('roid',        1,  _T('Repository object ID')),
         ('crID',        1,  _T("Created by")),
         ('clID',        1,  _T("Designated registrar")),
         ('upID',        1,  _T("Updated by")),
         ('crDate',      1,  _T('Created on')),
         ('trDate',      1,  _T('Last transfer on')),
         ('upDate',      1,  _T('Last update on')),
         ('exDate',      1,  _T('Expiration date')),
         ('valExDate',   1,  _T('Validation expires at')), # valid to date
         ('publish',     1,  _T('Include into ENUM dict')),
         ('nsset',       1,  _T('NSSET ID')),
         ('keyset',      1,  _T('KEYSET ID')),
         ('authInfo',    1,  _T('Password for transfer')),
         ('status.s',    1,  _T('Status')),
         ('status',      1,  _T('Status message')),
         ('registrant',  1,  _T('Registrant ID')),
         ('admin',       1,  _T('Administrative contact')),
         ('tempcontact', 1,  _T('Temporary contact')),
         )),

       'nsset:info': ('nsset',(
         ('id',          1,  _T('NSSET ID')),
         ('roid',        1,  _T('Repository object ID')),
         ('crID',        1,  _T("Created by")),
         ('clID',        1,  _T("Designated registrar")),
         ('upID',        1,  _T("Updated by")),
         ('crDate',      1,  _T('Created on')),
         ('trDate',      1,  _T('Last transfer on')),
         ('upDate',      1,  _T('Last updated on')),
         ('authInfo',    1,  _T('Password for transfer')),
         ('status.s',    1,  _T('Status')),
         ('status',      1,  _T('Status message')),
         ('tech',        1,  _T('Technical contact')),
         ('ns',          1,  _T('Name servers')),
         ('reportlevel', 1,  _T('Report level')),
         )),

       'keyset:info': ('keyset',(
         ('id',          1,  _T('KEYSET ID')),
         ('roid',        1,  _T('Repository object ID')),
         ('crID',        1,  _T("Created by")),
         ('clID',        1,  _T("Designated registrar")),
         ('upID',        1,  _T("Updated by")),
         ('crDate',      1,  _T('Created on')),
         ('trDate',      1,  _T('Last transfer on')),
         ('upDate',      1,  _T('Last updated on')),
         ('authInfo',    1,  _T('Password for transfer')),
         ('status.s',    1,  _T('Status')),
         ('status',      1,  _T('Status message')),
         ('tech',        1,  _T('Technical contact')),
         ('ds',          1,  _T('DS records')),
         ('dnskey',      1,  _T('DNSKEY records')),
         ('reportlevel', 1,  _T('Report level')),
         )),
         
       'contact:create': ('contact',(
         ('id',          1,  _T('Contact ID')),
         ('crDate',      1,  _T('Created on')),
         )),
         
       'nsset:create': ('nsset',(
         ('id',          1,  _T('NSSET ID')),
         ('crDate',      1,  _T('Created on')),
         )),

       'keyset:create': ('keyset',(
         ('id',          1,  _T('KEYSET ID')),
         ('crDate',      1,  _T('Created on')),
         )),
         
       'domain:create': ('domain',(
         ('name',        1,  _T('Domain name')),
         ('crDate',      1,  _T('Created on')),
         ('exDate',      1,  _T('Expiration date')),
         )),

       'hello': ('',(
         ('lang',        2,  _T('Available languages')),
         ('svID',        1,  _T('Server ID')),
         ('svDate',      2,  _T('Server date')),
         ('version',     2,  _T('Available protocols')),
         ('objURI',      2,  _T('Objects URI')),
         ('extURI',      2,  _T('Extensions URI')),
         ('dcp',         2,  _T('Data Collection policy')),
         )),

       'domain:list': ('',(
         ('list',        1,  _T('List')),
         ('count',       1,  _T('Count')),
         )),

       'poll': ('',(
         ('msgQ.count',  1,  _T('Queue size')),
         ('msgQ.id',     1,  _T('Message ID')),
         ('qDate',       1,  _T('Message date')),
         ('msg.nodes',   1,  _T('Message type')),
         ('msg',         1,  _T('Message content')),
         )),

       'domain:renew': ('domain',(
         ('name',        1,  _T('Domain name')),
         ('exDate',      1,  _T('Expiration date')),
         )),
         
       'fred:listcontacts': ('',(
         ('count',       1,  _T('Number of records')),
         ('notify',      2,  _T('Notify')),
         )),
       'fred:listnssets': ('',(
         ('count',       1,  _T('Number of records')),
         ('notify',      2,  _T('Notify')),
         )),
       'fred:listkeysets': ('',(
         ('count',       1,  _T('Number of records')),
         ('notify',      2,  _T('Notify')),
         )),
       'fred:listdomains': ('',(
         ('count',       1,  _T('Number of records')),
         ('notify',      2,  _T('Notify')),
         )),
         
       'fred:getresults': ('',(
         ('list',        1,  _T('List')),
         )),

       'fred:domainsbycontact': ('',(
         ('count',       1,  _T('Count')),
         ('notify',      2,  _T('Notify')),
         )),

       'fred:domainsbynsset': ('',(
         ('count',       1,  _T('Count')),
         ('notify',      2,  _T('Notify')),
         )),

       'fred:nssetsbycontact': ('',(
         ('count',       1,  _T('Count')),
         ('notify',      2,  _T('Notify')),
         )),

       'fred:nssetsbyns': ('',(
         ('count',       1,  _T('Count')),
         ('notify',      2,  _T('Notify')),
         )),
         
    }
    # append similar objects
    sort_by_names['contact:list']   = sort_by_names['domain:list']
    sort_by_names['nsset:list']     = sort_by_names['domain:list']
    sort_by_names['keyset:list']    = sort_by_names['domain:list']
    sort_by_names['fred:domainsbykeyset']  = sort_by_names['fred:domainsbynsset']
    sort_by_names['fred:keysetsbycontact'] = sort_by_names['fred:nssetsbycontact']
    sort_by_names['fred:keysetsbyns']      = sort_by_names['fred:nssetsbyns']
    
    return sort_by_names
    
class Message(eppdoc_assemble.Message):
    "Client EPP commands."

    def get_sort_by_names(self, command_name):
        'Prepare column names for sorted output answer.'
        if re.match('check_',self._dct.get('command',[''])[0]):
            # check commands sort by parameters
            names = map(lambda s: (s,1,s), self._dct.get('name',[])) # (key, verbose_level, description)
        else:
            # othes commands sort by defined namse
            scope = self.sort_by_names.get(command_name,None)
            if scope:
                if scope[0]:
                    names = map(lambda i: ('%s:%s'%(scope[0],i[0]),i[1],i[2]),scope[1])
                else:
                    names = scope[1]
            else:
                names = []
        return names

    def __init__(self, manager):
        eppdoc_assemble.Message.__init__(self, manager)
        self._command_params = make_command_parameters()
        self.sort_by_names = make_sort_by_names()
    
    def reset_translation(self):
        'Reset struct with translation after changing language'
        self._command_params = make_command_parameters()
        self.sort_by_names = make_sort_by_names()
        self.make_param_required_types()
    
def test(commands):
    import pprint
    import session_base
    manager = session_base.ManagerBase()
    epp = Message(manager)
    manager.load_config()
    print "#"*60
    for cmd in commands:
        print "COMMAND:",cmd
        m = re.match('(\S+)',cmd)
        if not m: continue
        cmd_name = m.group(1)
        epp.reset()
        errors, example, stop = epp.parse_cmd(cmd_name, cmd, manager._conf, 0, 2)
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
                print 'VALID?', manager.is_epp_valid(xmlepp)
        print "EXAMPLE:",epp.get_command_line(manager._session[session_base.NULL_VALUE])
        print '='*60

def test_help(command_names):
    import terminal_controler
    import session_base
    manager = session_base.ManagerBase()
    colored_output = terminal_controler.TerminalController()
    colored_output.set_mode(options['color'])
    epp = Message(manager)
    for command_name in command_names:
        command_line,command_help,notice, examples = epp.get_help(command_name)
        print colored_output.render(command_line)
        print colored_output.render(command_help)
        print colored_output.render(notice)
        print '\nExamples:'
        print '\n'.join(examples)
        print '\n\n'

if __name__ == '__main__':
    # Test only
    test(("update_contact reg-id () () (('' '' ('' City '' '' CZ)) '' '' '' (0) '' '' notify@mail.cz)",))
