# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
from gettext import gettext as _T
import copy #!!! test

NOPROMPT = 0
UNFINITE = 100
IS_STRING,IS_DICT = range(2)
patt_not_slash = re.compile(r'(\\+)$')
patt_key = re.compile('-+(.+)')
patt_name_pos = re.compile(r'(\w+)\[([^\]]+)\]')

def __slash_occured__(text):
    ret=0
    m = patt_not_slash.search(text)
    if m:
        ret = len(m.group(1))%2
    return ret

def parse(dct, root_cols, text_line):
    """Parse values from text and put thjem into dict.
    text is in format:
    
    value "value with space" 'other value with space'
    -key = value ("more than one", "second value")
    """
    errors=[]
    cols = root_cols
##    if cols:
##        max_col_id = len(cols)
##    else:
##        max_col_id = -1
    col_id = 0
    blank_pattern = re.compile('\s',re.S)
    key = sep = ''
    quot=[]
    group=[]
    prev_group = []
    prev_dct = []
    is_group=0
    tokens = re.split('(=|\'|"|,|\(|\)|\s+)', text_line)
    for pos in range(len(tokens)):
##        if max_col_id != -1 and col_id >= max_col_id: break
        token = tokens[pos]
        if token=='': continue
##        print "-->TOKEN: '%s'"%token
        if sep:
            # part string token
            if token==sep and not __slash_occured__(tokens[pos-1]):
                sep=''
                token = ''.join(quot)
                quot=[]
                if is_group:
                    group.append(token)
                else:
                    if key:
                        # uložení na pozici klíče
                        insert_on_key(errors,dct,root_cols,key,token)
                    else:
                        if cols:
                            row = cols[col_id]
                            key = row[0]
                        else:
                            key = col_id
                        col_id+=1
##                    if cols == None or key in cols:
                        print "1.STRING dct[%s] = '%s'"%(key,token)
                        if type(dct.get(key,None)) == list:
                            dct[key].append(token)
                        else:
                            dct[key] = token
##                    else:
##                        errors.append("%s: '%s'."%(_T('Unknown parameter name'),key))
                    key = ''
            else:
                quot.append(token)
        else:
            # part single token
            if token in '\'"':
                sep = token
            elif token[0] == '-':
                m = patt_key.match(token)
                if m: key = m.group(1)
            elif token in '=,' and pos:
                pass
            elif token == '(':
                if is_group:
                    prev_group.append(group)
                    group.append([])
                    group = group[-1]
                is_group += 1
            elif token == ')':
                is_group -= 1
                if is_group < 0:
                    # kontrola na podtečení token underflow: )
                    errors.append(_T('data-parser: token underflow: )'))
                    is_group = 0
                if len(prev_group): group = prev_group.pop()
                if not is_group:
                    # skupina se uloží
                    if key:
                        insert_on_key(errors,dct,root_cols,key,group)
                    else:
                        if cols:
                            row = cols[col_id]
                            key = row[0]
                        else:
                            key = col_id
                        col_id+=1
##                    if group:
                        if cols == None or key in cols:
                            print "2.GROUP dct[%s] = '%s'"%(key,token)
                            if type(dct.get(key,None)) == list:
                                dct[key].append(group)
                            else:
                                dct[key] = group
                        else:
                            errors.append("%s: '%s'."%(_T('Unknown parameter name'),key))
                    key = ''
                    group=[]
            elif blank_pattern.match(token):
                pass
            else:
                if token[-1]==',': token = token[:-1]
                if is_group:
                    if(token): group.append(token)
                    print "SINGLE-TOKEN: is_group=",is_group,'GROUP:',group
                else:
                    print "SINGLE-TOKEN: '%s' KEY: '%s'"%(token,key)
                    if key:
                        # uložení na pozici klíče
                        insert_on_key(errors,dct,root_cols,key,token)
                    else:
                        if cols:
                            row = cols[col_id]
                            key = row[0]
                            print "(key)'%s' = cols[%d]"%(key,col_id)
                        else:
                            key = col_id
                        col_id+=1
