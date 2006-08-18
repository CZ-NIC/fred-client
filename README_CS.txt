# -*- coding: utf8 -*-
# Tento dokument je ulozen v kodovani UTF-8.

##################################################################

    Manuál pro ccRegClient konzoli a knihovnu ccReg
    
    Verze 1.1

##################################################################

CO JE ccRegClient:

ccRegClient je sada scriptů v jazyce Python postavených na ccReg knihovně
a určených ke komunikaci s EPP serverem.
Sada obsahuje EPP konzoli a skripty určené pro použití v shellu.


OBSAH:

    1. Licence
    2. Požadavky na systém a instalace
    3. Popis jednotlivých programů a configu
    4. Program ccreg_console.py
    5. Programy ccreg_create.py a ccreg_sender.py
    6. knihovna ccReg a popis API


================================================

    1. Licence

================================================
Licence je v souboru ccReg/LICENSE.



================================================

    2. Požadavky na systém a instalace

================================================
Pokyny k instalaci jsou v souboru INSTALL.



================================================

    3. Popis jednotlivých programů,
       parametry a config

================================================

Dostupné skripty jsou následující:
 
    ccreg_client.py   - spouští EPP konzoli nebo sekvenci crate+send (pro shell)
    ccreg_console.py  - EPP konzole, komunikuje s EPP serverem
    ccreg_create.py   - Vytboří zdrojový EPP XML příkaz
    ccreg_sender.py   - Odešle soubor na EPP server

------------------------------------------------

    3.1 Parametry (OPTIONS)

------------------------------------------------

Skripty se dají spouštět s parametry. Jaké parametry lze použít zjistíte 
zadáním parametru --help nebo -?:

    $ ccreg_client.py --help
    $ ccreg_client.py -?

Použití: python ccreg_console.py [OPTIONS]
Konzole pro komunikaci s EPP serverem.

OPTIONS s hodnotami:
    -s --session  název session, který se má použít pro spojení s EPP serverem
                  session hodnoty jsou načteny z config souboru a mohou obsahovat
                  cesty k certifikátu, soukromému klíči, 
                   
    -h --host     jméno host (přepíše config hodnotu)
    -u --user     jméno user (přepíše config hodnotu)
    -p --password heslo (přepíše config hodnotu)
    -l --lang     jazyková verze
    -v --verbose  mód výpisu: 1,2,3; default: 1
                  1 - zkrácený
                  2 - plný
                  3 - plný & XML zdroje
    -c --command  odeslání příkatu na EPP server
                  příklad: --command='info-domain nic.cz'

OPTIONS:
    -r --colors   zapnutí barevného výstupu
    -? --help     tento help


------------------------------------------------

    3.2 Config

------------------------------------------------
Config je společný pro všechny skripty a je uložen v souboru .ccReg.conf. 
Nejdříve se hledá v adresáři společném pro všechny uživatele. 
Na POSIX systémech je to /etc, v MS Windows v adresáři nastaveném v proměnné
$ALLUSERSPROFILE.
Pokud tam není nalezen, hledá se v domovském adresáři uživatele.
Konfig soubor lze vygenerovat v konzoli. Spusťte si konzoli
příkazem ccreg_console.py (nebo ccreg_client.py) a zadejte příkaz "config create".
Další podrobnosti naleznete v části popisu práce s konzolí (4. Program ccreg_console).

V konfigu se nachází sekce connect, kde jsou uloženy cesty k certifikátům
a informace o serveru. Také tam můžou být přihlašovací údaje pro login.
Příkaz ''login'' tak může být zadán bez parametrů.

Zde je příklad konfigu:

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

Sekcí ''connect'' může být více. Která z nich se při startu použije se nastaví
pomocí parametru --session. Například si vytvoříte sekci [connect_myeppserver]
tu pak aktivujete: 

    $ ccreg_client.py --session=myeppserver     (nebo -s myeppserver)

    [connect_myeppserver]
    dir=/test/certificates
    host = myeppserver.cz
    ssl_cert = %(dir)s/cert.pem
    ssl_key  = %(dir)s/key.pem
    username = myusername
    password = mypassword

