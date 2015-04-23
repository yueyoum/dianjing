# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       http
Date Created:   2015-04-22 03:17
Description:

"""
import struct

from django.http import HttpResponse

from protomsg import MESSAGE_TO_ID

NUM_FILED = struct.Struct('>i')



class ProtobufResponse(object):
    def __new__(cls, msg):
        if not msg.session:
            msg.session = ""
        data = ProtobufResponse.pack(msg)
        return HttpResponse(data, content_type='text/plain')


    @staticmethod
    def pack(msg):
        data = msg.SerializeToString()
        data_id = MESSAGE_TO_ID[msg.DESCRIPTOR.name]
        data_len = len(data)

        packed = '%s%s%s' % (
            NUM_FILED.pack(data_id),
            NUM_FILED.pack(data_len),
            data
        )

        return packed
