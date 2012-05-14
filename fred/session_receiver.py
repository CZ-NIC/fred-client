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
import operator
import eppdoc
from eppdoc_assemble import DISCLOSES
from session_base import *
from session_command import ManagerCommand, COLOR
from translate import encoding
"""
This class ManagerReceiver cover all previous ancestors
base, transfer and command into one session manager object.
This part provides about the server answers and parse them
for output process.

There is function  api_command() and class FredError
what are used in client API.
"""
SEPARATOR = '-'*60
ANSW_RESULT, ANSW_CODE, ANSW_MSG = range(3)

class ManagerReceiver(ManagerCommand):
    """EPP client support.
    This class manage creations of the EPP documents.
    """
    def __init__(self, cwd=None):
        self._cwd = cwd
        ManagerCommand.__init__(self, cwd=self._cwd)

    #==================================================
    #
    # function for save values from the server answer
    # process_answer() -> answer_response() -> answer_response_result()
    #                  -> answer_greeting()
    #
    #==================================================
    def __append_note_from_dct__(self,dict_data,cols):
        """Append columns values from dict to note stack.
        cols = ('column-name','column-name','column-name attr-name attr-name','node')
        TODO: prijde zrusit
        """
        dct = self._dct_answer['data']
        for column_name in cols:
            lcol = column_name.split(' ') # node_name, atributess
            if len(lcol)>1:
                value = eppdoc.get_dct_value(dict_data, lcol[0])
                node_name = lcol[0]
                for a in lcol[1:]:
                    val = eppdoc.get_dct_attr(dict_data, lcol[0], a)
                    if val: append_dct(dct,'%s.%s'%(node_name,a),val) # attributes
            else:
                value = eppdoc.get_dct_value(dict_data, column_name)
                if value: append_dct(dct,column_name,value)

    def __code_isnot_1000__(self, data, label):
        """Append standard message if answer code is not 1000.
        Returns FALSE - code is 1000; TRUE - code is NOT 1000;
        <extValue>
            <value>
                <poll op='ack'/>
            </value>
            <reason>Required parameter msgID is missing</reason>
        </extValue>
        """
        if data[ANSW_CODE] == 1000: return 0
        extValue = data[ANSW_RESULT].get('extValue',[])
        if type(extValue) not in (list,tuple): extValue = (extValue,)
        extra_message = []
        tags = self._session[OUTPUT_TYPE] in ('html','php') and ('&lt;','&gt;','&lt;/','/&gt;') or ('<','>','</','/>')
        for item in extValue:
            value = item.get('value',{})
            for key in value.keys():
                if self._session[VERBOSE] > 1:
                    attributes=[]
                    for attr in item['value'][key].get('attr',[]):
                        attributes.append("%s='%s'"%attr)
                    attribs = len(attributes) and ' %s'%' '.join(attributes) or ''
                    elvalue = value[key].get('data',u'')
                    if type(elvalue) in (list, tuple):
                        elvalue = ' '.join(elvalue)
                    if elvalue:
                        stoptag = tags[1]
                        endtag = u'%s%s%s'%(tags[2],key,tags[1])
                    else:
                        stoptag = tags[3]
                        endtag = ''
                    extra_message.append('%s: %s%s%s%s%s%s'%(_T('Element that caused a server error condition'),get_ltext(tags[0]),get_ltext(key),get_ltext(attribs),stoptag,get_ltext(elvalue),get_ltext(endtag)))
                if item.has_key('reason'): extra_message.append('%s: %s'%(_T('Reason'), get_ltext(item['reason'].get('data',''))))
        if len(extra_message):
            self._dct_answer['errors'].extend(extra_message)
        return 1 # code is NOT 1000
        
    def answer_response(self):
        "Part of process answer - parse response node."
        # Here we are fooking for particular function to parse answer.
        # If it doesn't exist we display whole answer by default method
        display_src = 1 # Dislapy whole answer?  1 - yes, 0 - no
        response = self._dict_answer.get('response',None)
        if response:
            result = response.get('result',None)
            if result:
                try:
                    code = int(eppdoc.get_dct_attr(result,(),'code'))
                except ValueError, msg:
                    self._dct_answer['code'].append('%s: %s'%(_T('Invalid response code'),msg))
                    code = 0