V sekci ''session'' jsou tato nastavení:

    poll_ack = on/off 
        Při ''on'' se po odeslání příkazu ''poll req'' automaticky
        pošle i ''poll ack''.

    confirm_send_commands = on/off
        Všechny editační příkazy (create, delete, update, ...) vyžadují v konzoli
        pozvrzení před odesláním na server. Toto potvrzení lze vypnout/zapnout.

    validate = on/off
        K validaci se používá externí program xmllint. Validaci lze vypnout
        a dokumnety se tak na server posílají bez ověření platnosti formátu.

    schema = /installdir/schemas/all-1.0.xsd
        Adresář, kde má validátor hledat schemata, podle kterých dokumenty ověřuje.

    colors = on/off
        Výstup na terminál může být barevný, pokud to terminál umožňuje.

    verbose = 1/2/3
        Úroveň výpisu 1 - stručná, 2 - celá, 3 - celá + XML zdrojové dokumenty.

    lang = en/cs
        Jazyková verze. Pokud není zadána žádná hodnota, tak se bere nastavení
        z proměnné LANG prostředí OS. Dostupné jsou zatím jen angličtina a čeština.
        Jazykovou verzi můžete nastavit i pomocí parametru při spuštění skriptu.


================================================

    4. Program ccreg_console.py

================================================

ccreg_console.py je konzole, která komunikuje s EPP serverem. Konzoli spustíte
příkazem:

    $ ccreg_console.py

Pokud máte v configu správně nadefinovánu cestu k certifikátům a uložené login a heslo, 
tak můžete jednoduše zadat ''login'' a tím se spojíte s EPP serverem.
Konzole se ukončuje příkazem "quit" nebo jen krátce "q".

2.1 Zobrazení helpu

Jaké příkazy máte k dispozici zjistíte zadáním příkazu "help" (nebo h, ?).

    ccReg client verze 1.1 Zadejte "help", "license" nebo "credits" pro zobrazení více informací.
    > help

Help vypíše dvě části nápovědy:

    1) Dostupné EPP příkazy
    2) Příkazy relace (session) pro nastavení vnitřních proměnných 
       konzole



2.2 EPP příkazy

EPP příkaz zadáváte společně s jeho parametry. Jaké parametry příkaz
požaduje zjistíte, když zadáte "help příkaz" nebo zkráceně "h příkaz"
nebo také "? příkaz".
Například:

    > ?login

Vypíšou se podrobnosti o jednotlivých parametrech daného příkazu. 
Samotný příkaz zadáte tak, že napíšete název příkazu a za ním jeho parametry:

    > login moje-ID moje-heslo




2.2.1 Typy paramerů příkazu:

INSTRUKCE:

    * parametry zadávejte v pořadí, v jakém jsou vypsané v helpu
    * hodnoty s mezerami dejte do uvozovek
    * seznamy se definují pomocí závorek, položky seznamu můžou 
      (ale nemusí) být odděleny čárkami
    * pokud je v seznamu jen jedna položka, nemusí se závorky zadávat
    * jmenné prostory se také jako seznamy definují pomocí závorek
    * chcete-li seznam nebo jmenný porostor vynechat, zadejte jen 
      prázdné závorky
    * hodnoty mimo pořadí zadávejte pomocí klíče

VYSVĚTLENÍ:

    * jednoduchá hodnota:  my-value01
    * hodnota s mezerou:   'lorem ipsum'   "some value"
    * seznam:              (one two three)
    * jmenný prostor:      ((one two three) my-value01 'lorem ipsum' (enyky benyky) end-value)

Pokud hodnota parametru obsahuje mezeru, tak ji napište do uvozovek. 
Například:

    > login moje-ID "moje heslo s mezerami"

Některé parametry můžou obsahovat seznam hodnot. Například parametr 
"street" v příkazu create-contact.
Výpis části helpu:

    ?create-contact
    ...
    ... street (nepovinný)  seznam o maximálně 3 položkách.
    ...

