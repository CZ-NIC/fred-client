��    �        �   
      �  �   �  C  ;  �     B  F  �  �    8  �   S  '   �  *        ,     =     K     b     u     �  .   �     �     �     �       
   5     @     R     d  -   �     �  ,   �  ,   �       '   -     U     f  *   o     �     �  T   �          3  
   D  o   O  <   �  #   �        3   4  /   h     �     �     �  $   �  $   �  "     "   @  J   c     �     �     �     �  	   �       '     #   =  d   a  	   �     �  '   �  	          
   $   "      G      c      o   E   �      �   F   �   M   '!  U   u!  E   �!  s   "  I   �"  M   �"  H   #  8   f#  X   �#     �#     �#  H   $  C   J$     �$     �$     �$     �$     �$     �$  �  %  @   �'     �'     �'  ,   �'  &   +(     R(  @   b(     �(  <   �(  ?   �(     8)  G   O)     �)     �)     �)     �)     �)     �)     �)  
   �)     �)     *     *     ,*     F*     W*  
   c*  '   n*     �*  #   �*     �*     �*     �*     �*     �*     +     +  
    +     ++     E+     N+     `+     i+  &   p+     �+     �+     �+  
   �+  0   �+  
   �+     
,     ,     ,     <,     ?,     F,     S,     e,     t,  	   �,     �,  
   �,     �,  	   �,     �,  .  �,  Q   .  �   W.  �   ./     �/  �  �0  �  �2  �   X9  :   :  /   <:     l:     �:     �:     �:  $   �:  $   �:  /   ;     B;     U;  $   h;     �;     �;     �;     �;  0   �;  J   <     i<  )   {<  1   �<     �<  =   �<     1=  
   D=  @   O=  "   �=     �=  �   �=     Z>     t>  	   �>  �   �>  F   ?  +   b?     �?  ;   �?  1   �?     @     ,@     B@  &   Z@  (   �@  &   �@  &   �@  b   �@     [A     vA     �A  
   �A     �A     �A      �A  )   �A  k   "B     �B     �B  ,   �B  	   �B     �B  6   �B     6C     VC  !   fC  B   �C     �C  Q   �C  O   /D  Q   D  K   �D  �   E  R   �E  W   F  H   fF  @   �F  [   �F     LG     SG  b   [G  O   �G     H     *H     =H     XH  $   wH  	   �H  �  �H  J   ^K     �K     �K  C   �K  (   
L     3L  7   KL     �L  =   �L  ;   �L     M  Q   %M     wM     �M  
   �M     �M     �M     �M     �M  
   �M     �M  
   �M     �M  "   N     9N     KN     ZN  $   ^N  
   �N  4   �N  $   �N     �N     �N     �N     O     O     &O     3O     AO  
   ]O     hO     zO     �O  ,   �O     �O     �O     �O     �O  <   �O     'P     9P     GP  &   PP     wP     }P     �P     �P     �P     �P     �P     �P     �P     �P     �P     Q         �       �   f   �   K   k       N   G   m   ]   z       �   t   <   �   M       c   X       q      
       e       A   +   .   U   �   \      �                              �   9      !       $       Z   n       w      ~          g       V   �   �   @       H   �          �       :      4   �   ?   D   �   �   s   =   Q       }   #                     E   F   &           T   |              y       a      �   Y      �   J   %         R   7   j   �                               r   `   ^   �   d   '   i   _          "   8      1   �   x       �           o      O       v      b   S   C              5       �   L           2   >   /   {   �   �       B           -   *       �       �   0   [   (   I             u           �   l   6         	      P       h          �         �   �   3   ;           �       p   )   W      �   ,   �                
   The "login" command establishes an ongoing server session that preserves client identity
   and authorization information during the duration of the session. 
   The EPP "check" command is used to determine if an object can be
   provisioned within a repository.  It provides a hint that allows a
   client to anticipate the success or failure of provisioning an object
   using the "create" command as object provisioning requirements are
   ultimately a matter of server policy.
 
   The EPP "create" command is used to create an instance of an object.
   An object can be created for an indefinite period of time, or an
   object can be created for a specific validity period.
 
   The EPP "info" command is used to retrieve information associated
   with an existing object. The elements needed to identify an object
   and the type of information associated with an object are both
   object-specific, so the child elements of the <info> command are
   specified using the EPP extension framework.
 
   The EPP "transfer" command provides a query operation that allows a
   client to determine real-time status of pending and completed
   transfer requests.
   The EPP "transfer" command is used to manage changes in client
   sponsorship of an existing object.  Clients can initiate a transfer
   request, cancel a transfer request, approve a transfer request, and
   reject a transfer request using the "op" command attribute.
 
