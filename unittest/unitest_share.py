#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Usage: 
You MUST define TWO usernames in section connect in your my_unittest.conf:

    [connect_curlew]
    host = curlew
    username = REG-UNITTEST1
    password = 123456789
    username2 = REG-UNITTEST2
    password2 = 123456789

Than you can run $ %s --config=my_unittest.conf

General options:
  -?, --help       Show this help and exit
  -g  --log=filename      
                       name of log file
  -l LANGUAGE, --lang=LANGUAGE
                   Set user interface language
  -x, --no_validate
                   Disable client-side XML validation

Connection options:
  -f CONFIG, --config=CONFIG
                   Load configuration from config file
  -s SESSION, --session=SESSION
                   Use session from config file

  -h HOSTNAME, --host=HOSTNAME
                   Fred server host
  -p PORT, --port=PORT
                   Server port (default: 700)
  -u USERNAME, --user=USERNAME
                   Authenticate to server as user
  -w PASSWORD, --password=PASSWORD
                   Authenticate to server with password
  -c CERTIFICATE --cert=CERTIFICATE
                   Use SSL certificate to connect to server
  -k PRIVATEKEY --privkey=PRIVATEKEY
                   Use SSL private key to connect to server
"""
import sys, re, time
sys.path.insert(0, '..')
import random
import fred
from fred.translate import encoding
from fred.eppdoc_assemble import DISCLOSES
from fred.session_base import decamell


def is_not_empty(value):
    'True when value is not empty'
    if type(value) in (list, tuple):
        return len(value)
    return value != ''

def find_available_handle(epp_cli, type_object, prefix):
    'Find first available object.'
    available_handle = ''
    handles = []
    for n in range(30):
        handles.append('%s%02d'%(prefix,n))
    getattr(epp_cli,'check_%s'%type_object)(handles)
    for name in handles:
        if epp_cli.is_val(('data',name)) == 1:
            available_handle = name
            break
    return available_handle

def get_reason(client):
    'Returs reason a errors from client object'
    reason = get_local_text(client.is_val('reason'))
    er = []
    for error in client.is_val('errors'):
        er.append(get_local_text(error))
    return  '%s ERRORS:[%s]\nCOMMAND: %s'%(reason, '\n'.join(er), get_local_text(client._epp.get_command_line()))

def write_log_header(log_fp):
    log_fp.write('Created at %s\n'%time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))

def write_log_message(log_fp, message):
    if log_fp:
        log_fp.write(str(message))
    
def write_log(epp_cli, log_fp, log_step, fnc_name, fnc_doc, step=None):
    if log_fp and epp_cli._epp._raw_cmd:
        step_sep = ''
        if step:
            if step[0]==1: step_sep = '%s\n'%('#'*60)
            step_info = '### STEP: %d/%d ###\n'%step
            log_step = step
        elif log_step:
            step_info = '### STEP: %d/%d ###\n'%(log_step[0]+1,log_step[1])
            log_step = None
        else:
            step_info = ''
            step_sep = '%s\n'%('#'*60)
        cmd = epp_cli._epp._command_sent.encode(encoding)
        example = epp_cli._epp.get_command_line()
        log_fp.write('%s%s%s\nCOMMAND: %s\n>>> %s\n%s\n'%(step_sep,step_info,fnc_doc,cmd,example,'.'*60))
        log_fp.write(epp_cli._epp._raw_cmd)
        log_fp.write('%s\n%s\nANSWER: %s\n'%('-'*60,fnc_doc,cmd))
        answer = epp_cli.get_answer()
        if answer:
            log_fp.write('%s\n'%re.sub('\x1b(\\[|\\()\d*(m|B)','',answer))
        edoc = fred.eppdoc.Message()
        edoc.parse_xml(epp_cli._epp._raw_answer)
        parsed_xml = edoc.get_xml()
        if parsed_xml == '':
            # in case if is not possible parse XML answer
            parsed_xml = 'RAW ANSWER (UNPARSED): ' + epp_cli._epp._raw_answer
        log_fp.write(parsed_xml)
        log_fp.write('\n%s\n'%('='*60))

def reset_client(epp_cli):
    epp_cli._epp._command_sent = ''
    epp_cli._epp._raw_cmd = ''
    epp_cli._epp.reset_round()
    epp_cli._epp.reset_src()

def make_str(value):
    if type(value) in (tuple,list):
        arr=[]
        for item in value:
            arr.append(item.encode(encoding))
        value = '(%s)'%', '.join(arr)
    elif type(value) == unicode:
        value = value.encode(encoding)
    return value

def are_equal(val1,val2):
    'Compare values or lists. True - equal, False - not equal.'
    if type(val1) in (list, tuple):
        if type(val2) not in (list, tuple): return False
        lst2 = list(val2)
        if len(val1) == len(lst2):
            for v in val1:
                if v in lst2: lst2.pop(lst2.index(v))
            retv = len(lst2) == 0
        else:
            retv = False
    else:
        if re.match('(CID|NSSID):',val1,re.I):
            # identificators compare case insensitive
            val1 = val1.upper()
            val2 = val2.upper()
        retv = val1 == val2
    return retv

def err_not_equal(errors, data, key, refval):
    if data.has_key(key):
        if data[key] != refval:
            errors.append('Neplatny klic "%s" je "%s" (ma byt: "%s")'%(key,data[key],refval))
    else:
        if refval != '':
            # only in case if valuse is set:
            errors.append('Klic "%s" chybi! (mel by byt: "%s")'%(key,refval))

def check_date(date, nu, sql_date=None):
    'Check expected date.'
    if sql_date:
        ts = list(time.strptime(sql_date[:10],'%Y-%m-%d'))
    else:
        ts = list(time.localtime())
    num = int(nu['num'])
    if nu['unit'] == 'y':
        ts[0] += num
    else:
        ts[0] += num/12
        ts[1] += num%12
        if ts[1] > 12:
            ts[0] += 1
            ts[1] = ts[1]%12
    exdate = time.strftime('%Y-%m-%d',ts)
    return exdate == date[:10], exdate

def create_handle(prefix=''):
          return '%s%s'%(  prefix , random.randint( 0 , 1000000 )  )
#     return '%s%s'%( prefix , random.randint( 0 ,1000000 ) , )
# 'time.strftime( "%s" ,  time.gmtime() )' )


def create_enumdomain():
    return '%s.%s.%s.%s.%s.%s.%s.%s.%s.0.2.4.e164.arpa'%(  random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) , random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) , random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) ,  random.randint( 0 , 9 ) , )

def add_period(struct_time, year=0, month=0, day=0):
    """Add period. 
    IN: 
        struct_time = (2006, 11, 22, 11, 18, 54, 2, 326, 0)
        year        int
        month       int
        day         int
    OUT: t_time     float
    """
    # append days
    tt = list(struct_time)
    tt[2]+= day
    
    struct_time = time.localtime(time.mktime(tt))
    tt = list(struct_time)
    
    # append months and years
    tt[0]+=year
    tt[1]+= month
    tt[0]+= tt[1]/12
    tt[1] = tt[1]%12
    
    return time.mktime(tt)
    
def datedelta_from_now(year=0, month=0, day=0):
    'Returs date from now to defined date period. OUT: "2006-11-22"'
    return time.strftime("%Y-%m-%d",time.localtime(add_period(time.localtime(time.time()), year, month, day)))

def compare_disclose(cols, camell_disclose, camell_hide):
    'Compare disclose list.'
    c = {}
    disclose = map(decamell, camell_disclose)
    hide = map(decamell, camell_hide)
    disclose_or_hide = [n for n in DISCLOSES if n not in cols['data']]
    if cols['flag'] == 'n':
        c['disclose'] = disclose_or_hide
        c['hide'] = [n for n in DISCLOSES if n not in disclose_or_hide]
    else:
        c['hide'] = disclose_or_hide
        c['disclose'] = [n for n in DISCLOSES if n not in disclose_or_hide]
    is_error = not (are_equal(c['disclose'], disclose) and
                are_equal(c['hide'],hide))
    return (is_error, 
        'disclose(%s) hide(%s)'%(','.join(disclose),','.join(hide)), 
        'disclose(%s) hide(%s)'%(','.join(c['disclose']),','.join(c['hide']))
        )

def compare_ident(cols_ident, data):
    ident_type = data.get('contact:ident.type','')
    ident_number = data.get('contact:ident','')
    is_error = not(cols_ident['type'] == ident_type and cols_ident['number'] == ident_number)
    return is_error, '(%s)%s'%(ident_type,ident_number), '(%s)%s'%(cols_ident['type'],cols_ident['number'])
            
def compare_contact_info(prefix, cols, scope, key=None, pkeys=[]):
    'Check info-[object] against selected set.'
    prevkeys = ':'.join(pkeys)
    if key:
        data = scope[key]
    else:
        data = scope
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    #--------------------------------
    for k,v in cols.items():
        if k == 'notify_email': k = 'notifyEmail'
        if k == 'auth_info': k = 'authInfo'
        key = '%s:%s'%(prefix,k)
        if k == 'disclose':
            err, vals, v = compare_disclose(cols['disclose'], data.get('contact:disclose',[]), data.get('contact:hide',[]))
            if err:
                errors.append('Data nesouhlasi:\n%s.%s JSOU:%s MELY BYT:%s'%(prevkeys, key, make_str(vals), make_str(v)))
            continue
        if k == 'ident':
            err, vals, v = compare_ident(cols['ident'], data)
            if err:
                errors.append('Data nesouhlasi:\n%s.%s JSOU:%s MELY BYT:%s'%(prevkeys, key, make_str(vals), make_str(v)))
            continue
        if type(data) != dict: data = {key:data}
        if data.has_key(key):
            if type(v) is dict:
                pkeys.append(key)
                err = compare_contact_info(prefix, v, data, key, pkeys)
                pkeys.pop()
                if len(err): errors.extend(err)
            else:
                if type(data[key]) is list:
                    vals = tuple(data[key])
                else:
                    vals = data[key]
                    # converts string to array
                    if key == 'contact:street':
                        vals = vals.split('\n')
                if not are_equal(vals,v):
                    errors.append('Data nesouhlasi:\n%s.%s JSOU:%s MELY BYT:%s'%(prevkeys, key, make_str(vals), make_str(v)))
        else:
            # if value (v) is not empty ('') and key is not ...:disclose_flag
            if is_not_empty(v) and key != '%s:disclose_flag'%prefix: # except disclose_flag - it not shown
                errors.append('Chybi klic %s'%key)
                
    return errors
    
def compare_domain_info(epp_cli, cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    ##============================================================
    ##COLS:
    ##{   'name': 'hokus-pokus.cz', 
    ##    'period': {'num': u'3', 'unit': u'y'}, 
    ##    'contact': ('TDOMCONT01',), 
    ##    'nsset': 'TDOMNSSET01', 
    ##    'registrant': 'TDOMCONT01', 
    ##    'auth_info': 'heslicko'}
    ##------------------------------------------------------------
    ##DATA:
    ##{   'domain:contact': u'TDOMCONT01', 
    ##    'domain:crID': u'REG-UNITTEST1', 
    ##    'domain:clID': u'REG-UNITTEST1', 
    ##    'domain:name': u'hokus-pokus.cz', 
    ##    'domain:status.s': u'ok', 
    ##    'domain:exDate': u'2009-08-10T00:00:00.0Z', 
    ##    'domain:nsset': u'TDOMNSSET01', 
    ##    'domain:pw': u'heslicko', 
    ##    'domain:crDate': u'2006-08-10T09:58:16.0Z', 
    ##    'domain:roid': u'D0000000219-CZ', 
    ##    'domain:registrant': u'TDOMCONT01', 
    ##    'domain:renew': u'2009-08-10', 
    ##    'domain:contact.type': u'admin'}
    ##____________________________________________________________
    username, password = epp_cli._epp.get_actual_username_and_password()

    err_not_equal(errors, data, 'domain:clID', username)
    err_not_equal(errors, data, 'domain:name', cols['name'])
    err_not_equal(errors, data, 'domain:nsset', cols['nsset'])
    err_not_equal(errors, data, 'domain:keyset', cols['keyset'])
    err_not_equal(errors, data, 'domain:authInfo', cols['auth_info'])
    if not are_equal(data['domain:registrant'], cols['registrant']):
        errors.append('Data domain:registrant nesouhlasi. JSOU:%s MELY BYT:%s'%(make_str(data['domain:registrant']), make_str(cols['registrant'])))
    is_equal, exdate = check_date(data['domain:exDate'], cols['period'])
    if not is_equal:
        errors.append('Data domain:exDate nesouhlasi: jsou: %s a mely byt: %s'%(data['domain:exDate'], exdate))
    actual_time = time.strftime('%Y-%m-%d',time.localtime())
    if data['domain:crDate'][:10] != actual_time:
        errors.append('Data domain:crDate nesouhlasi: jsou: %s a mely by byt: %s'%(data['domain:crDate'],actual_time))
    return errors

    
def compare_nsset_info(epp_cli, cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
    errors = []
    ##============================================================
    ##COLS:
    ##{'tech': ('contact1',), 
    ##'id': 'test001', 
    ##'dns': (
    ##    {'name': 'ns.name1.cz', 'addr': ('127.0.0.1', '127.1.1.1', '127.2.2.2')}, 
    ##    {'name': 'ns.name2.cz', 'addr': ('126.0.0.1', '126.1.1.1', '126.2.2.2')}
    ##    ), 
    ##    'auth_info': 'heslo'}
    ##------------------------------------------------------------
    ##DATA:
    ##    saved_data = {'nsset:upID': u'REG-UNITTEST1', 
    ##        'nsset:status.s': u'ok', 
    ##        'nsset:id': u'test001', 
    ##        'nsset:crDate': u'2006-08-03T09:38:05.0Z', 
    ##        'nsset:ns': [
    ##            [u'ns.name2.cz', [u'126.0.0.1', u'126.1.1.1', u'126.2.2.2']], 
    ##            [u'ns.name1.cz', [u'127.0.0.1', u'127.1.1.1', u'127.2.2.2']]], 
    ##        'nsset:clID': u'REG-UNITTEST1', 
    ##        'nsset:roid': u'N0000000027-CZ', 
    ##        'nsset:tech': u'CONTACT1'}
    ##____________________________________________________________
    # not checked: 
    #   nsset:upID          u'REG-UNITTEST1'
    #   nsset:status.s      u'ok'
    #   nsset:crDate        u'2006-08-03T09:38:05.0Z'
    #   nsset:roid          u'N0000000027-CZ'
    key = 'nsset:upID'
    username, password = epp_cli._epp.get_actual_username_and_password()
    err_not_equal(errors, data, 'nsset:clID', username)
    err_not_equal(errors, data, 'nsset:id', cols['id'])

    tech = data.get('nsset:tech', [])
    if type(tech) in (str, unicode):
        tech = tech.split('\n')
    if type(tech) not in (list, tuple):
        tech = (tech, )
    if not are_equal(tech, cols['tech']):
        errors.append('Data nsset:tech nesouhlasi. JSOU:%s MELY BYT:%s'%(make_str(tech), make_str(cols['tech'])))
    
    ns = data.get('nsset:ns',[])
    dns = cols['dns']
    if len(ns) == len(dns):
        for name,addr in ns:
            ref_addr = None
            for d in dns:
                if d['name'] == name:
                    ref_addr = list(d['addr'])
                    break
            if ref_addr is None:
                errors.append('DNS name "%s" nebyl nalezen'%name)
            else:
                if addr != ref_addr:
                    errors.append('DNS "%s" addr nejsou shodne: jsou: %s maji byt: %s'%(name, str(addr), str(ref_addr)))
    else:
        errors.append('Seznam DNS nema pozadovany pocet. Ma %d a mel by mit %d.'%(len(ns),len(dns)))
    return errors

def compare_keyset_info(epp_cli, cols, data):
    'Check if values are equal'
    #print '%s\nCOLS:\n%s\n%s\nDATA:\n%s\n%s\n'%('='*60, str(cols), '-'*60, str(data), '_'*60)
#    COLS:
#    {'tech': ['CID:U1353636'], 
#    'auth_info': 'heslo', 
#    'id': 'KEYSID:U1128843', 
#    'ds': [{'alg': u'2', 'digest_type': u'3', 'digest': u'499602d2', 'key_tag': u'1'}, 
#           {'alg': u'22', 'digest_type': u'33', 'max_sig_life': u'1', 'digest': u'499602d2', 'key_tag': u'11'}]}
#    ------------------------------------------------------------
#    DATA:
#    {'keyset:roid': u'K0000000014-CZ', 
#    'keyset:ds': [[u'1', u'2', u'3', u'499602d2', u'0'], 
#                  [u'11', u'22', u'33', u'499602d2', u'1']], 
#    'keyset:tech': u'CID:U1353636', 
#    'keyset:crDate': u'2008-08-01T14:50:49+02:00', 
#    'keyset:clID': u'REG-FRED_A', 
#    'keyset:status': u'Objekt is without restrictions', 
#    'keyset:id': u'KEYSID:U1128843', 
#    'keyset:status.s': u'ok', 
#    'keyset:crID': u'REG-FRED_A', 
#    'keyset:authInfo': u'heslo'}
#    ____________________________________________________________

    errors = []

    key = 'keyset:upID'
    username, password = epp_cli._epp.get_actual_username_and_password()
    err_not_equal(errors, data, 'keyset:clID', username)
    err_not_equal(errors, data, 'keyset:id', cols['id'])

    tech = data.get('keyset:tech', [])
    if type(tech) in (str, unicode):
        tech = tech.split('\n')
    if type(tech) not in (list, tuple):
        tech = (tech, )
    if not are_equal(tech, cols['tech']):
        errors.append('Data keyset:tech nesouhlasi. JSOU:%s MELY BYT:%s'%(make_str(tech), make_str(cols['tech'])))
    
    # check DS
    ds_names = ('key_tag', 'alg', 'digest_type', 'digest', 'max_sig_life')
    ds = data.get('keyset:ds',[])
    cols_ds = cols['ds']
    if len(ds) == len(cols_ds):
        for pos in range(len(cols_ds)):
            for n in range(len(ds[pos])):
                ds_name = ds_names[n]
                #print "[%d,%d,%s]:"%(pos, n, ds_name), ds[pos][n], "!=", cols_ds[pos].get(ds_name, '0') #DEBUG
                if ds[pos][n] != cols_ds[pos].get(ds_name, '0'):
                    errors.append('Neplatna hodnota %s. Je: %s, ale ma byt: %s. %s' % (ds_name, ds[pos][n], cols_ds[pos][ds_name], str(ds[pos])))
    else:
        errors.append('Seznam DS nema pozadovany pocet. Ma %d a mel by mit %d.'%(len(ds),len(cols_ds)))
    return errors
    
    
get_local_text = fred.session_base.get_ltext

if __name__ == '__main__':
    print "This module is used by all fred unittests."
    print '(0, 6):', datedelta_from_now(0, 6)
    print '(0, 6, 13):', datedelta_from_now(0, 6, 13)
    print '(0, 6, 14):', datedelta_from_now(0, 6, 14)
