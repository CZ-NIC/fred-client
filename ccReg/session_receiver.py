# -*- coding: utf8 -*-
#!/usr/bin/env python
import operator
import eppdoc
from session_base import *
from session_command import ManagerCommand
from translate import _T

SEPARATOR = '-'*60
ANSW_RESULT, ANSW_CODE, ANSW_MSG = range(3)

class ManagerReceiver(ManagerCommand):
    """EPP client support.
    This class manage creations of the EPP documents.
    """

    #==================================================
    #
    # funkce pro uložení hodnot z odpovědi od serveru
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
        """
        if data[ANSW_CODE] != 1000:
            # standardní výstup chybového hlášení
            # detailní rozepsání chyby:
            if data[ANSW_RESULT].has_key('extValue'):
                extValue = data[ANSW_RESULT]['extValue']
                if type(extValue) not in (list,tuple): extValue = (extValue,)
                for item in extValue:
                    msg = [] # for values of nodes
                    msg_attr = [] # for attributes of values
                    if item.has_key('value'):
                        # if exists any nodes
                        for key in item['value'].keys():
                            if item['value'][key].get('data',None):
                                # join node value
                                msg.append('%s:'%item['value'][key].get('data',item['value'][key]))
                            if item['value'][key].get('attr',None):
                                # join node attributes
                                for attr in item['value'][key]['attr']:
                                    msg_attr.append("%s='%s'"%attr)
                    if item.has_key('reason'):
                        msg.append(item['reason'].get('data',item['reason']))
                    if len(msg_attr): msg.append('(%s)'%', '.join(msg_attr))
                    self._dct_answer['errors'].append(' '.join(msg))
        return data[ANSW_CODE] != 1000

    def answer_response(self):
        "Part of process answer - parse response node."
        # Zde se hledá, jestli na odpověd existuje funkce, ketrá ji zpracuje.
        # Pokud, ne, tak se odpověd zobrací celá standardním způsobem.
        display_src = 1 # Má se odpověd zobrazit celá? 1-ano, 0-ne
        response = self._dict_answer.get('response',None)
        if response:
            result = response.get('result',None)
            if result:
                try:
                    code = int(eppdoc.get_dct_attr(result,(),'code'))
                except ValueError, msg:
                    self._dct_answer['code'].append('%s: %s'%(_T('Invalid response code'),msg))
                    code = 0
                reason = eppdoc.get_dct_value(result,'msg')
                self._dct_answer['code'] = code
                self._dct_answer['reason'] = reason
                self._dct_answer['command'] = self._command_sent
                fnc_name = 'answer_response_%s'%self._command_sent.replace(':','_')
                if hasattr(self,fnc_name):
                    getattr(self,fnc_name)((result, code, reason))
                    display_src = 0 # Odpověd byla odchycena, není potřeba ji zobrazovat celou.
                else:
                    self.__code_isnot_1000__((result, code, reason), self._command_sent) # 'info:contact'
            else:
                self._dct_answer['errors'].append(_T('Missing result in the response message.'))
        else:
            self._dct_answer['errors'].append(_T('Unknown server response'))

    def process_answer(self, epp_server_answer):
        'Main function. Process incomming EPP messages. This funcion is called by listen socket.'
        # Hlavní funkce pro zpracování odpovědi. Rozparsuje XML, provede validaci a pak pokračuje
        # funkcí answer_response().
        self.__reset_src__()
        if epp_server_answer:
            self._raw_answer = epp_server_answer
            # create XML DOM tree:
            self._epp_response.reset()
            self._epp_response.parse_xml(eppdoc.correct_unbound_prefix(epp_server_answer))
            if self._epp_response.is_error():
                # při parsování se vyskytly chyby
                self.append_error(self._epp_response.get_errors())
            else:
                # validace
                invalid_epp = self.is_epp_valid(self._epp_response.get_xml())
                if invalid_epp:
                    # když se odpověd serveru neplatná...
                    self.append_note(_T('Server answer is not valid!'),('RED','BOLD'))
                    self.append_note(invalid_epp)
                    self.append_note('%s ${BOLD}validate off${NORMAL}.'%_T('For disable validator type'))
            if not self._epp_response.is_error():
                # když přišla nějaká odpověd a podařilo se jí zparsovat:
                self._dict_answer = self._epp_response.create_data()
                if self._dict_answer.get('greeting',None):
                    self.answer_greeting()
                elif self._dict_answer.get('response',None):
                    self.answer_response()
                else:
                    self.append_note(_T('Unknown response type'),('RED','BOLD'))
                    self.__put_raw_into_note__(self._dict_answer)
        else:
            self.append_note(_T("No response. EPP Server doesn't answer."))

    #==================================================
    #
    # Zpracování jednotlivých příchozích zpráv
    # funkce jsou ve tvaru [prefix]_[jméno příkazu]
    # answer_response_[command]
    #==================================================
    def answer_greeting(self):
        "Part of process answer - parse greeting node."
        dct = self._dct_answer['data']
        greeting = self._dict_answer['greeting']
        if not self._dct_answer['reason']: self._dct_answer['reason'] = _T('Greeting message incomming')
        for key in ('svID','svDate'):
            dct[key] = eppdoc.get_dct_value(greeting, key)
        svcMenu = greeting.get('svcMenu',{})
        for key in ('lang','version','objURI'):
            dct[key] = eppdoc.get_dct_value(svcMenu, key)
        self.defs[LANGS] = dct['lang'] = dct['lang'].split('\n')
        if type(self.defs[LANGS]) in (str,unicode):
            self.defs[LANGS] = (self.defs[LANGS],)
        self.defs[objURI] = dct['objURI'] = dct.get('objURI','').split('\n')
        self.defs[extURI] = eppdoc.get_dct_values(svcMenu, ('svcExtension','extURI'))
        if self.defs[objURI]:
            dct['objURI'] = self.defs[objURI]
        if self.defs[extURI]:
            dct['extURI'] = self.defs[extURI]
        adjust_dct_keys(dct,('lang','objURI','extURI'))

    def answer_response_logout(self, data):
        "data=(response,result,code,msg)"
        self.close()

    def answer_response_login(self, data):
        "data=(response,result,code,msg)"
        if data[ANSW_CODE] == 1000:
            self._session[ONLINE] = 1 # indikátor zalogování
            self._session[CMD_ID] = 1 # reset - první command byl login
            self._dct_answer['data']['session'] = '*** %s ***'%_T('Start session!')
        else:
            self._dct_answer['data']['session'] = '--- %s ---'%_T('Login failed')
            self.__code_isnot_1000__(data, 'login')

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
            contact_disclose = contact_infData['contact:disclose']
        except KeyError, msg:
            self.append_error('answer_response_contact_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(contact_infData,
                ('contact:id','contact:roid','contact:status s','contact:disclose flag'))
            self.__append_note_from_dct__(contact_postalInfo,('contact:name','contact:org'))
            contact_addr = contact_postalInfo.get('contact:addr',None)
            if contact_addr:
                self.__append_note_from_dct__(contact_addr,('contact:street','contact:city','contact:cc'))
            self.__append_note_from_dct__(contact_infData,('contact:email','contact:crID','contact:crDate','contact:upID','contact:upDate'))
            contact_disclose = contact_infData.get('contact:disclose',None)
            if contact_disclose:
                self.__append_note_from_dct__(contact_disclose,('contact:name','contact:org','contact:addr','contact:voice','contact:fax','contact:email'))

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
                ('domain:name','domain:roid','domain:status s','domain:registrant'
                ,'domain:contact','domain:contact type','domain:nsset','domain:clID','domain:crID'
                ,'domain:crDate','domain:upDate','domain:exDate','domain:upID'))
            authInfo = domain_infData.get('domain:authInfo',None)
            if authInfo: self.__append_note_from_dct__(authInfo,('domain:pw',))
            m = re.match('\d{4}-\d{2}-\d{2}', self.get_value_from_dict(('data','domain:exDate')))
            if m: self._dct_answer['data']['domain:renew'] = m.group(0) # value for renew-domain

    def answer_response_nsset_info(self, data):
        "data=(response,result,code,msg)"
        if self.__code_isnot_1000__(data, 'info:nsset'): return
        try:
            resData = self._dict_answer['response']['resData']
            nsset_infData = resData['nsset:infData']
        except KeyError, msg:
            self.append_error('answer_response_nsset_info KeyError: %s'%msg)
        else:
            self.__append_note_from_dct__(nsset_infData,('nsset:id','nsset:roid','nsset:clID','nsset:crID'
                ,'nsset:crDate','nsset:upID','nsset:trDate','nsset:authInfo','nsset:tech',
                'nsset:status s'))
            if nsset_infData.has_key('nsset:ns'):
                nsset_ns = nsset_infData['nsset:ns']
##                print "!!! nsset_ns:",nsset_ns
                dns = []
                if not type(nsset_ns) == list: nsset_ns = (nsset_ns,)
                for ns in nsset_ns:
##                    print "DNS:",ns #!!!
                    name = eppdoc.get_dct_value(ns, 'nsset:name')
                    addr = eppdoc.get_dct_value(ns, 'nsset:addr').split('\n')
##                    print "name:",name #!!!
##                    print "addr:",addr #!!!
##                    if not self._dct_answer['data'].has_key('dns'):
##                    dns = self._dct_answer['data'].get('dns',[])
                    dns.append([name,addr])
##                    print "!!! self._dct_answer['data']:",self._dct_answer['data']
                self._dct_answer['data']['nsset:ns'] = dns
##                print "!!! self._dct_answer['data']:",self._dct_answer['data']
##                    self._dct_answer['data']
##                    append_dct(self._dct_answer['data'],'dns',[name,addr])
                    
##                if type(nsset_ns) == list:
##                    for item in nsset_ns:
##                        self.__append_note_from_dct__(item,('nsset:name','nsset:addr'))
##                else:
##                    self.__append_note_from_dct__(nsset_ns,('nsset:name','nsset:addr'))
##                    self._dct_answer['data']

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
        #reason = eppdoc.get_dct_value(dict_data, '%s:reason'%names[0]) # nepovinný
        if code in ('1','true'):
            dct_answer['data'][value] = 1
        else:
            dct_answer['data'][value] = 0

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

    def answer_response_contact_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('contact','id'))

    def answer_response_domain_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('domain','name'))

    def answer_response_nsset_check(self, data):
        "data=(response,result,code,msg)"
        self.__answer_response_check__(data, ('nsset','id'))

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
        if data[ANSW_CODE] == 1301 and self._session[POLL_AUTOACK]:
            # automaticly answer 'poll ack' and remove message from server
            msg_id = self.get_value_from_dict(('data','id'))
            if msg_id: # if only ID exists
                dct = self._dct_answer # keep message from "req"
                self.api_command('poll',{'op':'ack','msg_id':msg_id})
                # Copy previous "req" answer to new from "ack" command.
                dct['code'] = self._dct_answer['code']
                dct['reason'] = 'req: %s\n        ack: %s'%(dct['reason'],self._dct_answer['reason'])
                data = dct['data']
                data['count'] = self.get_value_from_dict(('data','count'),self._dct_answer)
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

    def answer_response_domain_renew(self, data):
        self.__response_create__(data, ('domain','renew','renData'), ('name','exDate'))


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
        dct_params = adjust_dict(params)                                      # turn params into expecterd format
        self.create_command_with_params(command_name, dct_params)             # create EPP command
        self._raw_cmd = self._epp_cmd.get_xml()                               # get EPP in XML (string)
        if len(self._errors): raise ccRegError(self.fetch_errors())
        if self.is_online(command_name):                                      # go only if session is online.
            errors = self.is_epp_valid(self._raw_cmd)                         # check doc for EPP validation
            if len(errors): raise ccRegError(errors)
            if self.is_connected(): # if we are connect, lets communicate with the server
                self.send(self._raw_cmd)                                      # send to server
                if len(self._errors): raise ccRegError(self.fetch_errors())
                xml_answer = self.receive()                                   # receive answer
                self.process_answer(xml_answer)                               # process answer
                if len(self._errors): raise ccRegError(self.fetch_errors())
            else:
                raise ccRegError(_T("You are not connected! For connection type: connect or login"))
        else:
            self._dct_answer['errors'].append(_T('You are not logged. You must call login() before working on the server.')) # _T("XML EPP document was not created.")
        if len(self._errors): raise ccRegError(self.fetch_errors())
        return self._dct_answer



class ccRegError(StandardError):
    'ccReg EPP errors.'

    
def append_dct(dct,key,multiline):
    'Appends value at the dict key.'
    value = multiline.split('\n')
    if len(value) == 1: value = value[0]
    if dct.has_key(key):
        if type(dct[key]) == list:
            getattr(dct[key],{False:'append',True:'extend'}[type(value) is list])(value)
        else:
            dct[key] = [dct[key]]
            getattr(dct[key],{False:'append',True:'extend'}[type(value) is list])(value)
    else:
        dct[key] = value

    
def adjust_dict(dct_data):
    'Remove None and put items into list.'
    dct={}
    if type(dct_data) == dict:
        for k in dct_data:
            if dct_data[k] is None: continue
            if type(dct_data[k]) in (str,unicode):
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
                        if item != None: dct[k].append(item)
    return dct

def adjust_dct_keys(dct, names):
    'Keys must exists and values must be list or tuple.'
    for name in names:
        if dct.has_key(name):
            if type(dct[name]) not in (list,tuple):
                dct[name] = (dct[name],)
        else:
            dct[name] = ()
    
def test(name_amd_xml):
    m = ManagerReceiver()
    m._command_sent = name_amd_xml[0]
    m.process_answer(name_amd_xml[1])
    m.display()
    m.print_answer()
    m.__put_raw_into_note__(m._dict_answer)
    # m.__put_raw_into_note__(m._raw_answer)
    m.display()

if __name__ == '__main__':
    try:
        import test_incomming_messages
    except ImportError:
        print "Testing modul 'test_incomming_messages.py' is not included."
    else:
        # TEST selected document:
        # Data item has format: ('command:name',"""<?xml ...XML document... >""")
        # For example: ('nsset:info',"""<?xml ...<epp ...><response> ... </epp>""")
        test(test_incomming_messages.data[8])
