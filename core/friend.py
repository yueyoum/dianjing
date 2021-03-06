# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       friend
Date Created:   2015-07-29 16:22
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoFriend, MongoCharacter
from core.club import Club
from core.match import ClubMatch
from core.formation import Formation
from core.signals import friend_match_signal, friend_ok_signal

from utils.message import MessagePipe
from utils.operation_log import OperationLog

from config import ConfigErrorMessage, GlobalConfig
from config.settings import FRIEND_CANDIDATES_AMOUNT

from protomsg import friend_pb2
from protomsg.friend_pb2 import (
    FriendNotify,
    FriendRemoveNotify,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

# 服务器内部使用
FRIEND_STATUS_NOT = 1
FRIEND_STATUS_OK = 2
FRIEND_STATUS_PEER_CONFIRM = 3
FRIEND_STATUS_SELF_CONFIRM = 4

FRIEND_STATUS_TABLE = {
    FRIEND_STATUS_NOT: friend_pb2.FRIEND_NOT,
    FRIEND_STATUS_OK: friend_pb2.FRIEND_OK,
    FRIEND_STATUS_PEER_CONFIRM: friend_pb2.FRIEND_NEED_PEER_CONFIRM,
    FRIEND_STATUS_SELF_CONFIRM: friend_pb2.FRIEND_NEED_SELF_CONFIRM,
}

MAX_FRIEND_AMOUNT = 50


class FriendManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoFriend.exist(server_id, self.char_id):
            doc = MongoFriend.document()
            doc['_id'] = self.char_id
            MongoFriend.db(server_id).insert_one(doc)

    def get_info(self, friend_id):
        friend_id = int(friend_id)
        if not self.check_friend_exist(friend_id, expect_status=[FRIEND_STATUS_OK, FRIEND_STATUS_PEER_CONFIRM,
                                                                 FRIEND_STATUS_SELF_CONFIRM]):
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST"))

        club = Club(self.server_id, friend_id)
        return club

    def get_real_friends_ids(self):
        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id})
        friend_ids = []
        for k, v in doc['friends'].iteritems():
            if v == FRIEND_STATUS_OK:
                friend_ids.append(int(k))

        return friend_ids

    def get_candidates(self):
        char_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'level': 1}
        )

        level = char_doc['level']

        friend_doc = MongoFriend.db(self.server_id).find_one(
            {'_id': self.char_id}
        )

        def query(level_range):
            if level_range is not None:
                min_level = level - level_range
                if min_level < 1:
                    min_level = 1

                max_level = level + level_range

                condition = {
                    '$and': [
                        {'level': {'$gte': min_level}},
                        {'level': {'$lte': max_level}}
                    ]
                }
            else:
                condition = {}

            other_doc = MongoCharacter.db(self.server_id).find(
                condition,
                {'_id': 1}
            )

            _candidate_ids = []
            for d in other_doc:
                if d['_id'] != self.char_id and str(d['_id']) not in friend_doc['friends']:
                    _candidate_ids.append(d['_id'])

            return _candidate_ids

        candidate_ids = query(10)
        if len(candidate_ids) < FRIEND_CANDIDATES_AMOUNT:
            candidate_ids = query(30)
            if len(candidate_ids) < FRIEND_CANDIDATES_AMOUNT:
                candidate_ids = query(None)

        if len(candidate_ids) > FRIEND_CANDIDATES_AMOUNT:
            candidate_ids = random.sample(candidate_ids, FRIEND_CANDIDATES_AMOUNT)

        return candidate_ids

    def match(self, friend_id):
        friend_id = int(friend_id)
        if not self.check_friend_exist(friend_id):
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_OK"))

        club_one = Club(self.server_id, self.char_id)
        club_two = Club(self.server_id, friend_id)

        f_one = Formation(self.server_id, self.char_id)
        f_two = Formation(self.server_id, self.char_id)

        match = ClubMatch(club_one, club_two, 6, f_one.get_skill_sequence(), f_two.get_skill_sequence())
        msg = match.start()
        msg.key = ""
        msg.map_name = GlobalConfig.value_string("MATCH_MAP_FRIEND")

        friend_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            target_id=friend_id,
            win=msg.club_one_win
        )

        return msg

    def check_friend_exist(self, friend_id, expect_status=None):
        key = 'friends.{0}'.format(friend_id)
        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})

        status = doc['friends'].get(str(friend_id), FRIEND_STATUS_NOT)

        if not expect_status:
            expect_status = [FRIEND_STATUS_OK]

        return status in expect_status

    def add(self, name):
        doc = MongoCharacter.db(self.server_id).find_one({'name': name}, {'_id': 1})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("CHAR_NOT_EXIST"))

        char_id = doc['_id']
        key = 'friends.{0}'.format(char_id)

        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_OK:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND"))

        if status == FRIEND_STATUS_PEER_CONFIRM:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ADD_REQUEST_ALREADY_SENT"))

        if status == FRIEND_STATUS_SELF_CONFIRM:
            # 要添加的是，需要自己确认的，也就是对方也想添加我。那么就直接成为好友
            self.accept(char_id, verify=False)
            return

        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_PEER_CONFIRM}}
        )

        self.send_notify(ids=[char_id])
        FriendManager(self.server_id, char_id).someone_add_me(self.char_id)

    def accept(self, char_id, verify=True):
        char_id = int(char_id)
        key = 'friends.{0}'.format(char_id)

        if verify:
            doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})
            status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

            if status == FRIEND_STATUS_NOT or status == FRIEND_STATUS_PEER_CONFIRM:
                raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ACCEPT_ERROR"))

            if status == FRIEND_STATUS_OK:
                raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND"))

        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_OK}}
        )

        self.send_notify(ids=[char_id])
        FriendManager(self.server_id, char_id).someone_accept_me(self.char_id)

        friend_ok_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            friend_id=char_id
        )

    def remove(self, char_id):
        char_id = int(char_id)
        key = 'friends.{0}'.format(char_id)

        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_NOT:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST"))

        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        self.send_remove_notify(char_id)
        FriendManager(self.server_id, char_id).someone_remove_me(self.char_id)

    def someone_remove_me(self, from_id):
        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {'friends.{0}'.format(from_id): 1}}
        )

        self.send_remove_notify(from_id)

    def someone_accept_me(self, from_id):
        key = 'friends.{0}'.format(from_id)
        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_OK}}
        )

        friend_ok_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            friend_id=from_id
        )

        self.send_notify(ids=[from_id])

    def someone_add_me(self, from_id):
        key = 'friends.{0}'.format(from_id)

        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(from_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_NOT or status == FRIEND_STATUS_SELF_CONFIRM:
            # 如果不是好友，或者本来就在我的确认队列里，那么还是加入到确认队列
            new_status = FRIEND_STATUS_SELF_CONFIRM
        else:
            return

        MongoFriend.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {key: new_status}}
        )

        self.send_notify(ids=[from_id])

    def send_remove_notify(self, friend_id):
        notify = FriendRemoveNotify()
        notify.ids.append(str(friend_id))
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        notify = FriendNotify()

        if ids:
            projection = {"friends.{0}".format(_id): 1 for _id in ids}
            act = ACT_UPDATE
        else:
            projection = {"friends": 1}
            act = ACT_INIT

        notify.act = act
        notify.max_amount = MAX_FRIEND_AMOUNT

        doc = MongoFriend.db(self.server_id).find_one({'_id': self.char_id}, projection)
        friend_ids = [int(i) for i in doc['friends'].keys()]

        online_char_ids = OperationLog.get_recent_action_char_ids(self.server_id)

        for f in friend_ids:
            notify_friend = notify.friends.add()
            notify_friend.status = FRIEND_STATUS_TABLE[doc['friends'][str(f)]]

            friend_club = Club(self.server_id, f)
            notify_friend.club.MergeFrom(friend_club.make_protomsg())

            notify_friend.online = f in online_char_ids

        MessagePipe(self.char_id).put(msg=notify)
