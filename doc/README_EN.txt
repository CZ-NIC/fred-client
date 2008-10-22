
Manual for FredClient console and the Fred library

FredClient

   Written: 11/ 7/2006; Revised: 18/ 8/2006; 1/ 9/2006; 4/ 9/2006; 14/ 9/2006;
   27/ 9/2006; 1/11/2006; 7/11/2006; 17/1/2007;

   Copyright (c) 2007 CZ.NIC
     ______________________________________________________________

   CONTENTS

   What is FredClient:
   1. License
   2. System requirements and installation
   3. Description of individual programs, parameters and the configuration file 

        Options 
        Configuration file 

   4. The fred_client program 

        Display help
        EPP commands
        Syntax of command parameters
        Common parameter cltrid (Client transaction ID)
        No value/Empty value

              No value: NULL
              Empty value: '', ""

        Interactive parameter input mode
        Session commands

   5. Fred_create.py and fred_sender.py scripts 
   6. Integration of client into the PHP code
   7. Graphic interface in Qt4.
   8. The Fred library and description of API 

        Online documentation:
        Examples of library use

What is FredClient:

   FredClient is a set of Python scripts, based on the Fred library
   and intended for communication with the EPP server.

   This set includes an EPP console and scripts for use in shell.

Chapter 1. License

   The license is contained in the fred/LICENSE file.

Chapter 2. System requirements and installation

   Installation information is provided in the INSTALL file.

Chapter 3. Description of individual programs, parameters and the configuration file

   CONTENTS

   Options 
   Configuration file 

   The following scripts are provided:
   fred_client    - EPP console, communicates with the EPP server
   fred_create.py - Creates a source EPP XML command
   fred_sender.py - Sends the file to the EPP server

Options

   Scripts may be run with parameters. Enter
    --help or -? to find out which parameter to use:
    $ fred_client --help
    $ fred_client -?

Use: fred_client [parameters...]

Main parameters:
  -?, --help       Display help and terminate
  -V, --version    Display program version and terminate
  -l LANGUAGE, --lang=LANGUAGE
                   Set language version
  -v LEVEL, --verbose=LEVEL
                   Set list mode
                   1 - normal output
                   2 - display more detail
                   3 - display more detail and XML source
  -x, --no_validate
                   Deactivate XML validation at client side

Connection parameters:
  -f CONFIG, --config=CONFIG
                   Load configuration from file
  -s SESSION, --session=SESSION
                   Use session from configuration file

  -h HOSTNAME, --host=HOSTNAME
                   Fred server host
  -p PORT, --port=PORT\n"
                   Server port (default: 700)
  -u USERNAME, --user=USERNAME
                   Login as user
  -w PASSWORD, --password=PASSWORD
                   Login with password
  -c CERTIFICATE --cert=CERTIFICATE
                   Use a SSL certificate for connection
  -k PRIVATEKEY --privkey=PRIVATEKEY
                   Use a  SSL private key for connection

  -n, --nologin
                   Deactivate automatic connection to server after start
  -d COMMAND, --command=COMMAND
                   Send command to server and terminate
  -o OUTPUT_TYPE, --output=OUTPUT_TYPE
                   Display output as text (default), html, xml, php (Caution!

                   For testing only!)

  -q,  --qt
                   Run the client in Qt4 GUI (Caution! For testing only!)

Special parameters not displayed in help:
   -r, --cltrid    --cltrid=mycID_%04d
                   Own clTrID definition with command number

