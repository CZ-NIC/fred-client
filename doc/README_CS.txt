Manual pro FredClient konzoli a knihovnu fred

FredClient

   Vzniklo: 11. 7.2006; Revize: 18. 8.2006; 1. 9.2006; 4. 9.2006; 14.
   9.2006; 27. 9.2006; 1.11.2006; 7.11.2006; 17.1.2007;

   Copyright (c) 2007 CZ.NIC
     __________________________________________________________________

   Obsah

   Co je FredClient:
   1. Licence
   2. Pozadavky na system a instalace
   3. Popis jednotlivych programu, parametry a konfiguracni soubor

        Parametry pri spusteni (OPTIONS)
        Konfiguracni soubor

   4. Program fred_client

        Zobrazeni helpu
        EPP prikazy
        Syntaxe zadavani parameru prikazu
        Spolecny parametr cltrid (Client transaction ID)
        Zadna hodnota / Prazdna hodnota

              Zadna hodnota: NULL
              Prazdna hodnota: '', ""

        Interaktivni mod vkladani parametru
        Prikazy relace (session)

   5. Skripty fred_create.py a fred_sender.py
   6. Integrace klienta do PHP kodu
   7. Graficka nadstavba v Qt4.
   8. Knihovna fred a popis API

        Online dokumentace:
        Priklady prace s knihovnou

Co je FredClient:

   FredClient je sada scriptu v jazyce Python postavenych na fred knihovne
   a urcenych ke komunikaci s EPP serverem.

   Sada obsahuje EPP konzoli a skripty urcene pro pouziti v shellu.

Kapitola 1. Licence

   Licence je v souboru fred/LICENSE.

Kapitola 2. Pozadavky na system a instalace

   Pokyny k instalaci jsou v souboru INSTALL.

Kapitola 3. Popis jednotlivych programu, parametry a konfiguracni soubor

   Obsah

   Parametry pri spusteni (OPTIONS)
   Konfiguracni soubor

   Dostupne skripty jsou nasledujici:
   fred_client - EPP konzole, komunikuje s EPP serverem
   fred_create.py - Vytvori zdrojovy EPP XML prikaz
   fred_sender.py - Odesle soubor na EPP server

Parametry pri spusteni (OPTIONS)

   Skripty se daji spoustet s parametry. Jake parametry lze pouzit
   zjistite zadanim parametru --help nebo -?:
    $ fred_client --help
    $ fred_client -?

Pouziti: fred_client [parametry...]

Hlavni parametry:
  -?, --help       Zobrazit tuto napovedu a skoncit
  -V, --version    Zobrazit verzi programu a skoncit
  -l LANGUAGE, --lang=LANGUAGE
                   Nastaveni jazykove verze
  -v LEVEL, --verbose=LEVEL
                   Nastaveni modu vypisu
                   0 - zobrazit jen XML odpoved od EPP serveru
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
                   Zobrazit vystup jako text (default), html, xml, php (Pozor! J
en pro testovani!)
  -q,  --qt
                   Spustit klienta v Qt4 GUI (Pozor! Jen pro testovani!)

Specialni parametry, ktere se v helpu nezobrazuji:
   -r, --cltrid    --cltrid=mycID_%04d
                   Definice vlastniho clTrID s pridanim cisla prikazu

