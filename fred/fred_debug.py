#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# For internal use only! It is important during make installation file.
# Check this module if is not in installation. In case it is in, remove it.
#
"""This module is used for test and debugging application.
It is not uncluded in official release.
"""

def check_missing_names(body, columns, verbose_level, is_check, dct_data, used, column_verbose):
    'Check if any valus missing in outout. For DEBUGING only.'
    if columns and not is_check:
        # in mode SORT_BY_COLUMNS check if all names was used
        missing = [k for k in dct_data.keys() if k not in used and column_verbose.get(k,0) >= verbose_level]
        if len(missing):
            body.append(colored_output.render('\n${BOLD}${RED}Here needs FIX code: %s${NORMAL}'%'(%s)'%', '.join(missing)))
