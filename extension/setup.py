# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       setup.py
Date Created:   2015-10-28 17:52
Description:

"""

from distutils.core import setup, Extension

module1 = Extension('formula', sources=['wrap.c'])

setup(
    name='formula',
    version='1.0',
    ext_modules=[module1]
)
