# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_friend
Date Created:   2015-08-06 10:41
Description:

"""
from config import ConfigErrorMessage

from core.db import MongoDB
from core.friend import *
from core.mongo import Document

from dianjing.exception import GameException


test_char_id = 1
test_friend_id = 2
test_char_id1 = 3

test_server_id = 1


class TestFriend(object):

    def reSet(self):
        mongo = MongoDB.get(test_server_id)
        mongo.friend.drop()

    def create_char(self):
        mongo = MongoDB.get(test_server_id)
        data = mongo.character.find_one({'_id': test_friend_id})

        if not data:
            from core.character import Character
            Character.create(test_server_id, test_friend_id, "two", "club_two", 1)

    def is_friend_data(self):
        mongo = MongoDB.get(test_server_id)
        mongo.friend.update(
            {'_id': test_char_id},
            {'$set': {'friends.{0}'.format(test_friend_id): FRIEND_STATUS_OK}},
            upsert=True
        )

        mongo.friend.update(
            {'_id': test_friend_id},
            {'$set': {'friends.{0}'.format(test_char_id): FRIEND_STATUS_OK}},
            upsert=True
        )

    def friend_request(self):
        mongo = MongoDB.get(test_server_id)
        mongo.friend.update(
            {'_id': test_char_id},
            {'$set': {'friends.{0}'.format(test_friend_id): FRIEND_STATUS_PEER_CONFIRM}},
            upsert=True
        )
        mongo.friend.update(
            {'_id': test_friend_id},
            {'$set': {'friends.{0}'.format(test_char_id): FRIEND_STATUS_SELF_CONFIRM}},
            upsert=True
        )

    def setUp(self):
        self.reSet()

    def tearDown(self):
        self.reSet()

    def test_get_info_not_exist(self):
        try:
            FriendManager(test_server_id, test_char_id).get_info(test_friend_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_NOT_EXIST')
        else:
            raise Exception('test_get_info_not_exist error')

    def test_get_info(self):
        self.create_char()
        self.is_friend_data()
        char, club = FriendManager(test_server_id, test_char_id).get_info(test_friend_id)
        if not char or not club:
            raise Exception('test_get_info error')

    def match_friend_not_exist(self):
        try:
            FriendManager(test_server_id, test_char_id).match(test_friend_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_NOT_EXIST')
        else:
            raise Exception('test_get_info_not_exist error')

    def test_match(self):
        # TODO
        self.create_char()
        self.is_friend_data()
        msg = FriendManager(test_server_id, test_char_id).match(test_friend_id)
        print msg

    def test_add_char_not_exist(self):
        try:
            FriendManager(test_server_id, test_char_id).add('test')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('CHAR_NOT_EXIST')
        else:
            raise Exception('add_char_not_exist error')

    def test_add_already_friend(self):
        self.create_char()
        self.is_friend_data()
        try:
            FriendManager(test_server_id, test_char_id).add('two')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_ALREADY_IS_FRIEND')
        else:
            raise Exception('add_char_not_exist error')

    def test_add_request_sended(self):
        self.create_char()
        self.friend_request()
        try:
            FriendManager(test_server_id, test_char_id).add('two')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_ADD_REQUEST_SEEDED')
        else:
            raise Exception('add_request_sended error')

    def test_add(self):
        self.create_char()
        FriendManager(test_server_id, test_char_id).add('two')
        data = MongoDB.get(test_server_id).friend.find_one({'_id': test_char_id},
                                                           {'friends.{0}'.format(test_friend_id): 1})
        if not data['friends'][str(test_friend_id)]:
            raise Exception('test_add error')

    def test_accept_error(self):
        self.create_char()
        self.friend_request()
        try:
            FriendManager(test_server_id, test_char_id).accept(test_friend_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_ACCEPT_ERROR")
        else:
            raise Exception('test_accept_error error')

    def test_accept_already_friend(self):
        self.create_char()
        self.is_friend_data()
        try:
            FriendManager(test_server_id, test_friend_id).accept(test_char_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND")
        else:
            raise Exception('test_accept_already_friend error')

    def test_accept(self):
        self.create_char()
        self.friend_request()
        FriendManager(test_server_id, test_friend_id).accept(test_char_id)
        self_friend = MongoDB.get(test_server_id).friend.find_one({'_id': test_friend_id},
                                                             {'friends.{0}'.format(test_char_id): 1}
                                                             )

        fri_friend = MongoDB.get(test_server_id).friend.find_one({'_id': test_char_id},
                                                             {'friends.{0}'.format(test_friend_id): 1}
                                                             )

        if self_friend['friends'][str(test_char_id)] != FRIEND_STATUS_OK or \
                        fri_friend['friends'][str(test_friend_id)] != FRIEND_STATUS_OK:
            raise Exception('test_accept error')

    def test_remove_friend_not_exist(self):
        try:
            FriendManager(test_server_id, test_char_id).remove(test_friend_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST")
        else:
            raise Exception('test_remove_friend_not_exist error')

    def test_remove_friend(self):
        self.create_char()
        self.is_friend_data()
        FriendManager(test_server_id, test_char_id).remove(test_friend_id)
        mongo = MongoDB.get(test_server_id)
        self_friend = mongo.friend.find_one({'_id': test_char_id},
                                            {'friends.{0}'.format(test_friend_id): 1})
        fri_friend = mongo.friend.find_one({'_id': test_friend_id},
                                           {'friends.{0}'.format(test_char_id): 1}
                                           )
        if self_friend['friends'] or fri_friend['friends']:
            raise Exception('test_remove_friend error')

    # def test_someone_remove_me(self):
    #     pass
    #
    # def someone_accept_me(self):
    #     pass

    def someone_add_me(self):
        pass