Seznam zadáte tak, že hodnoty uzavřete do závorek:

    > create-contact my-ID my-name mail city 
            cc org (Vodičkova, "Na příkopě", "U přívozu") voice

Pokud zadáváte jen jednu hodnotu ze seznamu, tak závorky zadávat
nemusíte:

    > create-contact my-ID my-name mail city cc org Vodičkova voice

Parametry musíte zadávat v pořadí, v jakém jsou v helpu vypsány. Povinné
jsou vždy na začátku a nepovinné tak není nutné zadávat. Pro případ, že
chcete kromě povinných hodnot zadat ještě nějakou nepovinnou, která ale
NENÍ v pořadí, tak máte možnost ji zadat MIMO pořadí zadáním jména 
parametru - klíče. To řeší situaci, kdy by se kvůli jednomu parametru
na konci řady musely zadávat všechny parametry před ním.

Klíč (jméno parametru) se definuje pomocí jednoho nebo dvou spojovníků.
Například chcete v příkazu create-contact zadat kromě povinných údajů už
jen hodnotu "notify email", která se nachází právě na úplném konci
seznamu parametrů. Pak tuto hodnotu zadáte takto:

  > create-contact my-ID my-name mail city cc --notify_email = muj@mail.cz

Jaký má být klíč (název parametru) zjistíte z helpu daného příkazu.
Parametr s klíčem pak již nemusí být na "své" pozici, ale může být
kdekoliv v řadě mezi ostatními parametry. Takový parametr stojí "mimo"
pořadí a nenarušuje pozice ostatních parametrů bez klíče. Zde jsou 
do řady parametrů vloženy hodnoty s klíči "vat" a "notify_email":

    > create-contact my-ID my-name mail --vat = 12346 --notify_email = muj@mail.cz city cc

Některé příkazy mají parametry vnořené do dalších parametrů. Ty vytvářejí
jmenné prostory. Například v příkazu "create-contact" je parametr 
"disclose". Ten obsahuje další parametry "flag", "data", atd. Samotný
název "disclose" není v tomto případě název klíče, ale název jmenného
prostoru, ve kterém se nacházejí klíče "flag" a "data". Jmenné
prostory se definují stejně jako seznamy pomocí závorek:

  > create-contact my-ID my-name mail city cc org street sp pc 
        voice fax (n (name org addr voice fax email)) vat ssn

Pokud jmenný prostor nechcete zadávat, napište prostě jen prázdné
závorky. To platí i pro seznamy:

  > create-contact my-ID my-name mail city cc org street sp pc voice fax () vat ssn notify@email

Některé příkazy mají v parametrech seznamy jmenných prostorů. V takovém
případě pak závorky mají své významy podle toho, jak jsou hodnoty
strukturované. Například příkaz "update-nsset" má jeden 
nepovinný parametr "add". Pokud jej nechcete zadávat, tak napíšete:

  > update-nsset id () ...    - parametr add je nyní prázdný

Pokud ale "add" zadat chcete, tak "add" (jak vidíte v helpu) obsahuje
seznam devíti jmenných prostorů "dns"! Každý "dns" prostor pak dále
obsahuje parametr "name" a seznam "addr". Pokud chete tyto hodnoty zadat, 
tak musíte zapsat všechny závorky, které jsou nutné: První závorka pro definování 
jmenného prostoru "add". Druhá závorka pro začátek seznamu jmenných prostorů "dns".
Třetí závorka pro samotný jmenný prostor "dns". Teprve pak následuje
hodnota parametru "name". Za ním pak následuje závorka seznamu "addr":

  >  update-nsset nsset1 (((ns1.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132)), 
        (ns2.dns.cz (217.31.207.130, 217.31.207.131, 217.31.207.132))) (tech1, tech2, tech3) 
        (ok, clientTransferProhibited)) (((rem1.dns.cz, rem2.dns.cz) (tech-rem01, tech-rem02) 
            serverUpdateProhibited)) (password)