${BOLD}Session commands:${NORMAL}
${BOLD}q${NORMAL} (or ${BOLD}quit${NORMAL}, ${BOLD}exit${NORMAL}) # quit this application
${BOLD}help${NORMAL} (or ${BOLD}h${NORMAL}, ${BOLD}?${NORMAL})  # display this help
${BOLD}license${NORMAL} # display license
${BOLD}credits${NORMAL} # display credits
${BOLD}connect${NORMAL} (or directly login) # connect to the server (for test only)
${BOLD}validate${NORMAL} [on/off] # set validation or display actual setting
${BOLD}poll-ack${NORMAL} [on/off] # send "poll ack" straight away after "poll req"
${BOLD}raw-c${NORMAL}[ommand] [xml]/${BOLD}d${NORMAL}[ict] # display raw command (instead of raw you can also type ${BOLD}src${NORMAL})
${BOLD}raw-a${NORMAL}[nswer] [xml]/${BOLD}d${NORMAL}[ict]  # display raw answer
${BOLD}confirm${NORMAL} ${BOLD}on${NORMAL}/[off] # confirm editable commands befor sending to the server
${BOLD}config${NORMAL} # display actual config
${BOLD}config${NORMAL} ${BOLD}create${NORMAL} # create default config file in user home folder.
${BOLD}send${NORMAL} [filename] # send selected file to the server (for test only). If param is not valid file the command shows folder.
${BOLD}colors${NORMAL} [on/off] # turn on/off colored output
${BOLD}verbose${NORMAL} [number] # set verbose mode: 1 - brief (default); 2 - full; 3 - full & XML sources
 ${BOLD}${YELLOW}Start interactive input of params. To break type: ${NORMAL}${BOLD}!${NORMAL}[!!...] (one ${BOLD}!${NORMAL} for scope) (Value can be a list of max %d values.) (Value can be an unbouded list of values.) Actual config is Answer source Available EPP commands Broken connection. Certificate key file not found. Certificate names not set. Certificates missing. Try connect without SSL! Colors mode is Command source Command was sent to EPP server. Confirm has been set to Confirm is Connection broken Connection closed Create default config failed. Default config file saved. For more see help. Dir list Do you want send this command to the server? Document has wrong encoding. LookupError: %s EPP document is not valid End of interactive input. [press enter] Example of input Examples Fatal error: Create default config failed. For disable validator type For more type For stop interactive input type ! instead of value (or more "!" for leave sub-scope) Greeting message incomming Help for command IP address If this script runs under MS Windows and timeout is not zero, it is probably SLL bug! Set timeout back to zero. Impossible create connection. Required config values missing Impossible saving conf file. Reason Init SSL connection Instead "command" Select one from this list bellow: Internal Error: Master node '%s' doesn't exist. Interpreted answer Interpreted command Interrupt from user Invalid XML document. ExpatError: %s Invalid bracket definition (childs). Invalid bracket definition (list). Invalid bracket definition (mode). Invalid bracket. In key definition is only allowed a value or simple list. Invalid input format. Invalid parameter index Invalid response code LIST of DNS Load file Login failed Missing result in the response message. Missing values. Required minimum is Names what are not included into disclose list are set to opposite value of the disclose flag value. No config No data No response. EPP Server doesn't answer. Not found Open connection on host Param MUST be a value from this list Private key file not found. Send logout Server answer is not valid! Server doesn't return Greeting message. Contact server administrator. Start session! Temporary file for verify XML EPP validity cannot been created. Reason The EPP "delete" command is used to remove an instance of an existing object. The EPP "hello" request a "greeting" response message from an EPP server at any time. The EPP "logout" command is used to end a session with an EPP server. The EPP "poll" command is used to discover and retrieve service messages queued by a server for individual clients. The EPP "renew" command is used to extend validity of an existing object. The EPP "update" command is used to update an instance of an existing object. The server configuration is not valid. Contact the server administrator. This program needs Python 2.4 or higher. Your version is To start the interactive mode of input the command params type: ${BOLD}!command${NORMAL} Try Type Type "?command" (or "h(elp) command") for mode details about parameters. Unknown EPP command. Select one from EPP commands list (Type help). Unknown EPP command: %s. Unknown command Unknown parameter name Unknown response type Unknown server response Usage Usage: python ccreg_console.py [OPTIONS]