Konfiguracni soubor

   Konfiguracni soubor slouzi k ulozeni ruznych nastaveni klienta tak, aby
   pri kazdem spusteni byly hodnoty takove, jake je potrebujete mit.
   Napriklad se zde definuji jmena a umisteni souboru s certifikaty,
   adresa serveru, na ktery se ma klient pripojit, verze schemat a dalsi
   nastaveni.

   Konfiguracni soubor se implicitne hleda nejdrive v home uzivatele
   (~/.fred_client.conf), ktery skript spustil. Pokud tam neni nalezen,
   hleda se v adresari etc/fred (/etc/fred/fred_client.conf). Na POSIX
   systemech je to /etc/fred, v MS Windows to je v adresari nastavenem v
   promenne $ALLUSERSPROFILE. Prepinacem --config=filepath (nebo -f
   filepath) je mozne konfiguracni soubor nacist z libovolneho souboru.

   Pro zalozeni noveho konfiguracniho souboru je k dispozici priklad
   fred_client.conf.sample. Tento priklad muzete pouzit jako zaklad pro
   vas konfiguracni soubor. V prikladu jsou pro definici plne cesty k
   souborum pouzity promenne, ktere slouzi jako hodnoty, ktere lze vlozit
   do jinych polozek v dane sekci.

   Promenne se zapisuji ve tvaru %(nazev promenne)s. Napriklad:
   %(dir)s

   V tomto prikladu je definovana promenna jmenem dir. Ta musi byt v dane
   sekci take definovana:
   dir = /home/username/certificates

   Pak se takovyto zapis
   %(dir)s/private_key.pem

   po nacteni konfiguracniho souboru rozvine na:
   /home/username/certificates/private_key.pem

   Tato metoda umoznuje mit plnou adresu k souborum na jednom miste a
   doplnovat k ni jen jmeno potrebneho souboru. Pokud se vam ale tento
   zpusob zda prilis slozity, tak promenne pouzivat nemusite a v
   prislusnych polozkach zadejte misto promenne vzdy adresu celou.

   V prikladu konfiguracniho souboru se takto musi nastavit dve cesty:
   Jedna k certifikatum (pro dva soubory) a druha ke schematum.

   V konfiguracnim souboru se nachazi sekce connect, kde jsou ulozeny
   cesty k certifikatum a informace o serveru. Take tam jsou dalsi hodnoty
   napriklad username a password. Pokud se tyto hodnoty v konfiguracnim
   souboru nachazeji, tak je prikaz login pouzije jako parametry prikazu,
   ktere mu nebyly zadany.

   Sekci connect muze byt v konfiguracnim souboru vice. Ktera z nich se
   pri startu pouzije se nastavi pomoci parametru -s --session. Napriklad
   si vytvorite sekci [connect_myeppserver] tu pak aktivujete:
    $ fred_client --session=myeppserver     (nebo -s myeppserver)

    [connect_myeppserver]
    dir=/test/certificates
    host = myeppserver.cz
    ssl_cert = %(dir)s/cert.pem
    ssl_key  = %(dir)s/key.pem
    username = myusername
    password = mypassword

   V sekci session jsou tato nastaveni:
     * poll_autoack = on/off
       Pri on se po odeslani prikazu poll req automaticky posle i poll
       ack.
     * confirm_send_commands = on/off
       Vsechny editacni prikazy (create, delete, update, ...) vyzaduji v
       konzoli pozvrzeni pred odeslanim na server. Tuto funkci lze
       vypnout/zapnout.
     * validate = on/off
       K validaci se pouziva externi program xmllint. Validaci lze vypnout
       a dokumnety se tak na server posilaji bez overeni platnosti
       formatu.
     * schema = /installdir/schemas/all-1.0.xsd
       Soubor, ve kterem ma validator hledat schemata, podle kterych
       dokumenty overuje.
     * colors = on/off
       Vystup na terminal muze byt barevny, pokud to terminal umoznuje.
     * escaped_input = on/off
       Pokud je vstup escapovany (&lt;example&amp;test&gt;), nastavte tuto
       hodnotu na on.
     * verbose = 1/2/3
       Uroven vypisu 1 - strucna, 2 - cela, 3 - cela + XML zdrojove
       dokumenty.
     * lang = en/cs
       Jazykova verze. Pokud neni zadana zadna hodnota, tak se bere
       nastaveni z promenne LANG prostredi OS. Dostupne jsou zatim jen
       anglictina a cestina. Jazykovou verzi muzete take nastavit i pomoci
       parametru pri spusteni skriptu.
     * null_value = NULL
       Nastaveni zastupce pro hodnotu nic (Nil), ktera vyjadruje "zadnou
       hodnotu". Defaultne je nastaveno NULL. Tuto hodnotu pouzivame, kdyz
       chceme preskocit nektery z parametru prikazu. Zadani NULL znamena,
       ze jsme nezadali zadnou hodnotu na rozdil od '' nebo "", kdy jsme
       zadali hodnotu nulove delky.
       Format hodnoty NULL: Zastupce muze byt libovolny, ale nesmi
       obsahovat spojovnik (-), mezery a kulate zavorky.
       Vice se o teto hodnote dozvite v casti "Zadna hodnota / Prazdna
       hodnota"
     * skip_value = SKIP
       Specialni hodnota umoznujici vynechat XML element v EPP dokumentu.
       Zavedeno pro testovaci ucely. Aktualne lze tuto hodnotu pouzit
       pouze na element <clTRID>. Vychozi hodnota je nastavena na SKIP.
       Vychozi EPP dokument:
        REG-FRED_A@localhost> credit_info

        <?xml version="1.0"?>
        <epp>
            <fred:creditInfo/>
            <fred:clTRID>zhte004#11-08-12at09:00:27</fred:clTRID>
        </epp>

       Pri pouziti hodnoty SKIP:
        REG-FRED_A@localhost> credit_info SKIP

        <?xml version="1.0"?>
        <epp>
            <fred:creditInfo/>
        </epp>

       Format hodnoty SKIP: Zastupce muze byt libovolny, ale nesmi
       obsahovat spojovnik (-), mezery a kulate zavorky.
       Popis elementu clTRID: "Spolecny parametr cltrid (Client
       transaction ID)"
     * cltrid = myid%04d
       Vlastni hodnota cltrID - Client client transaction ID. Symbol %d je
       nahrazen cislem prikazu. Hodnota mezi % a d zarovnava cislo na
       ctyri cislice (doplni se nula).
     * reconnect = no
       V pripade, ze se behem komunikace spojeni prerusi, se klient pokusi
       spojeni znovu navazat. Timto zapisem se funkce automatickeho
       navazani spojeni vypne.

   V sekci connect jsou tato nastaveni:
     * dir = cesta k adresari s certifikaty
       Tato hodnota nahrazuje zastupce %(dir)s ve vsech polozkach dane
       sekce. V nasem pripade je v ni ulozena cesta k certifikatum.
     * ssl_cert = jmeno certifikatu
       Nazev souboru s certifikatem. Pred nim je uveden zastupce adresare
       dir, ktery je nahrazen hodnotou definovanou v teto sekci.
     * ssl_key = jmeno privatniho klice
       Nazev souboru s privatnim klicem. Pred nim je uveden zastupce
       adresare dir, ktery je nahrazen hodnotou definovanou v teto sekci.
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
       serveru. Pokud do uvedene doby odpoved neprijde, je spojeni
       povazovano za prerusene. Defaultne je nastaveno 10 vterin. Pozor! V
       MS Windows se muze u timeoutu vyskytnout bug, ktery zpusobi, ze se
       spojeni nenavaze. V takovem pripade nastavte timeout na nulu:
       timeout = 0
     * socket = IPv4/IPv6
       Nastaveni typu soketu na IPv4 nebo IPv6. Pokud neni tato hodnota
       zadana, tak se pouzije typ soketu, ktery nabizi server.
     * schema_version_[name] = 1.0
       Individualni nastaveni verze schemat pro objekty contact, nsset,
       domain, enum, fred a epp.
     * nologin = on/off
       Klient se ihned po spusteni pokusi spojit se serverem a zalogovat
       se. Tuto funkci je mozne vypnout nastavenim nologin = off.