Pokud "addr" není seznam, ale jen jedna hodnota, tak se závorky pro
"addr" zadávat nemusí:
(To je pravidlo již zmíněné v předchozím textu.)

  > update-nsset nsset-ID (((nsset1 217.31.207.130),(nsset2 217.31.207.130))
        tech status) ...

Takto složité zadávání naštěstí existuje jen v malém množství příkazů a
tento uvedený příklad zadání je vůbec nejsložitější ze všech. Kromě
toho máte možnost zadávat parametry příkazu v interaktivním módu - hezky
jeden za druhým. Navíc je vždy na konci helpu každého příkazu uveden
příklad zadání všech parametrů. 

Pokud chcete parametry přikazu zadávat interaktivně, napište před příkaz
vykřičník:

  > !update-nsset

Tím spustíte režim interaktivního vkládání parametrů. Konzole vždy
vypíše jméno parametru a čeká na zadání hodnoty. Pokud hodnotu nechcete
zadat, tak prostě stisknete enter a hodnota se přeskočí. Interaktivní
režim můžete kdykoliv ukončit zadáním vykřičníku. Tím se ukončí aktuální
jmenný prostor. Nacházíte-li se tedy v hlavním jmenném prostoru, tak se
interaktivní režim ukončí. Pokud je prompt zanořen do nějakého jmenného
prostoru, tak se ukončí pouze ten a interaktivní vkládání pokračuje
nadřazeným prostorem. Chcete-li vyskočit z vícenásobně vnořeného 
prostoru nebo ukončit režim celý, tak zadejte více vykřičníků najednou.
Jeden vykčiřník na jeden jmenný prostor. Nevadí bude-li jich více, než
požadovaný počet:

    > !update-nsset
    Start interaktivního zadávání parametrů. Pro ukončení zadejte: 
        ![!!...] (jeden ! pro každou podskupinu)
    > !update_nsset:id (povinný) > moje-id
    (Hodnota může být seznam o max. velikosti 9 položek.)
    > !update_nsset:add.ns[1/9].name (povinný) > ns1
    (Hodnota může být libovolně velký seznam.)
    > !update_nsset:add.ns[1/9].addr[1/oo] (nepovinný) > 127.0.0.1
    > !update_nsset:add.ns[1/9].addr[2/oo] (nepovinný) > 127.0.0.2
    > !update_nsset:add.ns[1/9].addr[3/oo] (nepovinný) > !
    > !update_nsset:add.ns[2/9].name (povinný) > ns2
    (Hodnota může být libovolně velký seznam.)
    > !update_nsset:add.ns[2/9].addr[1/oo] (nepovinný) > !!!!

Ještě jednou zpět k zadávání pomocí klíče: Klíč se zadává ve tvaru 
-[název parametru] [hodnota].
Například:

     -heslo "toto je moje heslo"

Toto zadání lze napsat i takto se stejným účinkem:

     --heslo = "toto je moje heslo"

Záleží na vás, který zápis se vám bude zdát čitelnější. Jak ale zadat
honodotu, která je součástí jmenného prostoru? Jednoduše pomocí tečkové
koncence:

    --add.ns.name = nsset_name

Takto jste definovali hodnotu nsset_name do jmenného porostoru "add", 
do první položky seznamu "ns", do parametru "name". Chcete-li uložit
hodnotu například do třetí položky seznamu "ns", tak zadejte:

    --add.ns[2].name = nsset_name

Dvojka je index seznamu v tomto případě o max. devíti položkách
(indexy 0 - 8).





2.2 Příkazy relace (session)

Konzole má svá vnitřní nastavení, která můžete nastavit. Pokud zadáte
příkaz bez parametrů, tak se pouze vypíše aktuální stav.

