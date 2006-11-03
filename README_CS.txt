
Manual pro FredClient konzoli a knihovnu fred

Verze 1.2

   Vzniklo: 11. 7.2006; Revize: 18. 8.2006; 1. 9.2006; 4. 9.2006; 14. 9.2006;
   27. 9.2006; 1.11.2006;

   Copyright (c) 2006 CZ.NIC
     _________________________________________________________________

   Obsah

   Co je FredClient:
   1. Licence
   2. Pozadavky na system a instalace
   3. Popis jednotlivych programu, parametry a config 

        Parametry (OPTIONS) 
        Konfiguracni soubor 

   4. Program fred_console.py 

        Zobrazeni helpu
        EPP prikazy
        Typy parameru prikazu
        Spolecny parametr cltrid (Client transaction ID)
        Zadna hodnota / Prazdna hodnota

              Zadna hodnota: NULL
              Prazdna hodnota: '', ""

        Prikazy relace (session)
        Testovaci prikazy

   5. Skripty fred_create.py a fred_sender.py 
   6. Integrace klienta do PHP kodu
   7. Knihovna fred a popis API 

        Online dokumentace:
        Priklady prace s knihovnou

Co je FredClient:

   FredClient je sada scriptu v jazyce Python postavenych na fred knihovne a
   urcenych ke komunikaci s EPP serverem.

   Sada obsahuje EPP konzoli a skripty urcene pro pouziti v shellu.

Kapitola 1. Licence

   Licence je v souboru fred/LICENSE.

Kapitola 2. Pozadavky na system a instalace

   Pokyny k instalaci jsou v souboru INSTALL.

Kapitola 3. Popis jednotlivych programu, parametry a config

   Obsah

   Parametry (OPTIONS) 
   Konfiguracni soubor 

   Dostupne skripty jsou nasledujici:
   fred_client.py - spousti EPP konzoli nebo sekvenci crate+send (pro shell)
   fred_console.py - EPP konzole, komunikuje s EPP serverem
   fred_create.py - Vytbori zdrojovy EPP XML prikaz
   fred_sender.py - Odesle soubor na EPP server

Parametry (OPTIONS)

   Skripty se daji spoustet s parametry. Jake parametry lze pouzit zjistite
   zadanim parametru --help nebo -?:
    $ fred_client.py --help
    $ fred_client.py -?

Pouziti: fred_console [parametry...]

Hlavni parametry:
  -?, --help       Zobrazit tuto napovedu a skoncit
  -V, --version    Zobrazit verzi programu a skoncit
  -l LANGUAGE, --lang=LANGUAGE
                   Nastaveni jazykove verze
  -v LEVEL, --verbose=LEVEL
                   Nastaveni modu vypisu
                   1 - normalni vystup
                   2 - zobrazit vice detailu
                   3 - zobrazit vice detailu a XML zdroje
  -x, --no_validate
                   Deaktivovat XML validaci na strane klienta

Parametry pro spojeni:
  -f CONFIG, --config=CONFIG
                   Nacteni konfigurace ze souboru
  -s SESSION, --session=SESSION
                   Pouzit session z konfiguracniho souboru

  -h HOSTNAME, --host=HOSTNAME
                   Fred server host
  -p PORT, --port=PORT\n"
                   Server port (default: 700)
  -u USERNAME, --user=USERNAME
                   Prihlasit se jako uzivatel
  -w PASSWORD, --password=PASSWORD
                   Prihlasit se s heslem
  -c CERTIFICATE --cert=CERTIFICATE
                   Pro spojeni pouzit SSL certifikat
  -k PRIVATEKEY --privkey=PRIVATEKEY
                   Pro spojeni pouzit SSL privatni klic

  -n, --nologin
                   Deaktivovat automaticke spojeni se serverem po startu
  -d COMMAND, --command=COMMAND
                   Odeslat prikaz na server a skoncit
  -o OUTPUT_TYPE, --output=OUTPUT_TYPE
                   Zobrazit vystup jako text (default), html, php

Konfiguracni soubor

   Konfiguracni soubor se implicitne hleda nejdrive v home uzivatele
   (~/.fred_client.conf), ktery skript spustil. Pokud tam neni nalezen, hleda
   se v adresari etc (/etc/fred_client.conf). Na POSIX systemech je to /etc, v
   MS Windows to je v adresari nastavenem v promenne $ALLUSERSPROFILE.
   Prepinacem --config=filepath (nebo -f filepath) je mozne konfiguracni soubor
   nacist z libovolneho souboru.

   Pro zalozeni noveho konfiguracniho souboru je k dispozici priklad
   config_example.txt. Tento priklad muzete pouzit jako zaklad pro vas
   konfiguracni soubor.

   V konfiguracnim souboru se nachazi sekce connect, kde jsou ulozeny cesty k
   certifikatum a informace o serveru. Take tam jsou dalsi hodnoty napriklad
   username a password. Pokud se tyto hodnoty v konfiguracnim souboru
   nachazeji, tak je prikaz login pouzije jako parametry prikazu, ktere mu
   nebyly zadany.

   Zde je priklad konfigu:
# Example of configuration file.
# Modify line with schema and dir=... set real path of your files.
# and save into /etc/fred_client.conf or ~/.fred_client.conf
#

