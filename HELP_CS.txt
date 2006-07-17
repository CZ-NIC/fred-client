# -*- coding: utf8 -*-
# Tento dokument je ulozen v kodovani UTF-8.

================================================

Manuál pro ccReg Client konzoli a knihovnu ccReg
    
Verze 1.0, Beta release

================================================

    1. Instalace
    2. Práce s Client konzolí
    3. knihovna ccReg a popis API



=============================

1. Instalace

=============================

Knihovna ccReg a na ní postavená "ccReg Client konzole" je napsána v ja-
zyce Python. Pro svůj běh potřebuje mít v systému  nainstalováno  běhové 
prostředí Python. Pokud se ve vašem systému Python nenachází, tak si jej
nainstalujte.  Instalační soubory jsou v obvyklých repozitářích  nebo na 
www.python.org.

Dále knihovna používá "xmllint" pro validaci XML. Tento program ale není
nutnou podmínkou funkčnosti klienta. Pokud se v systému nenachází, tak 
se ověřování automaticky vypne.



=============================

2. Práce s Client konzolí

=============================

"ccReg Client konsole" je určena ke komunikaci s EPP serverem. Konzole
přijímá na příkazové řádce příkazy od uživatele. Z příkazu sestaví podle
EPP schematu XML dokument. Tento dokument pak odešle na EPP server. 
Po té čeká na odpověď serveru. Odpověď serveru přije ve formátu XML EPP.
Tuto odpověď aplikace zpracuje a na výstup zobrazí jen podstatné hodnoty
odpovědi. Konzole tedy funguje jako odstínění uživatele od EPP formátu. 
Konzole se spustí příkazem:

    python ccreg_console.py [host] [lang]

Pokud parametr "host" není zadán, použije se defaultní hodnota nebo se
údaje přečtou z config souboru (pokud existuje). Pokud není zadán 
"lang", použuje se default "cs". Možné hodnoty jsou jen "cs" a "en". 
Paramery mohou být zadány v libovolném pořadí, konzole pozná, že cs/en
není jméno serveru.
Po spuštění se konzole zastaví na promptu,kde uživatel zadává jednotlivé
příkazy. Konzole se ukončuje příkazem "quit" nebo jen krátce "q".



2.1 Zobrazení helpu

Jaké příkazy máte k dispozici zjistíte zadáním příkazu "help" nebo jen
krátce "h" nebo "?".
Help vypíše dvě části nápovědy:

    1) Dostupné EPP příkazy
    2) Příkazy relace (session) pro nastavení vnitřních proměnných 
       konzole



2.2 EPP příkazy

EPP příkaz zadáváte společně s jeho parametry. Jaké parametry příkaz
požaduje zjistíte, když zadáte "help příkaz" nebo zkráceně "h příkaz"
nebo také "? příkaz".
Například:

    ?login

Vypíšou se podrobnosti o jednotlivých parametrech daného příkazu. Příkaz
zadáte tak,že napíšete název příkazu a za ním jeho parametry. Například:

    login moje-ID moje-heslo

Po stisknutí entru se příkaz převede na EPP XML dokument. Ten se ihned
odešle na server. Pak čeká na odpověď. Když server vrátí odpověď, tak ji
zpracuje a na konzoli vypíše hodnoty odpovědi.



2.2.1 Typy paramerů příkazu:


Pokud hodnota parametru obsahuje mezeru, tak ji napište do uvozovek. 
Například:

    login moje-ID "moje heslo s mezerami"

Některé parametry můžou obsahovat seznam hodnot. Například parametr 
"street" v příkazu create-contact.
Výpis části helpu:

    ?create-contact
    ...
    ... street (nepovinný)  seznam o maximálně 3 položkách.
    ...

Seznam zadáte tak, že hodnoty uzavřete do závorek:

    create-contact my-ID my-name mail city cc org (Vodičkova, \
            "Na příkopě", "U přívozu") voice

Pokud zadáváte jen jednu hodnotu ze seznamu, tak závorky zadávat
nemusíte:

    create-contact my-ID my-name mail city cc org Vodičkova voice

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

  create-contact my-ID my-name mail city cc --notify_email = muj@mail.cz

Jaký má být klíč (název parametru) zjistíte z helpu daného příkazu.
Parametr s klíčem pak již nemusí být na "své" pozici, ale může být
kdekoliv v řadě mezi ostatními parametry. Takový parametr stojí "mimo"
pořadí a nenarušuje pozice ostatních parametrů bez klíče. Zde jsou 
do řady parametrů vloženy hodnoty s klíči "vat" a "notify_email":

    create-contact my-ID my-name mail --vat = 12346 \
        --notify_email = muj@mail.cz city cc

Některé příkazy mají parametry vnořené do dalších parametrů.Ty vytvářejí
jmenné prostory. Například v příkazu "create-contact" je parametr 
"disclose". Ten obsahuje další parametry "flag", "name", atd. Samotný
název "disclose" není v tomto případě název klíče, ale název jmenného
prostoru, ve kterém se nacházejí klíče "flag", "name" atd. Jmenné
prostory se definují stejně jako seznamy pomocí závorek:

  create-contact my-ID my-name mail city cc org street sp pc voice fax \
       (flag name org addr voice fax email) vat ssn

