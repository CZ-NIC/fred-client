#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# $Id$
#
# Tento modul slouží k testování chybných EPP dokumentů.
#

def get_test_help():
    return [msg for k,msg in test_cmd.values()]
def get_test_key(cmd):
    key=None
    key_and_message = test_cmd.get(cmd,None)
    if key_and_message:
        key = key_and_message[0]
    return key

test_cmd={
     'err-format':  ('chybny-format',      u'err-format    Nesprávně formátované XML')
    ,'err-encoding':('kodovani-neodpovida',u'err-encoding  Dokument je uložen v jiném kódování, než je definováno v hlavičce.')
    ,'err-unknown': ('nezname-kodovani',   u'err-unknown   V dokumentu je definován neznámý typ kódování.')
    ,'err-entity':  ('neznama-entita',     u'err-entity    V dokumentu se nachází neznámá entita.')
    ,'err-cmd':     ('multi_command',      u'err-cmd       Test na zpracování více příkazů.')
    ,'err-1250':    ('kodovani-cp1250',    u'err-1250      Test na jiný typ kódování.')
    ,'ex-filename': ('odeslání souboru',    u'ex-[filename] Odeslání souboru z adresáře examples. Např: vzor-login.xml')
}