##                    if cols == None or key in cols:
                        print "3.TOKEN dct[%s] = '%s'"%(key,token)
                        if type(dct.get(key,None)) == list:
                            dct[key].append(token)
                        else:
                            dct[key] = token
##                    else:
##                        errors.append("%s: '%s'."%(_T('Unknown parameter name'),key))
                    key = ''
    return errors

def get_name_pos(errors,key,name,cols):
    'Parse index from key.'
    pos = None
    m = patt_name_pos.match(name)
    if m:
        name = m.group(1)
        try:
            pos = int(m.group(2))
        except ValueError:
            errors.append("%s: '%s' [%s]."%(_T('Invalid parameter index'),key,m.group(2)))
            pos = None
    if name not in [r[0]for r in cols]:
        errors.append("%s: '%s' (%s)."%(_T('Unknown parameter name'),key,name))
        name = ''
    return name,pos

def insert_on_key(errors,dct,cols,key,value):
    """Insert value into dict parsing key into dict scopes.
    errors (OUT) out error messages unknown parameter name
    dct (OUT) dict where value is put
    cols (IN) struct of columns
    key (IN) compouded name of dict keys
    value (IN) value what is put inside dict
    """
    scopes = key.split('.')
    for name in scopes[:-1]:
        name,pos = get_name_pos(errors,key,name,cols)
        if not name: return
        if dct.has_key(name):
            dct = dct[name]
            if type(dct)==list:
                if pos == None:
                    dct = dct[-1]
                else:
                    dct = insert_at_pos(errors,dct,cols,key,value,pos,IS_DICT)
        else:
            dct[name] = [{}]
            if pos == None:
                dct = dct[name][0]
            else:
                dct = insert_at_pos(errors,dct[name],cols,key,value,pos,IS_DICT)
        # scope v cols
        for row in cols:
            if row[0] == name:
                cols=()
                if len(row)>4: cols = row[4]
                break
    name = scopes[-1]
    name,pos = get_name_pos(errors,key,name,cols)
    if not name: return
    if dct.has_key(name):
        if type(dct[name]) == list:
            if pos != None:
                insert_at_pos(errors,dct[name],cols,key,value,pos,IS_STRING)
            else:
                dct[name].append(value)
        else:
            dct[name] = [dct[name], value]
            if pos != None:
                insert_at_pos(errors,dct[name],cols,key,value,pos,IS_STRING)
    else:
        if pos != None:
            dct[name]=['']
            insert_at_pos(errors,dct[name],cols,key,value,pos,IS_STRING)
        else:
            dct[name] = value

def insert_at_pos(errors,dct,cols,key,value,pos,is_dict):
    'Insert value into dict at name and position.'
    max = cols[0][1][1]+1
    if max < 3:
        errors.append("%s: [%s] '%s'."%(_T('Parameter index not allowed here'),pos,key))
        if is_dict:dct = dct[-1]
    else:
        if pos < max:
            while len(dct) <= pos:
                dct.append(('',{})[is_dict])
            if is_dict:
                dct = dct[pos]
            else:
                dct[pos] = value
        else:
            errors.append("%s: %d '%s' (%s %d)."%(_T('Index out of range'),pos,key,_T('last index must be'),max-1))
            if is_dict: dct = dct[-1]
    return dct

def cols_keynames(cols):
##    print "+++ cols_keynames",cols
    for row in cols:
        name,type = row[0:2]
        max = type[1]
        prompt = (1,0)[len(type)>2 and type[2]==NOPROMPT]
        if prompt:
            if max == UNFINITE:
                yield '(UNF) %s'%name
            else:
                for n in range(max):
                    yield name
        if len(row) > 4:
            for child in cols_keynames(row[4]):
                yield child
    
##def gen(n):
##    for x in range(n):
##        yield x
##    if n: 
##        for n in gen(n-1):
##            yield n
    
