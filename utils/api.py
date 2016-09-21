# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       api
Date Created:   2016-09-19 15:01
Description:

"""

import base64

from utils.message import MessagePipe


def get_extra_msgs(char_id):
    if not char_id:
        return ''

    extra_msgs = MessagePipe(char_id).get()
    # 去掉头部4字节长度， erlang发送的时候会自己添加
    extra_msgs = [base64.b64encode(msg[4:]) for msg in extra_msgs]
    return extra_msgs

# API return
# {
#     'code': 0,            0 正常， 其他 错误码
#     'data': {},           数据
#     'extra': [],          额外需要socket发送给客户端的字节
#     'others': [Other],    其他角色信息
# }
#
# Other format:
# {
#     'char_id': 0,         角色id
#     'data': {},           数据
#     'extra': []           额外发送
# }
#

class APIReturn(object):
    __slots__ = ['char_id', 'code', 'data', 'others']

    def __init__(self, char_id):
        self.char_id = char_id
        self.code = 0
        self.data = {}
        self.others = {}

    def set_data(self, k, v):
        self.data[k] = v

    def add_other_char(self, char_id):
        assert char_id not in self.others
        self.others[char_id] = {}

    def set_other_char_data(self, char_id, k, v):
        if char_id in self.others:
            self.others[char_id][k] = v
        else:
            self.others[char_id] = {k: v}

    def normalize(self):
        ret = {
            'code': self.code,
            'data': self.data,
            'extra': get_extra_msgs(self.char_id),
            'others': []
        }

        for k, v in self.others.iteritems():
            o = {
                'char_id': k,
                'data': v,
                'extra': get_extra_msgs(k)
            }

            ret['others'].append(o)

        if ret['code']:
            print "API Error Code: {0}".format(ret['code'])
        if ret['extra']:
            print "API return has extra"

        return ret