Configuration file

   The configuration file is used to save various client settings so that
   they are constant with every start. Users can
   for example define names and locations of certification files, address of server to which
   the client should connect, schema versions, etc.

   The configuration file is first looked up within the home directory of the user who initiated the script 
   (~/.fred_client.conf). When the home directory contains no config file, it is looked up 
   in the etc directory (/etc/fred_client.conf). On POSIX systems, this is /etc, in
   MS Windows, this is the directory defined in the $ALLUSERSPROFILE variable.
   The --config=filepath (or -f filepath) switch enables the configuration file to be
   loaded from any file.

   A sample is provided for creating a new configuration file:
   fred_client.conf.sample. Use this example as a basis for your own config file. In the example,
   variables are used to define full path to files.
   These variables can be used in other items in the given section.

   Variables are written as %(name of variable)s. Example:
   %(dir)s

   In the example, a variable called dir is defined. In the given section, this
  variable is also defined as:
   dir = /home/username/certificates

   This entry:
   %(dir)s/private_key.pem

   is expanded to:
   /home/username/certificates/private_key.pem after the configuration file is loaded

   This method enables us to have full file paths in one location and 
   only add the name of the file needed. If you find this too complicated,
   do not use variables and 
   enter the entire address in all items.

   In the configuration file example, two paths must be specified like this: One to
   the certificates (for two files) and one for the schemes.

   The configuration file contains a connect section, where paths to
   certificates and information on server are stored. It also contains other values, such as
   username and password. When these values are specified in the config file,
   the login command uses them as parameters eventhough
   they were not specified.

   A config file may contain several connect sections. The one to be used
   at start-up is set by the -s --session parameter. You can for example create a
   [connect_myeppserver] section and activate it by:
    $ fred_client --session=myeppserver     (or -s myeppserver)

    [connect_myeppserver]
    dir=/test/certificates
    host = myeppserver.cz
    ssl_cert = %(dir)s/cert.pem
    ssl_key  = %(dir)s/key.pem
    username = myusername
    password = mypassword

   The session section contains the following settings:
     * poll_autoack = on/off
       With "on", poll ack is automatically send after the poll req command.
     * confirm_send_commands = on/off
       All editing commands in the console (create, delete, update, ...) require
       a confirmation before they are send to the server. This function may be set
       on/off.
     * validate = on/off
       Validation uses an external program - xmllint. When validation is set to "off",
       documents are sent to server without validation of format.
     * schema = /installdir/schemas/all-1.0.xsd
       File in which the validator looks for schemes to validate
       documents.
     * colors = on/off
       The output may be colour-enabled, when possible.
     * escaped_input = on/off
       If your input is escaped (&lt;example&amp;test&gt;), set this value on.
     * verbose = 1/2/3
       List level 1 - brief, 2 - whole, 3 - whole + XML source documents.
     * lang = en/cs
       Language version. When no variable is set, settings from
       the LANG variable of the OS environment are used. English and
       Czech are available. Language version may also be set using the following parameter at
       script start-up.
     * null_value = NULL
       The Nil value - """no
       value""". is specified as NULL by default. Use this value when you want to
       leave one of the command parameters out. NULL means that
       no value was specified, unlike '' or "", when a
       zero-length value is specified.
       NULL value format: the value parameter can be anything, but can not include:
       hyphen (-), spaces and round brackets (()).
       See """Nil value/Empty
       value""" for more information
     * cltrid = myid%04d
       The cltrID (client transaction ID) value. The %d symbol
       is replaced by the command number. The value between % and d rounds the number to four digits
       (zero is added).
     * reconnect = no
       In case if connection fell down client try to reconnect. Type this phrase is behivor disabled.

   The connect section contains the following settings:
     * dir = path to folder with certificates
       This value replaces the %(dir)s parameters in all items in the given section. In
       our case, it contains the path to certificates.
     * ssl_cert = name of certificate
       Name of file containing the certificate. The dir parameter,
       to be replaced by the value defined for the given section, is in front of it.
     * ssl_key = private key name
       Name of file containing the private key. The dir parameter,
       to be replaced by the value defined for the given section, is in front of it.
     * host = server_name
       Name of server to which the client is supposed to connect.
     * port = port_number
       Server port number. When not specified, 700 is used as default.
     * username = username
       Username needed to log into the system.
     * password = password
       Password needed to log into the system.
     * timeout = time of waiting for answer in seconds.
       The timeout settings tells the socket how long to wait for the answer from the 
       server. When no answer is received within the specified time, 
       connection is considered interrupted. The default value is 10 seconds. CAUTION ! In MS Windows,
       the timeout procedure may contain a bug, which causes the connection not to be completed. In
       such a case, set the timeout to zero: timeout = 0
     * socket = IPv4/IPv6
       Setting the type of socket to IPv4 or IPv6. When this value is not specified,
       the socket type offered by server is used.
     * schema_version_[name] = 1.0
       Individual settings of schema version for the contact, nsset, domain,
       enum, fred and epp objects.
     * nologin = on/off
       The client will attempt to connect to the server and log in immediately after start-up.
       This function may be switched off by selecting nologin = off.

