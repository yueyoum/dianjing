# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-10 11:35
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoEliteMatch
from core.abstract import AbstractClub, AbstractStaff
from core.club import Club
from core.match import ClubMatch
from core.package import Drop
from core.resource import Resource

from utils.message import MessagePipe

from config import ConfigEliteArea, ConfigEliteMatch, ConfigErrorMessage, ConfigStaff

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.elite_match_pb2 import (
    ELITE_AREA_FINISH,
    ELITE_AREA_NOT_OPEN,
    ELITE_AREA_OPEN,
    EliteNotify,
    EliteTimesNotify
)

ELITE_MAX_TIMES = 20


class EliteNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id, level):
        super(EliteNPCStaff, self).__init__()

        self.id = _id
        self.level = level

        config = ConfigStaff.get(_id)
        self.race = config.race

        self.jingong = config.jingong + config.jingong_grow * (level - 1)
        self.qianzhi = config.qianzhi + config.qianzhi_grow * (level - 1)
        self.xintai = config.xintai + config.xintai_grow * (level - 1)
        self.baobing = config.baobing + config.baobing_grow * (level - 1)
        self.fangshou = config.fangshou + config.fangshou_grow * (level - 1)
        self.yunying = config.yunying + config.yunying_grow * (level - 1)
        self.yishi = config.yishi + config.yishi_grow * (level - 1)
        self.caozuo = config.caozuo + config.caozuo_grow * (level - 1)

        skills = config.skill_ids
        self.skills = {i: 1 for i in skills}


class EliteNPCClub(AbstractClub):
    __slots__ = []

    def __init__(self, elite_match_id):
        super(EliteNPCClub, self).__init__()

        config = ConfigEliteMatch.get(elite_match_id)

        self.id = elite_match_id

        self.match_staffs = config.staffs
        self.policy = config.policy
        self.name = config.club_name
        self.flag = config.club_flag

        for i in self.match_staffs:
            self.staffs[i] = EliteNPCStaff(i, config.staff_level)

        self.qianban_affect()


def get_next_restore_timestamp():
    now = arrow.utcnow()
    next_hour = now.replace(hours=1)

    next_hour = arrow.Arrow(
        next_hour.year,
        next_hour.month,
        next_hour.day,
        next_hour.hour,
        0,
        0,
        0,
        tzinfo=next_hour.tzinfo
    )

    return next_hour.timestamp


class EliteMatch(object):
    __slots__ = ['server_id', 'char_id', 'cur_times']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'cur_times': 1}
        )

        if not doc:
            doc = MongoEliteMatch.document()
            doc['_id'] = self.char_id
            doc['cur_times'] = ELITE_MAX_TIMES
            doc['areas'] = {
                '1': {
                    str(ConfigEliteArea.get(1).first_match_id()): 0
                }
            }

            MongoEliteMatch.db(self.server_id).insert_one(doc)

        self.cur_times = doc['cur_times']

    @classmethod
    def cronjob_clean_match_times(cls):
        # 清理每关打过的次数
        pass

    def open_area(self, aid, send_notify=True):
        config = ConfigEliteArea.get(aid)
        if not config:
            return

        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}'.format(aid): 1}
        )

        if str(aid) in doc['areas']:
            return

        updater = {
            'areas.{0}'.format(aid): {
                str(config.first_match_id()): 0
            }
        }

        MongoEliteMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        if send_notify:
            self.send_notify(area_id=aid)

    def cost_cur_times(self):
        if self.cur_times <= 0:
            raise GameException(ConfigErrorMessage.get_error_id("ELITE_TOTAL_NO_TIMES"))

        self.cur_times -= 1
        # TODO lock
        MongoEliteMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'cur_times': self.cur_times}}
        )

        self.send_times_notify()

    def start(self, mid):
        config_match = ConfigEliteMatch.get(mid)
        if not config_match:
            raise GameException(ConfigErrorMessage.get_error_id("ELITE_MATCH_NOT_EXIST"))

        aid = config_match.area_id

        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}'.format(aid): 1}
        )

        areas = doc['areas'].get(str(aid), {})
        if not areas:
            raise GameException(ConfigErrorMessage.get_error_id("ELITE_AREA_NOT_OPEN"))

        config_area = ConfigEliteArea.get(aid)

        club = Club(self.server_id, self.char_id)
        if club.level < config_area.need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

        cur_times = areas.get(str(mid), -1)
        if cur_times == -1:
            raise GameException(ConfigErrorMessage.get_error_id("ELITE_MATCH_NOT_OPEN"))

        if cur_times >= config_match.max_times:
            raise GameException(ConfigErrorMessage.get_error_id("ELITE_MATCH_REACH_MAX_TIMES"))

        self.cost_cur_times()

        npc_club = EliteNPCClub(mid)
        match = ClubMatch(club, npc_club)
        msg = match.start()

        updater = {'has_matched': True}

        drop = Drop()
        if msg.club_one_win:
            drop = Drop.generate(config_match.reward)
            message = u"Elite Match {0}".format(mid)
            Resource(self.server_id, self.char_id).save_drop(drop, message=message)

            # 当前关卡次数加一
            updater['areas.{0}.{1}'.format(aid, mid)] = cur_times + 1

            # 开启后面的关卡或者大区
            next_match_id = config_area.next_match_id(mid)
            if next_match_id:
                updater['areas.{0}.{1}'.format(aid, next_match_id)] = 0

            else:
                next_area_id = ConfigEliteArea.next_area_id(aid)
                if next_area_id:
                    self.open_area(next_area_id)

        MongoEliteMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )
        self.send_notify(area_id=aid, match_id=mid)

        return msg, drop.make_protomsg()

    def send_notify(self, area_id=None, match_id=None):
        if area_id:
            act = ACT_UPDATE
            area_ids = [area_id]
        else:
            act = ACT_INIT
            area_ids = ConfigEliteArea.INSTANCES.keys()

        def get_match_ids(_aid):
            if area_id:
                if match_id:
                    return [match_id]
                return ConfigEliteArea.get(area_id).match_ids

            return ConfigEliteArea.get(_aid).match_ids

        doc = MongoEliteMatch.db(self.server_id).find_one({'_id': self.char_id})

        notify = EliteNotify()
        notify.act = act
        for aid in area_ids:
            notify_area = notify.area.add()
            notify_area.id = aid

            matchs = doc['areas'].get(str(aid), {})
            if not matchs:
                notify_area.status = ELITE_AREA_NOT_OPEN
                continue

            if set([int(i) for i in matchs]) == set(ConfigEliteArea.get(aid).match_ids):
                notify_area.status = ELITE_AREA_FINISH
            else:
                notify_area.status = ELITE_AREA_OPEN

            for mid in get_match_ids(aid):
                cur_times = matchs.get(str(mid), -1)

                notify_area_match = notify_area.match.add()
                notify_area_match.id = mid
                notify_area_match.cur_times = cur_times

        MessagePipe(self.char_id).put(msg=notify)

    def send_times_notify(self):
        notify = EliteTimesNotify()
        notify.max_times = ELITE_MAX_TIMES
        notify.cur_times = self.cur_times

        if self.cur_times >= ELITE_MAX_TIMES:
            notify.next_timestamp = 0
        else:
            notify.next_timestamp = get_next_restore_timestamp()

        MessagePipe(self.char_id).put(msg=notify)
