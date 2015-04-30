# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       msgpipe
Date Created:   2015-04-29 23:19
Description:

"""
import struct

from core.db import redis_client
from protomsg import MESSAGE_TO_ID


EXPIRE = 3600
NUM_FILED = struct.Struct('>i')


class MessageFactory(object):
    @staticmethod
    def pack(msg):
        if not msg.session:
            msg.session = ""

        data = msg.SerializeToString()
        data_id = MESSAGE_TO_ID[msg.DESCRIPTOR.name]
        data_len = len(data)

        packed = '%s%s%s' % (
            NUM_FILED.pack(data_id),
            NUM_FILED.pack(data_len),
            data
        )

        return packed




class MessagePipe(object):
    __slots__ = ['char_id', 'key']
    def __init__(self, char_id):
        self.char_id = char_id
        self.key = "msg:{0}".format(self.char_id)

    def put(self, msg=None, data=None):
        # data is Serialized msg
        if msg is not None:
            data = MessageFactory.pack(msg)

        assert data is not None

        with redis_client.pipeline() as p:
            p.rpush(self.key, data)
            p.expire(self.key, EXPIRE)

    def get(self):
        with redis_client.pipeline() as p:
            data = p.lrange(self.key, 0, -1)
            p.delete(self.key)

        return data

    def clean(self):
        redis_client.delete(self.key)

