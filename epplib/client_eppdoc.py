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
import eppdoc

class Message(eppdoc.Message):
    "Client EPP commands."

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:] for name in dir(self.__class__) if name[:9]=='assemble_']

    #===========================================
    #
    # Process commands
    #
    #===========================================
    
    #-------------------------------------------
    # Session management
    #-------------------------------------------
    def assemble_hello(self, params=None):
        self.load_EPP_template('hello')

    def assemble_login(self, params):
        """Client EPP command: login
        params: (username, password, newpassword) ('user','pass','')
        """
        self.load_EPP_template('login')
        if len(self.errors): return
        self.put_value('clID', params[0])
        self.put_value('pw', params[1])
        if len(params)<3 or params[2]=='':
            # nové heslo nebylo zadáno, tag se odebere ze šablony
            self.remove_node('newPW')
        else:
            self.put_value('newPW', params[2])
        # kontrola na povinné položky
        map(self.check_node, ('clID','pw'))

    def assemble_info(self, params=None):
        'Client EPP command: info'
        self.load_EPP_template('info')
        if len(self.errors): return
        obj_info = self.new_node_by_name('info', 'obj:info')
        attr=(
            ('xmlns:obj','urn:ietf:params:xml:ns:obj'),
            ('xsi:schemaLocation','urn:ietf:params:xml:ns:obj obj.xsd')
        )
        self.append_attribNS(obj_info, attr)
        self.put_value('obj:name', u'Pokusné jméno', 'obj:info') #!!!

    def assemble_logout(self, params=None):
        self.load_EPP_template('logout')

    #-------------------------------------------
    # Dotazovací (query)
    #-------------------------------------------
    def assemble_check(self, params=None):
        self.load_EPP_template('check')

    def __assemble_info__(self, data):
        'Support fo assemble_info_...() functions.'
        self.create()
        for v in data:
            value, attr = None,None
            parent_name, name = v[0:2]
            if len(v)>2: value = v[2]
            if len(v)>3: attr  = v[3]
            self.new_node_by_name(parent_name, name, value, attr)
        
    def assemble_info_contact(self, params):
        "params must have ('name','clTRID')"
        self.__assemble_info__((
            ('epp', 'command'),
            ('command', 'info'),
            ('info','contact:info',None,(
            ('xmlns:contact','http://www.nic.cz/xml/epp/contact-1.0'),
            ('xsi:schemaLocation','http://www.nic.cz/xml/epp/contact-1.0 contact-1.0.xsd')
            )),
            ('contact:info', 'contact:id', params[0]),
            ('command', 'clTRID', params[1])
        ))

    def assemble_info_domain(self, params):
        "params must have ('name','clTRID')"
        self.__assemble_info__((
            ('epp', 'command'),
            ('command', 'info'),
            ('info','domain:info',None,(
            ('xmlns:domain','http://www.nic.cz/xml/epp/domain-1.0'),
            ('xsi:schemaLocation','http://www.nic.cz/xml/epp/domain-1.0 domain-1.0.xsd')
            )),
            ('domain:info', 'domain:name', params[0]),
            ('command', 'clTRID', params[1])
        ))

    def assemble_info_nsset(self, params):
        "params must have ('name','clTRID')"
        self.__assemble_info__((
            ('epp', 'command'),
            ('command', 'info'),
            ('info','nsset:info',None,(
            ('xmlns:nsset','http://www.nic.cz/xml/epp/nsset-1.0'),
            ('xsi:schemaLocation','http://www.nic.cz/xml/epp/nsset-1.0 nsset-1.0.xsd')
            )),
            ('nsset:info', 'nsset:id', params[0]),
            ('command', 'clTRID', params[1])
        ))

    def assemble_poll(self, params=None):
        self.load_EPP_template('poll')
    def assemble_transfer(self, params=None):
        self.load_EPP_template('transfer')

    #-------------------------------------------
    # Výkonné (transform)
    #-------------------------------------------
    def assemble_create(self, params=None):
        self.load_EPP_template('create')
    def assemble_delete(self, params=None):
        self.load_EPP_template('delete')
    def assemble_renew(self, params=None):
        self.load_EPP_template('renew')
    def assemble_update(self, params=None):
        self.load_EPP_template('update')

    #===========================================

def test_command(command, label):
    "Test if template si valid."
    epp = Message()
    cmd = command.split()
    fnc_name = "assemble_%s"%cmd[0]
    if hasattr(epp, fnc_name):
        getattr(epp, fnc_name)(cmd[1:])
    else:
        print "Error: Command not found."
    errors, xmlepp = epp.get_results()
    print '%s:'%label
    print 'XMLEPP:',xmlepp
    print 'ERRORS:',errors
    print '-'*60

if __name__ == '__main__':
    # Test na jednotlivé příkazy
    test_command('login moje-jmeno moje-heslo', 'TEST login')
    test_command('info', 'TEST info')
