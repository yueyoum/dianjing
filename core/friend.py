# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       friend
Date Created:   2015-07-29 16:22
Description:

"""

from dianjing.exception import GameException

from core.db import get_mongo_db
from core.mongo import Document
from core.character import Character
from core.club import Club
from core.match import ClubMatch

from utils.message import MessagePipe

from config import ConfigErrorMessage

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


class FriendManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.mongo = get_mongo_db(server_id)

        doc = self.mongo.friend.find_one({'_id': char_id}, {'_id': 1})
        if not doc:
            doc = Document.get("friend")
            doc['_id'] = self.char_id
            self.mongo.friend.insert_one(doc)


    def get_info(self, friend_id):
        key = 'friends.{0}'.format(friend_id)
        doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})

        if str(friend_id) not in doc['friends']:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST"))

        char = Character(self.server_id, friend_id)
        club = Club(self.server_id, friend_id)
        return (char, club)


    def match(self, friend_id):
        key = 'friends.{0}'.format(friend_id)
        doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})

        if str(friend_id) not in doc['friends']:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST"))

        club_one = Club(self.server_id, self.char_id)
        club_two = Club(self.server_id, friend_id)

        match = ClubMatch(club_one, club_two)
        msg = match.start()
        return msg


    def add(self, name):
        doc = self.mongo.character.find_one({'name': name}, {'_id': 1})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("CHAR_NOT_EXIST"))

        char_id = doc['_id']
        key = 'friends.{0}'.format(char_id)

        doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_OK:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND"))

        if status == FRIEND_STATUS_SELF_CONFIRM:
            # 要添加的是，需要自己确认的，也就是对方也想添加我。那么就直接成为好友
            self.accept(char_id, verify=False)
            return

        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_PEER_CONFIRM}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[char_id])
        FriendManager(self.server_id, char_id).someone_add_me(self.char_id)


    def accept(self, char_id, verify=True):
        key = 'friends.{0}'.format(char_id)

        if verify:
            doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})
            status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

            if status == FRIEND_STATUS_NOT or status == FRIEND_STATUS_PEER_CONFIRM:
                raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ACCEPT_ERROR"))

            if status == FRIEND_STATUS_OK:
                raise GameException(ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND"))


        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_OK}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[char_id])
        FriendManager(self.server_id, char_id).someone_accept_me(self.char_id)


    def remove(self, char_id):
        key = 'friends.{0}'.format(char_id)

        doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(char_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_NOT:
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST"))

        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        self.send_remove_notify(char_id)
        FriendManager(self.server_id, char_id).someone_remove_me(self.char_id)


    def someone_remove_me(self, from_id):
        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$unset': {'friends.{0}'.format(from_id): 1}}
        )

        self.send_remove_notify(from_id)


    def someone_accept_me(self, from_id):
        key = 'friends.{0}'.format(from_id)
        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$set': {key: FRIEND_STATUS_OK}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[from_id])



    def someone_add_me(self, from_id):
        key = 'friends.{0}'.format(from_id)

        doc = self.mongo.friend.find_one({'_id': self.char_id}, {key: 1})
        status = doc['friends'].get(str(from_id), FRIEND_STATUS_NOT)

        if status == FRIEND_STATUS_NOT or status == FRIEND_STATUS_SELF_CONFIRM:
            # 如果不是好友，或者本来就在我的确认队列里，那么还是加入到确认队列
            new_status = FRIEND_STATUS_SELF_CONFIRM
        else:
            raise RuntimeError(
                "Invalid status in someone_add_me. char_id: {0}, from_id: {1}, status: {2}".format(
                    self.char_id,
                    from_id,
                    status
                )
            )


        self.mongo.friend.update_one(
            {'_id': self.char_id},
            {'$set': {key: new_status}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[from_id])

    def send_remove_notify(self, friend_id):
        notify = FriendRemoveNotify()
        notify.ids.append(friend_id)
        MessagePipe(self.char_id).put(msg=notify)




    def send_notify(self, act=ACT_INIT, ids=None):
        notify = FriendNotify()
        notify.act = act

        if ids:
            projection = {"friends.{0}".format(_id): 1 for _id in ids}
        else:
            projection = {"friends": 1}

        doc = self.mongo.friend.find_one({'_id': self.char_id}, projection)

        friend_ids = [int(i) for i in doc['friends'].keys()]

        char_docs = self.mongo.character.find(
            {'_id': {'$in': friend_ids}},
            # TODO, other fields
            {'name': 1, 'club': 1}
        )

        char_dict = {c['_id']: c for c in char_docs}

        for f in friend_ids:
            notify_friend = notify.friends.add()
            notify_friend.status = FRIEND_STATUS_TABLE[ doc['friends'][str(f)] ]
            notify_friend.id = f
            notify_friend.name = char_dict[f]['name']
            # TODO
            notify_friend.avatar = ""
            notify_friend.club_name = char_dict[f]['club']['name']
            notify_friend.club_flag = char_dict[f]['club']['flag']
            notify_friend.club_gold = char_dict[f]['club']['gold']
            notify_friend.club_level = char_dict[f]['club']['level']


        MessagePipe(self.char_id).put(msg=notify)

