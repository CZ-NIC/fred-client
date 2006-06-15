# -*- coding: utf8 -*-
#!/usr/bin/env python
import re, time
import os, commands
from gettext import gettext as _T
import terminal_controler

# Cesta ke schematům pro ověření validity EPP dokumentu
# vzažena relativně k rootu, tedy adresáři, ve kterém je umístěn
# adresář epplib
EPP_SCHEMA_PATH = '../mod_eppd/schemas/all-1.0.xsd'

# Colored output
colored_output = terminal_controler.TerminalController()

# názvy sloupců pro data sestavené při spojení se serverem
ONLINE,CMD_ID,LANG = range(3)
# názvy sloupců pro defaultní hodnoty
DEFS_LENGTH = 4
VERSION,LANGS,objURI,PREFIX = range(DEFS_LENGTH)

class ManagerBase:
    """This class hold buffers with error and note messages.
    Class collect messages and prepare them to outout.
    """
    def __init__(self):
        self._notes = [] # upozornění na chybné zadání
        self._errors = [] # chybová hlášení při přenosu, parsování
        self._sep = '\n' # oddělovač jednotlivých zpráv
        self._validate = 1 # automatické zapnutí validace EPP XML dokumentů
        self._validate_schema_path = EPP_SCHEMA_PATH
        #-----------------------------------------
        # Session data:
        #-----------------------------------------
        self._session = [0, 0, 'en'] # hodnoty vytvořené při sestavení session (ID, lang,...)
        # defaults
        self.defs = ['']*DEFS_LENGTH
        self.defs[VERSION] = '1.0'
        self.defs[LANGS] = ('en','cz') # seznam dostupných jazyků
        self.defs[objURI] = 'urn:ietf:params:xml:ns:obj1'
        self.defs[PREFIX] = '' # pro každé sezení nový prefix

    def get_errors(self, sep='\n'):
        return sep.join(self._errors)

    def append_error(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._errors, msg, color)

    def append_note(self, msg, color=''):
        "Join messages if only they are not empty."
        if msg: append_with_colors(self._notes, msg, color)

    def fetch_errors(self, sep='\n'):
        msg = sep.join(self._errors)
        self._errors = []
        return msg

    def fetch_notes(self, sep='\n'):
        msg = sep.join(self._notes)
        self._notes = []
        return msg

    def is_error(self):
        "Check if any error occurs."
        return len(self._errors)
        
    def is_note(self):
        "Check if any note is in the stack"
        return len(self._notes)

    def display(self):
        "Output all messages to stdout or log file."
        #TODO: log file
        if self.is_note():
            # hlášení, poznámka, hodnoty
            print colored_output.render(self.fetch_notes())
        if self.is_error():
            # chybová hlášení
            print colored_output.render('${MAGENTA}')
            print colored_output.render(self.fetch_errors())
            print colored_output.render('${NORMAL}')

    def __next_clTRID__(self):
        """Generate next clTRID value.
        format: [4 random ASCII chars][3 digits of the commands order]#[date and time]
        """
        self._session[CMD_ID]+=1 
        return ('%s%03d#%s'%(self.defs[PREFIX],self._session[CMD_ID],time.strftime('%y-%m-%dat%H:%M:%S')))

    def set_validate(self, cmd):
        "Set feature of the manager - it will or not validate EPP documents. cmd='validate on/off'"
        if re.match('validate$',cmd):
            # jen zobrazení stavu
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Status: Validation is'),('OFF','ON')[self._validate]))
        else:
            # změna stavu
            self._validate = (1,0)[re.match('validate\s+on',cmd, re.I)==None]
            self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Validation is set'),('OFF','ON')[self._validate]))

    def is_epp_valid(self, message):
        "Check XML EPP by xmllint. OUT: '' - correct; '...' any error occurs."
        if not self._validate: return '' # validace je vypnutá
        tmpname='tmp.xml'
        open(tmpname,'w').write(message)
        # kontrola validity XML
        valid = commands.getoutput('xmllint --schema %s %s'%(self._validate_schema_path, tmpname))
        os.unlink(tmpname)
        if valid[-9:]=='validates':
            valid='' # '' = žádné chybové hlášení. Když se vrátí prázdný řetězec, tak je XML validní.
        else:
            # když příkaz chybí na linuxu
            # když příkaz chybí ve Windows XP
            # Když nebyla nalezena schemata
            if re.search('command not found',valid) \
                or re.search(u'není názvem vnitřního ani vnějšího příkazu'.encode('cp852'),valid) \
                or re.search('Schemas parser error',valid):
                # sh: xmllint: command not found
                ##warning: failed to load external entity "../mod_eppd/schemas/all-1.0.xsd"
                ##Schemas parser error : Failed to locate the main schema resource at '../mod_eppd/schemas/all-1.0.xsd'.
                failed = re.search('warning: failed to load external entity "([^"]+)"',valid)
                if failed:
                    self.append_note('%s ${BOLD}%s${NORMAL}'%(_T('Error: Failed to load EPP schema'),failed.group(1)))
                else:
                    self.append_note('%s: %s'%(_T('XML validator is not available'),valid))
                self._validate = 0 # automatické vypnutí validace
                self.append_note('%s ${BOLD}validate on${NORMAL}.'%_T('Validator has been disabled. For enable type'))
                # pokud není validátor k dispozici, tak se to nepovažuje za chybu, 
                # na serveru se data stejně ověřují
                valid=''
            else:
                # odstraní se kopie zdrojového souboru, která je před popisem chyby
                m = re.search('</epp>\s*(.+)',valid,re.I)
                if m: valid = m.group(1)
        return valid

def append_with_colors(list_of_messages, msg, color):
    "Used by Manager::append_error() and Manager::append_note() functions"
    if type(color) in (list, tuple):
        c = ''.join(['${%s}'%c for c in color])
    else:
        c = '${%s}'%(color or 'YELLOW') # default
    list_of_messages.append('%s%s${NORMAL}'%(c,msg))
