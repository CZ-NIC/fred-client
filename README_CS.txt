
Manual pro ccRegClient konzoli a knihovnu ccReg

Verze 1.2

   Vzniklo: 11.7.2006; Revize: 18.8.2006; Revize: 1.9.2006; Revize: 4.9.2006;
   Revize: 14.9.2006; Revize: 27.9.2006;

   Copyright (c) 2006 CZ.NIC
     _________________________________________________________________

   Obsah

   Co je ccRegClient:
   1. Licence
   2. Pozadavky na system a instalace
   3. Popis jednotlivych programu, parametry a config 

        Parametry (OPTIONS) 
        Config 

   4. Program ccreg_console.py 

        Zobrazeni helpu
        EPP prikazy
        Typy parameru prikazu
        Spolecny parametr cltrid
        Zadna hodnota / Prazdna hodnota

              Zadna hodnota: NULL
              Prazdna hodnota: '', ""

        Prikazy relace (session)

   5. Skripty ccreg_create.py a ccreg_sender.py 
   6. Knihovna ccReg a popis API 

        Online dokumentace:
        Priklady prace s knihovnou

Co je ccRegClient:

   ccRegClient je sada scriptu v jazyce Python postavenych na ccReg knihovne a
   urcenych ke komunikaci s EPP serverem.

   Sada obsahuje EPP konzoli a skripty urcene pro pouziti v shellu.

Kapitola 1. Licence

   Licence je v souboru ccReg/LICENSE.

Kapitola 2. Pozadavky na system a instalace

   Pokyny k instalaci jsou v souboru INSTALL.

Kapitola 3. Popis jednotlivych programu, parametry a config

   Obsah

   Parametry (OPTIONS) 
   Config 

   Dostupne skripty jsou nasledujici:
   ccreg_client.py - spousti EPP konzoli nebo sekvenci crate+send (pro shell)
   ccreg_console.py - EPP konzole, komunikuje s EPP serverem
   ccreg_create.py - Vytbori zdrojovy EPP XML prikaz
   ccreg_sender.py - Odesle soubor na EPP server

Parametry (OPTIONS)

   Skripty se daji spoustet s parametry. Jake parametry lze pouzit zjistite
   zadanim parametru --help nebo -?:
    $ ccreg_client.py --help
    $ ccreg_client.py -?

Pouziti: python ccreg_console.py [OPTIONS]
Konzole pro komunikaci s EPP serverem.

OPTIONS s hodnotami:
    -s --session  nazev session, ktery se ma pouzit pro spojeni s EPP serverem
                  session hodnoty jsou nacteny z config souboru a mohou obsahov
at
                  cesty k certifikatu, soukromemu klici,

    -h --host     jmeno host (prepise config hodnotu)
    -u --user     jmeno user (prepise config hodnotu)
    -p --password heslo (prepise config hodnotu)
    -l --lang     jazykova verze
    -v --verbose  mod vypisu: 1,2,3; default: 1
                  1 - zkraceny
                  2 - plny
                  3 - plny & XML zdroje
    -c --command  odeslani prikatu na EPP server
                  priklad: --command='info_domain nic.cz'
    -x --gui
                  klient se spusti v grafickem rezimu (na platforme Qt)

OPTIONS:
    -r --colors   zapnuti barevneho vystupu
    -? --help     tento help

