# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__.py
Date Created:   2015-04-30 15:23
Description:

"""

import os

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

files = os.listdir(CURRENT_PATH)
for f in files:
    if f.endswith('.py') and f != '__init__.py':
        __import__('signals.{0}'.format(f[:-3]))
