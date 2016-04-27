"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 03:19
Description:

"""
import random
import arrow

from django.conf import settings

from dianjing.exception import GameException

from config import ConfigDungeon, ConfigDungeonGrade, ConfigErrorMessage

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoDungeon
from core.match import ClubMatch
from core.club import Club
from core.unit import NPCUnit
from core.times_log import TimesLogDungeonMatchTimes

from protomsg.dungeon_pb2 import DungeonNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from utils.message import MessagePipe


DUNGEON_FREE_TIMES = 1


def get_init_open_dungeon():
    init_open = {}

    for k, v in ConfigDungeonGrade.INSTANCES.iteritems():
        if v.need_level == 1:
            if not init_open.get(str(v.belong), []):
                init_open[str(v.belong)] = []

            init_open[str(v.belong)].append(k)

    return init_open


class DungeonNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id):
        super(DungeonNPCStaff, self).__init__()

        self.id = str(_id)
        self.oid = _id
        self.after_init()


class DungeonNPCClub(AbstractClub):
    __slots__ = ['config']

    def __init__(self, dungeon_id):
        super(DungeonNPCClub, self).__init__()

        self.config = ConfigDungeonGrade.get(dungeon_id)
        self.id = dungeon_id

        self.name = self.config.name
        # TODO
        self.flag = 1

    def load_staffs(self, **kwargs):
        for position, _id, unit_id in self.config.npc_path:
            s = DungeonNPCStaff(_id)
            s.formation_position = position
            u = NPCUnit(unit_id, 0, 1)

            s.set_unit(u)
            s.calculate()
            self.formation_staffs.append(s)


class DungeonManager(object):
    # TODO: vip times add
    # TODO: vip TimesLog
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoDungeon.exist(self.server_id, self.char_id):
            doc = MongoDungeon.document()
            doc['_id'] = self.char_id
            for k in ConfigDungeon.INSTANCES.keys():
                doc['times'] = {str(k): DUNGEON_FREE_TIMES}

            doc['open'] = get_init_open_dungeon()
            MongoDungeon.db(self.server_id).insert_one(doc)

    def get_dungeon_today_times(self, tp):
        return TimesLogDungeonMatchTimes(self.server_id, self.char_id).count_of_today(tp)

    def start(self, dungeon_id):
        grade_conf = ConfigDungeonGrade.get(dungeon_id)
        club_one = Club(self.server_id, self.char_id)

        if grade_conf.need_level > club_one.level:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_CLUB_LEVEL_NOT_ENOUGH"))

        conf = ConfigDungeon.get(grade_conf.belong)
        # TODO: energy check
        # if conf.cost:
        #     raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_ENERGY_NOT_ENOUGH"))

        doc = MongoDungeon.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'times.{0}'.format(conf.id): 1}
        )

        if doc['times'][str(conf.id)] - self.get_dungeon_today_times(conf.id) <= 0:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_NO_TIMES"))

        club_two = DungeonNPCClub(dungeon_id)
        msg = ClubMatch(club_one, club_two).start()
        msg.key = str(dungeon_id)

        return msg

    def report(self, key, star):
        grade_id = int(key)
        conf = ConfigDungeonGrade.get(grade_id)

        TimesLogDungeonMatchTimes(self.server_id, self.char_id).record(sub_id=conf.belong, value=1)
        # TODO: remove energy

        drop = []
        if star > 0:
            for _id, _amount, _range in conf.drop:
                probability = random.randint(1, 101)
                if probability < _range:
                    drop.append([_id, _amount])

        self.send_notify(conf.belong)
        return drop

    def send_notify(self, tp=None):
        if tp:
            act = ACT_UPDATE
            projection = {'times.{0}'.format(tp): 1, 'open.{0}'.format(tp): 1}
        else:
            projection = {'times': 1, 'open': 1}
            act = ACT_INIT

        doc = MongoDungeon.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )
        today = arrow.utcnow().to(settings.TIME_ZONE).weekday()

        notify = DungeonNotify()
        notify.act = act
        for k, v in doc['times'].iteritems():
            conf = ConfigDungeon.get(int(k))
            if (today+1) not in conf.open_time:
                continue

            info = notify.info.add()
            info.tp = int(k)

            info.times = v - self.get_dungeon_today_times(int(k))

            for _id in doc['open'].get(k, []):
                info.id.append(_id)

        MessagePipe(self.char_id).put(msg=notify)