Config

   Config je spolecny pro vsechny skripty a je ulozen v souboru .ccReg.conf.
   Nejdrive se hleda v adresari spolecnem pro vsechny uzivatele. Na POSIX
   systemech je to /etc, v MS Windows v adresari nastavenem v promenne
   $ALLUSERSPROFILE.

   Pak se hleda v adresari, kde je umistena knihovna cReg. Pokud ani tam neni
   nalezen, hleda se v domovskem adresari uzivatele.

   Nazev a unisteni konfiguracniho souboru je mozne zadat pri spusteni pomoci
   prepinace -c CONFIGNAME, --config=CONFIGNAME.

   Konfig soubor lze vygenerovat v konzoli. Spustte si konzoli prikazem
   ccreg_console.py (nebo ccreg_client.py) a zadejte prikaz "config create".
   Dalsi podrobnosti naleznete v casti popisu prace s konzoli (4. Program
   ccreg_console).

   V konfigu se nachazi sekce connect, kde jsou ulozeny cesty k certifikatum a
   informace o serveru. Take tam muzou byt prihlasovaci udaje pro login. Prikaz
   login tak muze byt zadan bez parametru.

   Zde je priklad konfigu:
    [connect]
    dir=/installdir/certificates
    host = epp-test.ccreg.nic.cz
    port = 700
    ssl_cert = %(dir)s/epp_test_ccreg_nic_cz_cert.pem
    ssl_key  = %(dir)s/epp_test_ccreg_nic_cz_key.pem
    username = your-username
    password = your-password

    [session]
    poll_ack = off
    confirm_send_commands = on
    validate = on
    schema = /installdir/schemas/all-1.0.xsd
    colors = on
    verbose = 2
    lang = en

   Sekci connect muze byt vice. Ktera z nich se pri startu pouzije se nastavi
   pomoci parametru --session. Napriklad si vytvorite sekci
   [connect_myeppserver] tu pak aktivujete:
    $ ccreg_client.py --session=myeppserver     (nebo -s myeppserver)

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
       konzoli pozvrzeni pred odeslanim na server. Toto potvrzeni lze
       vypnout/zapnout.
     * validate = on/off
       K validaci se pouziva externi program xmllint. Validaci lze vypnout a
       dokumnety se tak na server posilaji bez overeni platnosti formatu.
     * schema = /installdir/schemas/all-1.0.xsd
       Adresar, kde ma validator hledat schemata, podle kterych dokumenty
       overuje.
     * colors = on/off
       Vystup na terminal muze byt barevny, pokud to terminal umoznuje.
     * verbose = 1/2/3
       Uroven vypisu 1 - strucna, 2 - cela, 3 - cela + XML zdrojove dokumenty.
     * lang = en/cs
       Jazykova verze. Pokud neni zadana zadna hodnota, tak se bere nastaveni z
       promenne LANG prostredi OS. Dostupne jsou zatim jen anglictina a
       cestina. Jazykovou verzi muzete nastavit i pomoci parametru pri
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
     * socket = IPv4/IPv6
       Nastaveni typu soketu na IPv4 nebo IPv6. Pokud neni tato hodnota zadana,
       tak se pouzije typ soketu, ktery nabizi server.
     * auto_login = on/off
       Pri nastaveni hodnoty auto_login na on se po skusteni konzole
       automaticky provede i priakz login.

Kapitola 4. Program ccreg_console.py

   Obsah

   Zobrazeni helpu
   EPP prikazy
   Typy parameru prikazu
   Spolecny parametr cltrid
   Zadna hodnota / Prazdna hodnota

        Zadna hodnota: NULL
        Prazdna hodnota: '', ""

   Prikazy relace (session)

   ccreg_console.py je konzole, ktera komunikuje s EPP serverem. Konzoli
   spustite prikazem:
    $ ccreg_console.py

   Pokud mate v configu spravne nadefinovanu cestu k certifikatum a ulozene
   login a heslo, tak muzete jednoduse zadat login a tim se spojite s EPP
   serverem. Konzole se ukoncuje prikazem "quit" nebo jen kratce "q".

Zobrazeni helpu

   Jake prikazy mate k dispozici zjistite zadanim prikazu "help" (nebo h, ?).
    ccReg client verze 1.1 Zadejte "help", "license" nebo "credits" pro zobraze
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
> login moje-ID moje-heslo

Typy parameru prikazu

   INSTRUKCE:
   parametry zadavejte v poradi, v jakem jsou vypsane v helpu
   hodnoty s mezerami dejte do uvozovek
   seznamy se definuji pomoci zavorek, polozky seznamu muzou (ale nemusi) byt
   oddeleny carkami
   pokud je v seznamu jen jedna polozka, nemusi se zavorky zadavat
   jmenne prostory se take jako seznamy definuji pomoci zavorek
   chcete-li seznam nebo jmenny porostor vynechat, zadejte jen prazdne zavorky
   hodnoty mimo poradi zadavejte pomoci klice

   VYSVETLENI:
   jednoducha hodnota: my-value01
   hodnota s mezerou: 'lorem ipsum' "some value"
   seznam: (one two three)
   jmenny prostor: ((one two three) my-value01 'lorem ipsum' (enyky benyky)
   end-value)

   Pokud hodnota parametru obsahuje mezeru, tak ji napiste do uvozovek.
   Napriklad:
> login moje-ID "moje heslo s mezerami"

   Nektere parametry muzou obsahovat seznam hodnot. Napriklad parametr "street"
   v prikazu create_contact. Vypis casti helpu:
    ?create_contact
    ...
    ... street (nepovinny)  seznam o maximalne 3 polozkach.
    ...


   Seznam zadate tak, ze hodnoty uzavrete do zavorek:
> create_contact my-ID my-name mail city
            cc org (Vodickova, "Na prikope", "U privozu") voice


   Pokud zadavate jen jednu hodnotu ze seznamu, tak zavorky zadavat nemusite:
    > create_contact my-ID my-name mail city cc org Vodickova voice


   Parametry musite zadavat v poradi, v jakem jsou v helpu vypsany. Povinne
   jsou vzdy na zacatku a nepovinne tak neni nutne zadavat. Pro pripad, ze
   chcete krome povinnych hodnot zadat jeste nejakou nepovinnou, ktera ale
   NENI v poradi, tak mate moznost ji zadat MIMO poradi zadanim jmena parametru
   - klice. To resi situaci, kdy by se kvuli jednomu parametru na konci rady
   musely zadavat vsechny parametry pred nim.

   Klic (jmeno parametru) se definuje pomoci jednoho nebo dvou spojovniku.
   Napriklad chcete v prikazu create_contact zadat krome povinnych udaju uz jen
   hodnotu "notify email", ktera se nachazi prave na uplnem konci seznamu
   parametru. Pak tuto hodnotu zadate takto:
  > create_contact my-ID my-name mail city cc --notify_email = muj@mail.cz


   Jaky ma byt klic (nazev parametru) zjistite z helpu daneho prikazu. Parametr
   s klicem pak jiz nemusi byt na "sve" pozici, ale muze byt kdekoliv v rade
   mezi ostatnimi parametry. Takovy parametr stoji "mimo" poradi a nenarusuje
   pozice ostatnich parametru bez klice. Zde jsou do rady parametru vlozeny
   hodnoty s klici "vat" a "notify_email":
    > create_contact my-ID my-name mail --vat = 12346 --notify_email = muj@mail
