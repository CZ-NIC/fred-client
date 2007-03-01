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
import re
from translate import encoding
"""This module provides parsing function parse() thats was written specialy
for parsing parameters on the EPP console command line. Parser recognize
tokens as a simple value, string with spaces and list of values.

For running parser needs column names and command line buffer.
Parser returns dictionary with names of columns as a dictionary keys and values
fetch out from command line. All values are put in list for unifique reading of the
results.
"""
UNFINITE = None
MOD_NORMAL, MOD_LIST, MOD_LIST_AGAIN, MOD_CHILD, MOD_CHILD_LIST, MOD_INSIDE_LIST = range(6)

# STUCT COLUMNS:
COL_NAME,COL_MINMAX,COL_ALLOWED,COL_HELP,COL_EXAMPLE,COL_PATTERN,COL_CHILDS = range(7)

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
        # in case only if it is not the end of the list
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
    __add_token__(dct, cols[current[-1]][COL_NAME], token)
    if mode[-1] not in (MOD_LIST, MOD_LIST_AGAIN):
        __next_key__(cols,current) # print error

def __append_mode_list__(mode):
    'Protection against of the multiple brackets.'
    mode.append((MOD_LIST,MOD_LIST_AGAIN)[mode[-1] == MOD_LIST])

def __new_scope__(col_scope, dct_scope, cols, cr, current, dct):
    'Set new scope of the column names and dictionary values. Returns new cols and dict scope.'
    column_name = cols[cr][COL_NAME]
    __add_token__(dct, column_name, {})
    dct_scope.append(dct)
    dct = dct[column_name][-1]
    col_scope.append(cols)
    cols = cols[cr][COL_CHILDS] # childs
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
            errors.append("%s: '%s' [%s]."%(_T('Invalid parameter index'),key.encode(encoding),m.group(2).encode(encoding)))
            pos = None
    children=None
    for row in cols:
        if row[0] == name:
            children = row[COL_CHILDS] # children
            break
    if children is None:
        errors.append("%s: '%s' (%s)."%(_T('Unknown parameter name'),key.encode(encoding),name.encode(encoding)))
        name = ''
    return name,pos,children

def __insert_on_pos__(dct, name, value, pos, empty_only):
    'Insert value into dict at name and position.'
    if not dct.has_key(name): dct[name] = ['']
    while pos >= len(dct[name]):
        dct[name].append('')
    if type(value) is list:
        d = dct[name]
        for itm in value:
            if pos < len(d):
                if empty_only and d[pos] != '':
                    pos+= 1
                    continue
            else:
                d.append('')
            d[pos] = itm
            pos+= 1
    else:
        if not empty_only or (empty_only and dct[name][pos] == ''):
            dct[name][pos] = value

def __get_on_pos__(dct,name,pos):
    'Get dict on the defined position.'
    if not dct.has_key(name): dct[name] = [{}]
    while pos >= len(dct[name]):
        dct[name].append({})
    return dct[name][-1]

def insert_on_key(errors, dct_root, cols, key, value, empty_only=0):
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
        if type(dct) == dict:
            dct = __get_on_pos__(dct,name,pos)
        else:
            # Invalid placed list or parameter name
            errors.append('%s: %s[%d]'%(_T('Misplaced list or key'),name.encode(encoding),pos))
    name = scopes[-1]
    name,pos,cols = __get_name_pos__(errors,key,name,cols)
    if name:
        if type(dct) == dict:
            __insert_on_pos__(dct,name,value,pos,empty_only)
        else:
            errors.append('%s: %s'%(_T('Misplaced list or key'),name.encode(encoding)))
#------------------------------------------


def parse(dct_root, cols_root, text_line):
    """Parse values from text and put them into dict.
    text is in format:
    
    value "value with space" 'other value with space'
    -key = value ("more than one", "second value")
    
    text_line MUST be unicode.
    """
    #print 'dct_root =',dct_root # TEST
    #print 'cols_root =',cols_root # TEST
    #print 'text_line = "%s"'%text_line # TEST
    #print '-'*30 # TEST
    errors=[]
    explicit_key = sep = ''
    quot=[]
    dct = dct_root
    dct_scope = []
    col_scope = []
    cols = cols_root
    current = [0]
    mode = [MOD_NORMAL]
    keyname_token = None # prom list for --key = (value, value)
    #
    tokens = re.split('(=|\'|"|,|\(|\)|\s+)', text_line)
    for pos in range(len(tokens)):
        token = tokens[pos]
        if token=='': continue
        if not len(mode):
            errors.append(_T('Invalid bracket definition (Missing close).'))
            break
        if sep:
            # part string token
            if token==sep and not __slash_occured__(tokens[pos-1]):
                sep=''
                token = ''.join(quot)
                quot=[]
                if explicit_key:
                    if keyname_token is None:
                        # save ont the key position
                        insert_on_key(errors,dct,cols_root,explicit_key,token)
                        explicit_key = ''
                        mode.pop()
                    else:
                        keyname_token.append(token)
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
                if m:
                    explicit_key = m.group(1)
                    mode.append(MOD_NORMAL)
            elif token in '=,' and pos:
                pass
            elif token == '(':
                # Bracket can be a three modes:
                # 1. list of values
                # 2. new scope - subset of the column names
                # 3. list of subsets of the column names
                if explicit_key:
                    # On explicit key definition is allowed only simple LIST.
                    __append_mode_list__(mode) # 1. list of values
                    if keyname_token is None:
                        keyname_token = [] # init
                    else:
                        errors.append(_T('Invalid bracket. Only value or simple list allowed in key definition.'))
                    continue
                cr = current[-1]
                if mode[-1] == MOD_CHILD_LIST:
                    mode.append(MOD_INSIDE_LIST)
                    cols,dct = __new_scope__(col_scope, dct_scope, cols, cr, current, dct)
                    if not len(cols):
                        errors.append(_T('Invalid bracket definition (list).'))
                        break
                    continue
                if cols[cr][COL_CHILDS]: # childs
                    max = cols[cr][COL_MINMAX][1]
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
                if explicit_key:
                    if mode[-1] == MOD_NORMAL:
                        insert_on_key(errors,dct,cols_root,explicit_key,keyname_token)
                        explicit_key = ''
                        mode.pop()
                        keyname_token = None # reset to empty
                    continue
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
                pass # omit blanks
            else:
                if token[-1]==',': token = token[:-1]
                if explicit_key:
                    if keyname_token is None:
                        # save value into position
                        insert_on_key(errors,dct,cols_root,explicit_key,token)
                        explicit_key = ''
                        mode.pop()
                    else:
                        keyname_token.append(token)
                else:
                    __append_token__(dct,cols,current,mode,token)
                    explicit_key = ''
    if len(mode) > 1:
        errors.append(_T('Invalid bracket definition (missing close).'))
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
    