Chapter 4. The fred_client program

   CONTENTS

   Display help
   EPP commands
   Syntax of command parameters
   Common parameter cltrid (Client transaction ID)
   No value/Empty value

        No value: NULL
        Empty value: '', ""

   Interactive parameter input mode
   Session commands

  The  fred_client is a console, which communicates with the EPP server. 
  Launch the console by the

    $ fred_client [options]

   When your configuration file contains a correct path to certificates and 
   login and password, you can connect to the 
   EPP server simply by entering the login name. The console is terminated using the "quit", or "q" command.

Display help

   Display commands you can use by entering "help" (or h, ?).
    FredClient version n.n.n Enter "help", "license" or "credits" to display

    more information.

    > help

   Help displays two parts of help files:
   1) Available EPP commands
   2) Session commands to set internal console variables

EPP commands

   All EPP commands (with the exception of hello), have their parameters. Which parameters
   and in what order they are specified is explained in the help file for the given command. Display the
   command help by entering "help command", or "h command", or "? command".
   When you want to know the parameters of the login command, enter:
   "help login".

   Example:

   > help login
   > ?login

   Detailed information on individual parameters of the given command are displayed. The
   command itself is entered by entering the command name and then its parameters:

   > login username password

Syntax of command parameters

   EPP command parameters have certain special requirements
   and use special syntax. Parameters for which this syntax does not have to be used are called 
   simple values. These are values which do not contain spaces and/or are not lists. Example:

   username password

   Parameters are separated by spaces.

   The special syntax contains the following elements:
     * ' " inverted commas (simple or double)
     * ( ) brackets
     * - = hyphen and equal
     * . full stop
     * [] square brackets

   Description of individual elements:
     * ' " are used to specify values which contain spaces and equal character.
       Such values should be surrounded by inverted commas. Single or double inverted commas may be used. Any characters my be used in between the commas, including
      brackets, hyphens and additional inverted commas. When the type of inverted commas used inside the parameter
       is the same as the inverted commas used to separate the parameter, a backslash (\)
       must be inserted in front of them:

       "text \"inverted commas\" text"

       In other cases, no backslash is required:

       "text with 'single' inverted commas"

       or

       'text with "double" inverted commas'

       or

       'text with = "equal" cahracter'


     * ( ) brackets are used for parameters which may include a list of
       values. For example the street parameter in the create_contact command may be 
       a list with up to three items. When a single street is to be specified,
       enter:

       street1

       The program knows the parameter should be a list and interprets the value as
       a list with one item. You do not have to enter: (street1).
       When more streets are to be entered, enter:

       (street1 street2 street3)

       Inverted commas may also be used:

       ("street 1", "street 2", "street 3")

       Commas may be used to separate the list items:

       (street1, street2, street3)
       (street1, street2, street3)
       ("street 1", "street 2", "street 3")

       Some commands have list-type parameters, containing
       further lists. Such list are called name spaces, because they contain
       further items which are defined by name. These items may be simple, or
       they may be further lists. Brackets must be entered so that the correct parameter structure is achieved. The structure of embedded lists is also
       explained in individual command helps. Each level is indented.
       For example the update_contact command contains the chg list, which in turn contains the
       postal_info list, which contains the values of name, org and another list of 
       addresses (addr). The addr list contains city, cc, street, etc. Such lists
       are specified as follows:

       ((name, org, (city, cc, street, sp, pc)) voice, fax, ...)

       Compare to examples listed in command help.

     * - = hyphen and equal 
       Parameters must be entered in a specific order.
       Compulsory items are always entered first. Commands
       may therefore be terminated after the last compulsory parameter. When you
       want to enter another non-compulsory parameter
       toward the end of the parameter, you would have to enter all 
       non-compulsory parameters before yours to ensure the correct order. This is not necessary when you enter the value using a
       """labelled parameter""".
       Labelled parameter is a way of entering a parameter value
       outside of the required order. This is done by entering the name of parameter to which the value
       corresponds. Use the command help to determine such name. Enter it as follows:

       -name value

       The program knows that the hyphen at the beginning denotes a name
       of parameter. the value follows. Several
       hyphens may be entered and an
       equal mark may be entered between the name and the value. Such entry would look as follows:

       --name = value

       Values defined using a named parameter are 
       OUTSIDE of the order of all other parameters. This means they can be used at
       any position between parameters and the values behind them still have the same
       position as if nothing was in front of them (see example below).
       When you call up help for the create_contact command, 
       the last but one parameter is notify_email. Apart from compulsory parameters, you want to
       input this value only (the first five parameters are compulsory: ID,
       name, email, town and country code). Enter:

       create_contact CID:ID name email@email town CZ --notify_email = my@email.net

       The position of the named parameter is arbitrary:

       create_contact --notify_email = my@email.net CID:ID name email@email town CZ

     * . full stop It is more complicated if you want to define a value 
       within an """embedded list""", that is a list within another list.
       Individual names in the list are joined by full stops then. Example:

       create_contact CID:ID name email@email town CZ --disclose.flag = y

     * [] square brackets When a value is an item in a list, 
       the input may be replaced by the lists's index. The index is input using a number in square 
       brackets:

       create_nsset nssid:nsset1 ((ns1.domain.cz (217.31.207.130 217.31.207.129))) --d
       ns.addr[1] = this_value_overwrites_second_address_217.31.207.129 cid:regid

   Overview:
   Always enter parameters in the order specified in help files.
   The number of spaces between individual values is arbitrary.
   Put values including spaces into inverted commas.
   Lists are defined using brackets, list items may be divided by
   commas.
   When a list contain a single item only, brackets do not have to be used.
   Enter values which are not in the specified order using """named parameters."""
   Link names of items embedded in several lists using full stops.