Console for communication with EPP server.

OPTIONS with values:
    -s --session  name of session used for connect to the EPP server
                  session values are read from config file
    -h --host     host name (overwrite config value)
    -u --user     user name (overwrite config value)
    -p --password (overwrite config value)
    -l --lang     language of session
    -v --verbose  display modes: 1,2,3; default: 1
                  1 - essensial values
                  2 - all returned values
                  3 - display XML sources
OPTIONS:
    -r --colors   set on colored output
    -? --help     this help
 Used certificat is not signed by verified certificate authority. VAT Validation process is Validator has been disabled. For enable type Value "%s" is not allowed here. Valid: Verbose mode is You are connected already. Type disconnect for close connection. You are logged already. You are not connected! For connection type: connect or login You are not connected! Type login for connection to the server. You are not connected. You are not logged. You must call login() before working on the server. You has been disconnected. accept only values add part address change part city contact contact ID contact name country code current expiration date disclose flag (default y) disclosed values domain name fax number index of message, required with op=ack! list of DNS list of values overflow. Maximum is list with max %d items. missing name new password not disclose notify email nsset address nsset name number of months or years optional organisation name password period period unit (y year(default), m month) poll ack is postal code postal informations query type readline module missing - cmd history is diabled registrant remove part required required only if part is set sp street tech contact technical contact unbounded list voice (phone number) your city your contact ID your email your login name your name your password Project-Id-Version: 1.0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2006-08-15 11:11+0200
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: Zdeněk Böhm <zdenek.bohm@nic.cz>
Language-Team: CS <info@nic.cz>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 
EPP příkaz "login" identifikuje uživatele a zahájí spojení s EPP serverem. 
   EPP Příkaz "check" se používá ke zjištění jestli se daný objekt
   v repozitáři nachází. To umožňuje řídit spouštění příkazu "create"
   a poté vyhodnotit jestli příkaz uspěl nebo ne.
 
   EPP příkaz "create" se používá pro vytvoření instance objektu.
   Objekt může být vytvořen na neučitý časový úsek nebo na přesně
   definované období.
 
   EPP příkaz "info" se používá ke zjištění informací spojených
   s vybraným objektem. Způsob identifikace objektu a typu
   navrácených informací spojených s objektem závisí na konkrétním
   typu info příkazu a případném použití EPP extension rozšíření.
 
   EPP příkaz "transfer" umožňuje zjišťovat aktuální stav
   nevyřízených anebo dokončených požadavků na transfer.
   Příkaz "transfer" se používá k ovládání změn
   na vybraném objektu. Klient může vyvolat požadavek
   na transfer. Nebo může požadovat zrušení požadavku, potvrzení
   požadavku a nebo odebrání požadavku. To vše pomocí atributu "op".
 