[connect]
dir=/home/username/certificates
host = epp-test.ccreg.nic.cz
port = 700
ssl_cert = %(dir)s/certificate.pem
ssl_key  = %(dir)s/private_key.pem
username = MYUSERNAME
password = MYPASSWORD
timeout = 10.0      # socket timeout in sec.
# socket = IPv6     # Force socket type. Valid values are: IPv4 and IPv6.
                    # othervice used type from offer of the server
# nologin = y       # turn off automatic login process after start up

[session]
schema = $python-site-packages/fred/schemas/all-1.0.xsd
poll_autoack = off           # send "poll ack" right after to "poll req"
confirm_send_commands = on   # confirm all editable commands
validate = on                # enable/disable xmllint
colors = yes                 # display colors on tty console
verbose = 2                  # set verbose level 1,2,3
# lang = en                  # if lang is not set, ti used value from os.enviro
n.LANG
# null_value = None          # substitution of NULL value
# auto_login = off           # disable automatic login after start client (defa
ult is ON)

   Sekci connect muze byt vice. Ktera z nich se pri startu pouzije se nastavi
   pomoci parametru -s --session. Napriklad si vytvorite sekci
   [connect_myeppserver] tu pak aktivujete:
    $ fred_client.py --session=myeppserver     (nebo -s myeppserver)

    [connect_myeppserver]
    dir=/test/certificates
    host = myeppserver.cz
    ssl_cert = %(dir)s/cert.pem
    ssl_key  = %(dir)s/key.pem
    username = myusername
    password = mypassword

   V sekci session jsou tato nastaveni:
     * poll_ack = on/off
       Pri on se po odeslani prikazu poll req automaticky posle i poll ack.
     * confirm_send_commands = on/off
       Vsechny editacni prikazy (create, delete, update, ...) vyzaduji v
       konzoli pozvrzeni pred odeslanim na server. Tuto funkci lze
       vypnout/zapnout.
     * validate = on/off
       K validaci se pouziva externi program xmllint. Validaci lze vypnout a
       dokumnety se tak na server posilaji bez overeni platnosti formatu.
     * schema = /installdir/schemas/all-1.0.xsd
       Soubor, ve kterem ma validator hledat schemata, podle kterych dokumenty
       overuje.
     * colors = on/off
       Vystup na terminal muze byt barevny, pokud to terminal umoznuje.
     * verbose = 1/2/3
       Uroven vypisu 1 - strucna, 2 - cela, 3 - cela + XML zdrojove dokumenty.
     * lang = en/cs
       Jazykova verze. Pokud neni zadana zadna hodnota, tak se bere nastaveni z
       promenne LANG prostredi OS. Dostupne jsou zatim jen anglictina a
       cestina. Jazykovou verzi muzete take nastavit i pomoci parametru pri
       spusteni skriptu.
     * null_value = NULL
       Nastaveni zastupce pro hodnotu nic (Nil), ktera vyjadruje """zadnou
       hodnotu""". Defaultne je nastaveno NULL. Tuto hodnotu pouzivame, kdyz
       chceme preskocit nektery z parametru prikazu. Zadani NULL znamena, ze
       jsme nezadali zadnou hodnotu na rozdil od '' nebo "", kdy jsme zadali
       hodnotu nulove delky.
       Format hodnoty NULL: Zastupce muze byt libovolny, ale nesmi obsahovat
       spojovnik (-), mezery a kulate zavorky.
       Vice se o teto hodnote dozvite v casti """Zadna hodnota / Prazdna
       hodnota"""

   V sekci connect jsou tato nastaveni:
     * dir = cesta k adresari s certifikaty
       Tato hodnota nahrazuje zastupce %(dir)s ve vsech polozkach dane sekce. V
       nasem pripade je v ni ulozena cesta k certifikatum.
     * ssl_cert = jmeno certifikatu
       Nazev souboru s certifikatem. Pred nim je uveden zastupce adresare dir,
       ktery je nahrazen hodnotou definovanou v teto sekci.
     * ssl_key = jmeno privatniho klice
       Nazev souboru s privatnim klicem. Pred nim je uveden zastupce adresare
       dir, ktery je nahrazen hodnotou definovanou v teto sekci.
     * host = jmeno_serveru
       Nazev serveru, ke kteremu se ma klient pripojit.
     * port = cislo_portu
       Cislo portu serveru. Pokud neni zadan, pouzije se default 700.
     * username = uzivatelske jmeno
       Uzivatelske jmeno potrebne k prihlaseni do systemu.
     * password = heslo
       Heslo potrebne k prihlaseni do systemu.
     * timeout = cas cekani na odpoved ve vterinach
       Nastaveni timeoutu rika socketu jak dlouho ma cekat na odpoved ze
       serveru. Pokud do uvedene doby odpoved neprijde, je spojeni povazovano
       za prerusene. Defaultne je nastaveno 10 vterin. Pozor! V MS Windows se
       muze u timeoutu vyskytnout bug, ktery zpusobi, ze se spojeni nenavaze. V
       takovem pripade nastavte timeout na nulu: timeout = 0
     * socket = IPv4/IPv6
       Nastaveni typu soketu na IPv4 nebo IPv6. Pokud neni tato hodnota zadana,
       tak se pouzije typ soketu, ktery nabizi server.
     * nologin = on/off
       Klient se ihned po spusteni pokusi spojit se serverem a zalogovat se.
       Tuto funkci je mozne vypnout nastavenim nologin = off.