Common parameter cltrid (Client transaction ID)

   Each EPP command, with the exception of hello, contains the <clTRID> tag. This is the last parameter.
   This value is an identifier of a transaction
    The identifier is defined by the client, it can be anything as long as
   formatting rules are observed.
   The identifier is non-compulsory and when not specified, the
   client adds it automatically.

   Another possibility of entering this parameter is to define it in the config file,
   or in options at client start-up.

   Individual commands within a session are numbered. When the cltrid value 
   contains %d, it is replaced by the command number:

   myCtrlID%d  - is converted to myCtrlID1, myCtrlID2, myCtrlID3, ...

   When you want the command number to always have the same number of digits, enter:

   myCtrlID%04d  - is converted to myCtrlID0001, myCtrlID0002, myCtrlID0003, ..
   .

No value/Empty value

No value: NULL

   The Nil value is a value which has not been entered. It is used to
   jump over parameters you do not want to enter. It is an alternative to
   entering values using named parameters. The default nill value
   is NULL.

   When you want to include only the compulsory parameters and the phone number (voice) in the create_contact command,
   there are four other parameters between the last compulsory parameter (pw) and the required one (voice). These are: org,
   street, sp, cp. Enter "the nill value" for these - NULL, unless you have changed the settings.
   This places the voice parameter at the correct position in the command parameters:
   create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword NULL

   NULL NULL NULL +420.222745111

   The above command will not create tags for org, street,
   sp and cp in the XML structure:

   <contact:id>CID:ID01</contact:id>

        <contact:postalInfo>
          <contact:name>Jan Novak</contact:name>
          <contact:addr>
            <contact:city>Praha</contact:city>
            <contact:cc>CZ</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>+420.222745111</contact:voice>

   In the interactive mode, the """nill value""" is entered by
   simply pressing the ENTER key.

   The definition of nill value may be changed using the null_value command. 
   It can also be defined in the configuration file.

Empty value: '', ""

   The empty value is a value without any content. It is a text
   with zero length. It is entered using empty inverted commas, '', or "". This value
   is used to enter zero length values. The difference between an
  empty and a nill value is that an empty value generates a tag in the XML
   document. Because the value is empty, the corresponding XML tag will also be empty.
   create_contact CID:ID01 'Jan Novak' info@mymail.cz Praha CZ mypassword '' ''
 '' '' +420.222745111

   This command generates XML code in which empty values are represented by empty tags:

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

   In the interactive mode, the """empty value""" is entered by
   empty inverted commas, '', or "".