.cz city cc


   Nektere prikazy maji parametry vnorene do dalsich parametru. Ty vytvareji
   jmenne prostory. Napriklad v prikazu "create_contact" je parametr
   "disclose". Ten obsahuje dalsi parametry "flag", "data", atd. Samotny nazev
   "disclose" neni v tomto pripade nazev klice, ale nazev jmenneho prostoru, ve
   kterem se nachazeji klice "flag" a "data". Jmenne prostory se definuji
   stejne jako seznamy pomoci zavorek:
  > create_contact my-ID my-name mail city cc org street sp pc
        voice fax (n (name org addr voice fax email)) vat ssn


   Pokud jmenny prostor nechcete zadavat, napiste proste jen prazdne zavorky.
   To plati i pro seznamy:
  > create_contact my-ID my-name mail city cc org street sp pc voice fax () vat
 ssn notify@email


   Nektere prikazy maji v parametrech seznamy jmennych prostoru. V takovem
   pripade pak zavorky maji sve vyznamy podle toho, jak jsou hodnoty
   strukturovane. Napriklad prikaz "update_nsset" ma jeden nepovinny parametr
   "add". Pokud jej nechcete zadavat, tak napisete:
  > update_nsset id () ...    - parametr add je nyni prazdny


   Pokud ale "add" zadat chcete, tak "add" (jak vidite v helpu) obsahuje seznam
   deviti jmennych prostoru "dns"! Kazdy "dns" prostor pak dale obsahuje
   parametr "name" a seznam "addr". Pokud chete tyto hodnoty zadat, tak musite
   zapsat vsechny zavorky, ktere jsou nutne: Prvni zavorka pro definovani
   jmenneho prostoru "add". Druha zavorka pro zacatek seznamu jmennych
   prostoru "dns". Treti zavorka pro samotny jmenny prostor "dns". Teprve pak
   nasleduje hodnota parametru "name". Za nim pak nasleduje zavorka seznamu
   "addr":
  >  update_nsset nsset1 (((ns1.dns.cz (217.31.207.130, 217.31.207.131, 217.31.
207.132)),
        (ns2.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132))) (tech1,
tech2, tech3)
        (ok, clientTransferProhibited)) (((rem1.dns.cz, rem2.dns.cz) (tech-rem0
1, tech-rem02)
            serverUpdateProhibited)) (password)


   Pokud "addr" neni seznam, ale jen jedna hodnota, tak se zavorky pro "addr"
   zadavat nemusi: (To je pravidlo jiz zminene v predchozim textu.)
  > update_nsset nsset-ID (((nsset1 217.31.207.130),(nsset2 217.31.207.130))
        tech status) ...


   Takto slozite zadavani nastesti existuje jen v malem mnozstvi prikazu a
   tento uvedeny priklad zadani je vubec nejslozitejsi ze vsech. Krome toho
   mate moznost zadavat parametry prikazu v interaktivnim modu - hezky jeden za
   druhym. Navic je vzdy na konci helpu kazdeho prikazu uveden priklad zadani
   vsech parametru.

   Pokud chcete parametry prikazu zadavat interaktivne, napiste pred prikaz
   vykricnik:
> !update_nsset

   Tim spustite rezim interaktivniho vkladani parametru. Konzole vzdy vypise
   jmeno parametru a ceka na zadani hodnoty. Pokud hodnotu nechcete zadat, tak
   proste stisknete enter a hodnota se preskoci. Interaktivni rezim muzete
   kdykoliv ukoncit zadanim vykricniku. Tim se ukonci aktualni jmenny prostor.
   Nachazite-li se tedy v hlavnim jmennem prostoru, tak se interaktivni rezim
   ukonci. Pokud je prompt zanoren do nejakeho jmenneho prostoru, tak se
   ukonci pouze ten a interaktivni vkladani pokracuje nadrazenym prostorem.
   Chcete-li vyskocit z vicenasobne vnoreneho prostoru nebo ukoncit rezim cely,
   tak zadejte vice vykricniku najednou. Jeden vykcirnik na jeden jmenny
   prostor. Nevadi bude-li jich vice, nez pozadovany pocet:
    > !update_nsset
    Start interaktivniho zadavani parametru. Pro ukonceni zadejte: !
    > !update_nsset:id (povinny) > moje-id
    (Hodnota muze byt seznam o max. velikosti 9 polozek.)
    > !update_nsset:add.ns[1/9].name (povinny) > ns1
    (Hodnota muze byt libovolne velky seznam.)
    > !update_nsset:add.ns[1/9].addr[1/oo] (nepovinny) > 217.31.207.130
    > !update_nsset:add.ns[1/9].addr[2/oo] (nepovinny) > 217.31.207.131
    > !update_nsset:add.ns[1/9].addr[3/oo] (nepovinny) >
    > !update_nsset:add.ns[2/9].name (povinny) > ns2
    (Hodnota muze byt libovolne velky seznam.)
    > !update_nsset:add.ns[2/9].addr[1/oo] (nepovinny) > !


   Jeste jednou zpet k zadavani pomoci klice: Klic se zadava ve tvaru -[nazev
   parametru] [hodnota]. Napriklad:
     -heslo "toto je moje heslo"

   Toto zadani lze napsat i takto se stejnym ucinkem:
     --heslo = "toto je moje heslo"

   Zalezi na vas, ktery zapis se vam bude zdat citelnejsi. Jak ale zadat
   honodotu, ktera je soucasti jmenneho prostoru? Jednoduse pomoci teckove
   koncence:
    --add.ns.name = nsset_name

   Takto jste definovali hodnotu nsset_name do jmenneho porostoru "add", do
   prvni polozky seznamu "ns", do parametru "name". Chcete-li ulozit hodnotu
   napriklad do treti polozky seznamu "ns", tak zadejte:
    --add.ns[2].name = nsset_name

   Dvojka je index seznamu v tomto pripade o max. deviti polozkach (indexy 0 -
   8).

