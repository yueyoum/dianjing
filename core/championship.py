# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       championship
Date Created:   2016-12-09 15:13
Description:

"""
import random
import arrow
import itertools
import requests

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

from core.plunder import PlunderFormation, Plunder, is_npc
from core.vip import VIP
from core.club import Club, get_club_property
from core.mail import MailManager
from core.resource import ResourceClassification
from core.match import ClubMatch, MatchRecord

from utils.message import MessagePipe, MessageFactory
from utils.functional import make_string_id, make_time_of_today
from utils.operation_log import OperationLog

from config import (
    GlobalConfig,
    ConfigErrorMessage,
    ConfigChampionBet,
    ConfigChampionRankReward,
    ConfigChampionScoreReward,
    ConfigChampionWinScore,
    ConfigPlunderNPC,
    ConfigNPCFormation,
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
from protomsg.match_pb2 import ClubMatchServerSideRequest, ClubMatchServerSideResponse

# XX强 进阶顺序
LEVEL_SEQ = [16, 8, 4, 2, 1]
LEVEL_NEXT_TABLE = {
    16: 8,
    8: 4,
    4: 2,
    2: 1,
}
LEVEL_PREVIOUS_TABLE = {v: k for k, v in LEVEL_NEXT_TABLE.iteritems()}

# 小组赛比赛时间
GROUP_MATCH_TIME = [
    [14, 0],
    [15, 0],
    [16, 0],
    [17, 0],
    [18, 0],
    [19, 0],
]
# GROUP_MATCH_TIME = [
#     [16, 5],
#     [16, 7],
#     [16, 9],
#     [16, 11],
#     [16, 13],
#     [16, 15],
# ]

LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE = {
    16: [19, 30],
    8: [20, 0],
    4: [20, 30],
    2: [21, 0],
}
# LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE = {
#     16: [16, 20],
#     8: [16, 25],
#     4: [16, 30],
#     2: [16, 35],
# }

# 开战前几分钟不能调整阵型和下注
MINUTES_LIMIT_FOR_FORMATION_AND_BET = 10

# [[(hour, minute), (hour, minute)] ...]
# 每个元素是两个 h, m 的组合
# 表示 在他们之间 的时间 是禁止的
TIME_LIMIT = []
for __h, __m in itertools.chain(GROUP_MATCH_TIME, LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE.values()):
    __m1 = __m - MINUTES_LIMIT_FOR_FORMATION_AND_BET
    if __m1 < 0:
        __m1 += 60
        __h1 = __h - 1
        assert __h1 >= 0
    else:
        __h1 = __h

    TIME_LIMIT.append(((__h1, __m1), (__h, __m)))

# 提前几分钟开打
MATCH_AHEAD_MINUTE = 1

# 允许报名 周几
APPLY_WEEKDAY = [
    # 0,  # 星期一
    1,  # 星期二
    # 2,  # 星期三
    3,  # 星期四
    # 4,  # 星期五
    5,  # 星期六
    # 6,  # 星期日
]

# 允许报名时间范围 hour, minute
APPLY_TIME_RANGE = [(8, 0), (13, 30)]

MATCH_SERVER_REQ_HEADERS = {'NMVC_APIRequest': 'StartCombat'}

AUTO_APPLY_VIP_LEVEL = GlobalConfig.value("CHAMPIONSHIP_AUTO_APPLY_VIP_LEVEL")
APPLY_CLUB_LEVEL_LIMIT = GlobalConfig.value("CHAMPIONSHIP_APPLY_LEVEL_LIMIT")


def make_pairs_from_flat_list(items):
    pairs = []
    for i in range(0, len(items) - 1, 2):
        pairs.append((items[i], items[i + 1]))

    return pairs


def check_club_level(silence=True):
    def deco(fun):
        def wrap(self, *args, **kwargs):
            """

            :type self: Championship
            """

            if self.club_level < APPLY_CLUB_LEVEL_LIMIT:
                if silence:
                    return

                raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

            return fun(self, *args, **kwargs)

        return wrap

    return deco


def check_time_limit(fun):
    def wrap(self, *args, **kwargs):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        for (_h1, _m1), (_h2, _m2) in TIME_LIMIT:
            if _h1 <= now.hour <= _h2 and _m1 <= now.minute < _m2:
                raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_FORMATION_FORBIDDEN"))

        return fun(self, *args, **kwargs)

    return wrap


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


# 报名前清理上一次残留信息
def before_apply(server_id):
    MongoChampionshipLevel.db(server_id).drop()
    MongoChampionship.db(server_id).update_many(
        {},
        {'$set': {
            'bet': {},
            'has_bet': False
        }}
    )

    basic_notify = make_common_basic_notify_msg(server_id)
    basic_data = MessageFactory.pack(basic_notify)

    level_notify = ChampionshipLevel(server_id).make_protomsg()
    level_data = MessageFactory.pack(level_notify)

    char_ids = OperationLog.get_recent_action_char_ids(server_id)
    for cid in char_ids:
        mp = MessagePipe(cid)
        mp.put(data=basic_data)
        mp.put(data=level_data)


# 取历史前N
def get_history_top_clubs(server_id):
    doc = MongoChampionHistory.db(server_id).find_one(
        {'_id': MongoChampionHistory.DOC_ID}
    )

    if not doc:
        return []

    clubs = []
    for i in doc['member_ids']:
        clubs.append((i, doc['info'][i]['name'], doc['info'][i]['flag']))

    return clubs


# 公共相同的 ChampionNotify， applied, bet 就每个角色自己设置
def make_common_basic_notify_msg(server_id):
    notify = ChampionNotify()
    notify.applied = False

    for lv in LEVEL_SEQ:
        notify_bet = notify.bet.add()
        notify_bet.level = lv
        # no bet info

    top_clubs = get_history_top_clubs(server_id)
    for i, name, flag in top_clubs:
        notify_top_club = notify.top_clubs.add()
        notify_top_club.id = i
        notify_top_club.name = name
        notify_top_club.flag = flag

    return notify


# 空的group消息
def make_empty_group_notify_msg():
    notify = ChampionGroupNotify()
    notify.my_score = 0
    notify.my_rank = 0

    return notify


# 清空championship
# NOTE 这个方法用不上
def totally_reset(server_id, send_notify=False):
    MongoChampionship.db(server_id).update_many(
        {},
        {'$set': {
            'applied': False,
            'bet': {},
            'has_bet': False,
        }}
    )

    MongoChampionshipGroup.db(server_id).drop()
    MongoChampionshipLevel.db(server_id).drop()

    if send_notify:
        basic_notify = make_common_basic_notify_msg(server_id)
        basic_data = MessageFactory.pack(basic_notify)

        group_notify = make_empty_group_notify_msg()
        group_data = MessageFactory.pack(group_notify)

        level_notify = ChampionshipLevel(server_id).make_protomsg()
        level_data = MessageFactory.pack(level_notify)

        char_ids = OperationLog.get_recent_action_char_ids(server_id)
        for cid in char_ids:
            mp = MessagePipe(cid)
            mp.put(data=basic_data)
            mp.put(data=group_data)
            mp.put(data=level_data)


class Match(object):
    __slots__ = ['server_id', 'id_one', 'info_one', 'id_two', 'info_two']

    def __init__(self, server_id, id_one, info_one, id_two, info_two):
        self.server_id = server_id
        self.id_one = id_one
        self.info_one = info_one
        self.id_two = id_two
        self.info_two = info_two

    def make_3_way_clubs(self, _id, _info):
        """

        :rtype: [core.abstract.AbstractClub]
        """
        clubs = []

        if is_npc(_id):
            for i in range(1, 4):
                npc_id = _info['ways_npc'][i - 1]
                club = ConfigNPCFormation.get(npc_id)
                club.id = _id
                club.name = _info['name']
                club.flag = _info['flag']

                clubs.append(club)
        else:
            cs = Championship(self.server_id, int(_id))
            for i in range(1, 4):
                way = cs.get_way_object(i)
                club = Club(self.server_id, int(_id), load_staffs=False)
                club.formation_staffs = way.formation_staffs

                clubs.append(club)

        return clubs

    def start(self):
        def one_way_match(_club_one, _club_two):
            _match = ClubMatch(_club_one, _club_two)
            _msg = _match.start(auto_load_staffs=False, check_empty=False)
            _msg.key = ""
            _msg.map_name = GlobalConfig.value_string("MATCH_MAP_CHAMPIONSHIP")

            _req = ClubMatchServerSideRequest()
            _req.match.MergeFrom(_msg)

            _data = _req.SerializeToString()

            _res = requests.post(match_server_url, headers=MATCH_SERVER_REQ_HEADERS, data=_data)

            response = ClubMatchServerSideResponse()
            response.ParseFromString(_res.content)

            if response.star > 0:
                _win = 1
            else:
                _win = 0

            return _win, _msg.SerializeToString(), response.record

        host, port = random.choice(settings.MATCH_SERVERS)
        match_server_url = 'http://{0}:{1}/'.format(host, port)

        one_clubs = self.make_3_way_clubs(self.id_one, self.info_one)
        two_clubs = self.make_3_way_clubs(self.id_two, self.info_two)

        # [one_wins, record_ids]
        one_wins = []
        info_sets = []
        for i in range(3):
            club_one = one_clubs[i]
            club_two = two_clubs[i]

            win, club_match, record = one_way_match(one_clubs[i], two_clubs[i])
            one_wins.append(win)

            info_sets.append((club_one.id, club_two.id, club_match, record))

        record_ids = MatchRecord.batch_create(self.server_id, info_sets)
        return one_wins, record_ids


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

            WAY_MAP[i].MONGO_COLLECTION.db(self.server_id).delete_one({'_id': self.char_id})
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

    def is_applied(self):
        # vip 自动apply
        if self.doc['applied']:
            return True

        if self.club_level < APPLY_CLUB_LEVEL_LIMIT:
            return False

        if VIP(self.server_id, self.char_id).level < AUTO_APPLY_VIP_LEVEL:
            return False

        return True

    @check_club_level(silence=False)
    def apply_in(self):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        if now.weekday() not in APPLY_WEEKDAY:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_APPLY_NOT_OPEN"))

        range_start = make_time_of_today(APPLY_TIME_RANGE[0][0], APPLY_TIME_RANGE[0][1])
        range_end = make_time_of_today(APPLY_TIME_RANGE[1][0], APPLY_TIME_RANGE[1][1])

        if now < range_start or now >= range_end:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_APPLY_NOT_OPEN"))

        if self.is_applied():
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_ALREADY_APPLIED"))

        self.doc['applied'] = True
        MongoChampionship.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'applied': True
            }}
        )

        self.send_basic_notify()

    @check_time_limit
    @check_club_level(silence=False)
    def bet(self, club_id, bet_id):
        cl = ChampionshipLevel(self.server_id)
        lv = cl.get_current_level()
        if lv == 1:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if str(lv) in self.doc['bet']:
            raise GameException(ConfigErrorMessage.get_error_id("CHAMPIONSHIP_ALREADY_BET"))

        if club_id not in cl.doc['levels'].get(str(lv), {}).get('member_ids', []):
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        config = ConfigChampionBet.get(bet_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if config.level != lv:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        rc = ResourceClassification.classify(config.cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Champion.bet:{0}".format(bet_id))

        bet_info = {
            'club_id': club_id,
            'bet_id': bet_id
        }

        self.doc['bet'][str(lv)] = bet_info
        self.doc['has_bet'] = True
        MongoChampionship.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'bet.{0}'.format(lv): bet_info,
                'has_bet': True,
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

    def find_way_id_by_staff_id(self, staff_id):
        for i in [1, 2, 3]:
            if self.get_way_object(i).is_staff_in_formation(staff_id):
                return i

        return 0

    @check_time_limit
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

    @check_time_limit
    @check_club_level(silence=False)
    def set_unit(self, way_id, slot_id, unit_id):
        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        w = self.get_way_object(way_id)
        w.set_unit(slot_id, unit_id)
        self.send_formation_notify()

    @check_time_limit
    @check_club_level(silence=False)
    def set_position(self, way_id, formation_slots):
        my_way = self.get_way_object(way_id)
        my_way.sync_slots(formation_slots)
        self.send_formation_notify()

    @check_club_level(silence=False)
    def sync_group(self):
        cg = ChampionshipGroup(self.server_id)
        cg.find_by_char_id(self.char_id)
        group_msg = cg.make_protomsg()
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

        cg = ChampionshipGroup(self.server_id)
        cg.find_by_char_id(self.char_id)
        group_msg = cg.make_protomsg()
        MessagePipe(self.char_id).put(msg=group_msg)

        cl = ChampionshipLevel(self.server_id)
        level_msg = cl.make_protomsg()
        MessagePipe(self.char_id).put(msg=level_msg)

    def send_basic_notify(self, basic_notify=None):
        if not basic_notify:
            basic_notify = make_common_basic_notify_msg(self.server_id)

        basic_notify.applied = self.is_applied()

        for bet in basic_notify.bet:
            bet_info = self.doc['bet'].get(str(bet.level), {})
            if bet_info:
                bet.bet_for = bet_info['club_id']
                bet.bet_id = bet_info['bet_id']

        MessagePipe(self.char_id).put(msg=basic_notify)

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

        # 只有在 find_by_char_id 并且找到group的清空下，才填充 _char_id
        self._char_id = None

        # 这两个仅仅是初始化group的适合保存信息的，
        # 后面查询到的数据，这两个并不填充
        self._member_ids = []
        self._info = {}

    def find_by_char_id(self, char_id):
        self.doc = MongoChampionshipGroup.db(self.server_id).find_one(
            {'member_ids': str(char_id)}
        )

        if self.doc:
            self.group_id = self.doc['_id']
            self._char_id = char_id

    def find_by_group_id(self, group_id):
        self.doc = MongoChampionshipGroup.db(self.server_id).find_one(
            {'_id': group_id}
        )

        if self.doc:
            self.group_id = group_id

    @classmethod
    def new(cls, server_id):
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
        doc['match_times'] = 1
        MongoChampionshipGroup.db(self.server_id).insert_one(doc)

    def get_scores_sorted(self):
        if not self.doc:
            return []

        scores = self.doc['scores'].items()
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores

    def get_top_two(self):
        scores = self.get_scores_sorted()
        return [scores[0][0], scores[1][0]]

    def start_match(self):
        match_times = self.doc['match_times']
        if match_times == 7:
            return match_times

        hour, minute = GROUP_MATCH_TIME[match_times - 1]
        match_at = make_time_of_today(hour, minute).timestamp

        scores = self.get_scores_sorted()
        pairs = make_pairs_from_flat_list(scores)

        for (id_one, _), (id_two, _) in pairs:
            info_one = self.doc['info'][id_one]
            info_two = self.doc['info'][id_two]

            m = Match(self.server_id, id_one, info_one, id_two, info_two)
            one_way_wins, record_ids = m.start()

            two_way_wins = [1 - _w for _w in one_way_wins]

            one_way_wins_count = len([_w for _w in one_way_wins if _w == 1])
            two_way_wins_count = len([_w for _w in two_way_wins if _w == 1])

            one_got_score = ConfigChampionWinScore.get(one_way_wins_count).score
            two_got_score = ConfigChampionWinScore.get(two_way_wins_count).score

            self.doc['scores'][id_one] += one_got_score
            self.doc['scores'][id_two] += two_got_score

            one_name = self.doc['info'][id_one]['name']
            two_name = self.doc['info'][id_two]['name']
            one_log = self.make_match_log(match_at, two_name, one_got_score, one_way_wins, record_ids)
            two_log = self.make_match_log(match_at, one_name, two_got_score, two_way_wins, record_ids)

            self.doc['logs'][id_one].append(one_log)
            self.doc['logs'][id_two].append(two_log)

            self.send_score_reward_mail(id_one, self.doc['scores'][id_one])
            self.send_score_reward_mail(id_two, self.doc['scores'][id_two])

        self.doc['match_times'] += 1
        MongoChampionshipGroup.db(self.server_id).update_one(
            {'_id': self.group_id},
            {'$set': {
                'scores': self.doc['scores'],
                'logs': self.doc['logs'],
                'match_times': self.doc['match_times'],
            }}
        )

        return self.doc['match_times']

    def send_score_reward_mail(self, club_id, score):
        if is_npc(club_id):
            return

        config = ConfigChampionScoreReward.get(score)
        if not config:
            return

        rc = ResourceClassification.classify(config.reward)
        attachment = rc.to_json()

        m = MailManager(self.server_id, int(club_id))
        m.add(config.mail_title, config.mail_content, attachment=attachment)

    @staticmethod
    def make_match_log(match_at, target_name, got_score, way_wins, record_ids):
        doc = MongoChampionshipGroup.document_match_log()
        doc['timestamp'] = match_at
        doc['target_name'] = target_name
        doc['got_score'] = got_score
        doc['way_wins'] = way_wins
        doc['record_ids'] = record_ids
        return doc

    def make_clubs_msg(self, scores=None):
        msgs = []
        if not scores:
            scores = self.get_scores_sorted()

        for index, (club_id, score) in enumerate(scores):
            rank = index + 1
            if rank >= 10:
                # 只发前10名
                break

            msg = MsgChampionClub()
            msg.id = club_id
            msg.name = self.doc['info'][club_id]['name']
            msg.flag = self.doc['info'][club_id]['flag']
            msg.rank = rank
            msg.score = score

            msgs.append(msg)

        return msgs

    def make_protomsg(self):
        if not self.doc:
            return make_empty_group_notify_msg()

        my_score = 0
        my_rank = 0
        scores = self.get_scores_sorted()
        for _index, (_id, _score) in enumerate(scores):
            if _id == str(self._char_id):
                my_score = _score
                my_rank = _index + 1
                break

        notify = ChampionGroupNotify()
        notify.my_score = my_score
        notify.my_rank = my_rank

        clubs = self.make_clubs_msg(scores=scores)

        for c in clubs:
            notify_club = notify.clubs.add()
            notify_club.MergeFrom(c)

        for log in self.doc['logs'][str(self._char_id)]:
            notify_log = notify.logs.add()
            notify_log.timestamp = log['timestamp']
            notify_log.target_name = log['target_name']
            notify_log.got_score = log['got_score']
            notify_log.way_wins.extend(log['way_wins'])
            notify_log.match_record_ids.extend(log['record_ids'])

        match_times = self.doc['match_times']
        if match_times > 6:
            notify.next_match_at = 0
        else:
            hour, minute = GROUP_MATCH_TIME[match_times - 1]
            notify.next_match_at = make_time_of_today(hour, minute).timestamp

            pairs = make_pairs_from_flat_list(scores)
            for (id_one, _), (id_two, _) in pairs:
                if id_one == str(self._char_id):
                    notify.next_target.id = id_two
                    notify.next_target.name = self.doc['info'][id_two]['name']
                    notify.next_target.flag = self.doc['info'][id_two]['flag']

                elif id_two == str(self._char_id):
                    notify.next_target.id = id_one
                    notify.next_target.name = self.doc['info'][id_one]['name']
                    notify.next_target.flag = self.doc['info'][id_one]['flag']

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

        vip_ids = VIP.query_char_ids(server_id, min_level=AUTO_APPLY_VIP_LEVEL)

        if vip_ids:
            club_docs = MongoCharacter.db(server_id).find(
                {'_id': {'$in': vip_ids}},
                {'level': 1}
            )

            for doc in club_docs:
                if doc['level'] >= APPLY_CLUB_LEVEL_LIMIT:
                    club_ids.add(doc['_id'])

        return list(club_ids)

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
            npc_doc = ConfigPlunderNPC.get(2).to_simple_doc()
            npc_id = npc_doc.pop('id')
            info[npc_id] = npc_doc

        ids = info.keys()
        random.shuffle(ids)

        # 把这些ids 随机分配到8个 group 中
        groups = []
        """:type: list[ChampionshipGroup]"""
        for i in range(8):
            g = ChampionshipGroup.new(server_id)
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

        char_ids = OperationLog.get_recent_action_char_ids(server_id)
        for cid in char_ids:
            g = ChampionshipGroup(server_id)
            g.find_by_char_id(cid)
            msg = g.make_protomsg()
            MessagePipe(cid).put(msg=msg)

    @classmethod
    def start_match(cls, server_id):
        groups = cls.find_all_groups(server_id)
        if not groups:
            return 0

        match_times = 0
        for g in groups:
            match_times = g.start_match()

        if match_times == 7:
            # 小组赛打完了
            # 其实这个drop没必要，不过以防万一
            MongoChampionshipLevel.db(server_id).drop()
            cl = ChampionshipLevel(server_id)
            cl.initialize()

            level_notify = cl.make_protomsg()
            level_data = MessageFactory.pack(level_notify)

            char_ids = OperationLog.get_recent_action_char_ids(server_id)
            for cid in char_ids:
                MessagePipe(cid).put(data=level_data)

        return match_times - 1


class ChampionshipLevel(object):
    __slots__ = ['server_id', 'doc']

    def __init__(self, server_id):
        self.server_id = server_id

        self.doc = MongoChampionshipLevel.db(self.server_id).find_one(
            {'_id': MongoChampionshipLevel.DOC_ID}
        )
        if not self.doc:
            self.doc = MongoChampionshipLevel.document()
            MongoChampionshipLevel.db(self.server_id).insert_one(self.doc)

    def initialize(self):
        # 16强初始化
        groups = ChampionshipGroupManager.find_all_groups(self.server_id)
        info = {}
        tops = []
        way_wins = {}
        record_ids = {}

        for g in groups:
            id_one, id_two = g.get_top_two()
            info[id_one] = g.doc['info'][id_one]
            info[id_two] = g.doc['info'][id_two]

            tops.append((id_one, id_two))
            way_wins[id_one] = g.doc['logs'][id_one][-1]['way_wins']
            record_ids[id_one] = g.doc['logs'][id_one][-1]['record_ids']

            way_wins[id_two] = g.doc['logs'][id_two][-1]['way_wins']
            record_ids[id_two] = g.doc['logs'][id_two][-1]['record_ids']

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
        self.save(16, member_ids, way_wins, record_ids, info=info)

    def get_current_level(self):
        return self.doc['current_level']

    def save(self, level, member_ids, way_wins, record_ids, info=None):
        level_doc = MongoChampionshipLevel.document_level()
        level_doc['member_ids'] = member_ids
        level_doc['way_wins'] = way_wins
        level_doc['record_ids'] = record_ids

        self.doc['levels'][str(level)] = level_doc
        self.doc['current_level'] = level

        updater = {
            'levels.{0}'.format(level): level_doc,
            'current_level': level,
        }
        if info:
            updater['info'] = info

        MongoChampionshipLevel.db(self.server_id).update_one(
            {'_id': MongoChampionshipLevel.DOC_ID},
            {'$set': updater}
        )

        self.send_rank_reward_mail(level)

    def send_rank_reward_mail(self, level):
        config = ConfigChampionRankReward.get(level)

        member_ids = self.doc['levels'][str(level)]['member_ids']

        rc = ResourceClassification.classify(config.reward)
        attachment = rc.to_json()

        for m in member_ids:
            if is_npc(m):
                continue

            m = MailManager(self.server_id, int(m))
            m.add(config.mail_title, config.mail_content, attachment=attachment)

    def send_bet_reward_mail(self, level, win_ids):
        # 找到所有bet的玩家，然后遍历
        docs = MongoChampionship.db(self.server_id).find({'has_bet': True})
        for doc in docs:
            bet_info = doc['bet'].get(str(level), {})
            if not bet_info:
                continue

            config = ConfigChampionBet.get(bet_info['bet_id'])
            if bet_info['club_id'] in win_ids:
                m_title = config.win_mail_title
                m_content = config.win_mail_content
                m_reward = config.win_reward
            else:
                m_title = config.lose_mail_title
                m_content = config.lose_mail_content
                m_reward = config.lose_reward

            rc = ResourceClassification.classify(m_reward)
            attachment = rc.to_json()
            m = MailManager(self.server_id, doc['_id'])
            m.add(m_title, m_content, attachment=attachment)

    def start_match(self):
        if not self.doc['levels']:
            return 0

        lv = self.doc['current_level']
        if lv == 1:
            return None

        next_level = LEVEL_NEXT_TABLE[lv]

        member_ids = self.doc['levels'][str(lv)]['member_ids']
        pairs = make_pairs_from_flat_list(member_ids)

        win_ids = []
        lose_ids = []

        way_wins = {}
        record_ids = {}
        for id_one, id_two in pairs:
            info_one = self.doc['info'][id_one]
            info_two = self.doc['info'][id_two]

            m = Match(self.server_id, id_one, info_one, id_two, info_two)
            one_way_wins, one_record_ids = m.start()
            two_way_wins = [1 - _w for _w in one_way_wins]
            one_way_wins_count = len([_w for _w in one_way_wins if _w == 1])

            if one_way_wins_count >= 2:
                win_ids.append(id_one)
                lose_ids.append(id_two)

                way_wins[id_one] = one_way_wins
                record_ids[id_one] = one_record_ids
            else:
                win_ids.append(id_two)
                lose_ids.append(id_one)

                way_wins[id_two] = two_way_wins
                record_ids[id_two] = one_record_ids

        self.save(next_level, win_ids, way_wins, record_ids)

        # 发送下注邮件
        self.send_bet_reward_mail(lv, win_ids)

        if next_level == 1:
            self.after_final_match()

        return lv

    def after_final_match(self):
        # 已经打完了，但还要得出第三四名，并记录前四名
        level_4_member_ids = self.doc['levels']['4']['member_ids'][:]
        level_2_member_ids = self.doc['levels']['2']['member_ids'][:]
        for i in level_2_member_ids:
            level_4_member_ids.remove(i)

        id_one = level_4_member_ids[0]
        id_two = level_4_member_ids[1]

        info_one = self.doc['info'][id_one]
        info_two = self.doc['info'][id_two]

        m = Match(self.server_id, id_one, info_one, id_two, info_two)
        one_way_wins, one_record_ids = m.start()
        # two_way_wins = [1 - _w for _w in one_way_wins]
        one_way_wins_count = len([_w for _w in one_way_wins if _w == 1])

        if one_way_wins_count >= 2:
            third = id_one
            fourth = id_two
        else:
            third = id_two
            fourth = id_one

        first = self.doc['levels']['1']['member_ids'][0]
        level_2_member_ids.remove(first)
        second = level_2_member_ids[0]

        MongoChampionHistory.db(self.server_id).drop()
        history_doc = MongoChampionHistory.document()
        history_doc['member_ids'] = [first, second, third, fourth]
        history_doc['info'] = {
            first: self.doc['info'][first],
            second: self.doc['info'][second],
            third: self.doc['info'][third],
            fourth: self.doc['info'][fourth],
        }

        MongoChampionHistory.db(self.server_id).insert_one(history_doc)

        # 清空小组赛
        MongoChampionshipGroup.db(self.server_id).drop()
        group_notify = make_empty_group_notify_msg()
        group_data = MessageFactory.pack(group_notify)

        # 清空玩家的报名标识
        MongoChampionship.db(self.server_id).update_many(
            {},
            {'$set': {
                'applied': False
            }}
        )

        char_ids = OperationLog.get_recent_action_char_ids(self.server_id)
        basic_notify = make_common_basic_notify_msg(self.server_id)
        for _cid in char_ids:
            MessagePipe(_cid).put(data=group_data)
            Championship(self.server_id, _cid).send_basic_notify(basic_notify=basic_notify)

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
            level16 = self.doc['levels'].get('16', {})
            if level16:
                for i in level16['member_ids']:
                    notify_club = notify.clubs.add()
                    notify_club.id = i
                    notify_club.name = self.doc['info'][i]['name']
                    notify_club.flag = self.doc['info'][i]['flag']

        for lv in levels:
            notify_level = notify.levels.add()

            notify_level.level = lv
            this_level = self.doc['levels'].get(str(lv), {})
            if this_level:
                for _mid in this_level['member_ids']:
                    notify_level_club = notify_level.clubs.add()
                    notify_level_club.id = _mid
                    notify_level_club.way_wins.extend(this_level['way_wins'][str(_mid)])
                    notify_level_club.match_record_ids.extend(this_level['record_ids'][str(_mid)])

            if lv == 16:
                notify_level.match_at = 0
            else:
                prev_lv = LEVEL_PREVIOUS_TABLE[lv]
                hour, minute = LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE[prev_lv]
                notify_level.match_at = make_time_of_today(hour, minute).timestamp

        return notify
