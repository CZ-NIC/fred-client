#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2018  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

"""This module is used for test and debugging application.
It is not uncluded in official release.
"""
from __future__ import unicode_literals

def check_missing_names(body, columns, verbose_level, is_check, dct_data, used, column_verbose):
    'Check if any valus missing in outout. For DEBUGING only.'
    if columns and not is_check:
        # in mode SORT_BY_COLUMNS check if all names was used
        missing = [k for k in dct_data.keys() if k not in used and column_verbose.get(k, 0) >= verbose_level]
        if len(missing):
            body.append(colored_output.render('\n${BOLD}${RED}Here needs FIX code: %s${NORMAL}' % '(%s)' % ', '.join(missing)))