Kapitola 4. Program fred_client

   Obsah

   Zobrazeni helpu
   EPP prikazy
   Syntaxe zadavani parameru prikazu
   Spolecny parametr cltrid (Client transaction ID)
   Zadna hodnota / Prazdna hodnota

        Zadna hodnota: NULL
        Prazdna hodnota: '', ""

   Interaktivni mod vkladani parametru
   Prikazy relace (session)

   fred_client je konzole, ktera komunikuje s EPP serverem. Konzoli
   spustite prikazem:
    $ fred_client

   Pokud mate v konfiguracnim souboru spravne nadefinovanu cestu k
   certifikatum a ulozene login a heslo, tak muzete jednoduse zadat login
   a tim se spojite s EPP serverem. Konzole se ukoncuje prikazem "quit"
   nebo jen kratce "q".

Zobrazeni helpu

   Jake prikazy mate k dispozici zjistite zadanim prikazu "help" (nebo h,
   ?).
    FredClient verze n.n.n Zadejte "help", "license" nebo "credits" pro zobrazen
i vice informaci.
    > help

   Help vypise dve casti napovedy:
   1) Dostupne EPP prikazy
   2) Prikazy relace (session) pro nastaveni vnitrnich promennych konzole

EPP prikazy

   Vsechny EPP prikazy (krome hello), maji sve parametry. Jake parametry
   to jsou a v jakem poradi se zadavaji naleznete v helpu daneho prikazu.
   Help prikazu si zobrazite zadanim "help prikaz" nebo zkracene "h
   prikaz" nebo take "? prikaz". Napriklad kdyz chcete znat parametry
   prikazu login, zadate: "help login".

   Priklad:
> help login
> ?login

   Vypisou se podrobnosti o jednotlivych parametrech daneho prikazu.
   Samotny prikaz zadate tak, ze napisete nazev prikazu a za nim jeho
   parametry:
> login username password

Syntaxe zadavani parameru prikazu

   Na zadani parametru EPP prikazu jsou kladeny zvlastni pozadavky, kvuli
   kterym byla zavedena specialni syntaxe. Parametry, na ktere neni nutne
   pouzit tuto syntaxi nazyvame jednoduche hodnoty. To jsou hodnoty, ve
   kterych se nevyskytuje mezera a ani to nejsou seznamy. Napriklad:
username password

   Parametry jsou oddeleny mezerou nebo mohou byt oddeleny i vice
   mezerami.

   Syntaxe obsahuje tyto prvky:
     * ' " uvozovky (jednoduche nebo dvojite)
     * ( ) zavorky
     * - spojovnik (divis) a = (rovna se)
     * . tecka
     * [] hranate zavorky

   Popis jednotlivych prvku:
     * ' " uvozovky resi pozadavek na zadani hodnoty, ktera obsahuje
       mezery nebo znak = (rovna se). Takova hodnota se uzavre do
       uvozovek. Je jedno jestli jednoduchych nebo dvojitych. Uvnitr
       uvozovek se pak mohou nachazet libovolne znaky vcetne zavorek,
       spojovniku a dalsich uvozovek. Pokud to jsou ale uvozovky shodne s
       temi, ktere jsou pouzity na uzavreni textu, tak se pred ne musi dat
       zpetne lomitko \ (backslash):
"text \"uvozovky\" text"
       Jinak mohou byt bez nej:
"text s 'jednoduchymi' uvozovkami"
       nebo
'text s "dvojtymi" uvozovkami'
       nebo
'text s rovnitkem = '
     * ( ) zavorky se pouzivaji pro parametr, ktery muze obsahovat seznam
       hodnot. Napriklad parametr street v prikazu create_contact muze byt
       seznam az o trech polozkach. Kdyz chcete zadat jen jednu ulici,
       staci zadat pouze:
ulice1
       Program vi, ze parametr ma byt seznam a tak tuto hodnotu vyhodnoti
       jako seznam s jednou polozkou. Nemusite tedy zadavat: (ulice1).
       Kdyz chcete zadat vice ulic, tak napisete:
(ulice1 ulice2 ulice3)
       Lze samozrejme kombinovat se syntaxi s uvozovkami:
