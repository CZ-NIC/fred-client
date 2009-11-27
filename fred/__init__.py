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
"""
import fred

try:
    epp = fred.Client()
    ret = epp.login("reg-lrr","123456789")
    if ret['code'] == 1000:
        ret = epp.check_contact(("handle1","handle2"))
        if ret['data']['handle1']:
            # handle is available
            ret = epp.create_contact("handle1", "My Name", "email@email.net", "City", "CZ")
            epp.print_answer(ret)
        ret = epp.info_contact("handle1")
        epp.print_answer(ret)
        epp.logout()
except fred.FredError, msg:
    print msg

# or you can use function is_val() what returns value without KeyError:
# You dont keep return values. The object holds them and functions is_val() and print_answer()  use them too.
# Next possibility previous example:
    
try:
    epp = fred.Client()
    epp.login("reg-lrr","123456789")
    if epp.is_val() == 1000:
        epp.check_contact(("handle1","handle2"))
        if epp.is_val(('data','handle1')):
            epp.create_contact("handle1", "My Name", "email@email.net", "City", "CZ")
        else:
            epp.info_contact("handle1")
            epp.print_answer()
        epp.logout()
except fred.FredError, msg:
    print msg

#
# Example to delete created contacts:
#
import fred
epp = fred.Client()
epp.login("REG-LRR","123456789")
if epp.is_val() == 1000:
    ret = epp.check_contact(("handle1","handle2"))
    if not epp.is_val(('data','handle1'), ret):
        print "Delete handle1"
        epp.delete_contact("handle1")
        epp.print_answer()
    if not epp.is_val(('data','handle2'), ret):
        print "Delete handle2"
        epp.delete_contact("handle2")
        epp.print_answer()
    print "Check if is deleted:"
    epp.check_contact(("handle1","handle2"))
    epp.print_answer()
    epp.logout()

"""
import sys
from session_receiver import ManagerReceiver
from session_receiver import FredError
import translate