Pokud jmenný prostor nechcete zadávat, napište prostě jen prázdné
závorky. To platí i pro seznamy:

    create-contact my-ID my-name mail city cc org street sp pc voice \
        fax () vat ssn notify@email

Některé příkazy mají v parametrech seznamy jmenných prostorů. V takovém
případě pak závorky mají své významy podle toho, jak jsou hodnoty
strukturované. Například příkaz "update-nsset" má jeden 
nepovinný parametr "add". Pokud jej nechcete zadávat, tak napíšete:

    update-nsset id () ...    - parametr add je nyní prázdný

Pokud ale "add" zadat chcete, tak "add" (jak vidíte v helpu) obsahuje
seznam devíti jmenných prostorů "ns"! Každý "ns" prostor pak dále
obsahuje parametr "name", seznam "addr", seznam "tech" a nakonec seznam
"status". Pokud chete všechny tyto hodnoty zadat, tak musíte zapsat
všechny závorky, které jsou nutné: První závorka pro definování jmenného
prostoru "add".Druhá závorka pro začátek seznamu jmenných prostorů "ns".
Třetí závorka pro samotný jmenný prostor "ns". Teprve pak následuje
hodnota parametru "name". Za ním pak následuje závorka seznamu "addr":

    update-nsset nsset-ID (((nsset1 (127.0.0.1, 127.0.0.2)), \
       (nsset2 (127.1.0.1, 127.1.0.2))) (tech1 tech2) (status1 status2))
        ...

Pokud "addr" není seznam, ale jen jedna hodnota, tak se závorky pro
"addr" zadávat nemusí:
(To je pravidlo již zmíněné v předchozím textu.)

    update-nsset nsset-ID (((nsset1 127.0.0.1),(nsset2 127.0.2.1)) \
        tech status) ...

Takto složité zadávání naštěstí existuje jen v malém množství příkazů a
tento uvedený příklad zadání je vůbec nejsložitější ze všech. Kromě
toho máte možnost zadávat parametry příkazu v interaktivním módu - hezky
jeden za druhým. Navíc je vždy na konci helpu každého příkazu uveden
příklad zadání všech parametrů. 

Pokud chcete parametry přikazu zadávat interaktivně, napište před příkaz
vykřičník:

    !update-nsset

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

    !update-nsset
    Start interaktivního zadávání parametrů. Pro ukončení zadejte: \
        ![!!...] (jeden ! pro každou podskupinu)
    !update_nsset:id (povinný) > moje-id
    (Hodnota může být seznam o max. velikosti 9 položek.)
    !update_nsset:add.ns[1/9].name (povinný) > ns1
    (Hodnota může být libovolně velký seznam.)
    !update_nsset:add.ns[1/9].addr[1/oo] (nepovinný) > 127.0.0.1
    !update_nsset:add.ns[1/9].addr[2/oo] (nepovinný) > 127.0.0.2
    !update_nsset:add.ns[1/9].addr[3/oo] (nepovinný) > !
    !update_nsset:add.ns[2/9].name (povinný) > ns2
    (Hodnota může být libovolně velký seznam.)
    !update_nsset:add.ns[2/9].addr[1/oo] (nepovinný) > !!!!

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


Shrnutí zadávání parametrů:

    - parametry zadávejte v pořadí, v jakém jsou vypsané v helpu
    - hodnoty s mezerami dejte do uvozovek
    - seznamy hodnot uzavřete do závorek, položky seznamu můžou 
      (ale nemusí) být odděleny čárkami
    - pokud je v seznamu jen jedna položka, nemusí se závorky zadávat
    - jmenné prostory pište do závorek
    - chcete-li seznam nebo jmenný porostor vynechat, zadejte jen 
      prázdné závorky
    - hodnoty mimo pořadí zadávejte pomocí klíče




2.2 Příkazy relace (session)

Konzole má svá vnitřní nastavení, která můžete nastavit. Pokud zadáte
příkaz bez parametrů, tak se pouze vypíše aktuální stav.

> lang cs/en
Přikazem "lang" nastavíte proměnnou typu jazyka, kterým chcete, aby 
vám EPP server odpovídal. Proměnnou tedy musíte nastavit PŘED odesláním
příkazu login. Pak už nastavení nebude mít žádný vliv.

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








=============================

3. Knihovna ccReg a popis API

=============================
Knihovna ccReg vám umoňuje implmentovat API rozhraní do vašich aplikací. Knihova i jednotlivé funkce
obsahují komentáře, podle kterých se můžete při implementaci řídit. V části __init__.py naleznete
i ukázky kódu.

Import knihovny provedete příkazem:

    >>> import ccReg

Instanci EPP klienta vytvoříte:

    >>> epp = ccReg.Client()

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
11.7.2006