Kapitola 4. Program fred_console.py

   Obsah

   Zobrazeni helpu
   EPP prikazy
   Typy parameru prikazu
   Spolecny parametr cltrid (Client transaction ID)
   Zadna hodnota / Prazdna hodnota

        Zadna hodnota: NULL
        Prazdna hodnota: '', ""

   Prikazy relace (session)
   Testovaci prikazy

   fred_console.py je konzole, ktera komunikuje s EPP serverem. Konzoli
   spustite prikazem:
    $ fred_console.py

   Pokud mate v configu spravne nadefinovanu cestu k certifikatum a ulozene
   login a heslo, tak muzete jednoduse zadat login a tim se spojite s EPP
   serverem. Konzole se ukoncuje prikazem "quit" nebo jen kratce "q".

Zobrazeni helpu

   Jake prikazy mate k dispozici zjistite zadanim prikazu "help" (nebo h, ?).
    FredClient verze 1.0.0 Zadejte "help", "license" nebo "credits" pro zobraze
ni vice informaci.
    > help

   Help vypise dve casti napovedy:
   1) Dostupne EPP prikazy
   2) Prikazy relace (session) pro nastaveni vnitrnich promennych konzole

EPP prikazy

   EPP prikaz zadavate spolecne s jeho parametry. Jake parametry prikaz
   pozaduje zjistite, kdyz zadate "help prikaz" nebo zkracene "h prikaz" nebo
   take "? prikaz".

   Napriklad:
> ?login

   Vypisou se podrobnosti o jednotlivych parametrech daneho prikazu. Samotny
   prikaz zadate tak, ze napisete nazev prikazu a za nim jeho parametry:
> login username password

Typy parameru prikazu

   INSTRUKCE:
   parametry zadavejte v poradi, v jakem jsou vypsane v helpu
   hodnoty s mezerami dejte do uvozovek
   seznamy se definuji pomoci zavorek, polozky seznamu muzou (ale nemusi) byt
   oddeleny carkami
   pokud je v seznamu jen jedna polozka, nemusi se zavorky zadavat
   jmenne prostory se take jako seznamy definuji pomoci zavorek
   chcete-li seznam nebo jmenny porostor vynechat, zadejte jen prazdne zavorky
   Hodnotu, kterou chcete preskocit zadejte jako """zadnou hodnotu""" (Zadna
   hodnota / Prazdna hodnota).
   hodnoty mimo poradi zadavejte pomoci klice

   VYSVETLENI:
   jednoducha hodnota: my-value01
   hodnota s mezerou: 'lorem ipsum' "some value"
   seznam: (one two three)
   jmenny prostor: ((one two three) my-value01 'lorem ipsum' (enyky benyky)
   end-value)

   Pokud hodnota parametru obsahuje mezeru, tak ji napiste do uvozovek.
   Napriklad:
> login username "moje heslo s mezerami"

   Nektere parametry muzou obsahovat seznam hodnot. Napriklad parametr "street"
   v prikazu create_contact. Vypis casti helpu:
    ?create_contact
    ...
    ... street                   Ulice (seznam o maximalne 3 polozkach.)
    ...


   Seznam zadate tak, ze hodnoty uzavrete do zavorek:
> create_contact CID:MYID ... (Vodickova, "Na prikope", "U privozu") ...


   Pokud zadavate jen jednu hodnotu ze seznamu, tak zavorky zadavat nemusite:
    > create_contact CID:MYID ... Vodickova ...


   Parametry musite zadavat v poradi, v jakem jsou v helpu vypsany. Povinne
   jsou vzdy na zacatku a nepovinne tak neni nutne zadavat. Pokud byste krome
   povinnych hodnot chteli zadat i nejakou nepovinnou, tak byste museli nejprve
   zadat vsechny hodnoty predchazejici te, kterou chcete zadat. Pro tento
   pripad umoznuje klient zadat hodnotu pomoci pojmenovaneho parametru - klice.
   Resi se tim tak situace, kdy chcete napriklad zadat jen jeden udaj, ktery je
   jeste k tomu nekde na konci seznamu parametru.

   Klic (jmeno parametru) se definuje pomoci jedne nebo dvou pomlcek, presneji
   receno spojovniku. Napriklad chcete v prikazu create_contact zadat krome
   povinnych udaju uz jen hodnotu notify_email (Oznameni na email), ktera se
   nachazi prave na uplnem konci seznamu parametru. Pak tuto hodnotu zadate
   takto:
  > create_contact CID:ID myname my@mail.com city cc --notify_email = muj@mail.
cz


   Jaky ma byt klic (nazev parametru) zjistite z helpu daneho prikazu. Parametr
   s klicem pak jiz nemusi byt na "sve" pozici, ale muze byt kdekoliv v rade
   mezi ostatnimi parametry. Takovy parametr stoji "mimo" poradi a nenarusuje
   pozice ostatnich parametru bez klice. Zde jsou do rady parametru vlozeny
   hodnoty s klici "vat" a "notify_email":
    > create_contact CID:ID myname my@mail.com --vat = 12346 --notify_email = m
uj@mail.cz city cc


   Nektere prikazy maji parametry vnorene do dalsich parametru. Ty vytvareji
   tak zvane jmenne prostory. Napriklad v prikazu "create_contact" je parametr
   "disclose". Ten obsahuje dalsi parametry "flag", "data". Samotny nazev
   "disclose" neni v tomto pripade nazev klice, ale nazev jmenneho prostoru, ve
   kterem se nachazeji klice "flag" a "data". Jmenne prostory se definuji
   stejne jako seznamy pomoci zavorek:
  > create_contact my-ID my-name mail city cc org street sp pc
        voice fax (n (name org addr voice fax email)) vat ssn


   Pokud jmenny prostor nechcete zadavat, napiste proste jen prazdne zavorky.
   To plati i pro seznamy:
  > create_contact CID:ID myname my@mail.com City CC Organisation Street SP PC
