#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Použití pro převod textu s diakritikou na čisté ASCII.
# Není to zcela dokončeno. 
# NEMÁ být součástí distribuce!!! Je to jen udělátko.
#
import sys
import re
import string

src = u'žščřďťňěáéíýóúůŽŠČŘĎŤŇĚÁÉÍÝÓÚŮ'  # ©„“ (ale nejde to tam dát)
dst =  'zscrdtneaeiyouuZSCRDTNEAEIYOUU'  # c""
enc = 'iso-8859-2'
## u'\u251c' ©
## u'\u201e'„   u'\u201c'“

if len(sys.argv) > 1:
    while 1:
        try:
            body = open(sys.argv[1]).read()
        except IOError, (no, msg):
            print 'Soubor nenalezen. IOError: [Errno %d] %s'%(no, msg)
            break
        encoding=''
        if len(sys.argv) > 2:
            encoding = sys.argv[2]
        else:
            for c in body:
                if c in '\xc4\xc5': ## UTF prefixy
                    encoding = 'utf-8'
                    break
                elif c in '\x8a\x8d\x8e\x9a\x9d\x9e': ## ŠŤŽšťž
                    encoding = 'cp1250'
                    break
                elif c in '\xa9\xab\xae\xb9\xbb\xbe': ## ŠŤŽšťž
                    encoding = 'iso-8859-2'
                    break
                elif c in '\x82\x85\x90\x9b\x9c\x9f\xa0\xa1\xa2\xa3\xa6\xa7\xac\xb5\xb7\xd4\xd5\xd6\xde\xe0\xe5\xe6\xe7\xfc':
                    # éůÉŤťčáíóúŽžČÁĚďŇÍŮÓňŠšŘ
                    encoding = 'cp852'
                    break
            if encoding:
                print u'Rozpoznáno kódování:',encoding
            else:
                print u'Kódování nebylo rozpoznáno. Musí se zadat jako parametr.'
                break
        if not encoding: break
        # odstranění znaků mimo ASCII
        # UnicodeEncodeError: 'charmap' codec can't encode characters in position 30-32: character maps to <undefined>
        body = re.sub(u'©'.encode('utf-8'),'(c)',body)
        body = re.sub(u'[„“]'.encode('utf-8'),'"',body)
        try:
            ubody = body.decode(encoding)
        except LookupError, msg:
            print 'LookupError:',msg
            break
        except UnicodeDecodeError, msg:
            print 'UnicodeDecodeError:',msg
            break
        charset = string.maketrans(src.encode(enc),dst)
        try:
            print ubody.encode(enc).translate(charset)
        except UnicodeEncodeError, msg:
            print 'UnicodeEncodeError:',msg
        break
else:
    print u"""Použití: cs2ascii.py soubor [kódování]

Vytiskne obsah souboru v US-ASCII (odstraní diakritiku).

Parametry:
    [kódování]
    Parametr kódování je nepovinný. Když není zadán, skript se jej pokusí
    zjistit. Pokud se kódování zjistit nepodařilo, musí se zadat.

Přikald použití:
    cs2ascii.py soubor.txt > ascii.txt
    cs2ascii.py soubor.txt cp1250 > ascii.txt
"""

"""Usage: cs2ascii.py file [encoding]

Print text from file as a ASCII.

OPTIONS:
    encoding
    Optional. Script try resolve it. If is not resolved, it MUST be set.

EXAMPLE:
    cs2ascii.py file.txt > ascii.txt
    cs2ascii.py file.txt cp1250 > ascii.txt
"""
