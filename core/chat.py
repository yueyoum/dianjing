# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       chat
Date Created:   2015-08-03 17:54
Description:

"""

import base64
import cPickle

import arrow

from django.conf import settings
from django.db.models import Q
from apps.gift_code.models import GiftCode, GiftCodeUsingLog

from dianjing.exception import GameException
from core.mongo import MongoCharacter
from core.common import CommonPublicChat, CommonUnionChat
from core.signals import chat_signal
from core.resource import ResourceClassification, item_id_to_money_text
from core.club import Club
from core.vip import VIP
from core.union import Union
from core.cooldown import ChatCD

from config import ConfigErrorMessage, GlobalConfig
from utils.message import MessagePipe, MessageFactory

from protomsg.chat_pb2 import CHAT_CHANNEL_PUBLIC, CHAT_CHANNEL_UNION, ChatNotify, ChatMessage, ChatSendRequest
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

CHAT_MAX_SIZE = 2000


class Chat(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def send(self, tp, channel, text):

        if tp != ChatSendRequest.NORMAL:
            if not settings.GM_CMD_OPEN:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            self.command(tp, text)
            return

        # check gift code
        try:
            gift = GiftCode.objects.get(id=text)
        except GiftCode.DoesNotExist:
            self.normal_chat(channel, text)
            return

        self.gift(gift)


    def normal_chat(self, channel, text):
        from tasks import world

        char_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'name': 1, 'vip': 1, 'level': 1}
        )

        union_id = 0
        if channel == CHAT_CHANNEL_PUBLIC:
            if char_doc['level'] < GlobalConfig.value("CHAT_LEVEL_LIMIT"):
                raise GameException(ConfigErrorMessage.get_error_id("CHAT_LEVEL_NOT_ENOUGH"))

            if ChatCD(self.server_id, self.char_id).get_cd_seconds():
                raise GameException(ConfigErrorMessage.get_error_id("CHAT_TOO_FAST"))

            if len(text) > CHAT_MAX_SIZE:
                raise GameException(ConfigErrorMessage.get_error_id("CHAT_TOO_LARGE"))

            ChatCD(self.server_id, self.char_id).set(GlobalConfig.value("CHAT_CD"))

        elif channel == CHAT_CHANNEL_UNION:
            union_id = Union(self.server_id, self.char_id).get_joined_union_id()
            if not union_id:
                raise GameException(ConfigErrorMessage.get_error_id("UNION_CHAT_NO_UNION"))
        else:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # 创建一个消息
        msg = ChatMessage()
        msg.channel = channel
        msg.club.id = str(self.char_id)
        msg.club.name = char_doc['name']
        msg.club.vip = VIP(self.server_id, self.char_id).level
        msg.msg = text
        data = base64.b64encode(msg.SerializeToString())

        # 立即通知自己
        notify = ChatNotify()
        notify.act = ACT_UPDATE
        notify_msg = notify.msgs.add()
        notify_msg.MergeFrom(msg)

        notify_bin = MessageFactory.pack(notify)
        MessagePipe(self.char_id).put(data=notify_bin)

        # 放入公共空间，让后面登陆的人都能看到
        # 等于离线消息
        if channel == CHAT_CHANNEL_PUBLIC:
            CommonPublicChat(self.server_id).push(data, slice_amount=20)
            # 给其他人广播通知
            arg = {
                'server_id': self.server_id,
                'exclude_chars': [self.char_id],
                'data': MessageFactory.pack(notify)
            }

            payload = cPickle.dumps(arg)
            world.broadcast(payload=payload)
        else:
            CommonUnionChat(self.server_id, union_id).push(data, slice_amount=20)
            arg = {
                'server_id': self.server_id,
                'exclude_chars': [self.char_id],
                'data': MessageFactory.pack(notify),
                'char_id': self.char_id
            }

            payload = cPickle.dumps(arg)
            world.broadcast_union_chat(payload=payload)

        chat_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id
        )


    def command(self, tp, data):
        from core.challenge import Challenge

        if tp == ChatSendRequest.ADD_ITEM:
            items = []
            try:
                for x in data.split(';'):
                    if not x or x == '\n' or x == '\r\n':
                        continue

                    _id, _amount = x.split(',')
                    items.append((int(_id), int(_amount)))

                resource_classified = ResourceClassification.classify(items)
                for _id, _amount in resource_classified.staff:
                    # GM命令可能会添加大量的staff, 这是错误情况
                    assert _amount < 1000
            except:
                raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

            resource_classified.add(self.server_id, self.char_id, message="Chat.command")

        elif tp == ChatSendRequest.SET_MONEY:
            setter = {}
            for x in data.split(";"):
                _id, _amount = x.split(',')
                name = item_id_to_money_text(int(_id))

                setter[name] = int(_amount)

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
                    'level': level
                }}
            )

            Club(self.server_id, self.char_id).send_notify()
        elif tp == ChatSendRequest.OPEN_ALL_CHALLENGE:
            Challenge(self.server_id, self.char_id).open_all()
        else:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    def gift(self, gift):
        """

        :type gift: GiftCode
        """

        if not gift.active:
            raise GameException(ConfigErrorMessage.get_error_id("GIFT_CODE_NOT_ACTIVE"))

        if gift.time_range1:
            time1 = arrow.get(gift.time_range1).timestamp
            if arrow.utcnow().timestamp < time1:
                raise GameException(ConfigErrorMessage.get_error_id("GIFT_CODE_NOT_STARTED"))

        if gift.time_range2:
            time2 = arrow.get(gift.time_range2).timestamp
            if arrow.utcnow().timestamp > time2:
                raise GameException(ConfigErrorMessage.get_error_id("GIFT_CODE_EXPIRED"))

        if gift.times_limit:
            condition = Q(char_id=self.char_id) & Q(gift_code=gift.id)
            using_times = GiftCodeUsingLog.objects.filter(condition).count()
            if using_times >= gift.times_limit:
                raise GameException(ConfigErrorMessage.get_error_id("GIFT_CODE_NO_TIMES"))

        # ALL OK
        items = gift.get_parsed_items()
        rc = ResourceClassification.classify(items)
        rc.add(self.server_id, self.char_id, message="Chat.gift:{0}".format(gift.id))


    def send_notify(self):
        notify = ChatNotify()
        notify.act = ACT_INIT

        values = []
        value1 = CommonPublicChat(self.server_id).get()
        if value1:
            values.append(value1)

        union = Union(self.server_id, self.char_id)
        union_id = union.get_joined_union_id()
        if union_id:
            value2 = CommonUnionChat(self.server_id, union_id).get()
            if value2:
                values.append(value2)

        for value in values:
            for v in value:
                msg = ChatMessage()
                try:
                    msg.MergeFromString(base64.b64decode(v))
                except:
                    continue

                notify_msg = notify.msgs.add()
                notify_msg.MergeFrom(msg)

        MessagePipe(self.char_id).put(msg=notify)