("ulice 1" "ulice 2" "ulice 3")
       Polozky seznamu je mozne krome mezer oddelit i carkou:
(ulice1,ulice2,ulice3)
(ulice1, ulice2, ulice3)
("ulice 1", "ulice 2", "ulice 3")

       Nektere prikazy maji parametr typu seznam, ktery dale obsahuje
       dalsi seznamy. Takovy seznam take nazyvame jmenny prostor, protoze
       obsahuje dalsi polozky, ktere lze definovat jmenem. Ty mohou byt
       jednoduche nebo to mohou byt dalsi seznamy. Je potreba zadavat
       zavorky tak, aby zapis odpovidal strukture parametru. Strukturu
       zanorenych seznamu zjistite take z helpu prikazu. Kazda uroven je
       odsazena.
       Napriklad prikaz update_contact obsahuje seznam chg, ktery dale
       obsahuje senzam postal_info, ktery obsahuje hodnoty name, org a
       jeste dalsi seznam addr. Seznam addr obsahuje polozky city, cc,
       street, atd. Takovy seznam se zapise asi takto:
((name, org, (city, cc, street, sp, pc)) voice, fax, ...)

       Porovnejte s priklady, ktere jsou uvedeny v helpu u kazdeho
       prikazu.
     * - spojovnik (divis) a = (rovna se). Parametry se musi zadavat ve
       stanovenem poradi. Nejdrive se vzdy zadavaji povinne polozky a pak
       nepovinne. Zadavani prikazu tedy muzete ukoncit za poslednim
       povinnym parametrem. Pokud ale chcete zadat jeste nejaky nepovinny,
       ktery se shodou okolnosti nachazi nekde vzadu nebo na konci rady
       parametru, museli byste zapsat i ty nepovinne parametry, ktere se
       nachazeji pred nim, aby se zachovalo spravne poradi. To vsak neni
       nutne pokud hodnotu zadate pomoci "pojmenovaneho parametru".
       Pojmenovany parametr je zpusob, jak vlozit hodnotu parametru mimo
       poradi. Princip je ten, ze se uvede jmeno parametru, kteremu
       hodnota patri. Toto jmeno zjistite z helpu prikazu. Pak jmeno a
       hodnotu zadate ve tvaru
-jmeno hodnota

       Podle spojovniku na zacatku slova parser pozna, ze se jedna o jmeno
       parametru. Za nim pak nasleduje hodnota. Tato syntaxe je volna v
       tom smeru, ze je mozne zadat spojovniku vice a mezi jmenem a
       hodnotou muze byt rovnitko. Pak takovy zapis vypada takto:
--jmeno = hodnota

       Hodnoty, ktere jsou definovany pomoci pojmenovaneho parametru,
       stoji MIMO poradi ostatnich parametru. To znamena, ze mohou byt
       uvedeny na kterekoliv pozici mezi parametry a hodnoty za nimi maji
       stale stejnou pozici, jako kdyby tam nic uvedeno nebylo (viz
       nasledujici priklad).
       Napriklad kdyz si vypisete help pro prikaz create_contact, tak
       predposledni parametr se jmenuje notify_email. Krome povinnych
       chcete zadat jiz pouze tuto hodnotu (povinnych je prvnich pet
       parametru: ID, jmeno, email, mesto a kod zeme). Pak zadate:
create_contact CID:ID jmeno email@email mesto CZ --notify_email = muj@email.net

       Na pozici pojmenovaneho parametru nezalezi:
create_contact --notify_email = muj@email.net CID:ID jmeno email@email mesto CZ

     * Tecka. Slozitejsi pripad nastane, kdyz chcete definovat hodnotu,
       ktera se nachazi v nejakem "zanorenem seznamu", tj. seznamu v jinem
       seznamu. Pak se jednotliva jmena seznamu spojuji pomoci tecky.
       Napriklad:
create_contact CID:ID jmeno email@email mesto CZ --disclose.flag = y

     * [] hranate zavorky. V pripade, ze hodnota je polozkou v seznamu, je
       mozne zadat i index seznamu. Ten se zadava pomoci cisla v hranatych
       zavorkach:
create_nsset nssid:nsset1 ((ns1.domain.cz (217.31.207.130 217.31.207.129))) --dn
s.addr[1] = tato_hodnota_prepise_druhou_adresu_217.31.207.129 cid:regid

   Shrnuti:
   Parametry zadavejte v poradi, v jakem jsou vypsane v helpu.
   Pocet mezer mezi hodnotami muze byt libovolny.
   Hodnoty s mezerami dejte do uvozovek.
   Seznamy se definuji pomoci zavorek, polozky seznamu muzou byt oddeleny
   carkami.
   Pokud je v seznamu jen jedna polozka, nemusi se zavorky zadavat.
   Hodnoty mimo poradi zadavejte pomoci "pojmenovaneho parametru."
   Jmena polozek zanorenych do vice seznamu spojite pomoci tecky.

