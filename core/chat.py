# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       chat
Date Created:   2015-08-03 17:54
Description:

"""

import base64
import cPickle

from dianjing.exception import GameException
from core.mongo import MongoCommon, MongoCharacter
from core.common import CommonChat
from core.signals import chat_signal

from config import ConfigErrorMessage
from utils.message import MessagePipe, MessageFactory

from protomsg.chat_pb2 import CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION, ChatNotify, ChatMessage
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


class Chat(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def send(self, channel, text):
        from tasks import world

        if channel not in [CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        char_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'name': 1, 'club.vip': 1}
        )

        msg = ChatMessage()
        msg.channel = channel
        msg.char.id = str(self.char_id)
        msg.char.name = char_doc['name']
        msg.char.vip = char_doc['club']['vip']
        msg.msg = text

        data = base64.b64encode(msg.SerializeToString())

        # TODO union chat
        MongoCommon.db(self.server_id).update_one(
            {'_id': CommonChat.ID},
            {'$push': {'value': {
                '$each': [data],
                '$slice': -20
            }}},
            upsert=True
        )

        notify = ChatNotify()
        notify.act = ACT_UPDATE
        notify_msg = notify.msgs.add()
        notify_msg.MergeFrom(msg)

        notify_bin = MessageFactory.pack(notify)

        arg = {
            'server_id': self.server_id,
            'exclude_chars': [self.char_id],
            'data': MessageFactory.pack(notify)
        }

        payload = cPickle.dumps(arg)
        world.broadcast(payload=payload)

        MessagePipe(self.char_id).put(data=notify_bin)

        chat_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id
        )

    def send_notify(self):
        notify = ChatNotify()
        notify.act = ACT_INIT

        value = CommonChat.get(self.server_id)

        for v in value:
            notify_msg = notify.msgs.add()
            notify_msg.MergeFromString(base64.b64decode(v))

        MessagePipe(self.char_id).put(msg=notify)
