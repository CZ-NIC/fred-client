# -*- coding: utf-8 -*-
import fred
from fred.translate import encoding, options, option_errors
from guiqt4.main import main

if __name__ == '__main__':
    msg_invalid = fred.check_python_version()
    if msg_invalid:
        print msg_invalid
    elif options['version']:
        epp = fred.ClientSession()
        print epp.version()
    else:
        if option_errors:
            print option_errors
        else:
            main([], options['lang'])