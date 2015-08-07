# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_friend
Date Created:   2015-08-06 10:41
Description:

"""
import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.friend import (
    FRIEND_STATUS_OK,
    FRIEND_STATUS_SELF_CONFIRM,
    FRIEND_STATUS_PEER_CONFIRM,
    FriendManager,
)
from core.club import Club
from core.character import Character

from core.staff import StaffManger

from config import ConfigStaff, ConfigErrorMessage



class TestFriend(object):
    @classmethod
    def setup_class(cls):
        # 建立一个 id 为2 的角色
        Character.create(1, 2, "two", "club_two", 1)

    @classmethod
    def teardown_class(cls):
        MongoDB.get(1).character.delete_one({'_id': 2})

    def setup(self):
        self.reset()

    def teardown(self):
        self.reset()


    def reset(self):
        MongoDB.get(1).friend.drop()
        MongoDB.get(1).staff.delete_many({'_id': {'$in': [1, 2]}})
        MongoDB.get(1).character.update_many(
            {'_id': {'$in': [1,2]}},
            {'$set': {
                'club.match_staffs': [],
                'club.tibu_staffs': []
            }}
        )


    def set_friend_data(self):
        MongoDB.get(1).friend.update_one(
            {'_id': 1},
            {'$set': {'friends.2': FRIEND_STATUS_OK}},
            upsert=True
        )

        MongoDB.get(1).friend.update(
            {'_id': 2},
            {'$set': {'friends.1': FRIEND_STATUS_OK}},
            upsert=True
        )

    def make_friend_request(self):
        MongoDB.get(1).friend.update_one(
            {'_id': 1},
            {'$set': {'friends.2': FRIEND_STATUS_PEER_CONFIRM}},
            upsert=True
        )

        MongoDB.get(1).friend.update_one(
            {'_id': 2},
            {'$set': {'friends.1': FRIEND_STATUS_SELF_CONFIRM}},
            upsert=True
        )


    def test_get_info_not_exist(self):
        try:
            FriendManager(1, 1).get_info(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_NOT_EXIST')
        else:
            raise Exception('test_get_info_not_exist error')


    def test_get_info(self):
        self.set_friend_data()
        char, club = FriendManager(1, 1).get_info(2)
        if not char or not club:
            raise Exception('test_get_info error')


    def match_friend_not_exist(self):
        try:
            FriendManager(1, 1).match(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_NOT_EXIST')
        else:
            raise Exception('test_get_info_not_exist error')

    def test_match_staff_not_ready(self):
        self.set_friend_data()
        try:
            FriendManager(1, 1).match(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY")
        else:
            raise Exception('error')

    def test_match(self):
        self.set_friend_data()

        staff_ids = random.sample(ConfigStaff.INSTANCES.keys(), 10)
        for i in staff_ids:
            StaffManger(1, 1).add(i)
            StaffManger(1, 2).add(i)

        Club(1, 1).set_match_staffs(staff_ids)
        Club(1, 2).set_match_staffs(staff_ids)

        FriendManager(1, 1).match(2)


    def test_add_char_not_exist(self):
        try:
            FriendManager(1, 1).add('test')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('CHAR_NOT_EXIST')
        else:
            raise Exception('add_char_not_exist error')


    def test_add_already_friend(self):
        self.set_friend_data()
        try:
            FriendManager(1, 1).add('two')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_ALREADY_IS_FRIEND')
        else:
            raise Exception('add_char_not_exist error')

    def test_add_request_already_sent(self):
        self.make_friend_request()

        try:
            FriendManager(1, 1).add('two')
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('FRIEND_ADD_REQUEST_ALREADY_SENT')
        else:
            raise Exception('add_request_sended error')


    def test_add(self):
        FriendManager(1, 1).add('two')
        data = MongoDB.get(1).friend.find_one(
            {'_id': 1},
            {'friends.2': 1}
        )

        assert data['friends']['2'] == FRIEND_STATUS_PEER_CONFIRM


    def test_accept_error(self):
        self.make_friend_request()

        try:
            FriendManager(1, 1).accept(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_ACCEPT_ERROR")
        else:
            raise Exception('test_accept_error error')

    def test_accept_already_friend(self):
        self.set_friend_data()
        try:
            FriendManager(1, 1).accept(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_ALREADY_IS_FRIEND")
        else:
            raise Exception('test_accept_already_friend error')


    def test_accept(self):
        self.make_friend_request()
        FriendManager(1, 2).accept(1)

        assert FriendManager(1, 1).check_friend_exist(2) is True
        assert FriendManager(1, 2).check_friend_exist(1) is True


    def test_remove_friend_not_exist(self):
        try:
            FriendManager(1, 1).remove(2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("FRIEND_NOT_EXIST")
        else:
            raise Exception('test_remove_friend_not_exist error')


    def test_remove_friend(self):
        self.set_friend_data()

        FriendManager(1, 1).remove(2)
        assert FriendManager(1, 1).check_friend_exist(2) is False
        assert FriendManager(1, 2).check_friend_exist(1) is False


    def test_send_remove_notify(self):
        FriendManager(1, 1).send_remove_notify(2)

    def test_send_notify(self):
        FriendManager(1, 1).send_notify()
