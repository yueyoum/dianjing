# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__.py
Date Created:   2015-09-02 13:39
Description:

"""


import os
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

for f in os.listdir(CURRENT_PATH):
    if f.endswith('.py') and f != '__init__.py':
        __import__('tasks.{0}'.format(f[:-3]))