Spolecny parametr cltrid (Client transaction ID)

   Kazdy EPP prikaz, krome prikazu hello, obsahuje tag <clTRID>. Ten je
   vzdy jako posledni z parametru a jmenuje se cltrid. Tato hodnota je
   identifikator transakce. Ten si stanovuje klient a muze byt libovolny v
   ramci formatovacich pravidel definovanych ve schematech pro tuto
   hodnotu. Identifikator je nepovinny a pokud neni zadan, tak jej klient
   automaticky doplni.

   Element <clTRID> lze potlacit specialni hodnotou SKIP.

   Dalsi moznost, jak zadat tento parametr je nadefinovat jej v
   konfiguracnim souboru nebo pri spusteni klienta v parametrech pri
   spusteni (options).

   Jednotlive prikazy jsou v ramci relace cislovany. Pokud se v hodnote
   cltrid vyskytne zastupce %d, je tento symbol nahrazen poradovym cislem
   prikazu:
myCtrlID%d  - je zkonvertovan na myCtrlID1, myCtrlID2, myCtrlID3, ...

   Chcete-li aby poradove cislo melo vzdy stejny pocet cislic, je mozne
   zadat:
myCtrlID%04d  - je zkonvertovan na myCtrlID0001, myCtrlID0002, myCtrlID0003, ...

Zadna hodnota / Prazdna hodnota

Zadna hodnota: NULL

   Vyraz Zadna hodnota predstavuje hodnotu, kterou jste nezadali. Slouzi
   nam k tomu, abychom mohli preskakovat parametry, ktere nechceme
   zadavat. Je to alternativa k zadavani hodnot pomoci pojmenovaneho
   parametru. Defaulte je zastupce zadne hodnoty nastaven na NULL.

   Napriklad, kdyz v prikazu create_contact chcete krome povinnych
   parametru uvest uz jen telefonni cislo (parametr voice). Mezi poslednim
   povinnym parametrem pw a poradovanym voice lezi jeste dalsi ctyri
   parametry: org, street, sp, cp. Misto nich zadate "zadnou hodnotu" -
   pokud jste nenastavili jinak, tak NULL. Tim jste telefonni cislo
   umistili na spravnou pozici v parametrech prikazu:
   create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword NULL N
ULL NULL NULL +420.222745111

   Uvedeny prikaz nebude v XML strukture vytvaret tagy pro hodnoty org,
   street, sp, cp:
<contact:id>CID:ID01</contact:id>
        <contact:postalInfo>
          <contact:name>Jan Novak</contact:name>
          <contact:addr>
            <contact:city>Praha</contact:city>
            <contact:cc>CZ</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>+420.222745111</contact:voice>

   V interaktivnim modu zadavani parametru zadate "zadnou hodnotu" proste
   tak, ze jenom stisknete ENTER.

   Definici zadne hodnoty lze v konzoli zmenit prikazem null_value a take
   je mozne si ji definovat v konfiguracnim souboru.

Prazdna hodnota: '', ""

   Vyraz Prazdna hodnota predstavuje hodnotu, ktera je prazdna. Je to tedy
   text o nulove delce. Ten zapisujeme praznymi uvozovkami '' nebo "".
   Tato hodnota nam slouzi k tomu, abychom mohli zadavat hodnoty nulove
   delky. Rozdil mezi praznou hodnotou a zadnou je v tom, ze tato hodnota
   generuje tag v XML dokumentu. Protoze je prazdna, tak dany XML tag bude
   take prazdny.
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

   V interaktivnim modu zadavani parametru zadame "prazdnou hodnotu" tak,
   ze zapiseme prazdne uvozovky '' nebo "".

Interaktivni mod vkladani parametru

   Interaktivni mod umoznuje zadavat hodnoty jednu za druhou, podle toho
   co prompt aktualne pozaduje. Tento zpusob je vhodny zejmena pokud
   nevite presne jak mate parametry zadat. Interaktivni mod se spousti
   pomoci vykricniku, ktery se napise pred prikaz:
> !update_nsset

   Konzole vzdy vypise jmeno parametru a ceka na zadani hodnoty. Pokud
   hodnotu nechcete zadat, tak proste stisknete enter a hodnota se
   preskoci. Interaktivni mod muzete kdykoliv zrusit stisknutim klaves
   Ctrl+C (C jako Cancel). Po zadani vsech povinnych parametru, kdy uz
   nechcete zadavat dalsi nepovinne hodnoty, lze interaktivni rezim
   dokoncit stiknutim klaves Ctrl+D (D jako Done nebo Dokoncit).

   V pripade zruseni interaktivniho modu se zadny prikaz nesestavi a nic
   se na server neposila. V pripade dokonceni modu se sestavi prikaz a na
   konzoli se vypise tak, jako byste jej zadali primo bez interaktivniho
   rezimu. Pak se prikaz odesle na server. V pripade, ze se jedna o
   "editacni" prikaz a je zapnuta funkce potvrzovani (confirm), tak se
   prikaz musi pred odeslanim na server jeste potvrdit:
