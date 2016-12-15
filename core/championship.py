# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       championship
Date Created:   2016-12-09 15:13
Description:

"""
import random
import arrow

from django.conf import settings

from dianjing.exception import GameException

from core.mongo import (
    MongoChampionship,
    MongoChampionshipFormationWay1,
    MongoChampionshipFormationWay2,
    MongoChampionshipFormationWay3,
    MongoChampionshipGroup,
    MongoChampionshipLevel,
    MongoChampionHistory,
    MongoCharacter,
)
from core.plunder import PlunderFormation, Plunder
from core.vip import VIP
from core.club import Club, get_club_property

from utils.message import MessagePipe, MessageFactory
from utils.functional import make_string_id, make_time_of_today

from config import (
    GlobalConfig,
    ConfigErrorMessage,
    ConfigChampionBet,
    ConfigChampionRankReward,
    ConfigChampionScoreReward,
    ConfigChampionWinScore,
    ConfigPlunderNPC,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.championship_pb2 import (
    CHAMPION_LEVEL_1,
    CHAMPION_LEVEL_2,
    CHAMPION_LEVEL_4,
    CHAMPION_LEVEL_8,
    CHAMPION_LEVEL_16,

    ChampionFormationNotify,
    ChampionGroupNotify,
    ChampionLevelNotify,
    ChampionNotify,
    ChampionClub as MsgChampionClub,
)

# XX强 进阶顺序
LEVEL_SEQ = [16, 8, 4, 2, 1]
LEVEL_NEXT_TABLE = {
    16: 8,
    8: 4,
    4: 2,
    2: 1,
}

# 小组赛比赛时间
GROUP_MATCH_HOUR = [14, 15, 16, 17, 18, 19]

# GROUP_MATCH_TIMES_TO_HOUR_TABLE = {
#     1: 14,
#     2: 15,
#     3: 16,
#     4: 17,
#     5: 18,
#     6: 19,
# }

LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE = {
    16: [19, 30],
    8: [20, 0],
    4: [20, 30],
    2: [21, 0],
}

# 允许报名 周几. 星期一从0开始
APPLY_WEEKDAY = [0, 1, 2, 3, 4, 5, 6]
# 允许报名时间 hour, minute
APPLY_TIME_RANGE = [(8, 0), (22, 30)]


def check_club_level(silence=True):
    def deco(fun):
        def wrap(self, *args, **kwargs):
            """

            :type self: Championship
            """

            if self.club_level < GlobalConfig.value("CHAMPIONSHIP_APPLY_LEVEL_LIMIT"):
                if silence:
                    return

                raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

            return fun(self, *args, **kwargs)

        return wrap

    return deco


class ChampionshipFormationWay1(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoChampionshipFormationWay1


class ChampionshipFormationWay2(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoChampionshipFormationWay2


class ChampionshipFormationWay3(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoChampionshipFormationWay3


WAY_MAP = {
    1: ChampionshipFormationWay1,
    2: ChampionshipFormationWay2,
    3: ChampionshipFormationWay3,
}


class Championship(object):
    __slots__ = ['server_id', 'char_id', 'doc', 'club_level']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoChampionship.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoChampionship.document()
            self.doc['_id'] = self.char_id
            MongoChampionship.db(self.server_id).insert_one(self.doc)

        self.club_level = get_club_property(self.server_id, self.char_id, 'level')

    @check_club_level(silence=True)
    def try_initialize(self, send_notify=True):
        if self.doc['active']:
            return

        # 从 掠夺阵型 拷贝
        p = Plunder(self.server_id, self.char_id)
        for i in [1, 2, 3]:
            way = p.get_way_object(i)
            doc = way.get_or_create_doc()

            WAY_MAP[i].MONGO_COLLECTION.db(self.server_id).insert_one(doc)

        self.doc['active'] = True
        MongoChampionship.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'active': True
            }}
        )

        if send_notify:
            self.send_notify()

    @check_club_level(silence=False)
    def apply_in(self):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        if now.weekday() not in APPLY_WEEKDAY:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_APPLY_NOT_OPEN"))

        range_start = make_time_of_today(APPLY_TIME_RANGE[0][0], APPLY_TIME_RANGE[0][1])
        range_end = make_time_of_today(APPLY_TIME_RANGE[1][0], APPLY_TIME_RANGE[1][1])

        if now < range_start or now > range_end:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_APPLY_NOT_OPEN"))

        if self.doc['applied']:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_ALREADY_APPLIED"))

        self.doc['applied'] = True
        MongoChampionship.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'applied': True
            }}
        )

        self.send_notify()

    @check_club_level(silence=False)
    def bet(self, club_id, bet_id):
        cl = ChampionshipLevel(self.server_id)
        lv = cl.get_current_level()
        if str(lv) in self.doc['bet']:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_ALREADY_BET"))

        if club_id not in cl.doc['levels'].get(str(lv), []):
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if not ConfigChampionBet.get(bet_id):
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        bet_info = {
            'club_id': club_id,
            'bet_id': bet_id
        }

        self.doc['bet'][str(lv)] = bet_info
        MongoChampionship.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'bet.{0}'.format(lv): bet_info
            }}
        )

        self.send_basic_notify()

    def get_way_object(self, way_id):
        """

        :rtype: PlunderFormation
        """
        try:
            way_class = WAY_MAP[way_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        return way_class(self.server_id, self.char_id, way_id)

    @check_club_level(silence=False)
    def set_staff(self, way_id, slot_id, staff_id):
        way_list = [1, 2, 3]
        if way_id not in way_list:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        way_list.remove(way_id)
        for i in way_list:
            w = self.get_way_object(i)
            w.try_unset_staff(staff_id)

        w = self.get_way_object(way_id)
        w.set_staff(slot_id, staff_id)

        self.send_formation_notify()

    @check_club_level(silence=False)
    def set_unit(self, way_id, slot_id, unit_id):
        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        w = self.get_way_object(way_id)
        w.set_unit(slot_id, unit_id)
        self.send_formation_notify()

    @check_club_level(silence=False)
    def set_position(self, way_id, formation_slots):
        my_way = self.get_way_object(way_id)
        my_way.sync_slots(formation_slots)
        self.send_formation_notify()

    def get_history_top_clubs(self):
        doc = MongoChampionHistory.db(self.server_id).find_one(
            {'_id': MongoChampionHistory.DOC_ID}
        )

        if not doc:
            return []

        clubs = []
        for i in doc['member_ids']:
            clubs.append((i, doc['info']['name'], doc['info']['flag']))

        return clubs

    @check_club_level(silence=False)
    def sync_group(self):
        group_msg = ChampionshipGroup.find_by_char_id(self.server_id, self.char_id).make_protomsg()
        if group_msg:
            MessagePipe(self.char_id).put(msg=group_msg)

    @check_club_level(silence=False)
    def sync_level(self):
        cl = ChampionshipLevel(self.server_id)
        current_lv = cl.doc['current_level']
        level_msg = cl.make_protomsg(level=current_lv)
        MessagePipe(self.char_id).put(msg=level_msg)

    @check_club_level(silence=True)
    def send_notify(self):
        self.send_basic_notify()
        self.send_formation_notify()

        group_msg = ChampionshipGroup.find_by_char_id(self.server_id, self.char_id).make_protomsg()
        if group_msg:
            MessagePipe(self.char_id).put(msg=group_msg)

        level_msg = ChampionshipLevel(self.server_id).make_protomsg()
        MessagePipe(self.char_id).put(msg=level_msg)

    def send_basic_notify(self):
        notify = ChampionNotify()
        notify.applied = self.doc['applied']

        for lv in LEVEL_SEQ:
            notify_bet = notify.bet.add()
            notify_bet.level = lv

            bet_info = self.doc['bet'].get(str(lv), {})
            if bet_info:
                notify_bet.bet_for = bet_info['club_id']
                notify_bet.bet_id = bet_info['bet_id']

        top_clubs = self.get_history_top_clubs()
        for i, name, flag in top_clubs:
            notify_top_club = notify.top_clubs.add()
            notify_top_club.id = i
            notify_top_club.name = name
            notify_top_club.flag = flag

        MessagePipe(self.char_id).put(msg=notify)

    def send_formation_notify(self):
        notify = ChampionFormationNotify()
        for i in [1, 2, 3]:
            notify_way = notify.formation.add()
            w = self.get_way_object(i)
            notify_way.MergeFrom(w.make_protobuf())

        MessagePipe(self.char_id).put(msg=notify)


class ChampionshipGroup(object):
    __slots__ = ['server_id', 'group_id', 'doc', '_char_id', '_member_ids', '_info']

    def __init__(self, server_id):
        self.server_id = server_id
        self.group_id = None
        self.doc = None

        self._char_id = None
        self._member_ids = []
        self._info = {}

    @classmethod
    def find_by_char_id(cls, server_id, char_id):
        obj = cls(server_id)
        obj._char_id = char_id
        obj.doc = MongoChampionshipGroup.db(server_id).find_one(
            {'members': char_id}
        )

        if obj.doc:
            obj.group_id = obj.doc['_id']

        return obj

    @classmethod
    def find_by_group_id(cls, server_id, group_id):
        obj = cls(server_id)
        obj.group_id = group_id
        obj.doc = MongoChampionshipGroup.db(server_id).find_one(
            {'_id': group_id}
        )

        return obj

    @classmethod
    def make_group(cls, server_id):
        obj = cls(server_id)
        obj.group_id = make_string_id()

        return obj

    def add_club(self, club_id, club_info):
        self._member_ids.append(club_id)
        self._info[club_id] = club_info

    def finish(self):
        doc = MongoChampionshipGroup.document()
        doc['_id'] = self.group_id
        doc['member_ids'] = self._member_ids
        doc['info'] = self._info
        doc['scores'] = {i: 0 for i in self._member_ids}
        doc['logs'] = {i: [] for i in self._member_ids}
        MongoChampionshipGroup.db(self.server_id).insert_one(doc)

    def get_scores_sorted(self):
        scores = self.doc['scores'].items()
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores

    def get_top_two(self):
        scores = self.get_scores_sorted()
        return [scores[0][0], scores[1][0]]

    def start_match(self):
        scores = self.get_scores_sorted()
        pairs = []
        for i in range(0, len(scores) - 1, 2):
            pairs.append((scores[i][0], scores[i + 1][0]))

        # TODO real match
        for id_one, id_two in pairs:
            one_got_score = random.choice([0, 1, 2, 3])
            two_got_score = 3 - one_got_score
            self.doc['scores'][id_one] += one_got_score
            self.doc['scores'][id_two] += two_got_score

            one_name = self.doc['info'][id_one]['name']
            two_name = self.doc['info'][id_two]['name']
            one_log = self.make_match_log(one_name, one_got_score, [1, 1, 1])
            two_log = self.make_match_log(two_name, two_got_score, [1, 1, 1])

            self.doc['logs'][id_one].append(one_log)
            self.doc['logs'][id_two].append(two_log)

        self.doc['match_times'] += 1
        MongoChampionshipGroup.db(self.server_id).update_one(
            {'_id': self.group_id},
            {'$set': {
                'scores': self.doc['scores'],
                'logs': self.doc['logs'],
                'match_times': self.doc['match_times'],
            }}
        )

    def make_match_log(self, target_name, got_score, way_wins):
        match_times = self.doc['match_times']
        hour = GROUP_MATCH_HOUR[match_times - 1]

        doc = MongoChampionshipGroup.document_match_log()
        doc['timestamp'] = make_time_of_today(hour, 0).timestamp
        doc['target_name'] = target_name
        doc['got_score'] = got_score
        doc['way_wins'] = way_wins
        return doc

    def make_clubs_msg(self):
        msgs = []
        scores = self.get_scores_sorted()

        for index, (club_id, score) in enumerate(scores):
            rank = index + 1
            if rank >= 10:
                # 只发前10名
                break

            msg = MsgChampionClub()
            msg.id = club_id
            msg.name = self.doc['members'][club_id]['name']
            msg.flag = self.doc['members'][club_id]['flag']
            msg.rank = rank
            msg.score = score

            msgs.append(msg)

        return msgs

    def make_protomsg(self):
        if not self._char_id:
            return

        notify = ChampionGroupNotify()
        clubs = self.make_clubs_msg()

        for c in clubs:
            notify_club = notify.clubs.add()
            notify_club.MergeFrom(c)

        for log in self.doc['logs'][str(self._char_id)]:
            notify_log = notify.logs.add()
            notify_log.timestamp = log['timestamp']
            notify_log.target_name = log['target_name']
            notify_log.got_score = log['got_score']
            notify_log.way_wins = log['way_wins']

        match_times = self.doc['match_times']
        if match_times > 6:
            notify.next_match_at = 0
        else:
            hour = GROUP_MATCH_HOUR[match_times - 1]
            notify.next_match_at = make_time_of_today(hour, 0).timestamp

        return notify


class ChampionshipGroupManager(object):
    @classmethod
    def find_all_groups(cls, server_id):
        """

        :rtype: list[ChampionshipGroup]
        """
        groups = []
        """:type: list[ChampionshipGroup]"""

        group_docs = MongoChampionshipGroup.db(server_id).find({})
        for doc in group_docs:
            g = ChampionshipGroup(server_id)
            g.group_id = doc['_id']
            g.doc = doc

            groups.append(g)

        return groups

    @classmethod
    def find_applied_clubs(cls, server_id):
        docs = MongoChampionship.db(server_id).find(
            {'applied': True},
            {'_id': 1}
        )

        club_ids = [doc['_id'] for doc in docs]
        club_ids = set(club_ids)

        # vip auto apply
        auto_apply_vip_level = GlobalConfig.value("CHAMPIONSHIP_AUTO_APPLY_VIP_LEVEL")
        apply_club_level_limit = GlobalConfig.value("CHAMPIONSHIP_APPLY_LEVEL_LIMIT")

        vip_ids = VIP.query_char_ids(server_id, min_level=auto_apply_vip_level)

        if vip_ids:
            club_docs = MongoCharacter.db(server_id).find(
                {'_id': {'$in': vip_ids}},
                {'level': 1}
            )

            for doc in club_docs:
                if doc['level'] >= apply_club_level_limit:
                    club_ids.add(doc['_id'])

        return club_ids

    @classmethod
    def assign_to_groups(cls, server_id, club_ids):
        club_amount = len(club_ids)

        if club_amount < 32:
            need_npc_amount = 32 - club_amount
        else:
            if club_amount % 2 == 0:
                need_npc_amount = 0
            else:
                need_npc_amount = 1

        info = {}
        if club_ids:
            club_docs = MongoCharacter.db(server_id).find(
                {'_id': {'$in': club_ids}},
                {'name': 1, 'flag': 1}
            )

            club_info = {doc['_id']: doc for doc in club_docs}

            for i in club_ids:
                info[str(i)] = {
                    'name': club_info[i]['name'],
                    'flag': club_info[i]['flag'],
                }

        for i in range(need_npc_amount):
            # TODO npc id
            npc_doc = ConfigPlunderNPC.get(2).to_simple_doc()
            npc_id = npc_doc.pop('id')
            info[npc_id] = npc_doc

        ids = info.keys()
        random.shuffle(ids)

        # 把这些ids 随机分配到8个 group 中
        groups = []
        """:type: list[ChampionshipGroup]"""
        for i in range(8):
            g = ChampionshipGroup.make_group(server_id)
            groups.append(g)

        g_index = 0
        while True:
            try:
                _id = ids.pop(0)
            except IndexError:
                break

            groups[g_index].add_club(_id, info[_id])
            g_index += 1
            if g_index >= 8:
                g_index = 0

        for g in groups:
            g.finish()

    @classmethod
    def start_match(cls, server_id):
        groups = cls.find_all_groups(server_id)
        for g in groups:
            g.start_match()


class ChampionshipLevel(object):
    __slots__ = ['server_id', 'doc']
    DOC_ID = 'championship_level'

    def __init__(self, server_id):
        self.server_id = server_id

        self.doc = MongoChampionshipLevel.db(self.server_id).find_one({'_id': self.DOC_ID})
        if not self.doc:
            self.doc = MongoChampionshipLevel.document()
            MongoChampionshipLevel.db(self.server_id).insert_one(self.doc)

    def initialize(self):
        # 16强初始化
        groups = ChampionshipGroupManager.find_all_groups(self.server_id)
        info = {}
        tops = []
        for g in groups:
            id_one, id_two = g.get_top_two()
            info[id_one] = g.doc['info'][id_one]
            info[id_two] = g.doc['info'][id_two]

            tops.append((id_one, id_two))

        # 1~4组第一名 vs 5~8组第二名
        # 1~4组第二名 vs 5~8组第一名
        member_ids = []
        for i in range(4):
            member_ids.append(tops[i][0])
            member_ids.append(tops[i + 4][1])

        for i in range(4):
            member_ids.append(tops[i][1])
            member_ids.append(tops[i + 4][0])

        self.doc['info'] = info
        self.save(16, member_ids, info=info)

    def get_current_level(self):
        return self.doc['current_level']

    def save(self, level, member_ids, info=None):
        self.doc['levels'][str(level)] = member_ids
        self.doc['current_level'] = level

        updater = {
            'levels.{0}'.format(level): member_ids,
            'current_level': level,
        }
        if info:
            updater['info'] = info

        MongoChampionshipLevel.db(self.server_id).update_one(
            {'_id': self.DOC_ID},
            {'$set': updater}
        )

    def start_match(self):
        lv = self.doc['current_level']
        next_level = LEVEL_NEXT_TABLE[lv]

        member_ids = self.doc['levels'][str(lv)]
        # TODO real match
        pairs = []
        for i in range(0, len(member_ids) - 1, 2):
            pairs.append((member_ids[i], member_ids[i + 1]))

        next_level_ids = []
        for id_one, id_two in pairs:
            if random.randint(1, 10) >= 5:
                next_level_ids.append(id_one)
            else:
                next_level_ids.append(id_two)

        self.save(next_level, next_level_ids)

        if next_level == 1:
            # 已经打完了，但还要得出第三名
            level_4_member_ids = self.doc['levels']['4'][:]
            level_2_member_ids = self.doc['levels']['2'][:]
            for i in level_2_member_ids:
                level_4_member_ids.remove(i)

            if random.randint(1, 10) >= 5:
                third = level_4_member_ids[0]
            else:
                third = level_4_member_ids[1]

            first = self.doc['levels']['1'][0]
            level_2_member_ids.remove(first)
            second = level_2_member_ids[0]

            MongoChampionHistory.db(self.server_id).drop()
            history_doc = MongoChampionHistory.document()
            history_doc['member_ids'] = [first, second, third]
            history_doc['info'] = {
                first: self.doc['info'][first],
                second: self.doc['info'][second],
                third: self.doc['info'][third],
            }

            MongoChampionHistory.db(self.server_id).insert_one(history_doc)

    def make_protomsg(self, level=None):
        if level:
            levels = [level]
            act = ACT_UPDATE
        else:
            levels = [CHAMPION_LEVEL_16, CHAMPION_LEVEL_8, CHAMPION_LEVEL_4, CHAMPION_LEVEL_2, CHAMPION_LEVEL_1]
            act = ACT_INIT

        notify = ChampionLevelNotify()
        notify.act = act

        if act == ACT_INIT:
            level16_member_ids = self.doc['levels'].get('16', [])
            for i in level16_member_ids:
                notify_club = notify.clubs.add()
                notify_club.id = i
                notify_club.name = self.doc['info'][i]['name']
                notify_club.flag = self.doc['info'][i]['flag']

        for lv in levels:
            notify_level = notify.levels.add()

            notify_level.level = lv
            notify_level.club_ids.extend(self.doc['levels'].get(str(lv), []))

            if lv == 1:
                notify_level.next_match_at = 0
            else:
                hour, minute = LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE[lv]
                notify_level.next_match_at = make_time_of_today(hour, minute).timestamp

        return notify
