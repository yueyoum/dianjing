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
from core.resource import ResourceClassification, item_id_to_money_text
from core.club import Club
from core.vip import VIP

from config import ConfigErrorMessage
from utils.message import MessagePipe, MessageFactory

from protomsg.chat_pb2 import CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION, ChatNotify, ChatMessage, ChatSendRequest
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


class Chat(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def send(self, tp, channel, text):
        from tasks import world

        if tp != ChatSendRequest.NORMAL:
            self.command(tp, text)
            return

        if channel not in [CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        char_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'club.name': 1, 'club.vip': 1}
        )

        msg = ChatMessage()
        msg.channel = channel
        msg.club.id = str(self.char_id)
        msg.club.name = char_doc['club']['name']
        msg.club.vip = VIP(self.server_id, self.char_id).level
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

    def command(self, tp, data):
        if tp == ChatSendRequest.ADD_ITEM:
            items = []
            for x in data.split(';'):
                _id, _amount = x.split(',')
                items.append((int(_id), int(_amount)))

                resource_classified = ResourceClassification.classify(items)
                resource_classified.add(self.server_id, self.char_id)

        elif tp == ChatSendRequest.SET_MONEY:
            setter = {}
            for x in data.split(";"):
                _id, _amount = x.split(',')
                name = item_id_to_money_text(int(_id))

                setter['club.{0}'.format(name)] = int(_amount)

            MongoCharacter.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': setter}
            )

            Club(self.server_id, self.char_id).send_notify()

        elif tp == ChatSendRequest.SET_CLUB_LEVEL:
            level = int(data)
            MongoCharacter.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'club.level': level
                }}
            )

            Club(self.server_id, self.char_id).send_notify()
        else:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))


    def send_notify(self):
        notify = ChatNotify()
        notify.act = ACT_INIT

        value = CommonChat.get(self.server_id)

        if value:
            for v in value:
                notify_msg = notify.msgs.add()
                notify_msg.MergeFromString(base64.b64decode(v))

        MessagePipe(self.char_id).put(msg=notify)