REG-LRR@epp-test.ccreg.nic.cz> !update_nsset
Start interaktivniho modu. Mod zrusite stisknutim Ctrl+C. Prikaz dokoncite kombi
naci Ctrl+D.
NSSET ID [povinny]: nssid:id01
Pridat hodnoty / Seznam DNS[1/9] / Jmenny server [povinny jen je-li tato cast za
dana]: ns1.dns.cz
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[1/oo] [nepovinny]: 217.31.207.
130
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[2/oo] [nepovinny]: 217.31.207.
131
Pridat hodnoty / Seznam DNS[1/9] / Adresa serveru[3/oo] [nepovinny]:
Pridat hodnoty / Seznam DNS[2/9] / Jmenny server [nepovinny]:
Pridat hodnoty / Technicky kontakt ID[1/oo] [nepovinny]: cid:myid01
Pridat hodnoty / Technicky kontakt ID[2/oo] [nepovinny]:
Pridat hodnoty / Stav[1/6] [nepovinny]:
Interaktivni mod ukoncen. [stisknete Enter]
Prikaz k odeslani:
update_nsset nssid:id01 (((ns1.dns.cz (217.31.207.130, 217.31.207.131))) cid:myi
d01)
Opravdu chcete odeslat tento porikaz na server? (y/N): y
nssid:id01 aktualizovano.
REG-LRR@epp-test.ccreg.nic.cz>

Prikazy relace (session)

   Konzole ma sva vnitrni nastaveni, ktera muzete zmenit primo z promptu.
   K tomu slouzi prikazy, ktere nazyvame prikazy relace. Nejsou to EPP
   prikazy a neslouzi ke komunikaci se serverem. Jsou urceny z nastaveni
   vnitrnich promennych konzole a nebo k zobrazeni jiz nastavenych hodnot.
   Takto nastavene hodnoty se neukladaji. Jsou platne jen po dobu relace -
   spusteni konzole. S ukoncenim aplikace zanikaji. Pokud chcete tato
   nastaveni mit trvala, musite je nastavit v konfiguracnim souboru.

   Hodnoty se nastavuji tak, ze se zada prikaz relace a za nim hodnota,
   ktera se ma priradit:
> poll_autoack on

   Pokud prikaz zadate bez parametru, tak se pouze vypise aktualni stav
   nastaveni.
> poll_autoack
poll_autoack je ON

   Seznam prikazu relace:

> poll_autoack [on/off]

   Pokud je tento prepinac ON, tak se po odeslani prikazu "poll req"
   automaticky odesila i "poll ack". Tuhle funkci asi nejvice ocenite,
   kdyz budete mit na serveru hodne zprav. Prikaz "poll req" zpravu ze
   serveru pouze zobrazi, ale pak se zprava musi ze serveru odstranint
   prikazem "poll ack ID-zpravy". Pri automatickem poll-ack se bude
   odstranovani provadet automaticky po zobrazeni zpravy.
> escaped_input [on/off]

   Pokud je vstup escapovany (&lt;example&amp;test&gt;), nastavte tuto
   hodnotu na on.
> confirm [on/off]

   U EPP editacnich prikazu, ktere nejak meni hodnoty na serveru (create,
   upadte, delete, transfer, renew), se pred odeslanim pozaduje potvrzeni
   k odeslani. Prepinacem "confirm OFF" lze toto potvrzovani vypnout.
> credits

   Prikaz credits zobrazi text s informacemi o klientovi.
> help [prikaz]

   Prikaz help zadany bez parametru zobrazi seznam dostupnych prikazu.
   Pokud se zada i parametr prikaz, tak se zobrazi detaily zadaneho
   prikazu. Stejny vyznam jako "help" maji i prikazy "h" a "?".
> lang [kod]

   Prikazem lang se prepina jazykova verze klienta a serveru. Pokud jste
   ale jiz zalogovani, tak je nutne se odlogovat a znovu zalogovat. Duvod
   je ten, ze typ jazykove verze se serveru sdeluje pouze pomoci prikazu
   "login". To je take druha moznost, jak prepnout na jinou jazykovou
   verzi: "login usename password cs" V teto verzi klienta i serveru jsou
   dostupne jen dva jazyky: en - anglictina; cs - cestina.
> license

   Prikaz license zobrazi text licence klienta.
> quit

   Prikaz quit odpoji klienta od serveru a ukonci aplikaci. Synonyma 'q' a
   'exit' maji stejnou funkci.
> validate [on/off]

   Timto prepinacem zapnete nebo vypnete proces validace XML dokumentu.
   Validace je v teto verzi realizovana pres externi program xmllint.
   Pokud neni v systemu pritomen, tak nastaveni ON nema zadny efekt.
   Validace overuje platnost XML dokumentu podle EPP schemat a to jak v
   odchozich, tak i prichozich zpravach. Pokud neni dokument validni, tak
   jej konzole na server neodesle. Nevalidni dokument vznikne napriklad
   tim, ze zadate hodnotu, ktera neodpovida konkretnimu schematu.
   Napriklad prilis kratke heslo. Konzole v teto verzi obsah hodnot nijak
   neoveruje, pouze zjistuje jestli byly zadany nebo ne.
> verbose [uroven]

   Klient zobrazuje ruzne informace. Ty jsou rozdeleny do urovni detailu.
   Prvni uroven zobrazovani (zakladni) je urcena pro bezneho uzivatele a
   vypisuje nezbytne minimum informaci, ktere jsou k praci nutne. Pro
   zvidave uzivatele je zacilena druha uroven, ktera vypisuje vsechna
   dostupna hlaseni, ktera se behem komunikace vyskytla. Treti uroven
   zobrazuje jeste navic XML zdrojove dokumenty, ktere si klient se
   serverem predava.
   Urovne vypisu detailu:
   1 - strucna (default)
   2 - vsechno
   3 - vsechno a XML zdroje.

   Uroven vypisu lze nastavit i pri spusteni prikazoveho radku. Viz
   konfiguracni soubor.
