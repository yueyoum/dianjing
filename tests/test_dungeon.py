"""
Author:         ouyang
Filename:       test_dungeon
Date Created:   2016-04-26 01:07
Description:

"""

from core.dungeon import DungeonManager
from core.mongo import MongoDungeon


class TestDungeonManager(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def setup(self):
        DungeonManager(self.server_id, self.char_id)

    def teardown(self):
        MongoDungeon.db(self.server_id).drop()

    def test_send_notify(self):
        DungeonManager(self.server_id, self.char_id).send_notify()
