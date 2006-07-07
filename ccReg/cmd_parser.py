# -*- coding: utf8 -*-
#!/usr/bin/env python
import re
from gettext import gettext as _T

UNFINITE = None
MOD_NORMAL, MOD_LIST, MOD_LIST_AGAIN, MOD_CHILD, MOD_CHILD_LIST, MOD_INSIDE_LIST = range(6)

_patt_not_slash = re.compile(r'(\\+)$')
_patt_key = re.compile('-+(.+)')
_patt_name_pos = re.compile(r'(\w+)\[([^\]]+)\]')
_patt_blank = re.compile('\s',re.S)

def __slash_occured__(text):
    ret=0
    m = _patt_not_slash.search(text)
    if m:
        ret = len(m.group(1))%2
    return ret

def __next_key__(cols,current):
    'Step on the next key in column list.'
    if current[-1]+1 < len(cols):
        # jen v případě, že to není kone pole
        current[-1] += 1 # next name

def __add_token__(dct,key,token):
    'Append and returns token.'
    if dct.has_key(key):
        dct[key].append(token)
    else:
        dct[key] = [token]
    return dct[key][-1]

def __append_token__(dct,cols,current,mode,token):
    'Append token on the column names list position.'
    __add_token__(dct, cols[current[-1]][0], token)
    if mode[-1] not in (MOD_LIST, MOD_LIST_AGAIN):
        __next_key__(cols,current) # print error

def __append_mode_list__(mode):
    'Protection against of the multiple brackets.'
    mode.append((MOD_LIST,MOD_LIST_AGAIN)[mode[-1] == MOD_LIST])

def __new_scope__(col_scope, dct_scope, cols, cr, current, dct):
    'Set new scope of the column names and dictionary values. Returns new cols and dict scope.'
    column_name = cols[cr][0]
    __add_token__(dct, column_name, {})
    dct_scope.append(dct)
    dct = dct[column_name][-1]
    col_scope.append(cols)
    cols = cols[cr][4] # childs
    current.append(0)
    return cols,dct

#------------------------------------------
# Insert value by key name: --key.name[1].param = value
# main fnc: insert_on_key()
#------------------------------------------
def __get_name_pos__(errors,key,name,cols):
    'Parse index from key (for example: anykey[index]).'
    pos = 0
    m = _patt_name_pos.match(name) # format: name[pos]
    if m:
        name = m.group(1)
        try:
            pos = int(m.group(2))
        except ValueError:
            errors.append("%s: '%s' [%s]."%(_T('Invalid parameter index'),key,m.group(2)))
            pos = None
    children=None
    for row in cols:
        if row[0] == name:
            children = row[4] # children
            break
    if children is None:
        errors.append("%s: '%s' (%s)."%(_T('Unknown parameter name'),key,name))
        name = ''
    return name,pos,children

def __insert_on_pos__(dct, name, value, pos, empty_only):
    'Insert value into dict at name and position.'
    if not dct.has_key(name): dct[name] = ['']
    while pos >= len(dct[name]):
        dct[name].append('')
    if empty_only:
        if dct[name][pos] == '':
            dct[name][pos] = value # set if only empy value
    else:
        dct[name][pos] = value

def __get_on_pos__(dct,name,pos):
    'Get dict on the defined position.'
    if not dct.has_key(name): dct[name] = [{}]
    while pos >= len(dct[name]):
        dct[name].append({})
    return dct[name][-1]

def __insert_on_key__(errors, dct_root, cols, key, value, empty_only=0):
    """Insert value into dict parsing key into dict scopes.
    errors (OUT) out error messages unknown parameter name
    dct (OUT) dict where value is put
    cols (IN) struct of columns
    key (IN) compounded name of dict keys
    value (IN) value what is put inside dict
    """
    scopes = key.split('.')
    dct = dct_root
    for name in scopes[:-1]:
        name,pos,cols = __get_name_pos__(errors,key,name,cols)
        if not name: return
        dct = __get_on_pos__(dct,name,pos)
    name = scopes[-1]
    name,pos,cols = __get_name_pos__(errors,key,name,cols)
    if name:
        __insert_on_pos__(dct,name,value,pos,empty_only)
#------------------------------------------


