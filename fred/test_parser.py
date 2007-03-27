#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cmd_parser

##dct_root =  {'command': [u'update_nsset']}
##cols_root = [(u'update_nsset', (1, 1), (), '', ()), ('id', (1, 1), (), 'nsset ID', ()), ('add', (0, 1), (), '\xc4\x8d\xc3\xa1st add', (('dns', (0, 9), (), 'seznam DNS', (('name', (1, 1), (), 'jm\xc3\xa9no nssetu', ()), ('addr', (0, None), (), 'IP adresa', ()))), ('tech', (0, None), (), 'technick\xc3\xbd kontakt', ()), ('status', (0, 6), ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok'), 'status', ()))), ('rem', (0, 1), (), '\xc4\x8d\xc3\xa1st remove', (('name', (0, 9), (), 'jm\xc3\xa9no', ()), ('tech', (0, None), (), 'technick\xc3\xbd kontakt', ()), ('status', (0, 6), ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok'), 'status', ()))), ('chg', (0, 1), (), '\xc4\x8d\xc3\xa1st change', (('pw', (0, 1), (), 'heslo', ()),))]
##text_line = 'update_nsset test02 --add.dns.addr (217.31.206.130, 217.31.206.129) --add.dns.name ns8.domain.cz'
##text_line = 'update_nsset test02 --add.dns.name ns8.domain.cz --add.dns.addr (217.31.206.130, 217.31.206.129) '
##text_line = 'update_nsset test02 --add.dns.addr (217.31.206.130, 217.31.206.129)'
##text_line = 'update_nsset test02 --add.dns.addr 217.31.206.130 --add.dns.addr[1] 217.31.206.129'

##dct_root = {'command': [u'create_contact']}
##cols_root = [(u'create_contact', (1, 1), (), '', ()), ('contact_id', (1, 1), (), 'va\xc5\xa1e kontaktn\xc3\xad ID', ()), ('name', (1, 1), (), 'va\xc5\xa1e jm\xc3\xa9no', ()), ('email', (1, 1), (), 'v\xc3\xa1\xc5\xa1 email', ()), ('city', (1, 1), (), 'm\xc4\x9bsto', ()), ('cc', (1, 1), (), 'k\xc3\xb3d zem\xc4\x9b', ()), ('org', (0, 1), (), 'n\xc3\xa1zev organizace', ()), ('street', (0, 3), (), 'ulice', ()), ('sp', (0, 1), (), '\xc4\x8d.p.', ()), ('pc', (0, 1), (), 'PS\xc4\x8c', ()), ('voice', (0, 1), (), 'telefon', ()), ('fax', (0, 1), (), 'fax', ()), ('disclose_flag', (0, 1), ('y', 'n'), 'p\xc5\x99ep\xc3\xadna\xc4\x8d zve\xc5\x99ejnit (default y)', ()), ('disclose', (0, 6), ('name', 'org', 'addr', 'voice', 'fax', 'email'), 'nezve\xc5\x99ej\xc5\x88ovat', ()), ('vat', (0, 1), (), 'DPH', ()), ('ssn', (0, 1), (), 'SSN', ()), ('notify_email', (0, 1), (), 'ozn\xc3\xa1men\xc3\xad na email', ())]
##text_line = 'create-contact regid --street (jedna dve tri) name mail city CZ'
##text_line = 'create-contact regid --street (    ) name mail city CZ'
##text_line = 'create-contact regid --street (jedna) name mail city CZ'
##text_line = 'create-contact regid --street (jedna dve tri) name mail city CZ'
##text_line = 'create-contact regid --street ("jedna safra" "dve cosi" "tri ano") name mail city CZ'
##text_line = 'create-contact regid --street[1] (jedna dve tri) name mail city CZ'
##text_line = 'create-contact regid --street ((jedna (dve tri) name mail city CZ'
##text_line = 'create-contact regid --street (jedna dve (hokus pokus) tri) name mail city CZ'

dct_root = {'command': [u'update_contact']}
cols_root =  [(u'update_contact', (1, 1), (), '', ()), ('contact_id', (1, 1), (), 'va\xc5\xa1e kontaktn\xc3\xad ID', ()), ('add', (0, 5), ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok'), 'add status', ()), ('rem', (0, 5), ('clientDeleteProhibited', 'clientTransferProhibited', 'clientUpdateProhibited', 'linked', 'ok'), 'remove status', ()), ('chg', (0, 1), (), 'change status', (('postal_info', (0, 1), (), 'po\xc5\xa1tovn\xc3\xad informace', (('name', (0, 1), (), 'jm\xc3\xa9no', ()), ('org', (0, 1), (), 'n\xc3\xa1zev organizace', ()), ('addr', (0, 1), (), 'adresa', (('street', (0, 3), (), 'ulice', ()), ('city', (1, 1), (), 'm\xc4\x9bsto', ()), ('sp', (0, 1), (), '\xc4\x8d.p.', ()), ('pc', (0, 1), (), 'pc', ()), ('cc', (1, 1), (), 'cc', ()))))), ('voice', (0, 1), (), 'telefon', ()), ('fax', (0, 1), (), 'fax', ()), ('email', (0, 1), (), 'v\xc3\xa1\xc5\xa1 email', ()), ('disclose_flag', (0, 1), ('y', 'n'), 'p\xc5\x99ep\xc3\xadna\xc4\x8d zve\xc5\x99ejnit (default y)', ()), ('disclose', (0, 6), ('name', 'org', 'addr', 'voice', 'fax', 'email'), 'Zve\xc5\x99ejnit \xc3\xbadaje', ()), ('vat', (0, 1), (), 'DPH', ()), ('ssn', (0, 1), (), 'SSN', ()), ('notify_email', (0, 1), (), 'ozn\xc3\xa1men\xc3\xad na email', ())))]
text_line = "update_contact myid '' '' (('' '' ((jedna, dve, tri) mesto '' '' CZ)))"

print "="*60
print "parse(dct_root, cols_root, text_line)"
print "text_line:",text_line

errors = cmd_parser.parse(dct_root, cols_root, text_line)
print "errors:",errors
print "dct_root:",dct_root