Voice Fax () Vat Ssn notify@email.com


   Nektere prikazy maji v parametrech seznamy jmennych prostoru. V takovem
   pripade pak zavorky maji sve vyznamy podle toho, jak jsou hodnoty seskupeny.
   Napriklad prikaz "update_nsset" ma jeden nepovinny parametr "add" (Pridat
   hodnoty). Pokud jej nechcete zadavat, tak napisete:
  > update_nsset id () ...    - parametr add je nyni prazdny


   Pokud ale "add" zadat chcete, tak "add" (jak vidite v helpu) obsahuje seznam
   deviti jmennych prostoru "dns"! Kazdy "dns" prostor pak dale obsahuje
   parametr "name" a seznam "addr". Pokud chete tyto hodnoty zadat, tak musite
   zapsat vsechny zavorky, ktere jsou nutne: Prvni zavorka pro definovani
   jmenneho prostoru "add". Druha zavorka pro zacatek seznamu jmennych
   prostoru "dns". Treti zavorka pro samotny jmenny prostor "dns". Teprve pak
   nasleduje hodnota parametru "name". Za nim pak nasleduje zavorka seznamu
   "addr":
  >  update_nsset NSSID:nsset1 (((ns1.dns.cz (217.31.207.130, 217.31.207.131, 2
17.31.207.132)),
        (ns2.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132))) (tech1,
tech2, tech3)
        (ok, clientTransferProhibited)) (((rem1.dns.cz, rem2.dns.cz) (CID:rem01
, CID:rem02)
            serverUpdateProhibited)) (password)


   Pokud "addr" neni seznam, ale jen jedna hodnota, tak se zavorky pro "addr"
   zadavat nemusi: (To je pravidlo jiz zminene v predchozim textu.)
  > update_nsset nsset-ID (((ns1.dns.cz 217.31.207.130),(ns2.dns.cz 217.31.207.
130))
        tech status) ...


   Takto slozite zadavani nastesti existuje jen v malem mnozstvi prikazu a
   tento uvedeny priklad zadani je vubec nejslozitejsi ze vsech. Krome toho
   mate moznost zadavat parametry prikazu v interaktivnim modu. Ten umoznuje
   zadavat parametry postupne - klient vyzve k zadani parametru a uzivatel je
   vyplnuje jeden za druhym. Na konci helpu u kazdeho prikazu je uveden priklad
   zadani vsech parametru.

   Interaktivni mod vkladani parametru se spousti pomoci vykricniku, ktery se
   napise pred prikaz:
> !update_nsset

   Tim spustite rezim interaktivniho vkladani parametru. Konzole vzdy vypise
   jmeno parametru a ceka na zadani hodnoty. Pokud hodnotu nechcete zadat, tak
   proste stisknete enter a hodnota se preskoci. Interaktivni rezim muzete
   kdykoliv zrusit stisknutim klaves Ctrl+C (C jako Cancel). Po zadani vsech
   povinnych parametru, kdy uz nechcete zadavat dalsi nepovinne hodnoty, lze
   interaktivni rezim dokoncit stiknutim klaves Ctrl+D (D jako Done nebo
   Dokoncit). V pripade zruseni interaktivniho modu se zadny prikaz nesestavi a
   nic se na server neposila. V pripade dokonceni modu se sestavi prikaz a na
   konzoli se vypise tak, jako byste jej zadali primo bez interaktivniho
   rezimu. Pak se prikaz odesle na server. V pripade, ze se jedna o
   """editacni""" prikaz a je zapnuta funkce potvrzovani (confirm), tak se prikaz
   musi pred odeslanim na server jeste potvrdit:
REG-LRR@epp-test.ccreg.nic.cz> !update_nsset
Start interaktivniho modu. Mod zrusite stisknutim Ctrl+C. Prikaz dokoncite komb
inaci Ctrl+D.
NSSET ID [povinny]: nssid:id01
Pridat hodnoty / Seznam DNS[1/9] / Jmenny server [povinny jen je-li tato cast z
adana]: ns1.dns.cz
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[1/oo] [nepovinny]: 217.31.207
.130
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[2/oo] [nepovinny]: 217.31.207
.131
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[3/oo] [nepovinny]:
Pridat hodnoty / Seznam DNS[2/9] / Jmenny server [nepovinny]:
Pridat hodnoty / Technicky kontakt ID[1/oo] [nepovinny]: cid:myid01
Pridat hodnoty / Technicky kontakt ID[2/oo] [nepovinny]:
Pridat hodnoty / Stav[1/6] [nepovinny]:
Interaktivni mod ukoncen. [stisknete Enter]
Prikaz k odeslani:
update_nsset nssid:id01 (((ns1.dns.cz (217.31.207.130, 217.31.207.131))) cid:my
id01)
Opravdu chcete odeslat tento porikaz na server? (y/N): y
nssid:id01 aktualizovano.
REG-LRR@epp-test.ccreg.nic.cz>


   Jeste jednou zpet k zadavani pomoci klice: Klic se zadava ve tvaru -[nazev
   parametru] [hodnota]. Napriklad:
     -heslo "toto je moje heslo"

   Toto zadani lze napsat i takto se stejnym ucinkem:
     --heslo = "toto je moje heslo"

   Zalezi na vas, ktery zapis se vam bude zdat citelnejsi. Jak ale zadat
   honodotu, ktera je soucasti jmenneho prostoru? Jednoduse pomoci teckove
   koncence:
    --add.dns.name = nsset_name

   Takto jste definovali hodnotu nsset_name do jmenneho porostoru "add", do
   prvni polozky seznamu "dns", do parametru "name". Chcete-li ulozit hodnotu
   napriklad do treti polozky seznamu "dns", tak zadejte:
    --add.dns[2].name = nsset_name

   Dvojka je index seznamu v tomto pripade o max. deviti polozkach (indexy 0 -
   8).

