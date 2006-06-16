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
import eppdoc

ONLY_ONE_VALUE = 1 # definice pro funkci __asseble_command__()

class Message(eppdoc.Message):
    "Client EPP commands."
    
    transfer_op = ('request','approve','cancel','query','reject')

    def get_client_commands(self):
        'Return available client commands.'
        return [name[9:] for name in dir(self.__class__) if name[:9]=='assemble_']

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

    def __asseble_command__(self, cols, params, one_only=0):
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
        for value in params[1]:
            data.append((col1, col2, value))
            if one_only: break
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
            ,('login', 'clID', params[1][0])
            ,('login', 'pw', params[1][1])
            ]
        if len(params[1])>2: cols.append(('login', 'newPW', params[1][2]))
        cols.extend([
             ('login', 'options')
            ,('options', 'version', params[2][0])
            ,('options', 'lang', params[2][2])
            ,('login', 'svcs')
            ,('svcs', 'objURI', params[2][1])
            ,('command', 'clTRID', params[0])
        ])
        self.__assemble_cmd__(cols)

    def assemble_logout(self, *params):
        "Assemble EPP command logount. *params: (('clTRID',),)"
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'logout'),
            ('command', 'clTRID', params[0][0])
        ))

    #-------------------------------------------
    # Dotazovací (query)
    #-------------------------------------------
    def assemble_check_contact(self, *params):
        "params must have ('clTRID',('name',['name','name',]))"
        self.__asseble_command__(('check','contact','id'), params)
        
    def assemble_check_domain(self, *params):
        "params must have ('clTRID',('name',['name','name',]))"
        self.__asseble_command__(('check','domain','name'), params)
        
    def assemble_check_nsset(self, *params):
        "params must have ('clTRID',('name',['name','name',]))"
        self.__asseble_command__(('check','nsset','id'), params)

    def assemble_info_contact(self, *params):
        "params must have ('clTRID',('name',))"
        self.__asseble_command__(('info','contact','id'), params, ONLY_ONE_VALUE)

    def assemble_info_domain(self, *params):
        "params must have ('clTRID',('name',))"
        self.__asseble_command__(('info','domain','name'), params, ONLY_ONE_VALUE)

    def assemble_info_nsset(self, *params):
        "params must have ('clTRID',('name',))"
        self.__asseble_command__(('info','nsset','id'), params, ONLY_ONE_VALUE)

    def assemble_poll(self, *params):
        """Počet zpráv ve frontě. Vrací první zprávu z fronty. ID zprávy a počet zpráv ve frontě.
        params must have ('clTRID',['req'],())
        """
        key = params[1][0]
        if key not in ('req','ack'): key = 'req' # automatické přiřazení defaultní hodnoty
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'poll', '', (('op',key),) ),
            ('command', 'clTRID', params[0])
        ))

    def __assemble_transfer__(self, names, params):
        "params must have ('clTRID',('name','op','heslo'))"
        if params[1][1] not in Message.transfer_op:
            params[1][1] = Message.transfer_op[0] # default value
        ns = '%s%s-%s'%(eppdoc.nic_cz_xml_epp_path,names[0],eppdoc.nic_cz_version)
        attr = (('xmlns:%s'%names[0],ns),
                ('xsi:schemaLocation','%s %s%s.xsd'%(ns,names[0],eppdoc.nic_cz_version)))
        self.__assemble_cmd__((
            ('epp', 'command'),
            ('command', 'transfer', '', (('op',params[1][1]),)),
            ('transfer', '%s:transfer'%names[0], '', attr),
            ('%s:transfer'%names[0], '%s:%s'%names, params[1][0]),
            ('%s:transfer'%names[0], '%s:authInfo'%names[0]),
            ('%s:authInfo'%names[0], '%s:pw'%names[0], params[1][2]),
            ('command', 'clTRID', params[0])
        ))

    def assemble_transfer_domain(self, *params):
        "params must have ('clTRID',('name','op','heslo'))"
        self.__assemble_transfer__(('domain','name'),params)

    def assemble_transfer_nsset(self, *params):
        "params must have ('clTRID',('name','op','heslo'))"
        self.__assemble_transfer__(('nsset','id'),params)

    #-------------------------------------------
    # Výkonné
    #-------------------------------------------
##    def assemble_create(self, *params):
##        self.load_EPP_template('create')
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

def test():
    import pprint
    epp = Message()
    epp.assemble_transfer_domain('llcc002#06-06-16at13:21:30', ['neco.cz', 'cosi', 'heslo'], ())
    errors, xmlepp = epp.get_results()
    print errors, xmlepp

    epp.assemble_transfer_nsset('llcc002#06-06-16at13:21:30', ['neco.cz', 'cosi', 'heslo'], ())
    errors, xmlepp = epp.get_results()
    print errors, xmlepp
    
if __name__ == '__main__':
    # Test na jednotlivé příkazy
##    test_command('login moje-jmeno moje-heslo', 'TEST login')
##    test_command('info', 'TEST info')
    test()
