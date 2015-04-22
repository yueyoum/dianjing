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
    __slots__ = ['msg',]
    def __new__(cls, msg, session=""):
        obj = ProtobufResponse(msg, session=session)
        data = obj.pack()
        # other_data = obj.get_other_data()
        # num_of_msgs = len(other_data) + 1
        #
        # result = '%s%s%s' % (
        #     NUM_FILED.pack(num_of_msgs),
        #     data,
        #     ''.join(other_data)
        # )

        return HttpResponse(data, content_type='text/plain')


    def __init__(self, msg, session=""):
        msg.session = session
        self.msg = msg

    def pack(self):
        data = self.msg.SerializeToString()
        data_id = MESSAGE_TO_ID[self.msg.DESCRIPTOR.name]
        data_len = len(data)

        packed = '%s%s%s' % (
            NUM_FILED.pack(data_id),
            NUM_FILED.pack(data_len),
            data
        )

        return packed

    def get_other_data(self):
        # if self.char_id:
        #     other_data = message_get(self.char_id)
        # else:
        #     other_data = []
        #
        # return other_data
        return []
