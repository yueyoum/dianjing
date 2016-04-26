"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 03:19
Description:

"""
import random

from dianjing.exception import GameException

from config import ConfigDungeon, ConfigDungeonGrade, ConfigErrorMessage

from core.mongo import MongoDungeon
from core.match import ClubMatch
from core.club import Club

from protomsg.dungeon_pb2 import DungeonNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from utils.message import MessagePipe


DungeonFreeTimes = 1


def get_init_open_dungeon():
    init_open = {}

    for k, v in ConfigDungeonGrade.INSTANCES.iteritems():
        if v.need_level == 1:
            if not init_open.get(str(v.belong), []):
                init_open[str(v.belong)] = []

            init_open[str(v.belong)].append(k)

    return init_open


class DungeonManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoDungeon.exist(self.server_id, self.char_id):
            doc = MongoDungeon.document()
            doc['_id'] = self.char_id
            for k in ConfigDungeon.INSTANCES.keys():
                doc['times'][str(k)] = DungeonFreeTimes

            doc['open'] = get_init_open_dungeon()
            MongoDungeon.db(self.server_id).insert_one(doc)

    def refresh(self):
        updater = {}
        for k in ConfigDungeon.INSTANCES.keys():
            updater['times'] = {str(k): DungeonFreeTimes}

        MongoDungeon.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater},
        )

    def start(self, dungeon_id):
        grade_conf = ConfigDungeonGrade.get(dungeon_id)
        if grade_conf.need_level:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_CLUB_LEVEL_NOT_ENOUGH"))

        conf = ConfigDungeon.get(grade_conf.belong)
        if conf.cost:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_ENERGY_NOT_ENOUGH"))

        doc = MongoDungeon.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'times.{0}'.format(conf.id): 1}
        )
        if doc['times'][str(conf.id)] <= 0:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_NO_TIMES"))

        club_one = Club(self.server_id, self.char_id)
        club_two = club_one
        msg = ClubMatch(club_one, club_two).start()
        msg.key = str(dungeon_id)

        return msg

    def report(self, key, star):
        grade_id = int(key)
        conf = ConfigDungeonGrade.get(grade_id)

        # TODO: remove energy
        MongoDungeon.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'times.{0}'.format(conf.belong): -1}}
        )

        drop = []
        if star > 0:
            for _id, _amount, _range in conf.drop:
                probability = random.random(1, 100)
                if probability < _range:
                    drop.append([_id, _amount])

        self.send_notify(conf.belong)
        return drop

    def send_notify(self, act=ACT_INIT, tp=None):
        if tp:
            act = ACT_UPDATE
            projection = {'times.{0}'.format(tp): 1, 'open.{0}'.format(tp): 1}
        else:
            projection = {}

        doc = MongoDungeon.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = DungeonNotify()
        notify.act = act
        for k, v in doc['times'].iteritems():
            info = notify.info.add()
            info.tp = k
            info.times = v
            for _id in doc['open'][k]:
                info.id.add(_id)
        print notify    
        MessagePipe(notify)
