# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       functional
Date Created:   2015-08-11 19:00
Description:

"""

import os
import uuid
import base64
import random
import string

def make_string_id():
    return str(uuid.uuid4())

def make_short_string_id():
    text = base64.b64encode(os.urandom(6))
    text = text.replace('+', random.choice(string.letters))
    text = text.replace('/', random.choice(string.letters))
    return text