Spolecny parametr cltrid (Client transaction ID)

   Kazdy EPP prikaz, krome prikazu hello, obsahuje tag <clTRID>. Ten je vzdy
   jako posledni z parametru a jmenuje se cltrid. Tato hodnota je identifikator
   transakce. Ten si stanovuje klient a muze byt libovolny v ramci
   formatovacich pravidel definovanych ve schematech pro tuto hodnotu.
   Identifikator je nepovinny a pokud neni zadan, tak jej klient automaticky
   doplni.

Zadna hodnota / Prazdna hodnota

Zadna hodnota: NULL

   Vyraz Zadna hodnota predstavuje hodnotu, kterou jste nezadali. Slouzi nam k
   tomu, abychom mohli preskakovat parametry, ktere nechceme zadavat. Defaulte
   je vyraz nastaven na NULL.

   Napriklad, kdyz v prikazu create_contact chtece krome povinnych parametru
   uvest uz jen telefonni cislo (parametr voice). Mezi poslednim povinnym
   parametrem pw a poradovanym voice lezi jeste dalsi ctyri parametry: org,
   street, sp, cp. Misto nich zadate "zadnou hodnotu" - pokud jste nenastavili
   jinak, tak NULL. Tim jste telefonni cislo umistili na spravnou pozici v
   parametrech prikazu:
   create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword NULL
NULL NULL NULL +420.222745111

   Uvedeny prikaz nebude v XML strukture vytvaret tagy pro hodnoty org, street,
   sp, cp:
<contact:id>CID:ID01</contact:id>
        <contact:postalInfo>
          <contact:name>Jan Novak</contact:name>
          <contact:addr>
            <contact:city>Praha</contact:city>
            <contact:cc>CZ</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>+420.222745111</contact:voice>

   V interaktivnim modu zadavani parametru zadate """zadnou hodnotu""" proste tak,
   ze jenom stisknete ENTER.

   Definici zadne hodnoty lze v konzoli zmenit prikazem null_value a take je
   mozne si ji definovat v konfiguracnim souboru.

Prazdna hodnota: '', ""

   Vyraz Prazdna hodnota predstavuje hodnotu, ktera je prazdna. Je to tedy text
   o nulove delce. Ten zapisujeme praznymi uvozovkami '' nebo "". Tato hodnota
   nam slouzi k tomu, abychom mohli zadavat hodnoty nulove delky. Rozdil mezi
   praznou hodnotou a zadnou je v tom, ze tato hodnota generuje tag v XML
   dokumentu. Protoze je prazdna, tak dany XML tag bude take prazdny.
   create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword '' ''
 '' '' +420.222745111

   Prikaz vygeneruje XML, ve kterem budou u prazdnych hodnot prazdne tagy:
<contact:id>CID:ID01</contact:id>
        <contact:postalInfo>
          <contact:name>Jan Novak</contact:name>
          <contact:org/>
          <contact:addr>
            <contact:street/>
            <contact:city>Praha</contact:city>
           <contact:sp/>
            <contact:pc/>
            <contact:cc>CZ</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>+420.222745111</contact:voice>

   V interaktivnim modu zadavani parametru zadame """prazdnou hodnotu""" tak, ze
   zapiseme prazdne uvozovky '' nebo "".

Prikazy relace (session)

   Konzole ma sva vnitrni nastaveni, ktera muzete nastavit. Pokud zadate prikaz
   bez parametru, tak se pouze vypise aktualni stav nastaveni.
> ! epp_prikaz

   Timto prikazem se spousti interaktivni mod zadavani parametru. Mod funguje
   jen pro EPP prikazy. Vkladani se ukonci automaticky po zadani vsech
   parametru nebo jej lze ukoncit stisknutim kombinace klaves Ctrl+D (Done)
   nebo zrusit Ctrl+C (Cancel).
> poll_autoack [on/off]

   Pokud je tento prepinac ON, tak se po odeslani prikazu "poll req"
   automaticky odesila i "poll ack". Tuhle funkci asi nejvice ocenite, kdyz
   budete mit na serveru hodne zprav. Prikaz "poll req" zpravu ze serveru pouze
   zobrazi, ale pak se zprava musi ze serveru odstranint prikazem "poll ack
   ID-zpravy". Pri automatickem poll-ack se bude odstranovani provadet
   automaticky po zobrazeni zpravy.
> confirm [on/off]

   U EPP editacnich prikazu, ktere nejak meni hodnoty na serveru (create,
   upadte, delete, transfer, renew), se pred odeslanim pozaduje potvrzeni k
   odeslani. Prepinacem "confirm OFF" lze toto potvrzovani vypnout.
