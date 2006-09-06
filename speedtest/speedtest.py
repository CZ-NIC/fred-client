#! /usr/bin/env python

##
## Podstatne nastaveni:
## * login je ze sekce [connect] v ~/.ccreg_client.conf
## * targets: pocet vygenerovanych zaznamu od kazdeho typu
## * threads: pocet spoustenych vlaken
## 
## Poznamky:
## 1) targets/threads musi byt delitelne beze zbytku
##         (napr. targets 6000, threads [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, ...]
## 2) minimalne na curlewu nema pocet threadu rozhodujici vliv
##         (curlew prumerne ~28 requestu za sekundu pri
##          rozsahu 2-20 threadu)
## 3) pocet 'targets' by nemel (nesmi :)) byt vetsi nez 999999
##         (formatuju totiz cisla na max 6 mist)
## 4) cim vetsi "targets", tim vetsi pametova narocnost, protoze
##    se vsechny XML dokumenty pro kazdy test drzi v RAM
##         (pro 1000 objektu to dela zhruba 173MB obsazene virt.memory)
## 5) cim vic threadu, tim vetsi "odmlka" mezi vygenerovanim
##    dokumentu a zacatkem jejich odesilani na server. pri
##    velkem poctu threadu uz taky nemusi stihat python
## 6) prefix pro kontakty / nssety / kontakty se generuje nahodne
##         (4 znaky, je pri behu zobrazen v zahlavi obrazovky)
## 7) na stroji kde to ma bezet musi byt nainstalovan 'dialog'
## 8) nikde, opravdu NIKDE se neodchytavaji zadne vyjimky
##         (proto radsi dukladne otestovat pred verejnou ukazkou :))
##
## K pocitani casu threadu:
## Nevim jak na ostre DB, ale proti curlewu mi vzdy casy sedely
## pro porovnani jsem pouzival nasledujici SQL dotazy
## pri prefixu napr.: 'LQMS'
## cas vytvoreni vsech kontaktu:
## select date_part('epoch',max(crdate))-date_part('epoch',min(crdate)) as delta from contact where handle like '%LQMS%';
##
## cas vytvoreni vsech nssetu:
## select date_part('epoch',max(crdate))-date_part('epoch',min(crdate)) as delta from nsset where handle like '%LQMS%';
##
## cas vytvoreni vsech domen: (nutno prevest prefix na mala pismena)
## select date_part('epoch',max(crdate))-date_part('epoch',min(crdate)) as delta from domain where fqdn like '%lqms%';
##
## Pokud to na ostre bude davat jine casy, tak pak by zbyvalo opravdu
## jen testovat prvni a posledni domenu ze seznamu a udelat rozdil mezi
## jejich casy. Pocitani casu je nyni ve funkci 'controller', ktera meri
## cas zaplneni fronty odpovidajicim poctem (= targets) odpovedi z epp
## objektu.
## 

import sys

## ----------- Settings --------------------------------------------

# Cesta k adresari s ccReg modulem
sys.path.insert(0, '../')

# Pocet vlaken
threads = 10
# Pocet objektu k vytvoreni
targets = 1000
# Smazat objekty? # True / False, 0 / 1, 'cokoliv' / None
delete_after_run = False

## ----------- SHOCK HAZARD ----------------------------------------
## ----------- NO USER SERVICEABLE PARTS INSIDE --------------------
## ----------- DO NOT EDIT AFTER THIS LINE -------------------------

## ... you have been warned ;-)

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

prefix = ''.join([ random.choice(string.ascii_lowercase) for i in range(4) ])
gepp = ccReg.ClientSession() # global epp for preloading of XML
contact_list_xml = []
contact_delete_list_xml = []
contact_list_id = []
contact_create_command = 'create_contact cid:%s%06d MyName email@email.cz Mesto CZ heslo'
contact_delete_command = 'delete_contact %s'
nsset_list_xml = []
nsset_delete_list_xml = []
nsset_list_id = []
nsset_create_command = 'create_nsset nssid:%s%06d passw ((ns1.domain.cz (217.31.207.130 217.31.207.129))) (%s)'
nsset_delete_command = 'delete_nsset %s'
domain_list_xml = []
domain_delete_list_xml = []
domain_list_id = []
domain_create_command = 'create_domain %s-%06d.cz pw %s %s' # prefix, num, cid, nssid
domain_delete_command = 'delete_domain %s'
list_id =  {'domain': domain_list_id, 'nsset': nsset_list_id, 'contact': contact_list_id}

list_xml = {	'domain': domain_list_xml,
		'domain_delete': domain_delete_list_xml,
		'nsset': nsset_list_xml, 
		'nsset_delete': nsset_delete_list_xml,
		'contact': contact_list_xml,
		'contact_delete': contact_delete_list_xml,
}

list_times = {	'domain': 0,
		'domain4sec': 0,
		'domain_delete': 0,
		'domain_delete4sec': 0,
		'nsset': 0,
		'nsset4sec': 0,
		'nsset_delete': 0,
		'nsset_delete4sec': 0,
		'contact': 0,
		'contact4sec': 0,
		'contact_delete': 0,
		'contact_delete4sec': 0,
		'average': 0,
}

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
    d.msgbox(msg, height=15, width=75, title=" System pro testovani vykonu systemu ccReg ")

def outro(d):
    global list_times
    msg = """\

Vygenerovani kontaktu trvalo: %(contact).2f sekund 
                             (%(contact4sec).2f za sekundu)
Vygenerovani nssetu trvalo: %(nsset).2f sekund 
                           (%(nsset4sec).2f za sekundu)
Vygenerovani domen trvalo: %(domain).2f sekund 
                          (%(domain4sec).2f za sekundu)

Smazani kontaktu trvalo: %(contact_delete).2f sekund 
                        (%(contact_delete4sec).2f za sekundu)
Smazani nssetu trvalo: %(nsset_delete).2f sekund 
                      (%(nsset_delete4sec).2f za sekundu)
Smazani domen trvalo: %(domain_delete).2f sekund 
                     (%(domain_delete4sec).2f za sekundu)

Prumerny pocet pozadavku za sekundu: %(average).2f

""" % (list_times)
    d.msgbox(msg, height=21, width=55, title=" System pro testovani vykonu systemu ccReg ")

