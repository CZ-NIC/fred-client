# -*- coding: utf8 -*-
#!/usr/bin/env python
import operator
import eppdoc
from session_base import *
from session_command import ManagerCommand
import translate
_T = translate._T

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
            lcol = column_name.split(' ')
            if len(lcol)>1:
                value = eppdoc.get_dct_value(dict_data, lcol[0])
                for a in lcol[1:]:
                    val = eppdoc.get_dct_attr(dict_data, lcol[0], a)
                    if val: append_dct(dct,a,val)
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
                    msg = []
                    if item.has_key('value'):
                        for key in item['value'].keys():
                            msg.append('%s:'%item['value'][key].get('data',item['value'][key]))
                    if item.has_key('reason'):
                        msg.append(item['reason'].get('data',item['reason']))
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
                fnc_name = 'answer_response_%s'%self._command_sent.replace(':','_')
                if hasattr(self,fnc_name):
                    getattr(self,fnc_name)((result, code, reason))
                    display_src = 0 # Odpověd byla odchycena, není potřeba ji zobrazovat celou.
            else:
                self._dct_answer['errors'].append(_T('Missing result in the response message.'))
        else:
            self._dct_answer['errors'].append(_T('Unknown server response'))
        if display_src:
            # Pokud odpověd neodchytila žádná funkce, tak se odpověd zobrazí celá.
            self.__put_raw_into_note__(self._dict_answer)

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
                    msg = _T('Server answer is not valid!')
                    self.append_note(msg,('RED','BOLD'))
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
        self.defs[LANGS] = eppdoc.get_dct_value(greeting, ('svcMenu','lang')).split('\n')
        if type(self.defs[LANGS]) in (str,unicode):
            self.defs[LANGS] = (self.defs[LANGS],)
        dct['lang'] = self.defs[LANGS]
        self.defs[objURI] = eppdoc.get_dct_values(greeting, ('svcMenu','objURI'))
        self.defs[extURI] = eppdoc.get_dct_values(greeting, ('svcMenu','svcExtension','extURI'))
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
        self.append_note(data[ANSW_MSG])
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
                ('contact:id','contact:roid','contact:status s'))
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
                ,'domain:contact type','domain:nsset','domain:clID','domain:crID'
                ,'domain:crDate','domain:exDate','domain:upID'))

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
                ,'nsset:crDate','nsset:upID','nsset:trDate','nsset:authInfo'))
            if nsset_infData.has_key('nsset:ns'):
                nsset_ns = nsset_infData['nsset:ns']
                if type(nsset_ns) == list:
                    for item in nsset_ns:
                        self.__append_note_from_dct__(item,('nsset:name','nsset:addr'))
                else:
                    self.__append_note_from_dct__(nsset_ns,('nsset:name','nsset:addr'))

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
        msgQ = None
        response = self._dict_answer.get('response',None)
        if response: msgQ = response.get('msgQ',None)
        if msgQ:
            self.__append_note_from_dct__(response,('msgQ count id',))
            self.__append_note_from_dct__(msgQ,('qDate','msg'))
        #if data[ANSW_CODE] == '1301' and self.__get_config__('session','poll_ack') == 'on':
        #    # automatická odpověd 'ack'
        #    xml_doc = self.create_eppdoc('poll ack')
        #    if xml_doc and self.is_connected():
        #        self.append_note(_T('Sending command poll ack'))
        #        self.send(xml_doc)

    def answer_response_domain_transfer(self, data):
        "data=(response,result,code,msg)"
        self.append_note('domain:transfer: ${BOLD}[%s]${NORMAL} %s'%(data[ANSW_CODE],data[ANSW_MSG]))

    def answer_response_nsset_transfer(self, data):
        "data=(response,result,code,msg)"
        self.append_note('nsset:transfer: ${BOLD}[%s]${NORMAL} %s'%(data[ANSW_CODE],data[ANSW_MSG]))

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
        dct_params = adjust_dict(params)                                                   # turn params into expecterd format
        self.create_command_with_params(command_name, dct_params) # create EPP command
        self._raw_cmd = self._epp_cmd.get_xml()                                        # get EPP in XML (string)
        if len(self._errors): raise ccRegError(self.fetch_errors())
        if self.is_online(command_name):                                                    # go only if session is online.
            errors = self.is_epp_valid(self._raw_cmd)                                    # check doc for EPP validation
            if len(errors): raise ccRegError(errors)
            if self.is_connected(): # if we are connect, lets communicate with the server
                self.send(self._raw_cmd)                                                         # send to server
                if len(self._errors): raise ccRegError(self.fetch_errors())
                xml_answer = self.receive()                                                     # receive answer
                self.process_answer(xml_answer)                                           # process answer
                if len(self._errors): raise ccRegError(self.fetch_errors())
            else:
                raise ccRegError(_T("You are not connected! For connection type: connect or login"))
        else:
            self._dct_answer['errors'].append(_T('You are not logged. You must call login() before working on the server.')) # _T("XML EPP document was not created.")
        if len(self._errors): raise ccRegError(self.fetch_errors())
        return self._dct_answer



class ccRegError(StandardError):
    'ccReg EPP errors.'

    
def append_dct(dct,key,value):
    'Appends value at the dict key.'
    if dct.has_key(key):
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [dct[key], vlalue]
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
    
def test(xml):
    m = ManagerReceiver()
    m._command_sent = 'transfer'
    m.process_answer(xml)

if __name__ == '__main__':
    test("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0
     epp-1.0.xsd">
  <command>
    <transfer op="request">
      <domain:transfer
       xmlns:domain="http://www.nic.cz/xml/epp/domain-1.0"
       xsi:schemaLocation="http://www.nic.cz/xml/epp/domain-1.0
       domain-1.0.xsd">
        <domain:name>example.cz</domain:name>
        <domain:authInfo>
            <domain:pw>2fooBAR</domain:pw>
        </domain:authInfo>
      </domain:transfer>
    </transfer>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>""")