> credits

   Prikaz credits zobrazi text s informacemi o klientovi.
> help [prikaz]

   Prikaz help zadany bez parametru zobrazi seznam dostupnych prikazu. Pokud se
   zada i parametr prikaz, tak se zobrazi detaily zadaneho prikazu. Stejny
   vyznam jako "help" maji i prikazy "h" a "?".
> lang [kod]

   Prikazem lang se prepina jazykova verze klienta a serveru. Pokud jste ale
   jiz zalogovani, tak je nutne se odlogovat a znovu zalogovat. Duvod je ten,
   ze typ jazykove verze se serveru sdeluje pouze pomoci prikazu "login". To je
   take druha moznost, jak prepnout na jinou jazykovou verzi: """login usename
   password cs""" V teto verzi klienta i serveru jsou dostupne jen dva jazyky: en
   - anglictina; cs - cestina.
> license

   Prikaz license zobrazi text licence klienta.
> quit

   Prikaz quit odpoji klienta od serveru a ukonci aplikaci. Synonyma 'q' a
   'exit' maji stejnou funkci.
> validate [on/off]

   Timto prepinacem zapnete nebo vypnete proces validace XML dokumentu.
   Validace je v teto verzi realizovana pres externi program xmllint. Pokud
   neni v systemu pritomen, tak nastaveni ON nema zadny efekt. Validace overuje
   platnost XML dokumentu podle EPP schemat a to jak v odchozich, tak i
   prichozich zpravach. Pokud neni dokument validni, tak jej konzole na server
   neodesle. Nevalidni dokument vznikne napriklad tim, ze zadate hodnotu,
   ktera neodpovida konkretnimu schematu. Napriklad prilis kratke heslo.
   Konzole v teto verzi obsah hodnot nijak neoveruje, pouze zjistuje jestli
   byly zadany nebo ne.
> verbose [uroven]

   Klient zobrazuje ruzne informace. Ty jsou rozdeleny do urovni detailu.
   Prvni uroven zobrazovani (zakladni) je urcena pro bezneho uzivatele a
   vypisuje nezbytne minimum informaci, ktere jsou k praci nutne. Pro zvidave
   uzivatele je zacilena druha uroven, ktera vypisuje vsechna dostupna hlaseni,
   ktera se behem komunikace vyskytla. Treti uroven zobrazuje jeste navic XML
   zdrojove dokumenty, ktere si klient se serverem predava.
   Urovne vypisu detailu:
   1 - strucna (default)
   2 - vsechno
   3 - vsechno a XML zdroje.

Testovaci prikazy

   Konzole ma nekolik testovacich prikazu, ktere je mozne pouzit k danym
   ucelum. Testovaci prikazy se v helpu nezobrazuji.
> raw-command [dict]
> raw-answer [dict]

   Tento prikaz ma podobnou funkci jako verbose uroven 3. Prikaz vypisuje
   zdrojovy XML dokument posledniho prikazu nebo odpovedi. Pokud tedy nemate
   verbose uroven prave nastavenu a chcete se na zdrojovy dokument podivat, tak
   prave k tomu je tento prikaz urcen. Misto "raw" lze zadat i "src" a oba
   prikazy funguji ve zkracene verzi:
    raw-c, raw-c d, src-c, src-c d, raw-a, raw-a d, src-a, src-a d

   Vysvetleni: Kazdy prikaz, ktery zadate v promptu se sestavi do XML EPP
   dokumentu. Pokud si chcete tento XML dokument prohlednout, tak zadate
   "src-c" a na vystup se vypise vygenerovane zdojove XML. Chcete-li videt XML
   zdojovy dokument od serveru, zadejte "src-a". Pokud je XML dokument
   neprehledny a vy chcete videt jasneji strukturu jednotlivych XML uzlu, tak
   zadejte "src-c d" (nebo "src-a d"). Konzole vypise hodnoty uzlu v
   prehlednejsi forme s odsazenim.
> config

   Prikaz zobrazuje jmeno a cestu pouziteho konfiguracniho souboru a interni
   promenne z nej nacetene.
> send [filename]

   Send je ryzi testovaci prikaz a slouzi k posilani libovolneho souboru na EPP
   server. Pokud jej zadate bez parametru, tak vypise aktualni adresar. Kdyz
   "send" zadate se jmenem platneho souboru, tak tento soubor odesle na EPP
   server:
    send some-folder/my-test-file.xml

> colors [on/off]

   Pokud to konzole umoznuje, tak timto prikazem lze zapnout zvyrazneni vytupu.
   To je v nekterych hlasenich zapsano tucne a barevne. Napriklad chyby jsou
   cervene, kladne vyrizeni prikazu zelene.
> null_value [nejaka_hodnota]

   Nastaveni reprezentace """zadne hodnoty""". Viz Zadna hodnota / Prazdna hodnota
   a Format hodnoty NULL.
> output [typ_vystupu]

   Prikaz output neni primo testovaci. Je urcen k nastaveni typu vystupu.
   Platne honodty jsou text, php, html. Podrobnejsi popis je na Integrace
   klienta do PHP kodu