> validate on/off
Tímto přepínačem zapnete nebo vypnete proces validace XML dokumentu. Validace je v této verzi
realizována přes externí program xmllint. Pokud není v systému přítomen, tak nastavení ON nemá
žádný efekt. Validace ověřuje platnost XML dokumentu podle EPP schemat a to jak v odchozích,
tak i příchozích zprávách. Pokud není dokument validní, tak jej konzole na server neodešle.
Nevalidní dokument vznikne například tím, že zadáte hodnotu, která neodpovídá konkrétnímu schématu.
Například příliš krátké heslo. Konzole v této verzi obsah hodnot nijak neověřuje, pouze zjišťuje
jestli byly zadány nebo ne.

> poll-ack [on/off]
Pokud je tento přepínač ON, tak se po odeslání příkazu "poll req" automaticky odesílá i "poll ack".
Tuhle funkci asi nejvíce oceníte, když budete mít na serveru hodně zpráv. Příkaz "poll req" zprávu
ze serveru pouze zobrazí, ale pak se zpráva musí ze serveru odstranint příkazem "poll ack ID-zprávy".
Při automatickém poll-ack se bude odstraňování provádět automaticky.

> raw-command [dict]
> raw-answer [dict]
Tyto příkazy nejsou přepínače interních proměnných, ale vypisují zdrojové tvary posledního příkazu
a odpovědi. Místo "raw" lze zadat i "src" a všechny fungují ve zkrácené verzi:

    raw-c, raw-c d, src-c, src-c d, raw-a, raw-a d, src-a, src-a d

Každý příkaz, který zadáte v promptu se sestaví do XML EPP dokumentu. Pokud si chcete tento
XML dokument prohlédnout, tak zadáte "src-c" a na výstup se vypíše vygenerované zdojové XML. 
Chcete-li vidět XML zdojový dokument od serveru, zadejte "src-a".
Pokud je XML dokument nepřehledný a vy chcete vidět jasněji strukturu jednotlivých XML uzlů,
tak zadejte "src-c d" (nebo "src-a d"). Konzole vypíše hodnoty uzlů v přehledné formě s odsazením.

> confirm [on/off]
U EPP editačních příkazů, které nějak mění hodnoty na serveru (create, upadte, delete, transfer, renew),
se před odesláním požaduje potvrzení k odeslání. Přepínačem "confirm OFF" lze toto potvrzování vypnout.

> config [create]
Konzole si hodnoty interních nastavení načítá z konfigu. Pokud ještě konfig nebyl vytvořen, tak se
nastaví defaultní hodnoty. Aktuální hodnoty konfigu lze zobrazit příkazem "config". Chcete-li
konfig vytvořit, zadejte "config create". Tím se vytvoří konfigurační soubor ".ccReg.conf" ve vašem
domovském adresáři. V konfigu si pak můžete nastavit cestu k vašemu certifikátu a další hodnoty.
Konzole se pokouší neprve načíst konfig z adresáře /etc (ve Windows z adresáře uvedeném v proměnné
prostředí $ALLUSERSPROFILE, ta bývá obvykle nastavena na "C:\Documents and Settings\All Users")
a poté načítá další konfig z adresáře uživatele. Na posix to je /home/[user], ve Windows je to 
"C:\Documents and Settings\[user]". Tak lze uložit hodnoty společné pro všechny uživatele.

Do konfigu lze uložit i jakýkoliv parametr libovolného EPP příkazu. Tyto hodnoty jsou pak
automaticky doplněny do parametrů, které jste při zadání příkazu nevložili. Například si můžete
uložit parametry příkazu login a ten pak již můžete zadávat bez parametrů. Parametry se do konfigu
ukládají tak, že se vytvoří sekce s prefixem "epp_" a názvem příkazu. Položky sekce pak odpovídají
způsobu vkládání parametrů pomocí klíče: klíč = hodnota. Zde je příklad části konfigu s loginem:

[epp_login]
username = muj-login
password = moje-heslo


> send
Přikaz "send" slouží k posílání libovolného souboru na EPP server. Tento příkaz je zde jen z testovacích
důvodů. Pokud "send" zadáte bez parametrů, tak vypíše aktuální adresář. Když "send" zadáte se
jménem platného souboru, tak tento soubor bez dalšího ptaní odešle na EPP server:

    send some-folder/my-test-file.xml

