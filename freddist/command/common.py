"""
freddist.common

Common functions for freddist.command classes
"""

import re

def replace_pattern(fileOpen, fileSave=None, values = []):
    """
    Replace given patterns with new values, for example in config files.
    Patterns and new values can contain regular expressions.
    Structure of values parameter looks like:
    [(pattern_1, new_val_1), (pattern_2, new_val_2), ...]
    """
    if not fileSave:
        fileSave = fileOpen
    body = open(fileOpen).read()

    for value in values:
        body = re.sub(value[0], value[1], body)

    open(fileSave, 'w').write(body)
