# -*- coding: utf8 -*-
#!/usr/bin/env python
#
"""Support of command line history.
"""
from translate import _T

class Completer:
    'Class holds history of commands.'
    def __init__(self, words):
        self.words = words
        self.prefix = None
        
    def complete(self, prefix, index):
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [w for w in self.words if w.startswith(prefix)]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

def set_history(words):
    'Activate support of the commands history.'
    try:
        import readline
    except ImportError:
        print _T('readline module missing - cmd history is diabled')
    else:
        completer = Completer(words)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