Interactive parameter input mode

   The interactive mode enables the user to enter values one after another, depending on what the
   prompt is requesting. This method is especially suitable when you do not know exactly
   how to specify the parameters. The interactive mode is switched on by entering
   exclamation mark (!) in front of a command:

   > !update_nsset

   The console then displays the name of the parameters and waits for the value to be specified. When you do not want to
   specify the value, press enter and it will be jumped over.
   The interactive mode is cancelled at any time by pressing Ctrl+C (C as in
   Cancel). After entering all compulsory parameters and when you do not wish to specify any non-compulsory ones, 
   switch the interactive mode off by pressing Ctrl+D
   (D as in Done).

   When the interactive mode is cancelled, the command is not completed and
   nothing is sent to the server. When the interactive mode is switched off (completed), the command is completed 
   as if it was entered without an interactive mode. The command
   is then sent to the server. For """editing""" commands and when the
   confirm function is on, the command must be confirmed before
   it is sent to the server:

   REG-LRR@epp-test.ccreg.nic.cz> !update_nsset
   Start the interactive mode. Cancel the mode by pressing Ctrl+C. Complete the command by pressing
   Ctrl+D.
   NSSET ID [compulsory]: nssid:id01
   Add values / List DNS[1/9] / Name server [compulsory when this part is entered]: ns1.dns.cz
   Add values / List DNS[1/9] / Server address [1/oo] [non-compulsory]: 217.31.207
   .130
   Add values / List DNS[1/9] / Server address [2/oo] [non-compulsory]: 217.31.207
   .131
   Add values / List DNS[1/9] / Server address [3/oo] [non-compulsory]:
   Add values / List DNS[2/9] / Name server [non-compulsory]:
   Add values / Technical contact ID[1/oo] [non-compulsory]: cid:myid01
   Add values / Technical contact ID[2/oo] [non-compulsory]:
   Add values / Status[1/6] [non-compulsory]:
   Interactive mode terminated. [press Enter]
   Send command:
   update_nsset nssid:id01 (((ns1.dns.cz (217.31.207.130, 217.31.207.131))) cid:my
   id01)
   Do you really want to send this command to the server? (y/N): y
   nssid:id01 updated.
   REG-LRR@epp-test.ccreg.nic.cz>


Session commands

   The console has certain internal settings, which can be changed directly from the prompt line. 
   This is done by commands called session commands. These are not EPP commands and are not
   intended for communication with the server. They are used to specify internal console settings, or
   to display them. 
   Settings specified in this way are not saved. They are only valid for the duration of the session.
   When you want to make such settings permanent, you have to specify them in the config file.

   The values are set by entering the session command, followed by the value to be used:

   > poll_autoack on

   When you enter a command without parameters, the current settings are displayed

   > poll_autoack
   poll_autoack is ON

   List of session commands:

   > poll_autoack [on/off]

   When this switch is ON, "poll ack" is automatically sent after "poll req" is entered. This function is useful when you have many messages at the server. The "poll req" displays the messages, but they have to be deleted by 
  entering "poll ack
   message_ID". With automated poll-ack, messages are automatically deleted
   after they are displayed.

   > escaped_input [on/off]

   If your input is escaped (&lt;example&amp;test&gt;), set this value on.

   > confirm [on/off]

   For EPP editing commands which change any server values (create,
   update, delete, transfer, renew), confirmation is requested before sending. The confirmation may be switched off by entering "confirm OFF".

   > credits

   The Credits command displays information on the client.

   > help [command]

   The Help command, entered without a parameter, displays a list of available commands. When a parameter is entered
   details of the given command are displayed. The
   "h" and "?" commands have the same meaning as "help".

   > lang [code]

   The lang command changes the language version of the client and the server. When you are logged on,
   you must log-off and on again for the change to take place. This is because the language version is
   communicated to the server in the "login" command. This is also an alternative how to
   switch to another language: """login username password cs"""
   In this client version, only two languages are available: en
   - English; cs - Czech.

   > license

   The license command displays the client license text.

   > quit

   The quit command disconnects the client from the server and finishes the session. 'q' and
   'exit' have the same function.

   > validate [on/off]

   This switch is used to switch on or off the process of validation of the XML document.
   Validation is done using an external program: xmllint. When it isnot available in the system, the ON setting has no effect. Validation checks the
   validity of the XML document according to EPP schemes in both outgoing and
   incoming messages. When a document is not valid, the console will not
   send it to the server. An invalid document is created when you enter
   a value which does not corresponds to the correct scheme. For example a password that is too short.
   The console does not check the values, it only verifies
   whether or not they were entered.

   > verbose [level]

   The client displays various information. This information has different level of detail.
   The first (basic) display level is used for normal users and 
   displays minimal information necessary for the use of the program. 
   The second level displays all messages,
   occurring during communicationThe third level displays all messages and the XML
   source documents exchanged between the client and the server
   Display levels
   1 - brief (default)
   2 - all
   3 - all plus XML source.

   The display level may also be changed in the command line. See
   Configuration file

   > fetch_from_info type of_command [not-in-the command-line]

   The fetch_from_info function enables a command to be created using values,
   loaded from one info-type command in the previous step. This is useful,
   when you want to create a new command with similar parameters
    Command types, which may be created using 
   fetch_from_info are: create, update, delete.

   For example when you want to create_contact, do the following three steps:
   1. Read the values: info_contact CID:ID
   2. Create command: fetch_from_info create
   3. Alter the command as necessary and send it to the server.

   When your terminal supports text insertion into command line (Unix), the
   command created in this way will be entered into the command line. When you want to display the command at the output
   instead of the command line, enter noprompt (or just n) as the parameter.

   When your terminal does not support prompt insertion (Windows), the command will be
   displayed at the output and you have to copy it into the
   command line.

