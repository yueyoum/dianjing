# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       common
Date Created:   2015-08-05 10:23
Description:

"""
import arrow

from dianjing.exception import GameException

from core.mongo import MongoCommon
from utils.functional import make_string_id
from core.lock import (
    LockTimeOut,
    LeaderboardArenaChatLock,
    LeaderboardPlunderChatLock,
    LeaderboardChampionshipChatLock,
)

from core.cooldown import LeaderboardArenaChatCD, LeaderboardPlunderChatCD, LeaderboardChampionshipChatCD

from utils.message import MessagePipe, MessageFactory
from utils.operation_log import OperationLog

from config import GlobalConfig, ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.leaderboard_pb2 import (
    LeaderboardArenaChatNotify,
    LeaderboardArenaChatRemoveNotify,
    LeaderboardPlunderChatNotify,
    LeaderboardPlunderChatRemoveNotify,
    LeaderboardChampionshipChatNotify,
    LeaderboardChampionshipChatRemoveNotify,
)


class BaseCommon(object):
    __slots__ = ['server_id']

    def __init__(self, server_id):
        self.server_id = server_id

    def get_id(self):
        raise NotImplementedError()

    def get(self):
        _id = self.get_id()
        doc = MongoCommon.db(self.server_id).find_one({'_id': _id})
        return doc.get('value', None) if doc else None

    def set(self, value):
        _id = self.get_id()
        MongoCommon.db(self.server_id).update_one(
            {'_id': _id},
            {'$set': {'value': value}},
            upsert=True
        )

    def push(self, value, slice_amount=None):
        if isinstance(value, (list, tuple)):
            value_list = list(value)
        else:
            value_list = [value]

        updater = {
            '$push': {
                'value': {
                    '$each': value_list,
                }
            }
        }

        if slice_amount:
            updater['$push']['value']['$slice'] = -slice_amount

        _id = self.get_id()
        MongoCommon.db(self.server_id).update_one(
            {'_id': _id},
            updater,
            upsert=True
        )

    def delete(self):
        _id = self.get_id()
        MongoCommon.db(self.server_id).delete_one({'_id': _id})


class CommonPublicChat(BaseCommon):
    __slots__ = []

    def get_id(self):
        return 'chat'


class CommonUnionChat(BaseCommon):
    __slots__ = ['union_id']

    def __init__(self, server_id, union_id):
        super(CommonUnionChat, self).__init__(server_id)
        self.union_id = union_id

    def get_id(self):
        return 'union_chat_{0}'.format(self.union_id)


class CommonWinningArena(BaseCommon):
    __slots__ = []

    def get_id(self):
        return 'winning_arena'


class CommonWinningPlunder(BaseCommon):
    __slots__ = []

    def get_id(self):
        return 'winning_plunder'


class CommonWinningChampionship(BaseCommon):
    __slots__ = []

    def get_id(self):
        return 'winning_championship'


class _CommonWinningChat(BaseCommon):
    __slots__ = ['char_id', 'doc']
    LOCK = None
    """:type: core.lock.RedisLock"""
    CD = None
    """:type: core.cooldown.CD"""
    NOTIFY = None
    REMOVE_NOTIFY = None

    def __init__(self, server_id, char_id):
        super(_CommonWinningChat, self).__init__(server_id)
        self.char_id = char_id
        _id = self.get_id()
        self.doc = MongoCommon.db(self.server_id).find_one({'_id': _id})
        if not self.doc:
            self.doc = MongoCommon.document()
            self.doc['_id'] = _id
            self.doc['value'] = []
            MongoCommon.db(self.server_id).insert_one(self.doc)

            # value: [
            #     {
            #         'msg_id': xx,
            #         'club_id': xx,
            #         'name': xx,
            #         'content': xx,
            #         'post_at': xx,
            #         'approval': xx,
            #         'last_update_at': xx,
            #     },
            #     ...
            # ]

    def get(self):
        return self.doc['value']

    def post(self, content):
        from core.club import get_club_property

        if self.CD(self.server_id, self.char_id).get_cd_seconds():
            raise GameException(ConfigErrorMessage.get_error_id("CHAT_TOO_FAST"))

        if len(content) > 300:
            raise GameException(ConfigErrorMessage.get_error_id("CHAT_TOO_LARGE"))

        try:
            with self.LOCK(self.server_id, self.char_id).lock(3, 3):
                now = arrow.utcnow().timestamp

                message = {
                    'msg_id': make_string_id(),
                    'club_id': str(self.char_id),
                    'name': get_club_property(self.server_id, self.char_id, 'name'),
                    'content': content,
                    'post_at': now,
                    'approval': 0,
                    'last_update_at': now,
                }

                _data = self.make_notify_data(message=message)
                self.broadcast(_data)

                self.doc['value'].insert(0, message)
                if len(self.doc['value']) > 100:
                    self.doc['value'].sort(key=lambda item: -item['last_update_at'])
                    removed = self.doc['value'].pop(-1)

                    remove_notify = self.REMOVE_NOTIFY()
                    remove_notify.msg_id = removed['msg_id']
                    self.broadcast(MessageFactory.pack(remove_notify))

                MongoCommon.db(self.server_id).update_one(
                    {'_id': self.get_id()},
                    {'$set': {
                        'value': self.doc['value']
                    }}
                )

        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("SERVER_BUSY"))

        self.CD(self.server_id, self.char_id).set(GlobalConfig.value("LEADERBOARD_CHAT_INTERVAL"))

    def approval(self, msg_id):
        index = -1
        for _index, message in enumerate(self.doc['value']):
            if message['msg_id'] == msg_id:
                index = _index
                break

        if index == -1:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        try:
            with self.LOCK(self.server_id, self.char_id).lock(3, 3):
                self.doc['value'][index]['approval'] += 1
                self.doc['value'][index]['last_update_at'] += arrow.utcnow().timestamp

                MongoCommon.db(self.server_id).update_one(
                    {'_id': self.get_id()},
                    {'$set': {
                        'value': self.doc['value']
                    }}
                )

                _data = self.make_notify_data(message=self.doc['value'][index])
                self.broadcast(_data)

        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("SERVER_BUSY"))

    def make_notify_data(self, message=None):
        if message:
            act = ACT_UPDATE
            value = [message]
        else:
            act = ACT_INIT
            value = self.doc['value']

        value.sort(key=lambda item: item['post_at'], reverse=True)

        notify = self.NOTIFY()
        notify.act = act
        notify.session = ""

        for v in value:
            notify_message = notify.messages.add()
            notify_message.msg_id = v['msg_id']
            notify_message.club_id = v['club_id']
            notify_message.name = v['name']
            notify_message.content = v['content']
            notify_message.timestamp = v['post_at']
            notify_message.approval = v['approval']

        return MessageFactory.pack(notify)

    def broadcast(self, data):
        char_ids = OperationLog.get_recent_action_char_ids(self.server_id, recent_minutes=5)
        if self.char_id not in char_ids:
            char_ids.append(self.char_id)

        for _id in char_ids:
            MessagePipe(_id).put(data=data)

    def send_notify(self):
        data = self.make_notify_data()
        MessagePipe(self.char_id).put(data=data)


class CommonArenaWinningChat(_CommonWinningChat):
    LOCK = LeaderboardArenaChatLock
    CD = LeaderboardArenaChatCD
    NOTIFY = LeaderboardArenaChatNotify
    REMOVE_NOTIFY = LeaderboardArenaChatRemoveNotify

    def get_id(self):
        return 'winning_arena_chat'


class CommonPlunderWinningChat(_CommonWinningChat):
    LOCK = LeaderboardPlunderChatLock
    CD = LeaderboardPlunderChatCD
    NOTIFY = LeaderboardPlunderChatNotify
    REMOVE_NOTIFY = LeaderboardPlunderChatRemoveNotify

    def get_id(self):
        return 'winning_plunder_chat'


class CommonChampionshipChat(_CommonWinningChat):
    LOCK = LeaderboardChampionshipChatLock
    CD = LeaderboardChampionshipChatCD
    NOTIFY = LeaderboardChampionshipChatNotify
    REMOVE_NOTIFY = LeaderboardChampionshipChatRemoveNotify

    def get_id(self):
        return 'winning_championship_chat'
