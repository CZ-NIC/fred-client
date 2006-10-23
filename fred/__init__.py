# -*- coding: utf8 -*-
#!/usr/bin/env python
"""
import ccReg

try:
    epp = ccReg.Client()
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
except ccReg.ccRegError, msg:
    print msg

# or you can use function is_val() what returns value without KeyError:
# You dont keep return values. The object holds them and functions is_val() and print_answer()  use them too.
# Next possibility previous example:
    
try:
    epp = ccReg.Client()
    epp.login("reg-lrr","123456789")
    if epp.is_val() == 1000:
        epp.check_contact(("handle1","handle2"))
        if epp.is_val(('data','handle1')):
            epp.create_contact("handle1", "My Name", "email@email.net", "City", "CZ")
        else:
            epp.info_contact("handle1")
            epp.print_answer()
        epp.logout()
except ccReg.ccRegError, msg:
    print msg

#
# Example to delete created contacts:
#
import ccReg
epp = ccReg.Client()
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
from session_receiver import ccRegError
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
    
    def __init__(self):
        self._epp = ManagerReceiver()

    def connect(self):
        'Connect to the server.'
        self._epp.connect()
    def close(self):
        'Close connection with server.'
        self._epp.close()

    #==============================================================
    
    def check_contact(self, name, cltrid=None):
        """Usage: check_contact name [,name2]
    
    PARAMS:

    name (required)     unbounded list

    RETURN data: {
                name: int,  # 0/1 (0-engaged name, 1-available name)
                name:reason: str, # if name is not accessible
    }

   The EPP "check" command is used to determine if an object can be
   provisioned within a repository.  It provides a hint that allows a
   client to anticipate the success or failure of provisioning an object
   using the "create" command as object provisioning requirements are
   ultimately a matter of server policy.
   """
        return self._epp.api_command('check_contact',{'name':name, 'cltrid':cltrid})

    def check_domain(self, name, cltrid=None):
        """Usage: check_domain name [,name2]

    PARAMS:

    name (required)     unbounded list

    RETURN data: {
                name: int,  # 0/1 (0-engaged name, 1-available name)
                name:reason: str, # if name is not accessible
    }

   The EPP "check" command is used to determine if an object can be
   provisioned within a repository.  It provides a hint that allows a
   client to anticipate the success or failure of provisioning an object
   using the "create" command as object provisioning requirements are
   ultimately a matter of server policy.
   """
        return self._epp.api_command('check_domain',{'name':name, 'cltrid':cltrid})

    def check_nsset(self, name, cltrid=None):
        """Usage: check_nsset name [,name2]

    PARAMS:

    name (required)     unbounded list

    RETURN data: {
                name: int,  # 0/1 (0-engaged name, 1-available name)
                name:reason: str, # if name is not accessible
    }

   The EPP "check" command is used to determine if an object can be
   provisioned within a repository.  It provides a hint that allows a
   client to anticipate the success or failure of provisioning an object
   using the "create" command as object provisioning requirements are
   ultimately a matter of server policy.
   """
        return self._epp.api_command('check_nsset',{'name':name, 'cltrid':cltrid})

    def create_contact(self, contact_id, name, email, city, cc, auth_info=None,
            org=None, street=None, sp=None, pc=None, voice=None, fax=None, 
            disclose=None, vat=None, ssn=None, notify_email=None, 
            cltrid=None):
        """Usage: create_contact contact-id name email city cc

    PARAMS:

    contact_id (required)
    name (required)
    email (required)
    city (required)
    cc (required)
    auth_info (required)
    org (optional)
    street (optional)           list with max 3 items.
    sp (optional)
    pc (optional)
    voice (optional)
    fax (optional)
    disclose (optional)
        flag (required) y/n default y
        data (required) list: (name,org,addr,voice,fax,email)
    vat (optional)
    ssn (optional)
        type (required)
        number (required)
    notify_email (optional)

    RETURN data: {
        contact:id     str
        contact:crDate str
    }

   The EPP "create" command is used to create an instance of an object.
   An object can be created for an indefinite period of time, or an
   object can be created for a specific validity period.

        """
        return self._epp.api_command('create_contact',{
            'contact_id':contact_id, 'name':name, 'email':email, 'city':city, 'cc':cc, 'auth_info':auth_info,
            'org':org, 'street':street, 'sp':sp, 'pc':pc, 'voice':voice, 'fax':fax,
            'disclose':disclose, 'vat':vat, 'ssn':ssn, 
            'notify_email':notify_email, 'cltrid':cltrid})

    def create_domain(self, name, registrant, auth_info=None, nsset=None, period=None, admin=None, val_ex_date=None, 
        cltrid=None):
        """Usage: create_domain name auth_info registrant

    PARAMS:

    name (required)
    auth_info (required)
    period (optional)
        num (required)
        unit (required) accept only values: (y,m)
    nsset (optional)
    registrant (optional)
    admin (optional)          unbounded list
    val_ex_date (optional)

    RETURN data: {domain:name, domain:crDate, domain:exDate}

   The EPP "create" command is used to create an instance of an object.
   An object can be created for an indefinite period of time, or an
   object can be created for a specific validity period.
    """
        return self._epp.api_command('create_domain',{'name':name,'auth_info':auth_info,
            'period':period,'registrant':registrant,'nsset':nsset,'admin':admin,
            'val_ex_date':val_ex_date, 'cltrid':cltrid})

    def create_nsset(self, nsset_id, dns, tech, auth_info=None, cltrid=None):
        """Usage: create_nsset id auth_info

    PARAMS:

    id (required)
    dns (required)               list with max 9 items.
        name (required)
        addr (optional)         unbounded list
    tech (required)             unbounded list
    auth_info (optional)

    RETURN data: {nsset:id, nsset:crDate}

   The EPP "create" command is used to create an instance of an object.
   An object can be created for an indefinite period of time, or an
   object can be created for a specific validity period.

    Examples:
    create_nsset exampleNsset auth_info
    create_nsset example1 auth_info ((ns1.domain.net (217.31.207.130 217.31.207.129)),(ns2.domain.net (217.31.206.130 217.31.206.129)),(ns3.domain.net (217.31.205.130 217.31.205.129))) reg-id

        """
        return self._epp.api_command('create_nsset',{'id':nsset_id, 'auth_info':auth_info, 'dns':dns, 'tech':tech, 'cltrid':cltrid})


    def delete_contact(self, contact_id, cltrid=None):
        """Usage: delete_contact id

    PARAMS:

    id (required)

    RETURN data: {}

    The EPP "delete" command is used to remove an instance of an existing object.

        """
        return self._epp.api_command('delete_contact',{'id':contact_id, 'cltrid':cltrid})


    def delete_domain(self, name, cltrid=None):
        """Usage: delete_domain name

    PARAMS:

    name (required)

    RETURN data: {}

    The EPP "delete" command is used to remove an instance of an existing object.
        """
        return self._epp.api_command('delete_domain',{'name':name, 'cltrid':cltrid})


    def delete_nsset(self, nsset_id, cltrid=None):
        """Usage: delete_nsset id

    PARAMS:

    id (required)

    RETURN data: {}

    The EPP "delete" command is used to remove an instance of an existing object.
        """
        return self._epp.api_command('delete_nsset',{'id':nsset_id, 'cltrid':cltrid})


    def hello(self):
        """Usage: hello

    PARAMS:

    RETURN data: {
            lang:    list
            objURI:  list
            extURI:  list
            version: str
            svID:    str
            svDate:  str
            }

    The EPP "hello" request a "greeting" response message from an EPP server at any time.
        """
        return self._epp.api_command('hello')


    def info_contact(self, name, cltrid=None):
        """Usage: info_contact name

    PARAMS:

    name (required)

    RETURN data: {
            contact:org, contact:roid, contact:email, contact:city, 
            s, contact:crDate, contact:street, contact:crID, 
            contact:upDate, contact:cc, contact:id, contact:upID, 
            contact:name
        }

   The EPP "info" command is used to retrieve information associated
   with an existing object. The elements needed to identify an object
   and the type of information associated with an object are both
   object-specific, so the child elements of the <info> command are
   specified using the EPP extension framework.
        """
        return self._epp.api_command('info_contact',{'name':name, 'cltrid':cltrid})


    def info_domain(self, name, cltrid=None):
        """Usage: info_domain name

    PARAMS:

    name (required)

    RETURN data: {
        domain:contact: (list)
        domain:crID: (unicode)
        domain:clID: (unicode)
        domain:upDate: (unicode)
        domain:name: (unicode)
        domain:status.s: (unicode)
        domain:exDate: (unicode)
        domain:nsset: (unicode)
        domain:upID: (unicode)
        domain:pw: (unicode)
        domain:crDate: (unicode)
        domain:roid: (unicode)
        domain:registrant: (unicode)
        domain:renew: (unicode)
        domain:contact.type: (list)
        }
        NOTE: domain:renew (you can use for renew_domain command)

   The EPP "info" command is used to retrieve information associated
   with an existing object. The elements needed to identify an object
   and the type of information associated with an object are both
   object-specific, so the child elements of the <info> command are
   specified using the EPP extension framework.
        """
        return self._epp.api_command('info_domain',{'name':name, 'cltrid':cltrid})


    def info_nsset(self, name, cltrid=None):
        """Usage: info_nsset name

    PARAMS:

    name (required)

    RETURN data: {}

   The EPP "info" command is used to retrieve information associated
   with an existing object. The elements needed to identify an object
   and the type of information associated with an object are both
   object-specific, so the child elements of the <info> command are
   specified using the EPP extension framework.
        """
        return self._epp.api_command('info_nsset',{'name':name, 'cltrid':cltrid})


    def login(self, username, password, new_password=None, cltrid=None):
        """Usage: login username password

    PARAMS:

    username (required)
    password (required)
    new-password (optional)

    RETURN data: {
        nsset:upID: (str)
        nsset:status.s: (str)
        nsset:id: (str)
        nsset:crDate: (str)
        nsset:ns: (list) ((nsset, (addr,addr,...)), (nsset, (addr,addr,...)), ...)
        nsset:clID: (str)
        nsset:roid: (str)
        nsset:tech: (str)
        }

   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session.
        """
        return self._epp.api_command('login',{'username':username, 
            'password':password, 'new-password':new_password, 'cltrid':cltrid})


    def logout(self, cltrid=None):
        """Usage: logout

    PARAMS:

    RETURN data: {}

    The EPP "logout" command is used to end a session with an EPP server.
        """
        return self._epp.api_command('logout',{'cltrid':cltrid})


    def poll(self, op, msg_id=None, cltrid=None):
        """Usage: poll op [msg_id]

    PARAMS:

    op (required) accept only values: (req,ack)

    RETURN data: {
        count: int
        id:    int
        msg:   str
        }

    The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients.

        """
        if not type(msg_id) in ('str','unicode'): msg_id = str(msg_id)
        return self._epp.api_command('poll',{'op':op,'msg_id':msg_id, 'cltrid':cltrid})


    def renew_domain(self, name, cur_exp_date, period=None, val_ex_date=None, cltrid=None):
        """Usage: renew_domain name cur_exp_date

    PARAMS:

    name (required)
    cur_exp_date (required)
    period (optional)
        num (required)
        unit (required) accept only values: (y,m)
    val_ex_date (optional)

    RETURN data: {domain:name, domain:exDate}

    The EPP "renew" command is used to extend validity of an existing object.
        """
        return self._epp.api_command('renew_domain',{'name':name, 'cur_exp_date':cur_exp_date, 
            'period':period, 'val_ex_date':val_ex_date, 'cltrid':cltrid})


    def transfer_contact(self, name, auth_info, cltrid=None):
        """Usage: transfer_contact name auth_info

    PARAMS:

    name (required) CONTACT-ID
    auth_info (required)

    RETURN data: {}

   The EPP "transfer" command provides a query operation that allows a
   client to determine real-time status of pending and completed
   transfer requests.
   The EPP "transfer" command is used to manage changes in client
   sponsorship of an existing object.  Clients can initiate a transfer
   request, cancel a transfer request, approve a transfer request, and
   reject a transfer request using the "op" command attribute.
        """
        return self._epp.api_command('transfer_contact',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})

    def transfer_domain(self, name, auth_info, cltrid=None):
        """Usage: transfer_domain name auth_info

    PARAMS:

    name (required)
    auth_info (required)

    RETURN data: {}

   The EPP "transfer" command provides a query operation that allows a
   client to determine real-time status of pending and completed
   transfer requests.
   The EPP "transfer" command is used to manage changes in client
   sponsorship of an existing object.  Clients can initiate a transfer
   request, cancel a transfer request, approve a transfer request, and
   reject a transfer request using the "op" command attribute.
        """
        return self._epp.api_command('transfer_domain',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})

    def transfer_nsset(self, name, auth_info, cltrid=None):
        """Usage: transfer_nsset name auth_info

    PARAMS:

    name (required) NSSET-ID
    auth_info (required)

    RETURN data: {}

   The EPP "transfer" command provides a query operation that allows a
   client to determine real-time status of pending and completed
   transfer requests.
   The EPP "transfer" command is used to manage changes in client
   sponsorship of an existing object.  Clients can initiate a transfer
   request, cancel a transfer request, approve a transfer request, and
   reject a transfer request using the "op" command attribute.
        """
        return self._epp.api_command('transfer_nsset',{'name':name, 'auth_info':auth_info, 'cltrid':cltrid})


    def update_contact(self, contact_id, add=None, rem=None, chg=None, cltrid=None):
        """Usage: update_contact contact-id

    PARAMS:

    contact_id (required)
    add (optional)              list with max 5 items.
    rem (optional)              list with max 5 items.
    chg (optional)
        postal_info (optional)
            name (optional)
            org (optional)
            addr (optional)
                street (optional)  list with max 3 items.
                city (required)
                sp (optional)
                pc (optional)
                cc (required)
        voice (optional)
        fax (optional)
        email (optional)
        auth_info (optional)
        disclose (optional)
            flag (required) y/n default y
            data (required) list: (name,org,addr,voice,fax,email)
        vat (optional)
        ssn (optional)
            type (required)
            number (required)
        notifyEmail (optional)

    RETURN data: {}

    The EPP "update" command is used to update an instance of an existing object.
        """
        return self._epp.api_command('update_contact',{'contact_id':contact_id, 'add':add, 
            'rem':rem, 'chg':chg, 'cltrid':cltrid})


    def update_domain(self, name, add=None, rem=None, chg=None, val_ex_date=None, cltrid=None):
        """Usage: update_domain name

    PARAMS:

    name (required)
    add (optional)
        admin (optional)      unbounded list
        status (optional)       list with max 8 items. accept only values: (clientDeleteProhibited,clientTransferProhibited,clientUpdateProhibited,linked,ok,serverDeleteProhibited,serverTransferProhibited,serverUpdateProhibited)
    rem (optional)
        admin (optional)      unbounded list
        status (optional)       list with max 8 items. accept only values: (clientDeleteProhibited,clientTransferProhibited,clientUpdateProhibited,linked,ok,serverDeleteProhibited,serverTransferProhibited,serverUpdateProhibited)
    chg (optional)
        nsset (optional)
        registrant (optional)
        auth_info (optional)
    val_ex_date (optional)

    RETURN data: {}

    The EPP "update" command is used to update an instance of an existing object.
        """
        return self._epp.api_command('update_domain',{'name':name, 
            'add':add, 'rem':rem, 'chg':chg, 'val_ex_date':val_ex_date, 'cltrid':cltrid})


    def update_nsset(self, nsset_id, add=None, rem=None, chg=None, cltrid=None):
        """Usage: update_nsset id

    PARAMS:

    id (required)
    add (optional)
        dns (optional)           list with max 9 items.
            name (required)
            addr (optional)     unbounded list
        tech (optional)         unbounded list
        status (optional)       list with max 6 items. accept only values: (clientDeleteProhibited,clientTransferProhibited,clientUpdateProhibited,linked,ok,serverDeleteProhibited,serverTransferProhibited,serverUpdateProhibited)
    rem (optional)
        name (optional)         list with max 9 items.
        tech (optional)         unbounded list
        status (optional)       list with max 6 items. accept only values: (clientDeleteProhibited,clientTransferProhibited,clientUpdateProhibited,linked,ok,serverDeleteProhibited,serverTransferProhibited,serverUpdateProhibited)
    chg (optional)
        auth_info (optional)

    RETURN data: {}

    The EPP "update" command is used to update an instance of an existing object.

    Examples:
    update_nsset nic.cz
    update_nsset nsset-ID (((nsset1.name.cz 127.0.0.1),(nsset2.name.cz (127.0.2.1 127.0.2.2)),) tech-add-contact ok) ("My Name",("Tech contact 1","Tech contact 2"),(clientDeleteProhibited ok)) (auth_info extension)
        """
        return self._epp.api_command('update_nsset',{'id':nsset_id, 'add':add, 'rem':rem, 'chg':chg, 'cltrid':cltrid})

    def list_contact(self, cltrid=None):
        """Usage: list_contact

    PARAMS:

    RETURN data: {
            count:   int
            list:    list
            }
    The EPP "list" command is used to list all ID of an existing object owning by registrant.
        """
        return self._epp.api_command('list_contact',{'cltrid':cltrid})
        
    def list_nsset(self, cltrid=None):
        """Usage: list_nsset

    PARAMS:

    RETURN data: {
            count:   int
            list:    list
            }
    The EPP "list" command is used to list all ID of an existing object owning by registrant.
        """
        return self._epp.api_command('list_nsset',{'cltrid':cltrid})

    def list_domain(self, cltrid=None):
        """Usage: list_domain

    PARAMS:

    RETURN data: {
            count:   int
            list:    list
            }
    The EPP "list" command is used to list all ID of an existing object owning by registrant.
        """
        return self._epp.api_command('list_domain',{'cltrid':cltrid})

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
        self._epp._validate = mode

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
    'Check for needed Python version. Returns "" if OK anf "..." not valid.'
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