> connect
Příkaz "connect" vytváří spojení s EPP serverem aniž by na něj cokoliv posílal. Pokud se spojení
podařilo, pošle EPP server zprávu "greeting" a tak se zobrazí na výstupu. Příkaz "connect" 
je zde z testovacích důvodů a není potřeba jej volat. Stačí zadat rovnou "login".

> colors [on/off] # zapnout/vypnout barevný výstup
> verbose [number] # nastavit mód výpisu: 1 - stručný (default); 2 - plný; 3 - plný & XML zdroje


================================================

    5. Skripty ccreg_create.py a ccreg_sender.py

================================================

Skripty ''ccreg_create.py'' a ''ccreg_sender.py'' jsou určeny pro použití v shell batchi.

''ccreg_create.py'' přijímá parametry se standardního vstupu a vygeneruje 
XML EPP dokument na standardní výstup. Například:

    $ python ccreg_create.py info-domain nic.cz
    $ ./ccreg_create.py info-domain nic.cz

<?xml version='1.0' encoding....

Pokud nastane nějaká chyba, tak vrací XML s chybovým hlášením:

    $ python ccreg_create.py inxo-domain nic.cz

<?xml encoding='utf-8'?><errors>inxo_domain nic.cz: Neznámý příkaz!</errors>

Příkazy se dají zřetězit:

    $ ./ccreg_create.py check-domain test.cz nic.cz | ./ccreg_create.py info-domain nic.cz


''ccreg_sender.py'' odesílá dokumenty na server. Skript se automaticky zaloguje, pak
předá dokument, zobrazí odpověď a odloguje se a ukončí. Pro správné zalogovájní je nutné
mít správně nastaven config.
Skript může odesílat dokumenty dvěma způsoby:

    1. dokumenty se uloží do souboru a skriptu se předají jména souborů. Skript
       je pak odesílá v uvedeném pořadí. Například:

    $ ./ccreg_create.py check-domain cosi.cz nic.cz > doc1.xml
    $ ./ccreg_create.py info-domain nic.cz > doc2.xml
    $ ./ccreg_sender.py doc1.xml doc2.xml

    2. PIPE - Zřetězením příkazů create a sender.
       Například:

    $ ./ccreg_create.py check-domain cosi.cz nic.cz | ./ccreg_create.py info-domain nic.cz | ./ccreg_sender.py



================================================

    6. Knihovna ccReg a popis API

================================================

Knihovna ccReg vám umoňuje implmentovat API rozhraní do vašich aplikací. Knihova i jednotlivé funkce
obsahují komentáře, podle kterých se můžete při implementaci řídit. V části __init__.py naleznete
i ukázky kódu.


** Online dokumentace:

Pokud si chcete projít jednotlivé třídy a funkce knihovny, tak k tomu můžete využít generátor
dokumentace, který je standardní součástí pythonu: Zadejte na příkazové řádce příkaz:

    $ pydoc -p 8080

Tím jste spustili webový server, který generuje strany dokumentace přímo ze zdrojových souborů.
Parametr -p udává na jakém portu je server spuštěn. Číslo portu můžete zadat jakékoliv jiné.
Nyní si otevřete prohlížeč a zadejte adresu: http://localhost:8080/. Otevře se strana, na které
v části ../site-packages naleznete odkaz na ccReg (package).

Pokud jste skripty neinstalovali, ale jen nakopírovali, nebo pokud se chcete podívat i na skripty
pracující s knihovnou ccReg, tak celý proces spuštění udělejte stejně, ale s tím rozdílem, že pydoc
spustíte z adresáře, kde máte tyto skripty uložené. Pak se v helpu zobrazí i ony:

    $ cd ccRegClient-1.1
    $ pydoc -p 8080

Server ukončíte stiskem Ctrl+C.


Import knihovny provedete příkazem:

    >>> import ccReg

