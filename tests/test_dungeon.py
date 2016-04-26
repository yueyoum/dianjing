"""
Author:         ouyang
Filename:       test_dungeon
Date Created:   2016-04-26 01:07
Description:

"""
from dianjing.exception import GameException

from core.dungeon import DungeonManager
from core.mongo import MongoDungeon

from config import ConfigErrorMessage

class TestDungeonManager(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def setup(self):
        DungeonManager(self.server_id, self.char_id)

    def teardown(self):
        MongoDungeon.db(self.server_id).drop()

    def test_refresh(self):
        DungeonManager(self.server_id, self.char_id).report(1, 1)
        DungeonManager(self.server_id, self.char_id).refresh()

        doc = MongoDungeon.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'times': 1}
        )

        for k, v in doc['times'].iteritems():
            assert v == 1

    def test_start_level_limit(self):
        try:
            DungeonManager(self.server_id, self.char_id).start(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("DUNGEON_CLUB_LEVEL_NOT_ENOUGH")
        else:
            Exception('error')

    def test_start_times_limit(self):
        try:
            DungeonManager(self.server_id, self.char_id).start(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("DUNGEON_ENERGY_NOT_ENOUGH")
        else:
            Exception('error')

    def test_start_energy_limit(self):
        try:
            DungeonManager(self.server_id, self.char_id).start(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("DUNGEON_NO_TIMES")
        else:
            Exception('error')

    def test_start(self):
        pass

    def test_report(self):
        drop = DungeonManager(self.server_id, self.char_id).report(1, 0)
        assert drop

        doc = MongoDungeon.db(self.server_id).find_one({'_id': self.char_id})
        assert doc['times']['1'] == 0

    def test_report_fail(self):
        drop = DungeonManager(self.server_id, self.char_id).report(1, 0)
        assert not drop

        doc = MongoDungeon.db(self.server_id).find_one({'_id': self.char_id})
        assert doc['times']['1'] == 0

    def test_send_notify(self):
        DungeonManager(self.server_id, self.char_id).send_notify()