##                if code == 2502:
##                    # Message: Session limit exceeded; server closing connection
##                    self.send_logout() # and close connection
                    
                reason = eppdoc.get_dct_value(result,'msg')
                self._dct_answer['code'] = code
                self._dct_answer['reason'] = reason
                self._dct_answer['command'] = self._command_sent
                fnc_name = 'answer_response_%s'%self._command_sent.replace(':','_')
                # 'command:',self._command_sent,'fnc_name:',fnc_name #TEST
                # Name of command is very important. It is key for choose function dispatching answer:
                # delete_(contact|nsset|domain) fnc_name: answer_response_contact_delete
                # sendauthinfo_(contact|nsset|domain) fnc_name: answer_response_fred_sendauthinfo
                #print 'HANDLE:', fnc_name # TEST display HANDLE +++
                #print 'COMMAND:', self._command_sent # +++
                if hasattr(self,fnc_name):
                    getattr(self,fnc_name)((result, code, reason))
                    display_src = 0 # Answer has been catch, we haven't display it again.
                else:
                    self.__code_isnot_1000__((result, code, reason), self._command_sent) # 'info:contact'
            else:
                self._dct_answer['errors'].append(_T('Missing result in the response message.'))
        else:
            self._dct_answer['errors'].append(_T('Unknown server response'))

    def process_answer(self, epp_server_answer):
        'Main function. Process incomming EPP messages. This funcion is called by listen socket.'
        # Main function for parsing the answer. Parse XML, make validation and continue
        # to function answer_response().
        debug_time = [('START',time.time())] # PROFILER
        self.reset_src()
        if epp_server_answer:
            self._raw_answer = epp_server_answer
            # create XML DOM tree:
            self._epp_response.reset()
            self._epp_response.parse_xml(epp_server_answer)
            
            
            debug_time.append(('Parse XML',time.time())) # PROFILER

            if self._epp_response.is_error():
                # Errors occurs during parsing
                self.append_error(self._epp_response.get_errors())
                
            if not self._epp_response.is_error():
                # When is comming some answer and it is valid and parsed succefully:
                self._dict_answer = self._epp_response.create_data()
                debug_time.append(('Create data',time.time())) # PROFILER
                if self._dict_answer.get('greeting',None):
                    self._dct_answer['command'] = self._command_sent
                    self.answer_greeting()
                elif self._dict_answer.get('response',None):
                    self.answer_response()
                    debug_time.append(('Manage response',time.time())) # PROFILER
                else:
                    self.append_note(_T('Unknown response type'),('RED','BOLD'))
                    self.__put_raw_into_note__(self._dict_answer)
        return debug_time

    #==================================================
    #
    # Process incomming messages
    # function names are in format [prefix]_[command_name]
    # answer_response_[command]
    #==================================================
    def answer_greeting(self):
        "Part of process answer - parse greeting node."
        dct = self._dct_answer['data']
        greeting = self._dict_answer['greeting']
        for key in ('svID','svDate'):
            dct[key] = eppdoc.get_dct_value(greeting, key)
        svcMenu = greeting.get('svcMenu',{})
        for key in ('lang','version','objURI'):
            dct[key] = eppdoc.get_dct_value(svcMenu, key)
        self.defs[LANGS] = dct['lang'] = dct['lang'].split('\n')
        if type(self.defs[LANGS]) in (str,unicode):
            self.defs[LANGS] = (self.defs[LANGS],)
        # list of protocol versions:
        if dct.has_key('version') and type(dct['version']) in (unicode, str):
            dct['version'] = dct['version'].split('\n')
        # check objURI and extURI
        msg_invalid_schema_version = []
        dct['objURI'] = dct.get('objURI','').split('\n')
        if dct['objURI']:
            self.check_schemas('objURI', self.defs[objURI], dct['objURI'])
        dct['extURI'] = eppdoc.get_dct_values(svcMenu, ('svcExtension','extURI'))
        if self.defs[extURI]:
            self.check_schemas('extURI', self.defs[extURI], dct['extURI'])
        #
        adjust_dct_keys(dct,('lang','objURI','extURI'))
        # data collection policy, access
        dcp = greeting.get('dcp',{})
        dcp_access = dcp.get('access',{}).keys() # all, none, null, personal, personalAndOther, other
        if 'all' in dcp_access:
            access = 1
            msg = _T('All data are disclosed.')
        else:
            access = 0
            msg = _T('All data are hidden.')
        # Server Disclose Policy
        self._epp_cmd.server_disclose_policy = access
        dct['dcp'] = msg

    def answer_response_login(self, data):
        "data=(response,result,code,msg)"
        host = self._session[HOST]
        if data[ANSW_CODE] == 1000:
            self._session[ONLINE] = 1 # login indicator
            self._session[CMD_ID] = 1 # reset - first command was login
            self.append_note(_T('Connected!'))
        else:
            self.append_error(_T('Login failed.'))
            self.__code_isnot_1000__(data, 'login')
        # Don't display messages 'Connecting to HOST, port NNN ...' and 'Connected!'
        self.remove_notes_from_no_text_ouptut()

    #-------------------------------------
    # *** info ***
    #-------------------------------------
    def answer_response_contact_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:contact'): return
        dct = self._dct_answer['data']
        try:
            resData = self._dict_answer['response']['resData']
            contact_infData = resData['contact:infData']
            contact_postalInfo = contact_infData['contact:postalInfo']
        except KeyError, msg:
            self.append_error('answer_response_contact_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(contact_infData,
                ('contact:id','contact:roid','contact:status s','contact:status',
                'contact:voice','contact:fax','contact:email',
                'contact:crID', 'contact:clID', 'contact:upID', 
                'contact:crDate', 'contact:trDate', 'contact:upDate'))
            self.__append_note_from_dct__(contact_postalInfo,('contact:name','contact:org'))
            contact_addr = contact_postalInfo.get('contact:addr',None)
            if contact_addr:
                self.__append_note_from_dct__(contact_addr,('contact:sp','contact:cc',
                    'contact:city','contact:street','contact:pc',))
            disclosed = list(DISCLOSES) + ['addr']
            not_disclosed = []
            condis = contact_infData.get('contact:disclose',None)
            if condis:
                for k,v in condis.items():
                    # decamell: replace notifyEmail -> notify_email
                    if v == {}: not_disclosed.append(decamell(k[8:]))
            for name in not_disclosed:
                if name in disclosed:
                    disclosed.pop(disclosed.index(name))
            dct['contact:disclose'] = disclosed
            dct['contact:hide'] = not_disclosed
            dct['contact:authInfo'] = eppdoc.get_dct_value(contact_infData, 'contact:authInfo')
            dct['contact:ident.type'] = eppdoc.get_dct_attr(contact_infData, 'contact:ident', 'type')
            dct['contact:ident'] = eppdoc.get_dct_value(contact_infData, 'contact:ident')
            dct['contact:notifyEmail'] = eppdoc.get_dct_value(contact_infData, 'contact:notifyEmail')
            dct['contact:vat'] = eppdoc.get_dct_value(contact_infData, 'contact:vat')

    def answer_response_domain_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:domain'): return
        try:
            resData = self._dict_answer['response']['resData']
            domain_infData = resData['domain:infData']
        except KeyError, msg:
            self.append_error('answer_response_domain_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(domain_infData,
                ('domain:name','domain:roid','domain:status s','domain:status',
                 'domain:registrant','domain:admin','domain:tempcontact',
                 'domain:contact','domain:contact type','domain:nsset','domain:keyset',
                 'domain:crID','domain:clID','domain:upID',
                 'domain:crDate','domain:trDate','domain:upDate','domain:exDate','domain:authInfo'))
            valExDate = eppdoc.get_dct_value(self._dict_answer['response'], ('extension','enumval:infData','enumval:valExDate'))
            if valExDate:
                self._dct_answer['data']['domain:valExDate'] = valExDate
            # publish in ENUM dictionary
            publish = eppdoc.get_dct_value(self._dict_answer['response'], ('extension','enumval:infData','enumval:publish'))
            if publish:
                self._dct_answer['data']['domain:publish'] = {
                    'true': _T('yes'), 
                    'false': _T('no')}.get(publish, publish)
            
    def answer_response_anyset_info(self, prefix, data):
        "prefix=namespace data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:%s'%prefix): return
        try:
            resData = self._dict_answer['response']['resData']
            nsset_infData = resData['%s:infData'%prefix]
        except KeyError, msg:
            self.append_error('answer_response_%s_info KeyError: %s'%(prefix, msg))
        else:
            self.__append_note_from_dct__(nsset_infData, map(lambda n: '%s:%s'%(prefix, n),
                ('id','roid',
                'clID','crID','trID','upID',
                'crDate','trDate','upDate','authInfo','tech',
                'status s','status','reportlevel')))
            if nsset_infData.has_key('%s:ns'%prefix):
                nsset_ns = nsset_infData['%s:ns'%prefix]
                dns = []
                if not type(nsset_ns) == list: nsset_ns = (nsset_ns,)
                for row in nsset_ns:
                    name = eppdoc.get_dct_value(row, '%s:name'%prefix)
                    addr = eppdoc.get_dct_value(row, '%s:addr'%prefix).split('\n')
                    dns.append([name,addr])
                self._dct_answer['data']['%s:ns'%prefix] = dns
            if nsset_infData.has_key('%s:ds'%prefix):
                nsset_ns = nsset_infData['%s:ds'%prefix]
                dns = []
                if not type(nsset_ns) == list: nsset_ns = (nsset_ns,)
                for row in nsset_ns:
                    items = []
                    for key in ['keyTag', 'alg', 'digestType', 'digest', 'maxSigLife']:
                        value = eppdoc.get_dct_value(row, '%s:%s'%(prefix, key))
                        if value:
                            items.append(value)
                    if items:
                        dns.append(items)
                self._dct_answer['data']['%s:ds'%prefix] = dns

            if nsset_infData.has_key('%s:dnskey'%prefix):
                nsset_ns = nsset_infData['%s:dnskey'%prefix]
                dns = []
                if not type(nsset_ns) == list: nsset_ns = (nsset_ns,)
                for row in nsset_ns:
                    items = []
                    for key in ['flags', 'protocol', 'alg', 'pubKey']:
                        value = eppdoc.get_dct_value(row, '%s:%s'%(prefix, key))
                        if value:
                            items.append(value)
                    if items:
                        dns.append(items)
                self._dct_answer['data']['%s:dnskey'%prefix] = dns



    def answer_response_nsset_info(self, data):
        self.answer_response_anyset_info('nsset', data)

    def answer_response_keyset_info(self, data):
        self.answer_response_anyset_info('keyset', data)

    #-------------------------------------
    # *** check ***
    #-------------------------------------
    def __check_available__(self, dct_answer, dict_data, names, attr_name):
        """Assign available names for check_...() functions.
        names=('domain','name')
        """
        column_name = '%s:%s'%names
        value = eppdoc.get_dct_value(dict_data, column_name)
        code = eppdoc.get_dct_attr(dict_data, column_name, attr_name)
        reason_key = '%s:reason'%value
        dct_answer['data'][value] = code in ('1','true') and 1 or 0
        dct_answer['data'][reason_key] = eppdoc.get_dct_value(dict_data, '%s:reason'%names[0])
        if dct_answer['data'][value] == 1 and dct_answer['data'][reason_key] == '':
            dct_answer['data'][reason_key] = _T('Not in registry: Object is available.')

    def __answer_response_check__(self, data, names):
        """Process all check_[command]() functions. 
        data=(response,result,code,msg)
        names=('check-type','column-name')
        """
        if self.__code_isnot_1000__(data, '%s:check'%names[0]): return
        try:
            resData = self._dict_answer['response']['resData']
            chunk_chkData = resData['%s:chkData'%names[0]]
            chunk_cd = chunk_chkData['%s:cd'%names[0]]
        except KeyError, msg:
            errmsg = 'answer_response_%s_check KeyError: %s'%(names[0],msg)
            self.append_error(errmsg)
            self._dct_answer['errors'].append(errmsg)
        else:
            if operator.isSequenceType(chunk_cd):
                for item in chunk_cd:
                    self.__check_available__(self._dct_answer, item, names, 'avail')
            else:
                self.__check_available__(self._dct_answer, chunk_cd, names, 'avail')
            # append status according to code
            # FUTURE: This message will be generated on the server.
            status = (_T('Not available'), _T('Available'))
            d = self._dct_answer['data']
            for k,v in d.items():
                if type(v) == int:
                    key = '%s:reason'%k
                    d[key] = '%s. %s'%(status[v],get_ltext(d[key]))


    def answer_response_contact_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('contact','id'))

    def answer_response_domain_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('domain','name'))

    def answer_response_nsset_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('nsset','id'))

    def answer_response_keyset_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('keyset','id'))


    def get_nodes_with_xmlns(self, dmsg):
        "Returns the list of nodes with their xmlns"
        retval = []
        if dmsg is None:
            return retval
        for key, data in dmsg.items():
            xmlns = ''
            for attr_key, att_value in data.get('attr', []):
                # split prefix and local name
                attr_pref, attr_name = eppdoc.split_qattr_key(attr_key)
                key_pref, key_name = eppdoc.split_prexis_name(key)
                # if attribute is xmlns and prefix is equal with node prefix
                if attr_pref == 'xmlns' and attr_name == key_pref:
                    # then join ns definition to node name
                    xmlns = " xmlns=%s" % att_value
                    break
            retval.append("%s%s" % (eppdoc.remove_ns(key), xmlns))
        return retval


    def answer_response_poll(self, data):
        "data=(response,result,code,msg)"
        label='poll'
        if self.__code_isnot_1000__(data, label) and data[ANSW_CODE] != 1301: return
        msgQ = None
        response = self._dict_answer.get('response',None)
        if response: msgQ = response.get('msgQ',None)
        if msgQ:
            self.__append_note_from_dct__(response,('msgQ count id',))
            self.__append_note_from_dct__(msgQ,('qDate','msg'))
            if not self._dct_answer['data'].has_key('msg'):
                # if message is not simple text but XML document:
                dmsg = msgQ.get('msg')
                self._dct_answer['data']['msg.nodes'] = self.get_nodes_with_xmlns(dmsg)
                if dmsg is not None and len(dmsg) == 1:
                    # remove topmost element if it is only one
                    key, dmsg = dmsg.popitem()
                self._dct_answer['data']['msg'] = '\n'+eppdoc.prepare_display(dmsg, self._session[COLORS])
        # convert str to int:
        for key in ('id','count'):
            sval = self.get_value_from_dict(('data','msgQ.%s'%key))
            if sval:
                try:
                    self._dct_answer['data']['msgQ.%s'%key] = int(sval)
                except ValueError, msg:
                    self._dct_answer.append(msg)
                    
        if data[ANSW_CODE] == 1301 and self._session[POLL_AUTOACK]:
            # automaticly answer 'poll ack' and remove message from server
            msg_id = self.get_value_from_dict(('data','msgQ.id'))
            if msg_id: # if only ID exists
                dct = self._dct_answer # keep message from "req"
                self.api_command('poll',{'op':'ack','msg_id':str(msg_id)})
                # Copy previous "req" answer to new from "ack" command.
                dct['code'] = self._dct_answer['code']
                dct['reason'] = 'req: %s\n%sack: %s'%(dct['reason'],' '*(self._ljust+1), self._dct_answer['reason'])
                data = dct['data']
                data['msgQ.count'] = self.get_value_from_dict(('data','msgQ.count'), self._dct_answer)
                if data['msgQ.count'] is None:
                    data['msgQ.count'] = 0
                if self.get_value_from_dict(('data','msg'),self._dct_answer):
                    data['msg'] = '\n'.join((data['msg'], self._dct_answer['data']['msg']))
                if len(self._dct_answer['errors']): dct['errors'].extend(self._dct_answer['errors'])
                self._dct_answer = dct


    def __response_create__(self, data, columns, keys):
        """data=(response,result,code,msg) 
        columns=('domain','renew','renData')
        keys=('name','exDate')"""
        if self.__code_isnot_1000__(data, '%s:%s'%columns[:2]): return
        objData = self.get_value_from_dict(('response','resData','%s:%s'%(columns[0],columns[2])),self._dict_answer)
        if objData:
            for key in keys:
                scope = '%s:%s'%(columns[0],key)
                self._dct_answer['data'][scope] = eppdoc.get_dct_value(objData, scope)

    def answer_response_contact_create(self, data):
        self.__response_create__(data, ('contact','create','creData'), ('id','crDate'))

    def answer_response_domain_create(self, data):
        self.__response_create__(data, ('domain','create','creData'), ('name','crDate','exDate'))

    def answer_response_nsset_create(self, data):
        self.__response_create__(data, ('nsset','create','creData'), ('id','crDate'))

    def answer_response_keyset_create(self, data):
        self.__response_create__(data, ('keyset','create','creData'), ('id','crDate'))
        
    def answer_response_domain_renew(self, data):
        self.__response_create__(data, ('domain','renew','renData'), ('name','exDate'))


    def __answer_response_list__(self, data, columns):
        'Dispatch list answers.'
        if self.__code_isnot_1000__(data, '%s:list'%columns[0]): return
        try:
            resData = self._dict_answer['response']['resData']
            listData = resData['%s:listData'%columns[0]] # contact:listData
        except KeyError, msg:
            self.append_error('answer_response_list:%s KeyError: %s'%(columns[0],msg))
        else:
            self._dct_answer['data']['list'] = eppdoc.get_dct_values(listData, '%s:%s'%columns)
            self._dct_answer['data']['count'] = len(self._dct_answer['data']['list'])
        
    def answer_response_contact_list(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_list__(data, ('contact','id'))
    def answer_response_nsset_list(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_list__(data, ('nsset','id'))
    def answer_response_keyset_list(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_list__(data, ('keyset','id'))
    def answer_response_domain_list(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_list__(data, ('domain','name'))
        
    def answer_response_credit_info(self, data):
        self.answer_response_fred_creditinfo(data)

    def answer_response_fred_creditinfo(self, data):
        'Prepare creditinfo for display'
        if self.__code_isnot_1000__(data, 'fred:creditinfo'): return
        try:
            resData = self._dict_answer['response'].get('resData',{})
            res_credit_info = resData.get('fred:resCreditInfo',{})
        except KeyError, msg:
            self.append_error('answer_response_fred_creditinfo KeyError: %s'%msg)
        else:
            # if answer returns only one zone, we need simualte list of zones.
            zones = res_credit_info.get('fred:zoneCredit',[])
            if type(zones) is dict: zones = [zones]
            for zone in zones:
                # {'fred:zone': {'data': u'0.2.4.e164.arpa'},  'fred:credit': {'data': u'201.50'} }, 
                key    = eppdoc.get_dct_value(zone, 'fred:zone')
                value = eppdoc.get_dct_value(zone, 'fred:credit')
                self._dct_answer['data'][key] = value


    def __loop_getresults__(self, command_type):
        'Make getresults loop until any data comming'
        # send get_result command
        # parse and print answer
        # stop if no data

        self._loop_status = LOOP_FIRST_STEP
        
        self.print_answer()
        self.display() # display errors or notes
        
        while 1:
            self._loop_status = LOOP_INSIDE # inside loop
            try:
                self.api_command('get_results')
            except FredError, fe:
                self.append_error('\n'.join(fe.args))
                self.display() # display errors or notes
                break
            run_loop = self._dct_answer.get('data', {'count':0}).get('count', 0)
            if run_loop < 1:
                self._loop_status = LOOP_LAST_STEP
            self.print_answer()
            
            self.display() # display errors or notes
            if run_loop < 1:
                break
            
        self._loop_status = LOOP_NONE
        self.reset_round()
        self.reset_src() # this is in process_answer() but it must be here for case NOT is_online()
        

    def __fred_listobjects__(self, data, command_type, notify):
        'Shared for all responses of the listObject'
        # command_type = fred:listdomains
        if self.__code_isnot_1000__(data, command_type): return
        
        try:
            resData = self._dict_answer['response'].get('resData',{})
        except KeyError, msg:
            self.append_error('__fred_listdomains__ KeyError: %s'%msg)
        else:
            fred_info_response = resData.get('fred:infoResponse',{})
            fred_count = fred_info_response.get('fred:count',None)
            if type(fred_count) is dict and fred_count.has_key('data'):
                self._dct_answer['data']['count'] = fred_count['data']
                try:
                    count = int(fred_count['data'])
                except ValueError, msg:
                    self.append_error('__fred_listobjects__ ValueError: %s'%msg)
                    count = 0
                if count == 0:
                    notify = _T('The list is empty.')
                self._dct_answer['data']['notify'] = notify
                
        if self._epp_cmd.getresults_loop:
            # special mode for list_(contact|nsset|domain)s commands
            self.__loop_getresults__(command_type)


    def answer_response_fred_listcontacts(self, data):
        'Handler for fred:listcontacts command'
        self.__fred_listobjects__(data, 'fred:listcontacts', _T("""
The list of the contacts is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_listnssets(self, data):
        'Handler for fred:listnssets command'
        self.__fred_listobjects__(data, 'fred:listnssets', _T("""
The list of the nssets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_listkeysets(self, data):
        'Handler for fred:listkeysets command'
        self.__fred_listobjects__(data, 'fred:listkeysets', _T("""
The list of the keysets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))
    
    def answer_response_fred_listdomains(self, data):
        'Handler for fred:listdomains command'
        self.__fred_listobjects__(data, 'fred:listdomains', _T("""
The list of the domains is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_getresults(self, data):
        'Shared for all responses of the listObject'
        if self.__code_isnot_1000__(data, 'fred:getresults'): return
        try:
            resData = self._dict_answer['response'].get('resData',{})
        except KeyError, msg:
            self.append_error('__fred_getresults__ KeyError: %s'%msg)
        else:
            fred_results_list = resData.get('fred:resultsList',{})
            fred_item = fred_results_list.get('fred:item',None)
            if fred_item is None:
                pass
            else:
                if type(fred_item) not in (list, tuple):
                    fred_item = (fred_item, )
                report = []
                if fred_item:
                    report = [fred_item[n]['data'] for n in range(len(fred_item))]
                self._dct_answer['data']['list'] = report
                if not self._epp_cmd.getresults_loop:
                    self._dct_answer['data']['count'] = len(report)


    def answer_response_fred_domainsbycontact(self, data):
        'Handler for fred:domainsbycontact command'
        self.__fred_listobjects__(data, 'fred:domainsbycontact', _T("""The list of the domains is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_domainsbynsset(self, data):
        'Handler for fred:domainsbynsset command'
        self.__fred_listobjects__(data, 'fred:domainsbynsset', _T("""The list of the nssets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))
    
    def answer_response_fred_domainsbykeyset(self, data):
        'Handler for fred:domainsbykeyset command'
        self.__fred_listobjects__(data, 'fred:domainsbykeyset', _T("""The list of the domains is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_nssetsbycontact(self, data):
        'Handler for fred:nssetsbycontact command'
        self.__fred_listobjects__(data, 'fred:nssetsbycontact', _T("""The list of the nssets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_keysetsbycontact(self, data):
        'Handler for fred:keysetsbycontact command'
        self.__fred_listobjects__(data, 'fred:keysetsbycontact', _T("""The list of the keysets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_nssetsbyns(self, data):
        'Handler for fred:nssetsbyns command'
        self.__fred_listobjects__(data, 'fred:nssetsbyns', _T("""The list of the nssets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))

    def answer_response_fred_keysetsbyns(self, data):
        'Handler for fred:keysetsbyns command'
        self.__fred_listobjects__(data, 'fred:keysetsbyns', _T("""The list of the keysets is ready on the server buffer 
and pointer is set at the beginning of the list.
Call get_results command for gain data."""))
        
    #-------------------------------------------------
    #
    # Main API function
    #
    #-------------------------------------------------
    def api_command(self, command_name, params=None):
        """Process command from API. Main API function.
        Create EPP command - send to server - receive answer - parse answer to dict - returns dict.
        """
        self.reset_round()
        self.reset_src() # this is in process_answer() but it must be here for case NOT is_online()
        dct_params = adjust_dict(params)                                      # turn params into expecterd format
        self.create_command_with_params(command_name, dct_params)             # create EPP command
        self._raw_cmd = self._epp_cmd.get_xml()                               # get EPP in XML (string)
        if len(self._errors): raise FredError(self.fetch_errors())
        if self.is_online(command_name):                                      # go only if session is online.
            # check doc for EPP validation
            errors = self.is_epp_valid(self._raw_cmd, _T('Command data XML document failed to validate.'))
            if len(errors): raise FredError(errors)
            if self.is_connected(): # if we are connect, lets communicate with the server
                self.send(self._raw_cmd)                                      # send to server
                if len(self._errors): raise FredError(self.fetch_errors())
                xml_answer = self.receive()                                   # receive answer
                error_validate_answer = self.is_epp_valid(xml_answer, _T('Server answer XML document failed to validate.')) # validate answer
                if self.run_as_unittest and not self._session[VALIDATE]:
                    # TEST: validate the server's answer in unittest:
                    self._session[VALIDATE] = 1
                    error_validate_answer = self.is_epp_valid(xml_answer, _T('Server answer XML document failed to validate.'))
                    self._session[VALIDATE] = 0
                self.process_answer(xml_answer)                               # process answer
                if len(error_validate_answer):
                    self._errors.append(error_validate_answer)                # join validate error AFTER process
                if command_name == 'logout': self.close()
                if len(self._errors): raise FredError(self.fetch_errors())
            else:
                errors = _T('You are not logged. First type login.')
                raise FredError(errors)
        else:
            self._dct_answer['errors'].append(_T('You are not logged. You must call login() before working on the server.'))
        if len(self._errors): raise FredError(self.fetch_errors())
        return self._dct_answer

    #-------------------------------------------------


class FredError(StandardError):
    'Fred EPP errors.'
    def __init__(self, message):
        StandardError.__init__(self, message)
        # Encode unicode message into the local encoding. session_base.get_unicode()
        self.args = (get_ltext(message),)


def append_dct(dct, key, value):
    'Appends value at the dict key.'
    
    # split value into lines if contains enter(s)
    if '\n' in value:
        value = value.split('\n')
    
    if dct.has_key(key):
        if type(dct[key]) is not list:
            dct[key] = [dct[key]] # keep all data in lists
        getattr(dct[key], type(value) in (list, tuple) and 'extend' or 'append')(value)
    else:
        dct[key] = value

    
def adjust_dict(dct_data):
    'Remove None and put items into list.'
    dct={}
    if type(dct_data) == dict:
        for k in dct_data:
            if dct_data[k] is None: continue
            if type(dct_data[k]) == str: dct_data[k] = unicode(dct_data[k], encoding)
            if type(dct_data[k]) == unicode:
                dct[k] = [dct_data[k]]
            elif type(dct_data[k]) == dict:
                d = adjust_dict(dct_data[k])
                if len(d): dct[k] = [d]
            else:
                dct[k] = []
                for item in dct_data[k]:
                    if type(item) == dict:
                        d = adjust_dict(item)
                        if len(d): dct[k].append(d)
                    else:
                        if item != None:
                            if type(item) == str: item = unicode(item, encoding)
                            dct[k].append(item)
    return dct

def adjust_dct_keys(dct, names):
    'Keys must exists and values must be list or tuple.'
    for name in names:
        if dct.has_key(name):
            if type(dct[name]) not in (list,tuple):
                dct[name] = (dct[name],)
        else:
            dct[name] = ()

def test(name_and_xml):
    m = ManagerReceiver()
    #m._session[VERBOSE] = 2
    m._command_sent = name_and_xml[0]
    m.process_answer(name_and_xml[1])
    #m._session[14] = 'php' # OUTPUT_TYPE
    m.display()
    m.print_answer()
    print "API OUTPUT:", m._dct_answer
#    m.__put_raw_into_note__(m._dict_answer)
#    m.display()

if __name__ == '__main__':
    try:
        import test_incomming_messages
    except ImportError:
        print "Testing modul 'test_incomming_messages.py' is not included."
    else:
        # TEST selected document:
        # Data item has format: ('command:name',"""<?xml ...XML document... >""")
        # For example: ('nsset:info',"""<?xml ...<epp ...><response> ... </epp>""")
        test(test_incomming_messages.data[22])
        #map(test, test_incomming_messages.data)
        #test(test_incomming_messages.data[9]) # test na contact:info status
