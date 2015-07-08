# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       crypto
Date Created:   2015-04-22 14:56
Description:

"""

from Crypto.Cipher import AES
from django.conf import settings

BLOCK_SIZE = 16
MODE = AES.MODE_CBC
KEY = settings.AES_KEY
IV = settings.AES_CBC_IV


class BadEncryptedText(Exception):
    pass


def encrypt(text):
    length = len(text)
    a, b = divmod(length, BLOCK_SIZE)
    rest = (a + 1) * BLOCK_SIZE - length - 1

    text = '%s|%s' % (text, rest * '*')
    obj = AES.new(KEY, MODE, IV)
    return obj.encrypt(text)


def decrypt(text):
    if len(text) % BLOCK_SIZE != 0:
        raise BadEncryptedText()

    obj = AES.new(KEY, MODE, IV)
    result = obj.decrypt(text)

    head, tail = result.rsplit('|', 1)
    return head