def parse(dct_root, cols_root, text_line):
    """Parse values from text and put them into dict.
    text is in format:
    
    value "value with space" 'other value with space'
    -key = value ("more than one", "second value")
    """
    errors=[]
    explicit_key = sep = ''
    quot=[]
    dct = dct_root
    dct_scope = []
    col_scope = []
    cols = cols_root
    current = [0]
    mode = [MOD_NORMAL]
    #
    tokens = re.split('(=|\'|"|,|\(|\)|\s+)', text_line)
    for pos in range(len(tokens)):
        token = tokens[pos]
        if token=='': continue
        if not len(mode):
            errors.append(_T('Invalid bracket definition (mode).'))
            break
        if sep:
            # part string token
            if token==sep and not __slash_occured__(tokens[pos-1]):
                sep=''
                token = ''.join(quot)
                quot=[]
                if explicit_key:
                    # uložení na pozici klíče
                    __insert_on_key__(errors,dct,cols_root,explicit_key,token)
                else:
                    __append_token__(dct,cols,current,mode,token)
                    explicit_key = ''
            else:
                quot.append(token)
        else:
            # part single token
            if token in '\'"':
                sep = token
            elif token[0] == '-':
                m = _patt_key.match(token)
                if m: explicit_key = m.group(1)
            elif token in '=,' and pos:
                pass
            elif token == '(':
                # Bracket can be a three modes:
                # 1. list of values
                # 2. new scope - subset of the column names
                # 3. list of subsets of the column names
                if explicit_key:
                    # On explicit key definition is allowed only simple LIST.
                    __append_mode_list__(mode)
                    continue
                cr = current[-1]
                if mode[-1] == MOD_CHILD_LIST:
                    mode.append(MOD_INSIDE_LIST)
                    cols,dct = __new_scope__(col_scope, dct_scope, cols, cr, current, dct)
                    if not len(cols):
                        errors.append(_T('Invalid bracket definition (list).'))
                        break
                    continue
                if cols[cr][4]: # childs
                    max = cols[cr][1][1]
                    if max > 1:
                        # 3. list of subsets of the column names
                        mode.append(MOD_CHILD_LIST)
                    else:
                        # 2. new scope - subset of the column names
                        mode.append(MOD_CHILD)
                        cols,dct = __new_scope__(col_scope, dct_scope, cols, cr, current, dct)
                        if not len(cols):
                            errors.append(_T('Invalid bracket definition (childs).'))
                            break
                else:
                    __append_mode_list__(mode) # 1. list of values
                
            elif token == ')':
                btype = mode.pop()
                if btype == MOD_INSIDE_LIST:
                    # end of the group values
                    cols = col_scope.pop()
                    dct = dct_scope.pop()
                    current.pop()
                    continue
                elif btype == MOD_CHILD:
                    cols = col_scope.pop()
                    dct = dct_scope.pop()
                    current.pop()
                if btype != MOD_LIST_AGAIN:
                    __next_key__(cols,current)

            elif _patt_blank.match(token):
                pass # ommit blanks
            else:
                if token[-1]==',': token = token[:-1]
                if explicit_key:
                    # save value into position
                    __insert_on_key__(errors,dct,cols_root,explicit_key,token)
                else:
                    __append_token__(dct,cols,current,mode,token)
                explicit_key = ''
    return errors

#----------------------------------
# TEST ONLY:
#----------------------------------
def __debug_dict__(dct,deep=0):
    'For test only.'
    indent = '\t'*deep
    for key in dct.keys():
        print '%s%s: ['%(indent,key),
        dct_item = None
        for pos in range(len(dct[key])):
            if pos: print ',',
            dct_item = dct[key][pos]
            if type(dct_item) == dict:
                __debug_dict__(dct_item,deep+1)
            else:
                print dct_item,
        if dct_item and type(dct_item) == dict:
            print '%s]'%indent
        else:
            print ']'
    
def test():
    'For test only.'
    cols = (
        ('command-name',(1,1),(),'help',()),
        ('id',(1,1),(),'help',()),
        ('add',(0,1),(),'help',(
            ('ns',(0,9),(),'help',(
                ('name',(1,1),(),'help',()),
                ('addr',(0,9),(),'help',()),
            )),
            ('tech',(0,UNFINITE),(),'help',()),
            ('status',(0,6),('ok','linked','req'),'help',()),
        )),
        ('rem',(0,1),(),'help',(
            ('name',(0,9),(),'help',()),
            ('tech',(0,UNFINITE),(),'help',()),
            ('status',(0,6),('ok','linked','req'),'help',()),
        )),
        ('pw',(0,1),(),'help',()),
        )
    
    commands = (
    'create_nsset TEST-ID',
    "create_nsset TEST-ID --pw=my-password",
    "create_nsset TEST-ID --add.ns.name=add.domain.cz",
    "create_nsset TEST-ID --add.ns.name=add0.domain.cz --add.ns[2].name=add2.domain.cz",
    'create_nsset TEST-ID () () my-password',
    'create_nsset TEST-ID1 (((add1.domain.cz 127.0.0.1) (add2.domain.cz (127.2.0.1 127.2.0.2))) "my add tech" add-status) (re.name.cz (rem-technik1, rem-technik2, rem-technik3) rem-status) password',
    """create_nsset TEST-ID 
        (
        ((ns1.domain.net 194.23.54.1),(ns2.domain.net (194.23.54.1,194.23.54.2))), technic, linked
        ) 
        (
            ns1-rem.nic.cz
            (tech-rem1, tech-rem2, tech-rem3)
            ok
        )
        password""",
    )
    for command_line in commands:
        print '='*60
        print command_line
        print '-'*60
        dct_root = {}
        errors = parse(dct_root, cols, command_line)
        print "ERRORS:",errors
        print 'RESULT:'
        __debug_dict__(dct_root)

if __name__ == '__main__':
    test()
