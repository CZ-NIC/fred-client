# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
from gettext import gettext as _T

patt_not_slash = re.compile(r'(\\+)$')
patt_key = re.compile('-+(.+)')

def __slash_occured__(text):
    ret=0
    m = patt_not_slash.search(text)
    if m:
        ret = len(m.group(1))%2
    return ret

def fill_dict(dct, cols, text):
    """Parse values from text and put thjem into dict.
    text is in format:
    
    value "value with space" 'other value with space'
    -key = value ("more than one", "second value")
    """
    errors=[]
    if cols:
        max_col_id = len(cols)
    else:
        max_col_id = -1
    col_id = 0
    blank_pattern = re.compile('\s',re.S)
    key = sep = ''
    quot=[]
    group=[]
    is_group=0
    tokens = re.split('(=|\'|"|,|\(|\)|\s+)', text)
    for pos in range(len(tokens)):
        if max_col_id != -1 and col_id >= max_col_id: break
        token = tokens[pos]
        if token=='': continue
        if sep:
            if token==sep and not __slash_occured__(tokens[pos-1]):
                sep=''
                token = ''.join(quot)
                quot=[]
                if is_group:
                    group.append(token)
                else:
                    if not key:
                        if cols:
                            key = cols[col_id]
                        else:
                            key = col_id
                        col_id+=1
                    if cols == None or key in cols:
                        if type(dct.get(key,None)) == list:
                            dct[key].append(token)
                        else:
                            dct[key] = token
                    else:
                        errors.append("%s: '%s'."%(_T('Unknown parameter name'),key))
                    key = ''
            else:
                quot.append(token)
        else:
            if token in '\'"':
                sep = token
            elif token[0] == '-':
                m = patt_key.match(token)
                if m: key = m.group(1)
            elif token in '=,' and pos:
                pass
            elif token == '(':
                is_group = 1
            elif token == ')':
                is_group = 0
                if not key:
                    if cols:
                        key = cols[col_id]
                    else:
                        key = col_id
                    col_id+=1
                if group:
                    if cols == None or key in cols:
                        if type(dct.get(key,None)) == list:
                            dct[key].append(token)
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
                else:
                    if not key:
                        if cols:
                            key = cols[col_id]
                        else:
                            key = col_id
                        col_id+=1
                    if cols == None or key in cols:
                        if type(dct.get(key,None)) == list:
                            dct[key].append(token)
                        else:
                            dct[key] = token
                    else:
                        errors.append("%s: '%s'."%(_T('Unknown parameter name'),key))
                    key = ''
    return errors


if __name__ == '__main__':
    text=""" =       
    value1,value2, "value-3 (with) space" 'other4 "value" = with\\\\\\' space' =
    --10 = out-of-order-data (value5) ("more, 6-A (than), 'some' one", second-6-B, "third, '6-B' \\"buzz\\" value")
    "last7 \\"buzz\\" END." 'eight is overwritten' --8 = "out of order: 8" 'nine-9, is "end" of dict.'
    --6="this is outside!"
    --5 "this is outside too and it'll be palced in 5. item."
"""
    cols = ['%d'%c for c in range(1,12)]

    cols = 'command nsset password ns addr'.split(' ')
    text = 'create_nsset pokus heslo (ns1.bazmek.net (194.23.54.1 194.23.54.2) ns2.bazmek.net 194.23.54.1)'

    dct = {}
    for key in cols:
        dct[key]=''
    print text
    print '-'*60
    print cols
    print dct
    print '-'*60
    errors = fill_dict(dct, cols, text)
    for k in dct.keys():
        print "[%s] '%s'"%(k,str(dct[k]))
    print "ERRORS:",errors
