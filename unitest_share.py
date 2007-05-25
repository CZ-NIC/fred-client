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
import random
import fred
from fred.translate import encoding


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
        log_fp.write(edoc.get_xml())
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
        ts = list(time.gmtime())
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
    
get_local_text = fred.session_base.get_ltext

if __name__ == '__main__':
    print "This module is used by all fred unittests."
    print '(0, 6):', datedelta_from_now(0, 6)
    print '(0, 6, 13):', datedelta_from_now(0, 6, 13)
    print '(0, 6, 14):', datedelta_from_now(0, 6, 14)