Instanci EPP klienta vytvoříte:

    >>> epp = ccReg.Client()

Ještě musíte načíst config, aby knihovna našla certifikát:

    >>> epp.load_config()

Chcete-li načíst jinou session - analogicky k parametru --session, tak zadejte:

    >>> epp.load_config('my-sessison-name')

Pak již můžete navázat spojení funkcí login:

    >>> retval = epp.login("username","password")

Každá funkce (EPP příkazu) vrací tuto "retval" hodnotu, která je typu dict a ve tvaru:

    {'reason': u'Text of answer reason', 
     'code': 1000,
     'command': 'command-name',  
     'errors': []
     'data': {'key': 'value' [,'next-key':'next-value']}, 
    }

Klíč "reason" (str) je vyrozumění serveru o stavu odpovědi.
Klíč "code" (int) je číslo, které definuje typ chyby. Číslo 1000 znamená OK - vše vpořádku.
Klíč "command" (str) je název příkazu, na který se odpověď vztahuje (který odpověď vyvolal).
Klíč "errors" (list) je seznam chyb, které server nalezl.
Klíč "data" (dict) je slovník s hodnotami individuálními pro každý jednotlivý příkaz.

Jaké klíče jsou v části "data" pro danou funkci (EPP příkaz) se dozvíte z dokumentace u každé funkce:

    >>> print epp.login.__doc__
    ...
    RETURN data: {...}
    ...

POZOR! V této verzi (1.0 beta release) má slovník tu vlastnost, že pokud
hodnota chybí, tak se klíč ve slovníku vůbec nevyskytuje. Dále, pokud je
v seznamu hodnot jen jedna položka, tak je typu string/unicode. Tyto
odlišnosti byste měli testovat.Ve finální verzi bude slovník pevně daný:
Klíč bude ve slovníku i když bude hodnota prázdná a seznam zůstane,
i když bude mít jen jednu položku.

Příklad: Když jsou vstupní data: 
    name = 'jmeno'
    addr = (1,2,3)
    tech = ('ok',)
    stat = ''

...tak se vytvoří takovýto slovník 'data':
    {'name': 'jmeno',
     'addr':['1','2','3']
     'tech':'ok'           # tady je type str a stat chybí
    }
...ale ve finální verzi by to mělo být takto:
    {'name': 'jmeno',
     'addr':['1','2','3']
     'tech':['ok',]
     'stat':''
    }

Návratovou hodnotu "retval" není nutné odchytávat, ukládá se do interní proměnné a lze ji kdykoliv
zobrazit funkcí print_answer():

    >>> epp.print_answer()

nebo testovat jakoukoliv hodnotu v retval pomocí funkce is_val():

    >>> epp.is_val('reason')
    u'Text of answer reason'

Každé volání další funkce EPP příkazu samozřejmě předchozí "retval" přepíše, takže uvedené dvě funkce
pracují vždy jen s poslední návratovou hodnotou. Pokud chcete návratovou hodnotu testovat nebo
zobrazit později, tak si ji uložte a pak ji předejte funkcím:

    >>> epp.print_answer(my_retval)
    >>> epp.is_val('reason', my_retval)

Funkci is_val() je možno zadat bez parametru. V takovém případě defaultně vrací hodnotu klíče "code":

    >>> epp.is_val()
    1000

Pokud chcete zjistit hodnotu v jakékoliv vnořené části slovníku, tak zadejte parametr jako cestu - 
seznam jmen (klíčů) slovníku:

    >>> epp.is_val(('data','next-key'))
    next-value

V případě, že daný klíč neexistuje, vrací funkce hodnotu None.

    >>> epp.is_val(('data','any-key'))
    None

Pokud se vyskytne nějaká chyba při přenosu nebo jiná, která zablokuje funkčnost, tak se generuje
výjimka ccRegError.




Tento help sepsal: 

Zdeněk Böhm, <zdenek.bohm@nic.cz>
Vzniklo: 11.7.2006
Revize:  18.8.2006