Spolecny parametr cltrid

   Kazdy EPP prikaz, krome prikazu hello, obsahuje tag <clTRID>. Tato hodnota
   je identifikator transakce. Ten si stanovuje klient a muze byt libovolny v
   ramci formatovacich pravidel definovanych ve schematech pro tuto hodnotu.
   Identifikator je nepovinny a pokud neni zadan, tak jej program automaticky
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
   bez parametru, tak se pouze vypise aktualni stav.
> validate on/off

   Timto prepinacem zapnete nebo vypnete proces validace XML dokumentu.
   Validace je v teto verzi realizovana pres externi program xmllint. Pokud
   neni v systemu pritomen, tak nastaveni ON nema zadny efekt. Validace overuje
   platnost XML dokumentu podle EPP schemat a to jak v odchozich, tak i
   prichozich zpravach. Pokud neni dokument validni, tak jej konzole na server
   neodesle. Nevalidni dokument vznikne napriklad tim, ze zadate hodnotu,
   ktera neodpovida konkretnimu schematu. Napriklad prilis kratke heslo.
   Konzole v teto verzi obsah hodnot nijak neoveruje, pouze zjistuje jestli
   byly zadany nebo ne.
> poll-ack [on/off]

   Pokud je tento prepinac ON, tak se po odeslani prikazu "poll req"
   automaticky odesila i "poll ack". Tuhle funkci asi nejvice ocenite, kdyz
   budete mit na serveru hodne zprav. Prikaz "poll req" zpravu ze serveru pouze
   zobrazi, ale pak se zprava musi ze serveru odstranint prikazem "poll ack
   ID-zpravy". Pri automatickem poll-ack se bude odstranovani provadet
   automaticky.
> raw-command [dict]
> raw-answer [dict]

   Tyto prikazy nejsou prepinace internich promennych, ale vypisuji zdrojove
   tvary posledniho prikazu a odpovedi. Misto "raw" lze zadat i "src" a vsechny
   funguji ve zkracene verzi:
    raw-c, raw-c d, src-c, src-c d, raw-a, raw-a d, src-a, src-a d

   Kazdy prikaz, ktery zadate v promptu se sestavi do XML EPP dokumentu. Pokud
   si chcete tento XML dokument prohlednout, tak zadate "src-c" a na vystup se
   vypise vygenerovane zdojove XML. Chcete-li videt XML zdojovy dokument od
   serveru, zadejte "src-a". Pokud je XML dokument neprehledny a vy chcete
   videt jasneji strukturu jednotlivych XML uzlu, tak zadejte "src-c d" (nebo
   "src-a d"). Konzole vypise hodnoty uzlu v prehledne forme s odsazenim.
> confirm [on/off]

   U EPP editacnich prikazu, ktere nejak meni hodnoty na serveru (create,
   upadte, delete, transfer, renew), se pred odeslanim pozaduje potvrzeni k
   odeslani. Prepinacem "confirm OFF" lze toto potvrzovani vypnout.
> config [create]

   Konzole si hodnoty internich nastaveni nacita z konfigu. Pokud jeste konfig
   nebyl vytvoren, tak se nastavi defaultni hodnoty. Aktualni hodnoty konfigu
   lze zobrazit prikazem "config". Chcete-li konfig vytvorit, zadejte "config
   create". Tim se vytvori konfiguracni soubor ".ccReg.conf" ve vasem domovskem
   adresari. V konfigu si pak muzete nastavit cestu k vasemu certifikatu a
   dalsi hodnoty. Konzole se pokousi neprve nacist konfig z adresare /etc (ve
   Windows z adresare uvedenem v promenne prostredi $ALLUSERSPROFILE, ta byva
   obvykle nastavena na "C:\Documents and Settings\All Users") a pote nacita
   dalsi konfig z adresare uzivatele. Na posix to je /home/[user], ve Windows
   je to "C:\Documents and Settings\[user]". Tak lze ulozit hodnoty spolecne
   pro vsechny uzivatele.
