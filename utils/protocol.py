# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       protocol
Date Created:   2016-03-31 10-21
Description:

"""

def get_protocol_field_names(protocol):
    return [f.name for f in protocol.DESCRIPTOR.fields]