${BOLD}${GREEN}Příkazy relace (session):${NORMAL}
${BOLD}q${NORMAL} (nebo ${BOLD}quit${NORMAL}, ${BOLD}exit${NORMAL}) # ukončit tuto aplikaci
${BOLD}help${NORMAL} (or ${BOLD}h${NORMAL}, ${BOLD}?${NORMAL})  # zobrazit tento help
${BOLD}license${NORMAL} # zobrazit licenci
${BOLD}credits${NORMAL} # zobrazit credits
${BOLD}connect${NORMAL} (nebo přímo login) ${CYAN}# připojení k serveru(jen pro testování)${NORMAL}
odpovídat.MUSÍ být nastaven PŘED odesláním login! Pak již nemá žádný efekt.${NORMAL}
${BOLD}validate${NORMAL} [on/off] ${CYAN}# nastavení validace nebo zjištění aktuálního stavu${NORMAL}
${BOLD}poll-ack${NORMAL} [on/off] ${CYAN}# pošle "poll ack" hned za příkazem "poll req"${NORMAL}
${BOLD}raw-c${NORMAL}[ommand] [xml]/${BOLD}d${NORMAL}[ict] ${CYAN}# zobrazit zdrojový tvar příkazu${NORMAL} (místo raw můžete zadat také ${BOLD}src${NORMAL})
${BOLD}raw-a${NORMAL}[nswer] [xml]/${BOLD}d${NORMAL}[ict]  ${CYAN}# zobrazit zdrojový tvar odpovědi${NORMAL}
${BOLD}confirm${NORMAL} ${BOLD}on${NORMAL}/[off]  ${CYAN}# potvrzení editačních příkazů před odesláním na server${NORMAL}
${BOLD}config${NORMAL} ${CYAN}# zobrazení aktuálních hodnot v config souboru (nebo defaultu)${NORMAL}
${BOLD}config${NORMAL} ${BOLD}create${NORMAL} ${CYAN}# vytvoření defaultního config souboru v adresáři uživatele (user home).${NORMAL}
${BOLD}send${NORMAL} [jméno] ${CYAN}# odešle soubor daného jména na server (jen testování). Pokud jméno není platný soubor, tak příkaz zobrazuje adresář.${NORMAL}
${BOLD}colors${NORMAL} [on/off] # zapnout/vypnoput barevný výstup
${BOLD}verbose${NORMAL} [number] # nastavit mód výpisu: 1 - stručný (default); 2 - plný; 3 - plný & XML zdroje
 ${BOLD}${YELLOW}Start interaktivního zadávání parametrů. Pro ukončení zadejte: ${NORMAL}${BOLD}!${NORMAL}[!!...] (jeden ${BOLD}!${NORMAL} pro každou podskupinu) (Hodnota může být seznam o max. velikosti %d položek.) (Hodnota může být libovolně velký seznam.) Aktuální config je Zdrojová odpověď Dostupné EPP příkazy Spojení bylo přerušeno. Soubor s certifikátem nebyl nalezen Jména certifikátů nejsou zadána  Certifikát chybí. Zkouším spojení bez SSL! Mód barevnosti je Zdrojový příkaz Příkaz byl odeslán na EPP server. Potvrzení bylo nastaveno na Potvrzení je nastaveno na Spojení přerušeno Spojení uzavřeno Vytvoření defaultního config souboru selhalo. Defaultní config soubor byl uložen. Další informace naleznete v helpu. Výpis adresáře Chcete odeslat tento poříkaz na server? Dokument má chybné kódování. LookupError: %s EPP dokument není validní Konec interaktivního zadání parametrů. [stiskněte enter] Příklad zadání Příklady Fatální chyba: Vytvoření defaultních config hodnot selhalo. Pro deaktivaci validátoru zadejte Pro více informací zadejte Interaktivní zadávání parametrů se přeruší zadáním "!" (nebo vícevykřičníků najednou, když jste v podskupině parametrů) Přišla Greeting zpráva Help pro příkaz IP adresa Jestliže tento skript běží v MS Windows a timeout není nula, tak se pravděpodobně jedná o SSL bug! Nastavte timeout zpět na nulu. Není možné vytvořit spojení. Požadované hodnoty z config chybí Není možné uložit config soubor. Důvod Aktivováno SSL spojení Místo "příkaz" vyberte jeden z následujícího seznamu: Interní chyba: Nadřazený uzel '%s' neexistuje. Přeložená odpověď Přeložený příkaz Přerušeno uživatelem Neplatný XML dokument. ExpatError: %s Nesprávné použití závorek (childs). Nesprávné použití závorek (list). Nesprávné použití závorek (mode). Neplatná závorka. V zadání hodnoty klíčem je povolena jen jedna hodnota nebo prostý seznam. Neplatný vstupní formát Neplatný index parametru Neplatný kód odpovědi Seznam DNS Načíst soubor Login se nezdařil V odpovědi chybí část result Chybí parametry. Požadované minimum je Jména která nejsou uvedena v seznamu disclose, jsou nastavena na opačnou hodnotu než má disclose flag. Žádný config Žádná data Žádná odpověď. EPP server neodpovídá. Nenalezen Navázáno spojení na host Parametr MUSÍ být hodnota z následujícího seznamu Privátní klíč nebyl nalezen Odeslán logout Odpověď serveru není validní! Server nevrátil Greeting odpověď. Kontaktujte správce serveru. Relace zahájena! Dočasný soubor pro ověření XML EPP validity se nepodařilo vytvořit. Důvod EPP příkaz "delete" se používá pro odebrání instance vybraného objektu. EPP příkazem "hello" si lze kdykoliv vyžádat od serveru odpověď "greeting". EPP příkaz "logout" se používá pro ukončení spojení s EPP serverem. EPP příkaz "poll" se používá k odběru servisních zpráv pro přihlášeného uživatele a ke zjištění počtu těchto zpráv uložených ve frontě. EPP příkaz "renew" se používá pro prodloužení platnosti vybraného objektu. EPP příkaz "update" se používá pro aktualizaci hodnot instance vybraného objektu. Server není správně nakonfigurován. Obraťte se na správce serveru. Tento program vyžaduje Python 2.4 nebo vyšší. Vaše verze je Interaktivní režim zadávání parametrů příkazu se spustí: ${BOLD}!příkaz${NORMAL} Zkuste Zadejte Více informací o parametrech příkazu získáte zadáním "?příkaz" (nebo "h(elp) příkaz"). Neznámý EPP příkaz. Vyberte jeden ze seznamu EPP příkazů (zadejte help). Neznámý EPP příkaz: %s. Neznámý příkaz Neznámé jméno parametru Neznámý typ části response Odpověď serveru nebyla rozpoznána Použití Použití: python ccreg_console.py [OPTIONS]