def test2():
    # column: name, (nim,max,is-prompt), ('allowed','values'), "help", (children columns)
    # StopIteration
    cols = (
        ('command-name',(1,1,NOPROMPT)),
        ('id',(1,1)),
        ('add',(0,1,NOPROMPT),None,"help",
            (
            ('ns',(0,9,NOPROMPT),None,"help",
                (
                ('name',(1,1)),
                ('addr',(0,9)),
                )
            ),
            ('tech',(0,UNFINITE)),
            ('status',(0,6),('ok','linked','req')),
            )
        ),
        ('rem',(0,1,NOPROMPT),None,'',
            (('name',(0,9)),
             ('tech',(0,UNFINITE)),
             ('status',(0,6),('ok','linked','req')),
            )
        ),
        ('pw',(0,1))
    )
##    cols_keynames(cols)
##    cn = cols_keynames(cols)
    for key in cols_keynames(cols):
##        print '-'*30
        print "OUT-KEY:",key
##    for i in gen(5):
##        print "I",i
    return
def x():
    text = """create_nsset POKUS-ID 
        (
        ((ns1.bazmek.net 194.23.54.1),(ns2.bazmek.net (194.23.54.1,194.23.54.2))), technic, linked
        ) 
        (
            ns1-rem.ni.cz
            (tech-rem1, tech-rem2, tech-rem3)
            (ok,req,linked)
        )
        heslo"""
    text = 'create_nsset POKUS-ID'
    text = "create_nsset POKUS-ID --pw='heslo bazmek' --add.ns.name = ns1.nic.cz --add.ns.name = ns2.nic.cz --add.ns.addr = 127.0.0.1"
    text = "create_nsset POKUS-ID --pw='heslo bazmek' --add.ns.name = ns1.nic.cz --add.ns[1].name = ns2.nic.cz --add.ns[0].addr = 127.0.0.1 --add.ns.addr = 127.0.1.1 --add.ns[0].addr = 127.0.0.2"
    text = "create_nsset POKUS-ID --add.ns[2].name = 'ns1.nic.cz jojo cosi'"
    print 'COLUMNS:',cols
    print 'COMMAND-LINE:',text
    dct = {}
    errors = parse(dct, cols, text)
    print 'RESULT-DCT:',dct
    print "ERRORS:",errors

def test1():
    text=""" =       
    value1,value2, "value-3 (with) space" 'other4 "value" = with\\\\\\' space' =
    --10 = out-of-order-data (value5) ("more, 6-A (than), 'some' one", second-6-B, "third, '6-B' \\"buzz\\" value")
    "last7 \\"buzz\\" END." 'eight is overwritten' --8 = "out of order: 8" 'nine-9, is "end" of dict.'
    --6="this is outside!"
    --5 "this is outside too and it'll be palced in 5. item."
"""
    cols = ['%d'%c for c in range(1,12)]

    cols = 'command nsset password ns_addr tech'.split(' ')
##    cols = ('command','nsset','password',('ns','addr'),'tech')
    text = 'create_nsset pokus heslo (ns1.bazmek.net ns2.bazmek.net) tech-contact'
    text = 'create_nsset pokus heslo ((ns1.bazmek.net 194.23.54.1),(ns2.bazmek.net (194.23.54.1,194.23.54.2))) tech-contact'
##    text = 'create_nsset pokus heslo (ns1.bazmek.net (194.23.54.1 194.23.54.2) ns2.bazmek.net 194.23.54.1) tech-contact'
##    text = 'create_nsset pokus heslo (ns1.bazmek.net))'
    dct = {}
    for key in cols:
        dct[key]=''
    print 'COMMAND LINE:',text
    print '-'*60
    print 'COLUMNS:',cols
    print 'EMPY-DICT:',dct
    print '-'*60
    errors = fill_dict(dct, cols, text)
    print "RESULT:"
    print dct
##    for k in dct.keys():
##        print "[%s] '%s'"%(k,str(dct[k]))
    print "ERRORS:",errors

if __name__ == '__main__':
    test2()