class Client:
    """EPP client API. Process whole EPP communication with server.
    Defaults values you can save into config file.
    
    Every function does:

        - check input parameters
        - fill missing params from config
        - build EPP command
        - send EPP command to the server
        - waiting for answer
        - receive EPP server ansver
        - compile answer to the dictionary
        - returns dict whith values from server
            dict has this format:
                code:     (int) number of answer code
                reason:  (str) message witt reason
                errors:   (list) errors
                data:     (dict) individual values - see doc or help in functions
        
    Functions accept parameters in this formats:
                       (for example)
        - string        login("user","pass")
        - list          check_domain(['domain1','domain2','domain3'])
        - dict          create_domain(period={'num':6, 'unit':'y'}, ...
        - list of dict  update_nsset('handle_nsset', {'dns':[{'name':'ns.name1', 'addr':'127.0.0.1'}, {'name':'ns.name2', 'addr':'127.2.2.2'}, ...], 'tech':'...'}, ...)

    Exception is raised if any error occurs.
    """
    def __init__(self, cwd=None):
        self._cwd = cwd
        self._epp = ManagerReceiver(cwd=self._cwd)

    def get_epp(self):
        return self._epp

    def connect(self):
        'Connect to the server.'
        self._epp.connect()

    def close(self):
        'Close connection with server.'
        self._epp.close()

    #==============================================================
    
    def check_contact(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'check_contact' command is used to determine if an contact can be
  provisioned within a repository. It provides a hint that allows a
  client to anticipate the success or failure of provisioning an contact
  using the 'create_contact' command as contact provisioning requirements are
  ultimately a matter of server policy.

SYNTAX:
  check_contact name [other_options]

OPTIONS:
  name (required)          Contact ID (unbounded list)
  cltrid                   Client transaction ID"""
        return self._epp.api_command('check_contact',{'name':name, 'cltrid':cltrid})

    def check_domain(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'check_domain' command is used to determine if an domain can be
  provisioned within a repository.  It provides a hint that allows a
  client to anticipate the success or failure of provisioning an domain
  using the 'create_domain' command as domain provisioning requirements are
  ultimately a matter of server policy.

SYNTAX:
  check_domain name [other_options]

OPTIONS:
  name (required)          Domain name (unbounded list)
  cltrid                   Client transaction ID"""
        return self._epp.api_command('check_domain',{'name':name, 'cltrid':cltrid})

    def check_nsset(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'check_nsset' command is used to determine if an NSSET can be
  provisioned within a repository.  It provides a hint that allows a
  client to anticipate the success or failure of provisioning an nsset
  using the 'create_nsset' command as NSSET provisioning requirements are
  ultimately a matter of server policy.

SYNTAX:
  check_nsset name [other_options]

OPTIONS:
  name (required)          NSSET ID (unbounded list)
  cltrid                   Client transaction ID"""
        return self._epp.api_command('check_nsset',{'name':name, 'cltrid':cltrid})

    def check_keyset(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'check_keyset' command is used to determine if an KEYSET can be
  provisioned within a repository.  It provides a hint that allows a
  client to anticipate the success or failure of provisioning an keyset
  using the 'create_keyset' command as KEYSET provisioning requirements are
  ultimately a matter of server policy.

SYNTAX:
  check_keyset name [other_options]

OPTIONS:
  name (required)          KEYSET ID (unbounded list)
  cltrid                   Client transaction ID"""
        return self._epp.api_command('check_keyset',{'name':name, 'cltrid':cltrid})


    def create_contact(self, contact_id, name, email, street, city, pc, cc, 
            sp=None, org=None, auth_info=None, voice=None, fax=None, 
            disclose=None, vat=None, ident=None, notify_email=None, 
            cltrid=None):
        """DESCRIPTION:
  The EPP 'create_contact' command is used to create an instance of the contact.
  Contact can be used for values of the owner, registrant or technical contact.

  Names what are not included into disclose list are set to opposite value of the disclose flag value.

  Identificator type can be:
     op        Number identity card
     passport  Number of passport
     mpsv      Number of Ministry of Labour and social affairs
     ico       Number of company
     birthday  Birthday date

SYNTAX:
  create_contact contact_id name email city cc [other_options]

OPTIONS:
  contact_id (required)    Contact ID
  name (required)          Name
  email (required)         Email
  street (required)        Street (list with max 3 items.)
  city (required)          City
  pc (required)            Postal code
  cc (required)            Country code
  sp                       State or province
  org                      Organisation
  auth_info                Password required by server to authorize the transfer
  voice                    Phone
  fax                      Fax
  disclose                 Disclose
    flag (required)        Disclose flag (default y)
                           (y,n)
    data                   Data for with is set the flag value (list with max 9 items.)
                           (voice,fax,email,vat,ident,notify_email)
  vat                      VAT (Value-added tax)
  ident                    Identificator
    number (required)      Identificator number
    type (required)        Identificator type
                           (op,passport,mpsv,ico,birthday)
  notify_email             Notification email
  cltrid                   Client transaction ID"""
        return self._epp.api_command('create_contact',{
            'contact_id':contact_id, 'name':name, 'email':email, 'city':city, 'cc':cc, 'auth_info':auth_info,
            'org':org, 'street':street, 'sp':sp, 'pc':pc, 'voice':voice, 'fax':fax,
            'disclose':disclose, 'vat':vat, 'ident':ident, 
            'notify_email':notify_email, 'cltrid':cltrid})

    def create_domain(self, name, registrant, auth_info=None, nsset=None, keyset=None, period=None, admin=None, val_ex_date=None, 
        cltrid=None):
        """DESCRIPTION:
  The EPP 'create_domain' command is used to create domain.
  A domain can be created for an indefinite period of time, or
  a domain can be created for a specific validity period. Basicly
  you can create two types of the domain: cz and ENUM.
  The difference is in parameter val_ex_date. It is required
  for ENUM domains.

SYNTAX:
  create_domain name registrant [other_options]

OPTIONS:
  name (required)          Domain name
  registrant (required)    Registrant ID
  auth_info                Password required by server to authorize the transfer
  nsset                    NSSET ID
  keyset                   KEYSET ID
  period                   Period
    num (required)         Number of months or years
    unit (required)        Period unit (y year(default), m month)
  admin                    Administrative contact ID (unbounded list)
  val_ex_date              Validation expires at date. This value is required for ENUM domains.
  cltrid                   Client transaction ID"""
        return self._epp.api_command('create_domain',{'name':name,'auth_info':auth_info,
            'period':period,'registrant':registrant, 'nsset':nsset, 'keyset':keyset, 'admin':admin,
            'val_ex_date':val_ex_date, 'cltrid':cltrid})

    def create_nsset(self, nsset_id, dns, tech, auth_info=None, reportlevel=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'create_nsset' command is used to create a record of the NSSET.

  Report level sets depth level of the technical test. These tests are maintained
  in regular intervals and in case of the problem the technical contact is informed.
  Report level is also applied on the test executed by the request throught EPP.
  Every test has report level (number) and run just a parts what have equal or
  lower level number. Valid range is from 0 to 10.

SYNTAX:
  create_nsset id dns tech [other_options]

OPTIONS:
  id (required)            NSSET ID
  dns (required)           LIST of DNS (minimum 2 items, list with max 9 items.)
    name (required)        Name server
    addr                   Server address (unbounded list)
  tech (required)          Technical contact (unbounded list)
  auth_info                Password required by server to authorize the transfer
  reportlevel              Report level. Range 0 - 10
  cltrid                   Client transaction ID"""
        return self._epp.api_command('create_nsset',{'id':nsset_id, 'auth_info':auth_info,
            'dns':dns, 'tech':tech, 'reportlevel':reportlevel, 'cltrid':cltrid})


    def create_keyset(self, keyset_id, dnskey, dnskeyref, tech, auth_info=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'create_keyset' command is used to create a record of the KEYSET.

SYNTAX:
  create_keyset id dnskey tech [other_options]

OPTIONS:
  id (required)            KEYSET ID
  dnskey                   LIST of keys (list with max 9 items.)
    flags (required)       Flags
    protocol (required)    Protocol
    alg (required)         Algorithm
    pub_key (required)     Public key code
  dnskeyref                LIST of filenames with dns keys (list with max 9 items.)
  tech (required)          Technical contact (unbounded list)
  auth_info                Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('create_keyset',{'id':keyset_id, 'auth_info':auth_info,
            'dnskey':dnskey, 'dnskeyref':dnskeyref, 'tech':tech, 'cltrid':cltrid})


    def delete_contact(self, contact_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'delete_contact' command is used to remove a record of the contact.

SYNTAX:
  delete_contact id [other_options]

OPTIONS:
  id (required)            Contact ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('delete_contact',{'id':contact_id, 'cltrid':cltrid})


    def delete_domain(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'delete_domain' command is used to remove a record of the domain.

SYNTAX:
  delete_domain name [other_options]

OPTIONS:
  name (required)          Domain name
  cltrid                   Client transaction ID"""
        return self._epp.api_command('delete_domain',{'name':name, 'cltrid':cltrid})


    def delete_nsset(self, nsset_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'delete_nsset' command is used to remove a record of the nsset.

SYNTAX:
  delete_nsset id [other_options]

OPTIONS:
  id (required)            NSSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('delete_nsset',{'id':nsset_id, 'cltrid':cltrid})


    def delete_keyset(self, keyset_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'delete_keyset' command is used to remove a record of the keyset.

SYNTAX:
  delete_keyset id [other_options]

OPTIONS:
  id (required)            KEYSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('delete_keyset',{'id':keyset_id, 'cltrid':cltrid})


    def hello(self):
        """DESCRIPTION:
  Command 'hello' is used to obtain information from the server.
  The server answer to 'hello' command is Greeting message. This message
  is used usualy at the begining of the session for getting some variables
  usefull for communication. Within Server version or ID you can got
  available languages, Data Collection policy etc.
  Command 'hello' you can call at any time.

SYNTAX:
  hello

OPTIONS:
"""
        return self._epp.api_command('hello')


    def info_contact(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'info_contact' command is used to retrieve information associated
  with an existing contact. The value 'Password for transfer' is shown only
  for privileged user.

SYNTAX:
  info_contact name [other_options]

OPTIONS:
  name (required)          Contact ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('info_contact',{'name':name, 'cltrid':cltrid})


    def info_domain(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'info_domain' command is used to retrieve information associated
  with an existing domain. The value 'Password for transfer' is shown only
  for privileged user. In addition for domain ENUM type the private values
  are also 'Registrant ID' and 'Administrative contact'.

SYNTAX:
  info_domain name [other_options]

OPTIONS:
  name (required)          Domain name
  cltrid                   Client transaction ID"""
        return self._epp.api_command('info_domain',{'name':name, 'cltrid':cltrid})


    def info_nsset(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'info_nsset' command is used to retrieve information associated
  with an existing NSSET. The value 'Password for transfer' is shown only
  for privileged user.

SYNTAX:
  info_nsset name [other_options]

OPTIONS:
  name (required)          NSSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('info_nsset',{'name':name, 'cltrid':cltrid})


    def info_keyset(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'info_keyset' command is used to retrieve information associated
  with an existing KEYSET. The value 'Password for transfer' is shown only
  for privileged user.

SYNTAX:
  info_keyset name [other_options]

OPTIONS:
  name (required)          KEYSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('info_keyset',{'name':name, 'cltrid':cltrid})


    def login(self, username, password, new_password=None, lang=None, cltrid=None):
        """DESCRIPTION:
  The "login" command establishes an ongoing server session that preserves client identity
  and authorization information during the duration of the session. Parametr "lang" set
  session and client language together. Language is possible to set also by option on the
  command line, or define it in configuration file or set by client command 'lang'.
  Using parameter 'new_password' you can change password.

SYNTAX:
  login username password [other_options]

OPTIONS:
  username (required)      Username
  password (required)      Password
  new_password             New password
  lang                     Language version
  cltrid                   Client transaction ID"""
        
        if self._epp._conf:
            # if parameters are set as a list, use first item only. This list haven't been never empty.
            if type(username) in (list,tuple): username = username[0]
            if type(password) in (list,tuple):  password = password[0]
            # We need save username+password to config section epp_login.
            # It is used by function get_actual_username_and_password() for obtain
            # actual login values. This is used in unittest for check value equality.
            self._epp._conf.set(self._epp._section_epp_login, 'username', username)
            self._epp._conf.set(self._epp._section_epp_login, 'password', password)

        return self._epp.api_command('login',{'username':username, 
            'password':password, 'new_password':new_password, 'lang':lang, 'cltrid':cltrid})


    def logout(self, cltrid=None):
        """DESCRIPTION:
  The EPP "logout" command is used to end a session with the server.
  But client will be still running. For close client type 'quit' (see help).
  Before quit the client send logout automaticly.

SYNTAX:
  logout [other_options]

OPTIONS:
  cltrid                   Client transaction ID"""
        return self._epp.api_command('logout',{'cltrid':cltrid})


    def poll(self, op, msg_id=None, cltrid=None):
        """DESCRIPTION:
  Poll command is used to discover and retrieve service messages. They are saved
  in the message queue. When you send poll with parameter op = req,
  you get only the last message from the queue. But this message
  still remains on the queue. For remove message from the queue set
  poll op = ack and ID of this message. So you needs to send two poll
  commands for manage one message: 1. reading, 2. removing.
  See help poll_autoack for client function that sends this commands together.

SYNTAX:
  poll op [other_options]

OPTIONS:
  op (required)            Query type
  msg_id (required)        Index of message (required only with op = 'ack')
  cltrid                   Client transaction ID"""
        if type(msg_id) is int:
            msg_id = str(msg_id) # allowed strings only
        return self._epp.api_command('poll',{'op':op,'msg_id':msg_id, 'cltrid':cltrid})


    def sendauthinfo_contact(self, contact_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_contact' command transmit request for send password
  to contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_contact id [other_options]

OPTIONS:
  id (required)            Contact ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_contact',{'id':contact_id, 'cltrid':cltrid})

    def sendauthinfo_domain(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_domain' command transmit request for send password
  to registrant email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_domain name [other_options]

OPTIONS:
  name (required)          Domain name
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_domain',{'name':name, 'cltrid':cltrid})

    def sendauthinfo_nsset(self, nsset_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_nsset' command transmit request for send password
  to technical contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_nsset id [other_options]

OPTIONS:
  id (required)            NSSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_nsset',{'id':nsset_id, 'cltrid':cltrid})

    def sendauthinfo_keyset(self, keyset_id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_keyset' command transmit request for send password
  to technical contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_keyset id [other_options]

OPTIONS:
  id (required)            KEYSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_keyset',{'id':keyset_id, 'cltrid':cltrid})

    def credit_info(self, cltrid=None):
        """DESCRIPTION:
  The EPP 'credit_info' command returns credit information.

SYNTAX:
  credit_info [other_options]

OPTIONS:
  cltrid                   Client transaction ID"""
        return self._epp.api_command('credit_info',{'cltrid':cltrid})

    def renew_domain(self, name, cur_exp_date, period=None, val_ex_date=None, cltrid=None):
        """DESCRIPTION:
  A domain names have a specified validity period. The server
  policy supports domain validity periods and the validity period
  is defined when a domain is created. This validity can be extended
  by the EPP 'renew_domain' command.

  Validity periods are measured in years or months with the appropriate
  units specified using the 'unit' attribute.  Valid values for the
  'unit' attribute are 'y' for years and 'm' for months.  The minimum
  and maximum allowable period is defined in the Communication rules.

SYNTAX:
  renew_domain name cur_exp_date [other_options]

OPTIONS:
  name (required)          Domain name
  cur_exp_date (required)  Expiration date
  period                   Period
    num (required)         Number of months or years
    unit (required)        Period unit (y year(default), m month)
  val_ex_date              Validation expires at
  cltrid                   Client transaction ID"""
        return self._epp.api_command('renew_domain',{'name':name, 'cur_exp_date':cur_exp_date, 
            'period':period, 'val_ex_date':val_ex_date, 'cltrid':cltrid})


    def transfer_contact(self, name, auth_info, cltrid=None):
        """DESCRIPTION:
  The EPP 'transfer_contact' command makes change in contact sponsorship
  of a designated registrar. New password for authorisation
  will be generated automaticly after succefull transfer.

SYNTAX:
  transfer_contact name auth_info [other_options]

OPTIONS:
  name (required)          Contact ID
  auth_info (required)     Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('transfer_contact',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})

    def transfer_domain(self, name, auth_info, cltrid=None):
        """DESCRIPTION:
  The EPP 'transfer_domain' command makes change in domain sponsorship
  of a designated registrar. New password for authorisation
  will be generated automaticly after succefull transfer.

SYNTAX:
  transfer_domain name auth_info [other_options]

OPTIONS:
  name (required)          Domain name of domain to change sponsorship
  auth_info (required)     Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('transfer_domain',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})

    def transfer_nsset(self, name, auth_info, cltrid=None):
        """DESCRIPTION:
  The EPP 'transfer_nsset' command makes change in NSSET sponsorship
  of a designated registrar. New password for authorisation
  will be generated automaticly after succefull transfer.

SYNTAX:
  transfer_nsset name auth_info [other_options]

OPTIONS:
  name (required)          NSSET ID
  auth_info (required)     Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('transfer_nsset',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})

    def transfer_keyset(self, name, auth_info, cltrid=None):
        """DESCRIPTION:
  The EPP 'transfer_keyset' command makes change in KEYSET sponsorship
  of a designated registrar. New password for authorisation
  will be generated automaticly after succefull transfer.

SYNTAX:
  transfer_keyset name auth_info [other_options]

OPTIONS:
  name (required)          KEYSET ID
  auth_info (required)     Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('transfer_keyset',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})


    def update_contact(self, contact_id, chg=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'update_contact' command is used to update values in the contact.
  
  Names what are not included into disclose list are set to opposite value of the disclose flag value.
  
  Identificator type can be:
     op        Number identity card
     passport  Number of passport
     mpsv      Number of Ministry of Labour and social affairs
     ico       Number of company
     birthday  Birthday date

SYNTAX:
  update_contact contact_id [other_options]

OPTIONS:
  contact_id (required)    Contact ID
  chg                      Change values
    postal_info            Postal informations
      name                 Name
      org                  Organisation
      addr                 Address
        street (required)  Street (list with max 3 items.)
        city (required)    City
        pc (required)      Postal code
        cc (required)      Country code
        sp                 State or province
    voice                  Phone
    fax                    Fax
    email                  Email
    auth_info              Password required by server to authorize the transfer
    disclose               Disclose
      flag (required)      Disclose flag (default y)
      data                 data for with is set the flag value (list with max 6 items.)
    vat                    VAT
    ident                  Identificator
      type (required)      Identificator type
      number (required)    Identificator number
    notify_email           Notification email
  cltrid                   Client transaction ID"""
        return self._epp.api_command('update_contact',{'contact_id':contact_id,
            'chg':chg, 'cltrid':cltrid})


    def update_domain(self, name, add_admin=None, rem_admin=None, rem_tempc=None, chg=None, val_ex_date=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'update_domain' command is used to update values in the domain.

SYNTAX:
  update_domain name [other_options]

OPTIONS:
  name (required)          Domain name
  add_admin                Administrative contact ID (unbounded list)
  rem_admin                Administrative contact ID (unbounded list)
  rem_tempc                Temporary contact ID (unbounded list)
  chg                      Change values
    nsset                  NSSET ID
    keyset                 KEYSET ID
    registrant             Registrant ID
    auth_info              Password required by server to authorize the transfer
  val_ex_date              Validation expires at
  cltrid                   Client transaction ID"""
        return self._epp.api_command('update_domain',{'name':name, 
            'add_admin':add_admin, 'rem_admin':rem_admin, 'rem_tempc':rem_tempc, 'chg':chg, 'val_ex_date':val_ex_date, 'cltrid':cltrid})


    def update_nsset(self, nsset_id, add=None, rem=None, auth_info=None, reportlevel=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'update_nsset' command is used to update values in the NSSET.

SYNTAX:
  update_nsset id [other_options]

OPTIONS:
  id (required)            NSSET ID
  add                      Add values
    dns                    List of DNS (list with max 9 items.)
      name (required)      Name server
      addr                 Server address (unbounded list)
    tech                   Technical contact ID (unbounded list)
  rem                      Remove values
    name                   Name server (list with max 9 items.)
    tech                   Technical contact ID (unbounded list)
  auth_info                Password required by server to authorize the transfer
  reportlevel              Report level. Range 0 - 10
  cltrid                   Client transaction ID"""
        return self._epp.api_command('update_nsset',{'id':nsset_id, 'add':add, 'rem':rem, 'auth_info':auth_info, 'reportlevel':reportlevel, 'cltrid':cltrid})

    def update_keyset(self, keyset_id, add=None, rem=None, auth_info=None, reportlevel=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'update_keyset' command is used to update values in the KEYSET.

SYNTAX:
  update_keyset id [other_options]

OPTIONS:
  id (required)            KEYSET ID
  add                      Add values
    dnskey                 LIST of keys (list with max 9 items.)
      flags (required)     Flags
      protocol (required)  Protocol
      alg (required)       Algorithm
      pub_key (required)   Public key code
    dnskeyref              LIST of filenames with dns keys (list with max 9 items.)
    tech                   Technical contact ID (unbounded list)
  rem                      Remove values
    dnskey                 LIST of keys (list with max 9 items.)
      flags (required)     Flags
      protocol (required)  Protocol
      alg (required)       Algorithm
      pub_key (required)   Public key code
    dnskeyref              LIST of filenames with dns keys (list with max 9 items.)
    tech                   Technical contact ID (unbounded list)
  auth_info                Password required by server to authorize the transfer
  cltrid                   Client transaction ID"""
        return self._epp.api_command('update_keyset',{'id':keyset_id, 'add':add, 'rem':rem, 'auth_info':auth_info, 'reportlevel':reportlevel, 'cltrid':cltrid})


    def sendauthinfo_contact(self, id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_contact' command transmit request for send password
  to contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_contact id [other_options]

OPTIONS:
  id (required)            Contact ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_contact',{'id':id, 'cltrid':cltrid})

    def sendauthinfo_nsset(self, id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_nsset' command transmit request for send password
  to technical contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_nsset id [other_options]

OPTIONS:
  id (required)            NSSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_nsset',{'id':id, 'cltrid':cltrid})

    def sendauthinfo_keyset(self, id, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_keyset' command transmit request for send password
  to technical contact email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_keyset id [other_options]

OPTIONS:
  id (required)            KEYSET ID
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_keyset',{'id':id, 'cltrid':cltrid})

    def sendauthinfo_domain(self, name, cltrid=None):
        """DESCRIPTION:
  The EPP 'sendauthinfo_domain' command transmit request for send password
  to registrant email. This command is usefull during transfer
  when owner and new registrar needn't require previous registrar for password.

SYNTAX:
  sendauthinfo_domain name [other_options]

OPTIONS:
  name (required)          Domain name
  cltrid                   Client transaction ID"""
        return self._epp.api_command('sendauthinfo_domain',{'name':name, 'cltrid':cltrid})

    def credit_info(self, cltrid=None):
        """DESCRIPTION:
  The EPP 'credit_info' command returns credit information.

SYNTAX:
  credit_info [other_options]

OPTIONS:
  cltrid                   Client transaction ID"""
        return self._epp.api_command('credit_info',{'cltrid':cltrid})

    def technical_test(self, id, level=None, name=None, cltrid=None):
        """DESCRIPTION:
  The EPP 'technical_test' command transmit request for technical test
  for particular NSSET and domain. The result of the test will be saved
  into the message queue from where the registrant can fetch it
  by poll command. Every test has report level (number) and run just
  a parts what have equal or lower level number. Valid range
  is from 0 to 10. Set report level in the command create_nsset
  and update_nsset.

SYNTAX:
  technical_test id name [other_options]

OPTIONS:
  id (required)            NSSET ID
  level                    Report range level (0 - 10; higher = more detailed)
  name                     Domain name
  cltrid                   Client transaction ID"""
        return self._epp.api_command('technical_test',{'id':id, 'level':level, 'name':name, 'cltrid':cltrid})

    def get_results(self, cltrid=None):
        """DESCRIPTION:
  Get results from server buffer. Server returns chunk of the list.
  Call 'get_results' again until you got all data.

SYNTAX:
  get_results [other_options]

OPTIONS:
  cltrid                   Client transaction ID

EXAMPLES:
  get_results"""
        return self._epp.api_command('get_results',{'cltrid':cltrid})

    def prep_contacts(self, cltrid=None):
        """DESCRIPTION:
  Prepare list of the contacts. This command fills server buffer by list 
  of contacts and set pointer at the beginning of the list. The list 
  is taken in sequence by calling command 'get_results' repeatedly 
  until any data comming.

SYNTAX:
  prep_contacts [other_options]

OPTIONS:
  cltrid                   Client transaction ID

EXAMPLES:
  prep_contacts"""
        return self._epp.api_command('prep_contacts',{'cltrid':cltrid})
        
    def prep_nssets(self, cltrid=None):
        """DESCRIPTION:
  Prepare list of the NSSETs. This command fills server buffer by list 
  of nssets and set pointer at the beginning of the list. The list 
  is taken in sequence by calling command 'get_results' repeatedly 
  until any data comming.

SYNTAX:
  prep_nssets [other_options]

OPTIONS:
  cltrid                   Client transaction ID

EXAMPLES:
  prep_nssets"""
        return self._epp.api_command('prep_nssets',{'cltrid':cltrid})

    def prep_keysets(self, cltrid=None):
        """DESCRIPTION:
  Prepare list of the KEYSETs. This command fills server buffer by list 
  of keysets and set pointer at the beginning of the list. The list 
  is taken in sequence by calling command 'get_results' repeatedly 
  until any data comming.

SYNTAX:
  prep_keysets [other_options]

OPTIONS:
  cltrid                   Client transaction ID

EXAMPLES:
  prep_keysets"""
        return self._epp.api_command('prep_keysets',{'cltrid':cltrid})
        
    def prep_domains(self, cltrid=None):
        """DESCRIPTION:
  Prepare list of the domains. This command fills server buffer by list 
  of domains and set pointer at the beginning of the list. The list is 
  taken in sequence by calling command 'get_results' repeatedly until 
  any data comming.

SYNTAX:
  prep_domains [other_options]

OPTIONS:
  cltrid                   Client transaction ID

EXAMPLES:
  prep_domains"""
        return self._epp.api_command('prep_domains',{'cltrid':cltrid})
        
    def prep_domains_by_nsset(self, id, cltrid=None):
        """DESCRIPTION:
  Prepare domains by NSSET. This command fills server buffer by list 
  of domains connected with defined nsset ID. The pointer is set 
  at the beginning of the list. The list is taken in sequence 
  by calling command 'get_results' repeatedly until any data comming.

SYNTAX:
  prep_domains_by_nsset id [other_options]

OPTIONS:
  id (required)            NSSET ID
  cltrid                   Client transaction ID

EXAMPLES:
  prep_domains_by_nsset NSSID:VALID"""
        return self._epp.api_command('prep_domains_by_nsset',{'id':id, 'cltrid':cltrid})
        
    def prep_domains_by_keyset(self, id, cltrid=None):
        """DESCRIPTION:
  Prepare domains by KEYSET. This command fills server buffer by list 
  of domains connected with defined keyset ID. The pointer is set 
  at the beginning of the list. The list is taken in sequence 
  by calling command 'get_results' repeatedly until any data comming.

SYNTAX:
  prep_domains_by_keyset id [other_options]

OPTIONS:
  id (required)            KEYSET ID
  cltrid                   Client transaction ID

EXAMPLES:
  prep_domains_by_keyset KEYSID:VALID"""
        return self._epp.api_command('prep_domains_by_keyset',{'id':id, 'cltrid':cltrid})

    def prep_domains_by_contact(self, id, cltrid=None):
        """DESCRIPTION:
  Prepare domains by contact. This command fills server buffer by list 
  of domains where occurs defined contact ID. It can be Registrant 
  ID or Admin ID or Temporary ID. The pointer is set at the beginning 
  of the list. The list is taken in sequence by calling command 
  'get_results' repeatedly until any data comming.

SYNTAX:
  prep_domains_by_contact id [other_options]

OPTIONS:
  id (required)            Contact ID
  cltrid                   Client transaction ID

EXAMPLES:
  prep_domains_by_contact CID:TECH"""
        return self._epp.api_command('prep_domains_by_contact',{'id':id, 'cltrid':cltrid})

    def prep_nssets_by_contact(self, id, cltrid=None):
        """DESCRIPTION:
  Prepare NSSETs by contact. This command fills server buffer by list 
  of nssets connected with defined technical contact ID. The pointer 
  is set at the beginning of the list. The list is taken in sequence 
  by calling command 'get_results' repeatedly until any data comming.

SYNTAX:
  prep_nssets_by_contact id [other_options]

OPTIONS:
  id (required)            Technical contact
  cltrid                   Client transaction ID

EXAMPLES:
  prep_nssets_by_contact CID:ADMIN"""
        return self._epp.api_command('prep_nssets_by_contact',{'id':id, 'cltrid':cltrid})

    def prep_keysets_by_contact(self, id, cltrid=None):
        """DESCRIPTION:
  Prepare KEYSETs by contact. This command fills server buffer by list 
  of keysets connected with defined technical contact ID. The pointer 
  is set at the beginning of the list. The list is taken in sequence 
  by calling command 'get_results' repeatedly until any data comming.

SYNTAX:
  prep_keysets_by_contact id [other_options]

OPTIONS:
  id (required)            Technical contact
  cltrid                   Client transaction ID

EXAMPLES:
  prep_keysets_by_contact CID:ADMIN"""
        return self._epp.api_command('prep_keysets_by_contact',{'id':id, 'cltrid':cltrid})
        
    def prep_nssets_by_ns(self, name, cltrid=None):
        """DESCRIPTION:
  Prepare NSSETs by NS. This command fills server buffer by list of nssets 
  connected with defined name server. The pointer is set at the beginning 
  of the list. The list is taken in sequence by calling command 'get_results'
  repeatedly until any data comming.

SYNTAX:
  prep_nssets_by_ns name [other_options]

OPTIONS:
  name (required)          Name server
  cltrid                   Client transaction ID

EXAMPLES:
  prep_nssets_by_ns mydomain.cz"""
        return self._epp.api_command('prep_nssets_by_ns',{'name':name, 'cltrid':cltrid})

    #==============================================================
        
    def get_answer_dct(self):
        """Returns dict object answer. Same as every function returns.
        You can use this if you dont catch retvals from functions.
        """
        return self._epp._dct_answer

    def get_answer(self, dct=None):
        "Returns str of dict object."
        return self._epp.get_answer(dct)

    def print_answer(self, dct=None):
        "Show dict object."
        self._epp.print_answer(dct)

    def print_errors(self):
        'Display interal results.'
        self._epp.display()

    def src(self):
        'Display EPP sources of the command and answer.'
        return '%s:\n%s\n%s\n%s:\n%s'%('Command',self._epp._raw_cmd,'-'*60,'Answer',self._epp._raw_answer)

    def set_validate(self, mode):
        'Set process validate ON/OFF. mode: 0/1.'
        self._epp.set_validate(mode)

    def is_val(self, names = 'code', dct=None):
        """Returns safetly value form dict (treat missing keys).
        Parametr names can by str or list ro tuple.
        """
        return self._epp.get_value_from_dict(names,dct)

    def is_logon(self):
        'Check if client is login on the server.'
        return self._epp.is_logon()

    def load_config(self, session=''):
        'Load config file.'
        if len(session): translate.options['session'] = session
        return self._epp.load_config(translate.options)

    def set_data_connect(self, dc):
        'Set data for connection: dc = {host: str, port: str, priv_key: str, cert: str, timeout: str }'
        return self._epp.set_data_connect(dc)
    
def check_python_version():
    """Check for needed Python version. Returns "" if OK anf "..." not valid.
    Alert! This function has no effect, because when translate module is imported
    it use function incompatible with older python version: gettext.translation()
    """
    if sys.version_info[:2] < (2,4):
        invalid = _T('This program requires Python 2.4 or higher. Your version is'),'.'.join([str(x) for x in sys.version_info[:3]])
    else:
        invalid = ''
    return invalid

class ClientSession(ManagerReceiver):
    "Use for console or batch applications."


if __name__ == '__main__':
    epp = Client()
    print epp.login("reg-lrr","123456789")
    print "[END]"