> send

   Prikaz "send" slouzi k posilani libovolneho souboru na EPP server. Tento
   prikaz je zde jen z testovacich duvodu. Pokud "send" zadate bez parametru,
   tak vypise aktualni adresar. Kdyz "send" zadate se jmenem platneho souboru,
   tak tento soubor bez dalsiho ptani odesle na EPP server:
    send some-folder/my-test-file.xml

> connect

   Prikaz "connect" vytvari spojeni s EPP serverem aniz by na nej cokoliv
   posilal. Pokud se spojeni podarilo, posle EPP server zpravu "greeting" a tak
   se zobrazi na vystupu. Prikaz "connect" je zde z testovacich duvodu a neni
   potreba jej volat. Staci zadat rovnou "login".
> colors [on/off]

   zapnout/vypnout barevny vystup
> verbose [number]

   nastavit mod vypisu: 1 - strucny (default); 2 - plny; 3 - plny & XML zdroje
> null_value [nejaka_hodnota]

   Nastaveni reprezentace """zadne hodnoty""". Viz Zadna hodnota / Prazdna hodnota
   a Format hodnoty NULL.

Kapitola 5. Skripty ccreg_create.py a ccreg_sender.py

   Skripty ccreg_create.py a ccreg_sender.py jsou urceny pro pouziti v shell
   batchi. ccreg_create.py prijima parametry se standardniho vstupu a
   vygeneruje XML EPP dokument na standardni vystup. Napriklad:
    $ python ccreg_create.py info_domain nic.cz
    $ ./ccreg_create.py info_domain nic.cz

   <?xml version='1.0' encoding....

   Pokud nastane nejaka chyba, tak vraci XML s chybovym hlasenim:
    $ python ccreg_create.py inxo_domain nic.cz

   <?xml encoding='utf-8'?><errors>inxo_domain nic.cz: Neznamy prikaz!</errors>

   Prikazy se daji zretezit:
    $ ./ccreg_create.py check_domain test.cz nic.cz | ./ccreg_create.py info_do
main nic.cz

   ccreg_sender.py odesila dokumenty na server. Skript se automaticky zaloguje,
   pak preda dokument, zobrazi odpoved a odloguje se a ukonci. Pro spravne
   zalogovajni je nutne mit spravne nastaven config.

   Skript muze odesilat dokumenty dvema zpusoby:

   1. dokumenty se ulozi do souboru a skriptu se predaji jmena souboru. Skript
   je pak odesila v uvedenem poradi. Napriklad:
    $ ./ccreg_create.py check_domain cosi.cz nic.cz > doc1.xml
    $ ./ccreg_create.py info_domain nic.cz > doc2.xml
    $ ./ccreg_sender.py doc1.xml doc2.xml

   2. PIPE - Zretezenim prikazu create a sender. Napriklad:
    $ ./ccreg_create.py check_domain cosi.cz nic.cz | ./ccreg_create.py info_do
main nic.cz | ./ccreg_sender.py

Kapitola 6. Knihovna ccReg a popis API

   Obsah

   Online dokumentace:
   Priklady prace s knihovnou

   Knihovna ccReg vam umonuje implmentovat API rozhrani do vasich aplikaci.
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
   ../site-packages naleznete odkaz na ccReg (package).

   Pokud jste skripty neinstalovali, ale jen nakopirovali, nebo pokud se chcete
   podivat i na skripty pracujici s knihovnou ccReg, tak cely proces spusteni
   udelejte stejne, ale s tim rozdilem, ze pydoc spustite z adresare, kde mate
   tyto skripty ulozene. Pak se v helpu zobrazi i ony:
    $ cd ccRegClient-1.1
    $ pydoc -p 8080

   Server ukoncite stiskem Ctrl+C.

Priklady prace s knihovnou

   Import knihovny provedete prikazem:
    >>> import ccReg

   Instanci EPP klienta vytvorite:
    >>> epp = ccReg.Client()

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
   funkcnost, tak se generuje vyjimka ccRegError.