Chapter 5. Fred_create.py and fred_sender.py scripts

   The fred_create.py and fred_sender.py scripts are intended for use in shell
   batch. fred_create.py accepts parameters from the standard input and generates
   XML EPP document at the standard output. Example:
    $ python fred_create.py info_domain nic.cz
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py
    $ cat file-with-commands.txt | ./fred_create.py

   <?xml version='1.0' encoding....

   When an error is detected, the XML is returned with an error message:
    $ python fred_create.py inxo_domain nic.cz

   <?xml encoding='utf-8'?><errors>inxo_domain nic.cz: Unknown command!</errors>

   fred_sender.py - sends the files to the server The script logs in automatically,
   sends the document, displays the reply and logs-off and terminates. The configuration
   file must contain the correct settings for the logging process to be successful.

   The script sends documents using two methods:

   1. documents are saved as files and filenames are given to the script. The script
   sends them in the specified order. Example:
    $ ./fred_create.py check_domain something.cz nic.cz > doc1.xml
    $ ./fred_create.py info_domain nic.cz > doc2.xml
    $ ./fred_sender.py doc1.xml doc2.xml

   2. PIPE - By chaining create and sender commands. Example:
    $ ./fred_create.py check_domain anything.cz nic.cz | ./fred_sender.py
    $ echo -en "check_domain nic.cz\ninfo_domain nic.cz" | ./fred_create.py | .

    /fred_sender.py

Chapter 6. Integration of client into the PHP code

   CAUTION ! The PHP support extension is in a development and  testing phase in this version of the client.
   The final solution may differ.

   The client also contains a sample PHP script, which demonstrates
   how to integrate the client into a PHP solution: doc/client_example.php. It is necessary to correctly set the
   route to client: $exec_path (unless the client was installed
   using the standard procedure). The $php_module_name variable
   sets redirection to file and $command_options enable addition of other parameters
   when necessary.

PHP Integration:

   The fred_client client may also be run by
   entering a command to be executed by the -d --command at the command line. In such a
   case, the console does not run and the client functions as a batch. 
   This is the same as the combination of fred_create.py and fred_sender.py. The client only
   executes the command, displays output and terminates itself. Login and
   logout are automated and are not displayed at output. The configuration
   file must be correctly defined so that login can take place
  

   The --output -o switch is used to modify the output to a desired format. When you only want to
   display the values in a browser, select HTML: --output=html.
   When you want to process the data in a PHP script, select PHP:
   --output=php.

   Overview of PHP integration:
   Start the client as an external program in PHP, for example by the passthru() function.
   Select the PHP output mode: --outout=php
   Redirect the client output into a writtable directory: ... >
   /cache/outout.php
   Enter the resulting code into the required_once('/cache/outout.php') page, 
   which makes the values available for the PHOP script.

   Variables from PHP output
   $fred_error_create_name = 'poll'; // name of invalid command
   $fred_error_create_value = 'op: Value "xxx" is not allowed. Valid is: (req,
   ack)'; // description of error which occurred during command creation.
   $fred_client_notes = array(); // list of messages during
   communication
   $fred_client_errors = array(); // list of errors occurring during communication
   $fred_encoding = 'utf-8'; // text encoding
   $fred_code = 1000; // return code of reply
   $fred_command = 'domain:info'; // name of command sent
   $fred_reason = 'Command completed successfully'; // description of return code
   $fred_reason_errors = array(); // details of values which caused return
   of the code with an error
   $fred_labels = array(); // list of value labels
   $fred_data = array(); // list of values
   $fred_source_command = '<?xml ... >'; source XML document of the command ( generated
   only in verbose 3).
   $fred_source_answer = '<?xml ... >'; source XML document of the reply 
  (generated only in verbose 3).

   Example of data:

   $fred_labels['domain:name'] = 'Domain name';
   $fred_data['domain:name'] = 'domain.cz';
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