Kapitola 5. Skripty fred_create.py a fred_sender.py

   Skripty fred_create.py a fred_sender.py jsou urceny pro pouziti v shell
   batchi. fred_create.py prijima parametry se standardniho vstupu a vygeneruje
   XML EPP dokument na standardni vystup. Napriklad:
    $ python fred_create.py info_domain nic.cz
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py
    $ cat file-with-commands.txt | ./fred_create.py

   <?xml version='1.0' encoding....

   Pokud nastane nejaka chyba, tak vraci XML s chybovym hlasenim:
    $ python fred_create.py inxo_domain nic.cz

   <?xml encoding='utf-8'?><errors>inxo_domain nic.cz: Neznamy prikaz!</errors>

   fred_sender.py odesila dokumenty na server. Skript se automaticky zaloguje,
   pak preda dokument, zobrazi odpoved a odloguje se a ukonci. Pro spravne
   zalogovajni je nutne mit spravne nastaven konfiguracni soubor.

   Skript muze odesilat dokumenty dvema zpusoby:

   1. dokumenty se ulozi do souboru a skriptu se predaji jmena souboru. Skript
   je pak odesila v uvedenem poradi. Napriklad:
    $ ./fred_create.py check_domain cosi.cz nic.cz > doc1.xml
    $ ./fred_create.py info_domain nic.cz > doc2.xml
    $ ./fred_sender.py doc1.xml doc2.xml

   2. PIPE - Zretezenim prikazu create a sender. Napriklad:
    $ ./fred_create.py check_domain cosi.cz nic.cz | ./fred_sender.py
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py | .
/fred_sender.py

Kapitola 6. Integrace klienta do PHP kodu

   Soucasti distribuce klienta je i ukazkovy PHP skript, ktery demonstruje, jak
   lze klienta zaclenit do PHP: client_example.php. V prikladu je nutne
   spravne nastavit cestu ke klientovi $exec_path (pokud ten nebyl nainstalovan
   standardnim zpusobem a system jej nenalezne). Promenou $php_module_name se
   nastavuje presmerovani do souboru a $command_options umoznuji pridat dalsi
   parametry, jsou-li treba.

   Popis zacleneni klienta:

   Klient fred_client.py lze spustit i tak, ze se mu v parametrech na
   prikazove radce zada prikaz, ktery ma vykonat -d --command. V takovem
   pripade se nespousti konzole, ale klient funguje jako batch. Stejne jako
   kombinace skriptu fred_create.py a fred_sender.py. Klient pouze zadany
   prikaz provede, zobrazi vystup a ukonci se. Prihlaseni a odhlaseni (login,
   logout) probehnou automaticky a na vystup se nevypisuji. Pro spravne
   prihlaseni je proto potrebne mit nastaveny konfiguracni soubor nebo vse
   definovat na prikazove radce.

   Prepinacem --output -o upravime vystup do pozadovaneho formatu. Pokud chceme
   v prohlizeci hodnoty pouze zobrazit, muzeme zadat typ HTML: --output=html.
   Chceme-li data dale zpracovavat PHP skriptem, nastavime typ PHP:
   --output=php.

   Shrnuti metody pouziti klienta v PHP:
   V PHP se klient spusti jako externi program napriklad funkci passthru().
   V parametrech se nastavi mod vypisu na PHP: --outout=php
   Vystup klienta se presmeruje do adresare s pravy zapisu: ... >
   /cache/outout.php
   Vysledny kod se vlozi do stranky required_once('/cache/outout.php') a tim
   jsou hodnoty PHP skriptu dostupne.

   Promenne z PHP vystupu
   $fred_error_create_name = 'poll'; // jmeno neplatneho prikazu
   $fred_error_create_value = 'op: Value "xxx" is not allowed. Valid is: (req,
   ack)'; // popis chyby, ktera se objevila pri vytvareni prikazu.
   $fred_client_notes = array(); // seznam hlaseni, ktere se generuje behem
   komunikace
   $fred_client_errors = array(); // seznam chyb, ktere vznikly behem komunikce
   $fred_encoding = 'utf-8'; // kodovani textu
   $fred_code = 1000; // navratovy kod odpovedi
   $fred_command = 'domain:info'; // nazev odeslaneho prikazu
   $fred_reason = 'Command completed successfully'; // popis navratoveho kodu
   $fred_reason_errors = array(); // detaily hodnot, ktere zpusobily navraceni
   kodu s chybou
   $fred_labels = array(); // seznam popisku hodnot
   $fred_data = array(); // seznam hodnot
   $fred_source_command = '<?xml ... >'; zdrojovy XML dokument prikazu generuje
   se jen ve verbose 3).
   $fred_source_answer = '<?xml ... >'; zdrojovy XML dokument odpovedi,
   generuje se jen ve verbose 3).

   Priklad dat:
$fred_labels['domain:name'] = 'Domain name';
$fred_data['domain:name'] = 'domena.cz';
$fred_labels['domain:roid'] = 'Repository object ID';
$fred_data['domain:roid'] = 'D0000000174-CZ';
$fred_labels['domain:crID'] = 'Created by';
$fred_data['domain:crID'] = 'REG-LRR';
$fred_labels['domain:clID'] = 'Designated registrar';
$fred_data['domain:clID'] = 'REG-LRR';
$fred_labels['domain:crDate'] = 'Created on';
$fred_data['domain:crDate'] = '2006-10-31T16:51:56+01:00';
$fred_labels['domain:exDate'] = 'Expiration date';
$fred_data['domain:exDate'] = '2009-10-31T01:00:00+01:00';
$fred_labels['domain:renew'] = 'Last renew on';