def create_contacts(d, num):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro kontakty ")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_list_xml.append(gepp.create_eppdoc(contact_create_command % (prefix, i))[1])
	contact_list_id.append('cid:%s%06d' % (prefix, i))
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % i, update_text=1)
    d.gauge_stop()

def delete_contacts(d):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro mazani kontaktu ")
    for i in range(len(list_id['contact'])):
	n = math.ceil((i+1)*100/len(list_id['contact']))
	contact_delete_list_xml.append(gepp.create_eppdoc(contact_delete_command % (list_id['contact'][i]))[1])
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % (i+1), update_text=1)
    d.gauge_stop()

def create_nssets(d, num):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro NSSETy ")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_id = random.choice(contact_list_id)
	nsset_list_xml.append(gepp.create_eppdoc(nsset_create_command % (prefix, i, contact_id))[1])
	nsset_list_id.append('nssid:%s%06d' % (prefix, i))
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % i, update_text=1)
    d.gauge_stop()

def delete_nssets(d):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro mazani NSSETu ")
    for i in range(len(list_id['nsset'])):
	n = math.ceil((i+1)*100/len(list_id['nsset']))
	nsset_delete_list_xml.append(gepp.create_eppdoc(nsset_delete_command % (list_id['nsset'][i]))[1])
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % (i+1), update_text=1)
    d.gauge_stop()

def create_domains(d, num):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro domeny ")
    for i in range(1, num+1):
	n = math.ceil(i*100/num)
	contact_id = random.choice(contact_list_id)
	nsset_id = random.choice(nsset_list_id)
	domain_list_xml.append(gepp.create_eppdoc(domain_create_command % (prefix, i, contact_id, nsset_id))[1])
	domain_list_id.append('%s-%06d.cz' % (prefix, i))
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % i, update_text=1)
    d.gauge_stop()

def delete_domains(d):
    d.gauge_start("Pripravuji objekt cislo: 1", title=" Generuji XML pro mazani domen ")
    for i in range(len(list_id['domain'])):
	n = math.ceil((i+1)*100/len(list_id['domain']))
	domain_delete_list_xml.append(gepp.create_eppdoc(domain_delete_command % (list_id['domain'][i]))[1])
	d.gauge_update(n, "Pripravuji objekt cislo: %d" % (i+1), update_text=1)
    d.gauge_stop()

def worker(epp, xmllist):
    for item in xmllist:
	epp.send(item)
	queue.put_nowait(epp.receive())
#	time.sleep(random.random()/10)
#	queue.put_nowait(item)
#	sys.stderr.write("\n%s" % item)

def create_workers(objtype):
    global workers
    workers = []
    xml = list_xml[objtype]
    for x in range(threads):
	epp = ccReg.ClientSession()
	epp.load_config(options['session'])
	epp.api_command('login', epp.get_default_params_from_config('login'))
	partlist = []
	for i in range(targets/threads):
	    partlist.append(xml.pop(xml.index(random.choice(xml))))
	t = threading.Thread(target=worker, args=(epp, partlist))
	workers.append(t)

def controller(d, objtype, msg):
    global workers, list_times
    starttime = time.time()
    d.gauge_start("Odesilam objekt cislo: 1", title=msg)
    [ t.setDaemon(1) for t in workers ]
    [ t.start() for t in workers ]
    for i in range(1, targets+1):
	n = math.ceil(i*100/targets)
	item = queue.get(True)
#	open('_xml_in.log', 'a').write("%s\n" % item)
	d.gauge_update(n, "Odesilam objekt cislo: %d" % i, update_text=1)
    endtime = time.time()
    totaltime = endtime-starttime
    list_times[objtype] = totaltime
    list_times["%s4sec" % (objtype)] = targets/totaltime
    d.gauge_stop()

def main():
    global list_times
    d = dialog.Dialog(dialog="dialog")
    d.add_persistent_args(["--backtitle", "Testovani vykonu systemu ccReg | Prefix: %s | david@nic.cz" % prefix.upper()])

    intro(d)
    
    create_contacts(d, targets)
#    open('_contact.xml', 'w').write('\n'.join(contact_list_xml))
    create_workers('contact')
    controller(d, 'contact', ' Vytvarim kontakty... ')

    create_nssets(d, targets)
#    open('_nsset.xml', 'w').write('\n'.join(nsset_list_xml))
    create_workers('nsset')
    controller(d, 'nsset', ' Vytvarim NSSETy... ')

    create_domains(d, targets)
#    open('_domain.xml', 'w').write('\n'.join(domain_list_xml))
    create_workers('domain')
    controller(d, 'domain', ' Vytvarim domeny... ')

    if delete_after_run:
	delete_domains(d)
	create_workers('domain_delete')
	controller(d, 'domain_delete', ' Mazu domeny... ')

	delete_nssets(d)
	create_workers('nsset_delete')
	controller(d, 'nsset_delete', ' Mazu NSSETy... ')

	delete_contacts(d)
	create_workers('contact_delete')
	controller(d, 'contact_delete', ' Mazu kontakty... ')

    values = [ list_times[z] for z in [ x for x in list_times.keys() if list_times[x] and x.endswith('4sec') ] ]
    list_times['average'] = sum(values)/len(values)

    outro(d)

if __name__ == "__main__": main()