Chapter 7. Graphic interface in Qt4.

   The description of the graphic interface is contained in the file. Look for
   README_QT4...

Chapter 8. The Fred library and description of API

   CONTENTS

   Online documentation:
   Examples of library use

   The "fred" library enables users to implement API interface into your applications.
   The library and the individual functions contain commentaries which will help you
  in implementation. The __init__.py section contains examples of code.

Online documentation:

   When you want to see individual classes and functions of the library, use the
   documentation generator, which is a standard part of Python: 
   Enter:
    $ pydoc -p 8080 at the command line

   If the server does not run, try:
    $ python `which pydoc` -p 8080

   This launches a web server, which generates documentation directly
   from source files. The -p parameter denotes the port at which the server runs.
   You may enter any other port number. Now open a browser and
   enter: http://localhost:8080/ into the address bar. A page is displayed, containing a link to fred (package) in the
   ../site-packages section.

   When you have not installed, just copied the scripts, or when 
   you want to see scripts used for the fred library, follow the same start-up
   procedure, but start pydoc from the directory
   where the scripts are saved. The scripts are then displayed in help:
    $ cd FredClient-n.n.n
    $ pydoc -p 8080

   Terminate the server by pressing Ctrl+C.

Examples of library use

   Import library:
    >>> import fred

   Install EPP client:
    >>> epp = fred.Client()

   Load the config file so that the library finds the certificate:
    >>> epp.load_config()

   When you want to load a different session, enter:
    >>> epp.load_config('my-sessison-name')

   Next, initiate connection using the login function:
    >>> retval = epp.login("username","password")

   Each (EPP command) function returns this "retval" dict-type value
   in the following form:
    {'reason': u'Text of answer reason',
     'code': 1000,
     'command': 'command_name',
     'errors': []
     'data': {'key': 'value' [,'next-key':'next-value']},
    }

   The "reason" (str) key is a server notification on the status of the reply.
   The "code" (int) key is a number defining the type of error. 1,000 means OK
   .
   The "command" (str) key is a name of command to which the reply refers to (which
   trigerred the reply).
   The "errors" (list) key is a list of errors found by the server.
   The "data" (dict) key is a glossary with individual values for each
   command.

   Example: input data:
    name = 'name'
    addr = (1,2,3)
    tech = ('ok',)
    stat = ''

   ...the 'data' glossary will look as follows:
    {'name': 'name',
     IO: 1, DI: 23
     'tech':'ok'           # the type is str and stat is missing
    }

   ...the final version should read like this:
    {'name': 'name',
     IO: 1, DI: 23
     'tech':['ok',]
     'stat':''
    }

   The "retval" (return value) is saved in the internal
   variable and may be displayed using print_answer():
    >>> epp.print_answer(),

   or tested using the is_val() function:
    >>> epp.is_val('reason')
    for 'Text of answer reason'

   Each call of another EPP command overwrites the previous "retval",
   so these two functions only work with the last return value.
   When you want to test or display the return value later, save it
   and then specify:
    >>> epp.print_answer(my_retval)
    >>> epp.is_val('reason', my_retval)

   The is_val() function may be entered without a parameter. In such a case, the default return is the 
  "code" key:
   >>> epp.is_val()
    1,000

   When you want to find a value in any embedded part of the glossary, enter
   the parameter as a path - list of names (keys) in glossary:
    >>> epp.is_val(('data','next-key'))
    next-value

   When the specified key does not exist, None is returned as a value.
    >>> epp.is_val(('data','any-key'))
    None

   When a transfer error, or another error which blocks functionality occurs,
   the FredError exception is generated.




