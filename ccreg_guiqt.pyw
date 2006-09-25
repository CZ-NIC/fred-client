# -*- coding: utf-8 -*-
import ccReg
from ccReg.translate import _T, encoding, options, option_errors
from guiqt.main import main

if __name__ == '__main__':
    msg_invalid = ccReg.check_python_version()
    if msg_invalid:
        print msg_invalid
    elif options['version']:
        epp = ccReg.ClientSession()
        print epp.version()
    else:
        if option_errors:
            print option_errors
        else:
            main([], options['lang'])
