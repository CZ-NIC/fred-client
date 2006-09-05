#! /usr/bin/env python

import sys
# insert path to directory with ccReg module
sys.path.insert(0, '../')
import os
import time
import math
import string
import dialog
import threading
import Queue
import random
import ccReg
from ccReg.translate import _T, options, option_errors, option_args

threads = 4
targets = 1000
prefix = 'exhaa'
gepp = ccReg.ClientSession() # global epp for preloading of XML
contact_list_xml = []
contact_list_id = []
contact_create_command = 'create_contact cid:%s%s MyName email@email.cz Mesto CZ heslo'
nsset_list_xml = []
nsset_list_id = []
nsset_create_command = 'create_nsset nssid:%s%s passw ((ns1.domain.cz (217.31.207.130 217.31.207.129)) (%s))'
domain_list_xml = []
domain_list_id = []
domain_create_command = 'create_domain %s-%s.cz pw %s %s' # prefix, num, cid, nssid
list_id =  {'domain': domain_list_id, 'nsset': nsset_list_id, 'contact': contact_list_id}
list_xml = {'domain': domain_list_xml, 'nsset': nsset_list_xml, 'contact': contact_list_xml}
list_times = {'domain': None, 'nsset': None, 'contact': None}
workers = []
queue = Queue.Queue()

def intro(d):
    msg = """\

Program nejdrive pred kazdym testem predgeneruje sadu XML dokumentu,
ktere pak odesle na server. Meri se cas samotneho prenosu mezi
klientem a serverem, cas potrebny k vygenerovani XML dokumentu se 
do vysledku nezapocitava.

Vychozi pocet pozadavku pro kazdy typ dotazu: %d
""" % (targets)
#    d.msgbox(msg, height=15, width=75, title="System pro testovani vykonu systemu ccReg")

def outro(d):
    global list_times
    msg = """\
Vygenerovani kontaktu trvalo: %(contact)s sekund
Vygenerovani nssetu trvalo: %(nsset)s sekund
Vygenerovani domen trvalo: %(domain)s sekund

""" % (list_times)
    d.msgbox(msg, height=15, width=75, title="System pro testovani vykonu systemu ccReg")

def create_contacts(d, num):
    d.gauge_start("Progress: 0%", title="Generuji XML pro kontakty")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_list_xml.append(gepp.create_eppdoc(contact_create_command % (prefix, i))[1])
	contact_list_id.append('cid:%s%s' % (prefix, i))
	d.gauge_update(n, "Progress: %d" % i, update_text=1)
    d.gauge_stop()

def create_nssets(d, num):
    d.gauge_start("Progress: 0%", title="Generuji XML pro NSSETy")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_id = random.choice(contact_list_id)
	nsset_list_xml.append(gepp.create_eppdoc(nsset_create_command % (prefix, i, contact_id))[1])
	nsset_list_id.append('nssid:%s%s' % (prefix, i))
	d.gauge_update(n, "Progress: %d" % i, update_text=1)
    d.gauge_stop()

def create_domains(d, num):
    d.gauge_start("Progress: 0%", title="Generuji XML pro domeny")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_id = random.choice(contact_list_id)
	nsset_id = random.choice(nsset_list_id)
	domain_list_xml.append(gepp.create_eppdoc(domain_create_command % (prefix, i, contact_id, nsset_id))[1])
	domain_list_id.append('%s-%s' % (prefix, i))
	d.gauge_update(n, "Progress: %d" % i, update_text=1)
    d.gauge_stop()

def worker(epp, xmllist):
    for item in xmllist:
#	epp.send(item)
#	queue.put_nowait(epp.receive())
	time.sleep(random.random()/10)
	queue.put_nowait(item)

def create_workers(objtype):
    global workers
    workers = []
    xml = list_xml[objtype]
    for x in range(threads):
	epp = ccReg.ClientSession()
	epp.load_config(options['session'])
	epp.api_command('login', {'username': ['REG-LRR'], 'password': ['123456789']})
	partlist = []
	for i in range(targets/threads):
	    partlist.append(xml.pop(xml.index(random.choice(xml))))
	t = threading.Thread(target=worker, args=(epp, partlist))
	t.setDaemon(1)
	workers.append(t)

def controller(d, objtype, msg):
    global workers, list_times
    starttime = time.time()
    d.gauge_start("Progress: 0%", title=msg)
    [ x.start() for x in workers ]
    for i in range(1, targets+1):
	n = math.ceil(i*100/targets)
	item = queue.get(True)
	d.gauge_update(n, "Progress: %d" % i, update_text=1)
    endtime = time.time()
    list_times[objtype] = endtime-starttime
    d.gauge_stop()


def main():
    d = dialog.Dialog(dialog="dialog")
    d.add_persistent_args(["--backtitle", "Testovani vykonu systemu ccReg"])

    intro(d)
    
    create_contacts(d, targets)
#    open('_contact.xml', 'w').write('\n'.join(contact_list_xml))
    create_workers('contact')
    controller(d, 'contact', 'Vytvarim kontakty')
#    sys.exit(0)

    create_nssets(d, targets)
#    open('_nsset.xml', 'w').write('\n'.join(nsset_list_xml))
    create_workers('nsset')
    controller(d, 'nsset', 'Vytvarim NSSETy')

    create_domains(d, targets)
#    open('_domain.xml', 'w').write('\n'.join(domain_list_xml))
    create_workers('domain')
    controller(d, 'domain', 'Vytvarim domeny')

    outro(d)

if __name__ == "__main__": main()
