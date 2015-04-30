# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       http
Date Created:   2015-04-22 03:17
Description:

"""

from django.http import HttpResponse
from utils.message import MessageFactory



class ProtobufResponse(object):
    def __new__(cls, msg):
        data = MessageFactory.pack(msg)
        return HttpResponse(data, content_type='text/plain')
