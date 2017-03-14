# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       winning
Date Created:   2017-02-13 14:31
Description:

"""
import base64

from dianjing.exception import GameException

from core.mongo import MongoArenaWinning, MongoPlunderWinning
from core.common import CommonWinningArena, CommonWinningPlunder, CommonWinningChampionship
from core.value_log import ValueLogWorshipTimes
from core.resource import ResourceClassification

from utils.message import MessagePipe
from utils.operation_log import OperationLog

from config import ConfigErrorMessage, ConfigItemUse

from protomsg.leaderboard_pb2 import (
    LeaderboardArenaWinningNotify,
    LeaderboardPlunderWinningNotify,
    LeaderboardChampionshipNotify,
    LeaderboardWorshipNotify,
)


class _Winning(object):
    MONGO_DOCUMENT = None
    """:type: core.mongo.BaseDocument"""
    COMMON = None
    """:type: core.common.BaseCommon"""
    NOTIFY = None

    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = None

        self.get_or_create_doc()

    def get_or_create_doc(self):
        self.doc = self.MONGO_DOCUMENT.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = self.MONGO_DOCUMENT.document()
            self.doc['_id'] = self.char_id
            self.MONGO_DOCUMENT.db(self.server_id).insert_one(self.doc)

    def set(self, win):
        self.doc['total_count'] += 1
        if win:
            self.doc['win_count'] += 1

        winning = self.doc['total_count'] ** 1.5 * (self.doc['win_count'] * 1.0 / self.doc['total_count'])
        self.doc['winning'] = round(winning, 2)

        self.MONGO_DOCUMENT.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'total_count': self.doc['total_count'],
                'win_count': self.doc['win_count'],
                'winning': self.doc['winning'],
            }}
        )

    def get(self):
        return self.COMMON(self.server_id).get()

    def send_notify(self):
        value = self.get()

        notify = self.NOTIFY()
        if value:
            try:
                notify.ParseFromString(base64.b64decode(value))
            except:
                notify = self.NOTIFY()

        MessagePipe(self.char_id).put(msg=notify)


class WinningArena(_Winning):
    MONGO_DOCUMENT = MongoArenaWinning
    COMMON = CommonWinningArena
    NOTIFY = LeaderboardArenaWinningNotify
    __slots__ = []

    @classmethod
    def cronjob(cls, sid):
        from core.club import Club
        from core.formation import Formation

        notify = cls.NOTIFY()
        notify.session = ""

        docs = cls.MONGO_DOCUMENT.db(sid).find({'winning': {'$gt': 0}}).sort('winning', -1).limit(10)
        if docs.count() == 0:
            data = notify.SerializeToString()
            value = None
        else:
            for doc in docs:
                msg_club = Club(sid, doc['_id']).make_protomsg()
                msg_slots = Formation(sid, doc['_id']).make_slot_msg()

                notify_club = notify.clubs.add()
                notify_club.club.MergeFrom(msg_club)
                notify_club.point = doc['winning']

                for _slot in msg_slots:
                    notify_club_slot = notify_club.slots.add()
                    notify_club_slot.MergeFrom(_slot)

            data = notify.SerializeToString()
            value = base64.b64encode(data)

        cls.COMMON(sid).set(value)
        cls.MONGO_DOCUMENT.db(sid).drop()

        for _cid in OperationLog.get_recent_action_char_ids(sid, recent_minutes=5):
            MessagePipe(_cid).put(data=data)


class WinningPlunder(_Winning):
    MONGO_DOCUMENT = MongoPlunderWinning
    COMMON = CommonWinningPlunder
    NOTIFY = LeaderboardPlunderWinningNotify
    __slots__ = []

    @classmethod
    def cronjob(cls, sid):
        from core.club import Club
        from core.plunder import Plunder

        notify = cls.NOTIFY()
        notify.session = ""

        docs = cls.MONGO_DOCUMENT.db(sid).find({'winning': {'$gt': 0}}).sort('winning', -1).limit(3)
        if docs.count() == 0:
            data = notify.SerializeToString()
            value = None
        else:
            for doc in docs:
                msg_club = Club(sid, doc['_id']).make_protomsg()
                _plunder = Plunder(sid, doc['_id'])

                notify_club = notify.clubs.add()
                notify_club.club.MergeFrom(msg_club)
                notify_club.point = doc['winning']

                for _way_id in [1, 2, 3]:
                    notify_club_formation = notify_club.formation.add()
                    notify_club_formation.MergeFrom(_plunder.get_way_object(_way_id).make_protobuf())

            data = notify.SerializeToString()
            value = base64.b64encode(data)

        cls.COMMON(sid).set(value)
        cls.MONGO_DOCUMENT.db(sid).drop()

        for _cid in OperationLog.get_recent_action_char_ids(sid, recent_minutes=5):
            MessagePipe(_cid).put(data=data)


class WinningChampionship(_Winning):
    COMMON = CommonWinningChampionship
    NOTIFY = LeaderboardChampionshipNotify
    __slots__ = []

    def get_or_create_doc(self):
        self.doc = None

    def set(self, win):
        raise RuntimeError("should be here")

    def set_to_common(self, msg):
        data = msg.SerializeToString()
        value = base64.b64encode(data)
        self.COMMON(self.server_id).set(value)

        for _cid in OperationLog.get_recent_action_char_ids(self.server_id, recent_minutes=5):
            MessagePipe(_cid).put(data=data)


class Worship(object):
    __slots__ = ['server_id', 'char_id', 'can_worship']
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.can_worship = ValueLogWorshipTimes(self.server_id, self.char_id).count_of_today() == 0
        if self.can_worship:
            self.can_worship = WinningArena(self.server_id, self.char_id).get() is not None

        if self.can_worship:
            self.can_worship = WinningPlunder(self.server_id, self.char_id).get() is not None

        if self.can_worship:
            self.can_worship = WinningChampionship(self.server_id, self.char_id).get() is not None

    def worship(self):
        if not self.can_worship:
            raise GameException(ConfigErrorMessage.get_error_id("WORSHIP_CANNOT"))

        config = ConfigItemUse.get(-3)
        rc = ResourceClassification.classify(config.using_result())
        rc.add(self.server_id, self.char_id)

        ValueLogWorshipTimes(self.server_id, self.char_id).record()
        self.can_worship = False
        self.send_notify()

        return rc

    def send_notify(self):
        notify = LeaderboardWorshipNotify()
        notify.can_worship = self.can_worship
        MessagePipe(self.char_id).put(notify)