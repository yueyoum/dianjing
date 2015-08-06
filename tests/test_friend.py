# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_friend
Date Created:   2015-08-06 10:41
Description:

"""
from config import ConfigErrorMessage

from core.db import MongoDB
from core.friend import FriendManager
from core.mongo import Document

from dianjing.exception import GameException


test_char_id = 1
test_char_id1 = 2
test_char_id2 = 3

test_server_id = 1


class TeatFriend(object):

    def reSet(self):
        mongo = MongoDB.get(test_server_id)
        mongo.friend.drop()


    def setUp(self):
        self.reSet()

    def tearDown(self):
        self.reSet()

    def test_get_info_not_exist(self):
        try:
            FriendManager(test_server_id, test_char_id).get_info(test_char_id1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get('FRIEND_NOT_EXIST')
        else:
            Exception('test_get_info_not_exist error')

    def test_get_info(self):
        data = FriendManager(test_server_id, test_char_id).get_info(test_char_id1)
        print data

    def match(self):
        pass

    def add(self):
        pass

    def accept(self):
        pass

    def remove(self):
        pass

    def someone_remove_me(self):
        pass

    def someone_accept_me(self):
        pass

    def someone_add_me(self):
        pass



