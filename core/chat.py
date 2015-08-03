# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       chat
Date Created:   2015-08-03 17:54
Description:

"""

import base64


from dianjing.exception import GameException
from core.db import get_mongo_db
from utils.message import MessagePipe

from config import ConfigErrorMessage


from protomsg.chat_pb2 import CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION, ChatNotify, ChatMessage


class Chat(object):
    CHAT_COMMON_MONGO_ID = 'chat'

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)


    def send(self, channel, text):
        if channel not in [CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        char_doc = self.mongo.character.find_one(
            {'_id': self.char_id},
            {'name': 1, 'club.vip': 1}
        )

        msg = ChatMessage()
        msg.channel = channel
        msg.char.id = self.char_id
        msg.char.name = char_doc['name']
        msg.char.vip = char_doc['club']['vip']
        msg.msg = text

        data = base64.b64encode(msg.SerializeToString())

        # TODO union chat
        self.mongo.common.update_one(
            {'_id': self.CHAT_COMMON_MONGO_ID},
            {'$push': {'chats': {
                '$each': [data],
                '$slice': -20
            }}},
            upsert=True
        )

        # TODO performance
        notify = ChatNotify()
        notify_msg = notify.msgs.add()
        notify_msg.MergeFrom(msg)

        for char in self.mongo.character.find():
            MessagePipe(char['_id']).put(msg=notify)


    def send_notify(self):
        notify = ChatNotify()

        msgs = self.mongo.common.find_one({'_id': self.CHAT_COMMON_MONGO_ID}, {'chats': 1})
        for m in msgs:
            notify_msg = notify.msgs.add()
            notify_msg.MergeFromString(base64.b64decode(m))

        MessagePipe(self.char_id).put(msg=notify)