Konzole pro komunikace s EPP serverem.

OPTIONS s hodnotami:
    -s --session  název session, který se má použít pro spojení s EPP serverem
                  session hodnoty jsou načteny z config souboru
    -h --host     jméno host (přepíše config hodnotu)
    -u --user     jméno user (přepíše config hodnotu)
    -p --password heslo (přepíše config hodnotu)
    -l --lang     jazyková verze
    -v --verbose  mód výpisu: 1,2,3; default: 1
                  1 - zkrácený
                  2 - plný
                  3 - plný & XML zdroje
OPTIONS:
    -r --colors   zapnutí barevného výstupu
    -? --help     tento help
 Použitý certifikát není podepsán uznávanou certifikační autoritou. DPH Validace je nastavena na Validátor byl deaktivován. Opětná aktivace se provede zadáním Hodnota "%s" není povolena. Platná je: Mód rozsahu výpisu je Již jste připojeni. Pro odpojení zadejte disconnect. Jste již zalogován Nejste připojeni! Po připojení zadejte: connect nebo login Nejste připojeni! Pro připojení k serveru zadejte login. Nejste připojeni. Nejste zalogováni. Před samotnou prací na serveru musíte volat funkci login() Spojení bylo ukončeno. povoleny pouze hodnoty část add adresa část change město kontakt kontakt ID jméno kontaktu kód země aktuální datum expirace přepínač zveřejnit (default y) Zveřejnit údaje jméno domény fax index zprávy, povinné při op=ack! seznam DNS Počet položek v seznamu je překročen. Maximum je seznam o maximálně %d položkách. chybí jméno nové heslo nezveřejňovat oznámení na email nsset adresa jméno nssetu počet měsíců nebo roků nepovinný název organizace heslo období jednotka období (y rok(default), m měsíc) poll ack je PSČ poštovní informace typ požadavku readline modul chybí - historie příkazů je deaktivována vlastník domény část remove povinný povinný jen je-li tato část zadána č.p. ulice tech. kontakt technický kontakt libovolně velký seznam telefon město vaše kontaktní ID váš email vaše login jméno vaše jméno vaše heslo 