Kapitola 7. Knihovna fred a popis API

   Obsah

   Online dokumentace:
   Priklady prace s knihovnou

   Knihovna "fred" vam umonuje implmentovat API rozhrani do vasich aplikaci.
   Knihova i jednotlive funkce obsahuji komentare, podle kterych se muzete pri
   implementaci ridit. V casti __init__.py naleznete i ukazky kodu.

Online dokumentace:

   Pokud si chcete projit jednotlive tridy a funkce knihovny, tak k tomu muzete
   vyuzit generator dokumentace, ktery je standardni soucasti pythonu: Zadejte
   na prikazove radce prikaz:
    $ pydoc -p 8080

   Tim jste spustili webovy server, ktery generuje strany dokumentace primo ze
   zdrojovych souboru. Parametr -p udava na jakem portu je server spusten.
   Cislo portu muzete zadat jakekoliv jine. Nyni si otevrete prohlizec a
   zadejte adresu: http://localhost:8080/. Otevre se strana, na ktere v casti
   ../site-packages naleznete odkaz na fred (package).

   Pokud jste skripty neinstalovali, ale jen nakopirovali, nebo pokud se chcete
   podivat i na skripty pracujici s knihovnou fred, tak cely proces spusteni
   udelejte stejne, ale s tim rozdilem, ze pydoc spustite z adresare, kde mate
   tyto skripty ulozene. Pak se v helpu zobrazi i ony:
    $ cd FredClient-1.0.0
    $ pydoc -p 8080

   Server ukoncite stiskem Ctrl+C.

Priklady prace s knihovnou

   Import knihovny provedete prikazem:
    >>> import fred

   Instanci EPP klienta vytvorite:
    >>> epp = fred.Client()

   Jeste musite nacist config, aby knihovna nasla certifikat:
    >>> epp.load_config()

   Chcete-li nacist jinou session - analogicky k parametru --session, tak
   zadejte:
    >>> epp.load_config('my-sessison-name')

   Pak jiz muzete navazat spojeni funkci login:
    >>> retval = epp.login("username","password")

   Kazda funkce (EPP prikazu) vraci tuto "retval" hodnotu, ktera je typu dict a
   ve tvaru:
    {'reason': u'Text of answer reason',
     'code': 1000,
     'command': 'command_name',
     'errors': []
     'data': {'key': 'value' [,'next-key':'next-value']},
    }

   Klic "reason" (str) je vyrozumeni serveru o stavu odpovedi.
   Klic "code" (int) je cislo, ktere definuje typ chyby. Cislo 1000 znamena OK
   - vse vporadku.
   Klic "command" (str) je nazev prikazu, na ktery se odpoved vztahuje (ktery
   odpoved vyvolal).
   Klic "errors" (list) je seznam chyb, ktere server nalezl.
   Klic "data" (dict) je slovnik s hodnotami individualnimi pro kazdy
   jednotlivy prikaz.

   Jake klice jsou v casti "data" pro danou funkci (EPP prikaz) se dozvite z
   dokumentace u kazde funkce:
    >>> print epp.login.__doc__
    ...
    RETURN data: {...}
    ...

   POZOR! V teto verzi (1.0 beta release) ma slovnik tu vlastnost, ze pokud
   hodnota chybi, tak se klic ve slovniku vubec nevyskytuje. Dale, pokud je v
   seznamu hodnot jen jedna polozka, tak je typu string/unicode. Tyto
   odlisnosti byste meli testovat.Ve finalni verzi bude slovnik pevne dany:
   Klic bude ve slovniku i kdyz bude hodnota prazdna a seznam zustane, i kdyz
   bude mit jen jednu polozku.

   Priklad: Kdyz jsou vstupni data:
    name = 'jmeno'
    addr = (1,2,3)
    tech = ('ok',)
    stat = ''

   ...tak se vytvori takovyto slovnik 'data':
    {'name': 'jmeno',
     'addr':['1','2','3']
     'tech':'ok'           # tady je type str a stat chybi
    }

   ...ale ve finalni verzi by to melo byt takto:
    {'name': 'jmeno',
     'addr':['1','2','3']
     'tech':['ok',]
     'stat':''
    }

   Navratovou hodnotu "retval" neni nutne odchytavat, uklada se do interni
   promenne a lze ji kdykoliv zobrazit funkci print_answer():
    >>> epp.print_answer()

   nebo testovat jakoukoliv hodnotu v retval pomoci funkce is_val():
    >>> epp.is_val('reason')
    u'Text of answer reason'

   Kazde volani dalsi funkce EPP prikazu samozrejme predchozi "retval" prepise,
   takze uvedene dve funkce pracuji vzdy jen s posledni navratovou hodnotou.
   Pokud chcete navratovou hodnotu testovat nebo zobrazit pozdeji, tak si ji
   ulozte a pak ji predejte funkcim:
    >>> epp.print_answer(my_retval)
    >>> epp.is_val('reason', my_retval)

   Funkci is_val() je mozno zadat bez parametru. V takovem pripade defaultne
   vraci hodnotu klice "code":
   >>> epp.is_val()
    1000

   Pokud chcete zjistit hodnotu v jakekoliv vnorene casti slovniku, tak zadejte
   parametr jako cestu - seznam jmen (klicu) slovniku:
    >>> epp.is_val(('data','next-key'))
    next-value

   V pripade, ze dany klic neexistuje, vraci funkce hodnotu None.
    >>> epp.is_val(('data','any-key'))
    None

   Pokud se vyskytne nejaka chyba pri prenosu nebo jina, ktera zablokuje
   funkcnost, tak se generuje vyjimka FredError.