> fetch_from_info typ_prikazu [ne-do-prikazove-radky]

   Funkce fetch_from_info umoznuje vytvorit prikaz z hodnot, ktere byly
   nacteny z jednoho z prikazu typu info v predchozim kroku. To je
   napriklad uzitecne, kdyz chcete vytvorit novy zaznam s velmi podobnymi
   udaji, jake jsou jiz v nejakem zzaznamu pouzity. Platne typy prikazu,
   ktere muzete pomoci fetch_from_info vytvorit jsou: create, update,
   delete.

   Napriklad, kdyz chcete vytvorit create_contact, provedte tyto tri
   kroky:
   1. Nactete hodnoty: info_contact CID:ID
   2. Vytvorte prikaz: fetch_from_info create
   3. Upravte prikaz jak potrebujete a pak jej odeslete na server.

   Pokud vas terminal podporuje vkladani textu do prikazove radky (Unix),
   bude vytvoreny prikaz vlozen primo do nej. Chcete-li prikaz misto do
   prikazove radky zobrazit jen na vystup, zadejte parametr noprompt (nebo
   jen n).

   Pokud vas terminal vkladani do promptu nepodporuje (Windows), bude
   prikaz zobrazen normalne na vystupu a musite si jej do prikazove radky
   zkopirovat nebo prepsat.

Kapitola 5. Skripty fred_create.py a fred_sender.py

   Skripty fred_create.py a fred_sender.py jsou urceny pro pouziti v shell
   batchi. fred_create.py prijima parametry se standardniho vstupu a
   vygeneruje XML EPP dokument na standardni vystup. Napriklad:
    $ python fred_create.py info_domain nic.cz
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py
    $ cat file-with-commands.txt | ./fred_create.py

   <?xml version='1.0' encoding....

   Pokud nastane nejaka chyba, tak vraci XML s chybovym hlasenim:
    $ python fred_create.py inxo_domain nic.cz

   <?xml encoding='utf-8'?><errors>inxo_domain nic.cz: Neznamy
   prikaz!</errors>

   fred_sender.py odesila dokumenty na server. Skript se automaticky
   zaloguje, pak preda dokument, zobrazi odpoved a odloguje se a ukonci.
   Pro spravne zalogovajni je nutne mit spravne nastaven konfiguracni
   soubor.

   Skript muze odesilat dokumenty dvema zpusoby:

   1. dokumenty se ulozi do souboru a skriptu se predaji jmena souboru.
   Skript je pak odesila v uvedenem poradi. Napriklad:
    $ ./fred_create.py check_domain cosi.cz nic.cz > doc1.xml
    $ ./fred_create.py info_domain nic.cz > doc2.xml
    $ ./fred_sender.py doc1.xml doc2.xml

   2. PIPE - Zretezenim prikazu create a sender. Napriklad:
    $ ./fred_create.py check_domain cosi.cz nic.cz | ./fred_sender.py
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py | ./
fred_sender.py

Kapitola 6. Integrace klienta do PHP kodu

   Pozor! Rozsireni klienta o podporu PHP je v teto verzi ve vyvojovem a
   testovacim stadiu. Finalni reseni se muze od tohoto vyvojoveho jeste
   lisit.

   Soucasti distribuce klienta je i ukazkovy PHP skript, ktery
   demonstruje, jak lze klienta zaclenit do PHP: doc/client_example.php. V
   prikladu je nutne spravne nastavit cestu ke klientovi $exec_path (pokud
   ten nebyl nainstalovan standardnim zpusobem a system jej nenalezne).
   Promenou $php_module_name se nastavuje presmerovani do souboru a
   $command_options umoznuji pridat dalsi parametry, jsou-li treba.

   Popis zacleneni klienta:

   Klient fred_client lze spustit i tak, ze se mu v parametrech na
   prikazove radce zada prikaz, ktery ma vykonat -d --command. V takovem
   pripade se nespousti konzole, ale klient funguje jako batch. Stejne
   jako kombinace skriptu fred_create.py a fred_sender.py. Klient pouze
   zadany prikaz provede, zobrazi vystup a ukonci se. Prihlaseni a
   odhlaseni (login, logout) probehnou automaticky a na vystup se
   nevypisuji. Pro spravne prihlaseni je proto potrebne mit nastaveny
   konfiguracni soubor nebo vse definovat na prikazove radce.

   Prepinacem --output -o upravime vystup do pozadovaneho formatu. Pokud
   chceme v prohlizeci hodnoty pouze zobrazit, muzeme zadat typ HTML:
   --output=html. Chceme-li data dale zpracovavat PHP skriptem, nastavime
   typ PHP: --output=php.

   Shrnuti metody pouziti klienta v PHP:
   V PHP se klient spusti jako externi program napriklad funkci
   passthru().
   V parametrech se nastavi mod vypisu na PHP: --output=php
   Vystup klienta se presmeruje do adresare s pravy zapisu: ... >
   /cache/output.php
   Vysledny kod se vlozi do stranky required_once('/cache/output.php') a
   tim jsou hodnoty PHP skriptu dostupne.

   Promenne z PHP vystupu
   $fred_error_create_name = 'poll'; // jmeno neplatneho prikazu
   $fred_error_create_value = 'op: Value "xxx" is not allowed. Valid is:
   (req, ack)'; // popis chyby, ktera se objevila pri vytvareni prikazu.
   $fred_client_notes = array(); // seznam hlaseni, ktere se generuje
   behem komunikace
   $fred_client_errors = array(); // seznam chyb, ktere vznikly behem
   komunikce
   $fred_encoding = 'utf-8'; // kodovani textu
   $fred_code = 1000; // navratovy kod odpovedi
   $fred_command = 'domain:info'; // nazev odeslaneho prikazu
   $fred_reason = 'Command completed successfully'; // popis navratoveho
   kodu
   $fred_reason_errors = array(); // detaily hodnot, ktere zpusobily
   navraceni kodu s chybou
   $fred_labels = array(); // seznam popisku hodnot
   $fred_data = array(); // seznam hodnot
   $fred_source_command = '<?xml ... >'; zdrojovy XML dokument prikazu
   generuje se jen ve verbose 3).
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

