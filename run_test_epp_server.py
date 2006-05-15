# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
import epplib.server_session

if __name__ == '__main__':
    import sys
    interactive = None
    if len(sys.argv)>1:
        if sys.argv[1]=='i':
            interactive = 'yes' # zapnutí promptu
    epplib.server_session.test('', 700, interactive)