Kapitola 7. Graficka nadstavba v Qt4.

   Popis graficke nadstavby klienta je v samostatnem souboru README_QT4.

Kapitola 8. Knihovna fred a popis API

   Obsah

   Online dokumentace:
   Priklady prace s knihovnou

   Knihovna "fred" vam umonuje implmentovat API rozhrani do vasich
   aplikaci. Knihova i jednotlive funkce obsahuji komentare, podle kterych
   se muzete pri implementaci ridit. V casti __init__.py naleznete i
   ukazky kodu.

Online dokumentace:

   Pokud si chcete projit jednotlive tridy a funkce knihovny, tak k tomu
   muzete vyuzit generator dokumentace pydoc, ktery je standardni soucasti
   pythonu. Generator ma nekolik modu cinnosti. Popis naleznete v helpu
   pydoc. Pokud jako parametr zadate nazev souboru nebo modulu, tak se
   dokumentace zobrazuje ve stylu manualove stranky:
    $ pydoc fred

   Chcete-li generator spustit, jako HTML server, tak zadejte na prikazove
   radce prikaz:
    $ pydoc -p 8080

   Pokud se server nespusti, tak zkuste:
    $ python `which pydoc` -p 8080

   Tim jste spustili webovy server, ktery generuje strany dokumentace
   primo ze zdrojovych souboru. Parametr -p udava na jakem portu je server
   spusten. Cislo portu muzete zadat jakekoliv jine. Nyni si otevrete
   prohlizec a zadejte adresu: http://localhost:8080/. Otevre se strana,
   na ktere v casti ../site-packages naleznete odkaz na fred (package).

   Pokud jste skripty neinstalovali, ale jen nakopirovali, nebo pokud se
   chcete podivat i na skripty pracujici s knihovnou fred, tak cely proces
   spusteni udelejte stejne, ale s tim rozdilem, ze pydoc spustite z
   adresare, kde mate tyto skripty ulozene. Pak se v helpu zobrazi i ony:
    $ cd FredClient-n.n.n
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

   Kazda funkce (EPP prikazu) vraci tuto "retval" hodnotu, ktera je typu
   dict a ve tvaru:
    {'reason': u'Text of answer reason',
     'code': 1000,
     'command': 'command_name',
     'errors': []
     'data': {'key': 'value' [,'next-key':'next-value']},
    }

   Klic "reason" (str) je vyrozumeni serveru o stavu odpovedi.
   Klic "code" (int) je cislo, ktere definuje typ chyby. Cislo 1000
   znamena OK - vse vporadku.
   Klic "command" (str) je nazev prikazu, na ktery se odpoved vztahuje
   (ktery odpoved vyvolal).
   Klic "errors" (list) je seznam chyb, ktere server nalezl.
   Klic "data" (dict) je slovnik s hodnotami individualnimi pro kazdy
   jednotlivy prikaz.

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

   Kazde volani dalsi funkce EPP prikazu samozrejme predchozi "retval"
   prepise, takze uvedene dve funkce pracuji vzdy jen s posledni
   navratovou hodnotou. Pokud chcete navratovou hodnotu testovat nebo
   zobrazit pozdeji, tak si ji ulozte a pak ji predejte funkcim:
    >>> epp.print_answer(my_retval)
    >>> epp.is_val('reason', my_retval)

   Funkci is_val() je mozno zadat bez parametru. V takovem pripade
   defaultne vraci hodnotu klice "code":
   >>> epp.is_val()
    1000

   Pokud chcete zjistit hodnotu v jakekoliv vnorene casti slovniku, tak
   zadejte parametr jako cestu - seznam jmen (klicu) slovniku:
    >>> epp.is_val(('data','next-key'))
    next-value

   V pripade, ze dany klic neexistuje, vraci funkce hodnotu None.
    >>> epp.is_val(('data','any-key'))
    None

   Pokud se vyskytne nejaka chyba pri prenosu nebo jina, ktera zablokuje
   funkcnost, tak se generuje vyjimka FredError.
