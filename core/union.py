# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 15:04
Description:

"""

import math
from collections import OrderedDict

import arrow
from pymongo.errors import DuplicateKeyError

from dianjing.exception import GameException

from core.mongo import MongoUnion, MongoUnionMember
from core.resource import ResourceClassification, money_text_to_item_id
from core.value_log import (
    ValueLogUnionSignInTimes,
    ValueLogUnionExploreTimes,
    ValueLogUnionHarassTimes,
    ValueLogUnionHarassBuyTimes,
)

from core.club import Club, batch_get_club_property, get_club_property
from core.vip import VIP
from core.mail import MailManager
from core.cooldown import UnionExploreCD
from core.staff import StaffManger

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import (
    GlobalConfig,
    ConfigErrorMessage,
    ConfigUnionSignin,
    ConfigUnionLevel,
    ConfigUnionExplore,
    ConfigUnionExploreRankReward,
    ConfigUnionMemberExploreRankReward,
    ConfigUnionHarassBuyTimesCost,
    ConfigUnionSkill,
)

from config.text import (
    UNION_AUTO_TRANSFER_OLD_OWNER_MAIL_TITLE,
    UNION_AUTO_TRANSFER_OLD_OWNER_MAIL_CONTENT,
    UNION_AUTO_TRANSFER_NEW_OWNER_MAIL_TITLE,
    UNION_AUTO_TRANSFER_NEW_OWNER_MAIL_CONTENT,
    UNION_MANUAL_TRANSFER_NEW_OWNER_MAIL_TITLE,
    UNION_MANUAL_TRANSFER_NEW_OWNER_MAIL_CONTENT,
    UNION_QUIT_TRANSFER_NEW_OWNER_MAIL_TITLE,
    UNION_QUIT_TRANSFER_NEW_OWNER_MAIL_CONTENT,
)

from protomsg.union_pb2 import (
    UnionMyAppliedNotify,
    UnionMyCheckNotify,
    UnionNotify,
    UnionMember as MsgMember,
    UnionExploreNotify,
    UnionSkillNotify,
)
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

BULLETIN_MAX_LENGTH = 255

UNION_COIN_ID = 30020
UNION_SKILL_POINT_ID = 30025


class ExploreInfo(object):
    __slots__ = ['server_id', 'char_id', 'current_times', 'max_times', 'remained_times']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.max_times = GlobalConfig.value("UNION_EXPLORE_TIMES")
        self.current_times = ValueLogUnionExploreTimes(server_id, char_id).count_of_today()
        self._calculate()

    def _calculate(self):
        self.remained_times = self.max_times - self.current_times
        if self.remained_times < 0:
            self.remained_times = 0

    def get_cd(self):
        return UnionExploreCD(self.server_id, self.char_id).get_cd_seconds()

    def check_cd(self):
        if self.get_cd():
            raise GameException(ConfigErrorMessage.get_error_id("UNION_EXPLORE_CD"))

    def record(self):
        ValueLogUnionExploreTimes(self.server_id, self.char_id).record()
        UnionExploreCD(self.server_id, self.char_id).set(GlobalConfig.value("UNION_EXPLORE_CD"))

        self.current_times += 1
        self._calculate()


class HarassInfo(object):
    __slots__ = ['server_id', 'char_id',
                 'current_times', 'max_times', 'remained_times',
                 'current_buy_times', 'remained_buy_times',
                 'vip_max_buy_times', 'buy_cost',
                 ]

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.max_times = GlobalConfig.value("UNION_HARASS_TIMES")
        self.current_times = ValueLogUnionHarassTimes(server_id, char_id).count_of_today()
        self.current_buy_times = ValueLogUnionHarassBuyTimes(server_id, char_id).count_of_today()

        self.vip_max_buy_times = VIP(server_id, char_id).union_harass_buy_times
        self._calculate()

    def _calculate(self):
        self.buy_cost = ConfigUnionHarassBuyTimesCost.get_cost(self.current_buy_times + 1)

        self.remained_buy_times = self.vip_max_buy_times - self.current_buy_times
        if self.remained_buy_times < 0:
            self.remained_buy_times = 0

        self.remained_times = self.max_times + self.current_buy_times - self.current_times
        if self.remained_times < 0:
            self.remained_times = 0

    def buy_times(self):
        if not self.remained_buy_times:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_HARASS_NO_BUY_TIMES"))

        cost = [(money_text_to_item_id('diamond'), self.buy_cost)]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="HarassInfo.buy_times")

        ValueLogUnionHarassBuyTimes(self.server_id, self.char_id).record()

        self.current_buy_times += 1
        self._calculate()

    def record(self):
        ValueLogUnionHarassTimes(self.server_id, self.char_id).record()
        self.current_times += 1
        self._calculate()


class _UnionInfo(object):
    __slots__ = ['server_id', 'id', 'name', 'bulletin', 'owner', 'level', 'contribution', 'rank']

    def __init__(self, server_id, doc):
        self.server_id = server_id

        self.id = doc['_id']
        self.name = doc['name']
        self.bulletin = doc['bulletin']
        self.owner = doc['owner']
        self.level = doc['level']
        self.contribution = doc['contribution']

        self.rank = None

    @property
    def members_amount(self):
        return MongoUnionMember.db(self.server_id).find({'joined': self.id}).count()

    @property
    def all_contribution(self):
        contribution = self.contribution
        for lv in range(self.level - 1, 0, -1):
            contribution += ConfigUnionLevel.get(lv).contribution

        return contribution


def get_all_unions(server_id):
    """

    :rtype: dict[str, _UnionInfo]
    """
    docs = MongoUnion.db(server_id).find({}, {'create_at': 0, 'apply_list': 0})

    unions = []
    for doc in docs:
        unions.append(_UnionInfo(server_id, doc))

    unions.sort(key=lambda item: item.all_contribution, reverse=True)

    res = OrderedDict()
    for index, u in enumerate(unions):
        u.rank = index + 1
        res[u.id] = u

    return res


class _MemberClub(Club):
    __slots__ = ['contribution', 'today_contribution']

    def __init__(self, server_id, char_id, contribution, today_contribution):
        super(_MemberClub, self).__init__(server_id, char_id)
        self.contribution = contribution
        self.today_contribution = today_contribution

    def make_member_protomsg(self):
        msg = MsgMember()
        msg.id = str(self.id)
        msg.flag = self.flag
        msg.name = self.name
        msg.level = self.level
        msg.power = self.power
        msg.total_contribution = self.contribution
        msg.today_contribution = self.today_contribution

        return msg


class Union(object):
    def __new__(cls, server_id, char_id):
        """

        :rtype: IUnion
        """
        member_doc = MongoUnionMember.db(server_id).find_one({'_id': char_id})
        if not member_doc:
            member_doc = MongoUnionMember.document()
            member_doc['_id'] = char_id
            MongoUnionMember.db(server_id).insert_one(member_doc)

        if not member_doc['joined']:
            return UnionNotJoined(server_id, char_id, member_doc, None)

        union_doc = MongoUnion.db(server_id).find_one({'_id': member_doc['joined']})
        if union_doc['owner'] == char_id:
            return UnionOwner(server_id, char_id, member_doc, union_doc)

        return UnionMember(server_id, char_id, member_doc, union_doc)


class IUnion(object):
    __slots__ = ['server_id', 'char_id', 'member_doc', 'union_doc']

    def __init__(self, server_id, char_id, member_doc, union_doc):
        self.server_id = server_id
        self.char_id = char_id
        self.member_doc = member_doc
        self.union_doc = union_doc

    def get_joined_union_id(self):
        raise NotImplementedError()

    def get_joined_union_owner_id(self):
        raise NotImplementedError()

    def get_member_ids(self):
        raise NotImplementedError()

    def create(self, name):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def apply_union(self, union_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def set_bulletin(self, content):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def agree(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def refuse(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def kick(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def transfer(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def quit(self):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def sign_in(self, _id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def check_level(self, target_level):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def explore(self, staff_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def harass(self, union_id, staff_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def harass_buy_times(self):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def add_explore_point(self, point):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def query_by_explore_point_rank(self):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def skill_level_up(self, skill_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def get_union_skill_talent_effects(self):
        raise NotImplementedError()

    def send_all_notify(self):
        self.send_notify()
        self.send_my_applied_notify()
        self.send_my_check_notify()
        self.send_explore_notify()
        self.send_skill_notify()

    def send_notify(self, **kwargs):
        raise NotImplementedError()

    def send_my_applied_notify(self):
        raise NotImplementedError()

    def send_my_check_notify(self):
        raise NotImplementedError()

    def send_explore_notify(self):
        raise NotImplementedError()

    def send_skill_notify(self):
        raise NotImplementedError()


# 没有加入公会
class UnionNotJoined(IUnion):
    __slots__ = []

    def get_joined_union_id(self):
        return ''

    def get_joined_union_owner_id(self):
        return 0

    def get_member_ids(self):
        return []

    def get_union_skill_talent_effects(self):
        return []

    def create(self, name):
        cost = [(money_text_to_item_id('diamond'), GlobalConfig.value("UNION_CREATE_COST"))]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)

        doc = MongoUnion.document()
        doc['_id'] = make_string_id()
        doc['create_at'] = arrow.utcnow().timestamp
        doc['name'] = name
        doc['owner'] = self.char_id

        try:
            MongoUnion.db(self.server_id).insert_one(doc)
        except DuplicateKeyError:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_NAME_HAS_TAKEN"))

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'joined': doc['_id'],
                'joined_at': arrow.utcnow().timestamp
            }}
        )

        rc.remove(self.server_id, self.char_id, message="Union.create")
        Union(self.server_id, self.char_id).send_all_notify()

    def apply_union(self, union_id):
        kick_flag = self.member_doc.get('kick_flag', False)
        quit_flag = self.member_doc.get('quit_flag', False)

        if kick_flag or quit_flag:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_APPLY_QUIT_OR_KICK"))

        doc = MongoUnion.db(self.server_id).find_one({'_id': union_id})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_NOT_EXIST"))

        config = ConfigUnionLevel.get(doc['level'])

        if MongoUnionMember.db(self.server_id).find({'joined': union_id}).count() >= config.members_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_APPLY_MEMBERS_LIMIT"))

        MongoUnion.db(self.server_id).update_one(
            {'_id': union_id},
            {'$addToSet': {
                'apply_list': self.char_id
            }}
        )

        self.send_my_applied_notify()

        u = Union(self.server_id, doc['owner'])
        u.send_my_check_notify()

    def send_notify(self):
        notify = UnionNotify()
        notify.id = ""
        notify.name = ""
        notify.bulletin = ""
        notify.level = 0
        notify.contribution = 0
        notify.rank = 0
        notify.my_contribution = 0
        notify.signin_id = 0
        MessagePipe(self.char_id).put(msg=notify)

    def send_my_applied_notify(self):
        docs = MongoUnion.db(self.server_id).find({'apply_list': self.char_id}, {'_id': 1})
        ids = [d['_id'] for d in docs]

        notify = UnionMyAppliedNotify()
        notify.union_ids.extend(ids)
        MessagePipe(self.char_id).put(msg=notify)

    def send_my_check_notify(self):
        pass

    def send_explore_notify(self):
        pass

    def send_skill_notify(self):
        pass


class UnionJoined(IUnion):
    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(UnionJoined, self).__init__(*args, **kwargs)

        updater = {}
        if 'skills' not in self.member_doc:
            self.member_doc['skills'] = {}
            updater['skills'] = {}

        if not self.member_doc.get('explore_staff', 0):
            self.member_doc['explore_staff'] = ConfigUnionExplore.get_staff_id()
            self.member_doc['harass_staff'] = ConfigUnionExplore.get_staff_id()

            updater['explore_staff'] = self.member_doc['explore_staff']
            updater['harass_staff'] = self.member_doc['harass_staff']

        if updater:
            MongoUnionMember.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

    def get_joined_union_id(self):
        return self.member_doc['joined']

    def get_joined_union_owner_id(self):
        return self.union_doc['owner']

    def get_member_ids(self):
        docs = MongoUnionMember.db(self.server_id).find(
            {'joined': self.union_doc['_id']},
            {'_id': 1}
        )

        return [d['_id'] for d in docs]

    def get_union_skill_talent_effects(self):
        talent_ids = []
        for k, v in self.member_doc['skills'].iteritems():
            _id = ConfigUnionSkill.get(int(k)).levels[v].talent_id
            if _id:
                talent_ids.append(_id)

        return talent_ids

    def create(self, name):
        raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_CREATE_ALREADY_IN"))

    def apply_union(self, union_id):
        raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_APPLY_ALREADY_IN"))

    def quit(self, kick=False, send_notify=True):
        self.member_doc['joined'] = 0
        self.member_doc['joined_at'] = 0
        self.member_doc['contribution'] = 0
        self.member_doc['today_contribution'] = 0

        if kick:
            flag = 'kick_flag'
        else:
            flag = 'quit_flag'

        self.member_doc[flag] = True

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'joined': 0,
                'joined_at': 0,
                'contribution': 0,
                'today_contribution': 0,
                flag: True,
            }}
        )

        if send_notify:
            self.send_notify_to_all_members()

    def sign_in(self, _id):
        """

        :rtype: ResourceClassification
        """
        if self.get_signed_id():
            raise GameException(ConfigErrorMessage.get_error_id("UNION_ALREADY_SIGNED"))

        config = ConfigUnionSignin.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if config.vip:
            VIP(self.server_id, self.char_id).check(config.vip)

        rc = ResourceClassification.classify(config.cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Union.sign_in")

        self.add_contribution(config.contribution, send_notify=False)

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id, message="Union.sign_in")

        ValueLogUnionSignInTimes(self.server_id, self.char_id).record(sub_id=_id)

        self.send_notify()
        return rc

    def check_level(self, target_level):
        if self.union_doc['level'] < target_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_LEVEL_NOT_ENOUGH"))

    def add_contribution(self, value, send_notify=True):
        # 给自己加
        self.member_doc['contribution'] += value
        self.member_doc['today_contribution'] += value

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'contribution': self.member_doc['contribution'],
                'today_contribution': self.member_doc['today_contribution']
            }}
        )

        # 给公会加
        union_contribution = self.union_doc['contribution'] + value
        level = self.union_doc['level']

        while True:
            if level >= ConfigUnionLevel.MAX_LEVEL:
                level = ConfigUnionLevel.MAX_LEVEL

                if union_contribution >= ConfigUnionLevel.get(ConfigUnionLevel.MAX_LEVEL).contribution:
                    union_contribution = ConfigUnionLevel.get(ConfigUnionLevel.MAX_LEVEL).contribution

                break

            up_need = ConfigUnionLevel.get(level).contribution
            if union_contribution < up_need:
                break

            union_contribution -= up_need
            level += 1

        self.union_doc['level'] = level
        self.union_doc['contribution'] = union_contribution

        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'level': level,
                'contribution': union_contribution
            }}
        )

        if send_notify:
            self.send_notify()

    def get_signed_id(self):
        times = ValueLogUnionSignInTimes(self.server_id, self.char_id).batch_count_of_today()
        if not times:
            return 0

        _id = times.keys()[0]
        return int(_id)

    def get_members(self):
        """

        :rtype: list[_MemberClub]
        """
        owner = self.union_doc['owner']
        docs = MongoUnionMember.db(self.server_id).find({'joined': self.union_doc['_id']})

        owner_doc = None
        members = []
        for doc in docs:
            if doc['_id'] == owner:
                owner_doc = doc
                continue

            members.append(_MemberClub(self.server_id, doc['_id'], doc['contribution'], doc['today_contribution']))

        members.sort(key=lambda item: item.contribution, reverse=True)

        if owner_doc:
            members.insert(0, _MemberClub(self.server_id, owner_doc['_id'], owner_doc['contribution'],
                                          owner_doc['today_contribution']))
        return members

    def get_members_amount(self):
        return MongoUnionMember.db(self.server_id).find({'joined': self.union_doc['_id']}).count()

    def get_rank(self):
        unions = get_all_unions(self.server_id)
        return unions[self.union_doc['_id']].rank

    def explore(self, staff_id):
        staff = StaffManger(self.server_id, self.char_id).get_staff_object(staff_id)

        ei = ExploreInfo(self.server_id, self.char_id)
        ei.check_cd()
        if not ei.remained_times:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_EXPLORE_NO_TIMES"))

        if staff.oid == self.member_doc['explore_staff']:
            param = 2
        else:
            param = 1

        ei.record()

        union_coin = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 3 * param)
        explore_point = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 10 * param)
        union_skill_point = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 4 * param)

        self.add_explore_point(explore_point)

        reward = ConfigUnionExplore.get_explore_reward()
        reward = [(_id, _amount * param) for _id, _amount in reward]
        reward.append((UNION_COIN_ID, union_coin))
        reward.append((UNION_SKILL_POINT_ID, union_skill_point))

        rc = ResourceClassification.classify(reward)
        rc.add(self.server_id, self.char_id, message="UnionJoined.explore")

        self.member_doc['explore_staff'] = ConfigUnionExplore.get_staff_id()
        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'explore_staff': self.member_doc['explore_staff']
            }}
        )

        self.send_explore_notify()
        return explore_point, rc

    def harass(self, union_id, staff_id):
        doc = MongoUnion.db(self.server_id).find_one({'_id': union_id}, {'owner': 1})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_NOT_EXIST"))

        staff = StaffManger(self.server_id, self.char_id).get_staff_object(staff_id)

        hi = HarassInfo(self.server_id, self.char_id)
        if not hi.remained_times:
            hi.buy_times()

        if staff.oid == self.member_doc['harass_staff']:
            param = 2
        else:
            param = 1

        hi.record()

        union_coin = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 3.5 * param)
        explore_point = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 7 * param)
        union_skill_point = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 5 * param)

        my_explore_point = int((math.pow(staff.level, 0.2) + math.pow(staff.step + 1, 0.5)) * 5 * param)
        self.add_explore_point(my_explore_point)

        Union(self.server_id, doc['owner']).add_explore_point(-explore_point)

        reward = ConfigUnionExplore.get_harass_reward()
        reward = [(_id, _amount * param) for _id, _amount in reward]
        reward.append((UNION_COIN_ID, union_coin))
        reward.append((UNION_SKILL_POINT_ID, union_skill_point))

        rc = ResourceClassification.classify(reward)
        rc.add(self.server_id, self.char_id, message="UnionJoined.harass")

        self.member_doc['harass_staff'] = ConfigUnionExplore.get_staff_id()
        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'harass_staff': self.member_doc['harass_staff']
            }}
        )

        self.send_explore_notify()
        return explore_point, rc, my_explore_point

    def harass_buy_times(self):
        hi = HarassInfo(self.server_id, self.char_id)
        hi.buy_times()
        self.send_explore_notify()

    def add_explore_point(self, point):
        # point 如果大于零，就是给自己和公会都加
        # 如果小于零，只减公会的
        if point > 0:
            self.member_doc['explore_point'] = self.member_doc.get('explore_point', 0) + point
            MongoUnionMember.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': {
                    'explore_point': point
                }}
            )

            self.union_doc['explore_point'] = self.union_doc.get('explore_point', 0) + point
            MongoUnion.db(self.server_id).update_one(
                {'_id': self.union_doc['_id']},
                {'$inc': {
                    'explore_point': point
                }}
            )

        elif point < 0:
            old_point = self.union_doc.get('explore_point', 0)
            if abs(point) > old_point:
                point = -old_point

            self.union_doc['explore_point'] = old_point + point
            MongoUnion.db(self.server_id).update_one(
                {'_id': self.union_doc['_id']},
                {'$inc': {
                    'explore_point': point
                }}
            )

    def query_by_explore_point_rank(self):
        result, self_info = get_unions_ordered_by_explore_point(self.server_id, self.char_id, around_rank=2)
        return result, self_info

    def skill_level_up(self, skill_id):
        config = ConfigUnionSkill.get(skill_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_SKILL_NOT_EXIST"))

        current_level = self.member_doc['skills'].get(str(skill_id), 0)
        if current_level >= config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_SKILL_REACH_SELF_MAX_LEVEL"))

        if current_level >= self.union_doc['level'] * 3:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_SKILL_LEVEL_LIMITED_BY_UNION_LEVEL"))

        rc = ResourceClassification.classify(config.levels[current_level].cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="UnionJoined.skill_level_up")

        self.member_doc['skills'][str(skill_id)] = current_level + 1
        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'skills.{0}'.format(skill_id): current_level + 1
            }}
        )

        Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs(send_notify=True)
        self.send_skill_notify(skill_id=skill_id)

    def send_notify_to_all_members(self, rank=None, send_my_check_notify=False):
        if rank is None:
            rank = self.get_rank()

        docs = MongoUnionMember.db(self.server_id).find(
            {'joined': self.union_doc['_id']},
            {'_id': 1}
        )

        for doc in docs:
            u = Union(self.server_id, doc['_id'])
            u.send_notify(rank=rank)
            if send_my_check_notify:
                u.send_my_check_notify()

    def send_notify(self, rank=None):
        notify = UnionNotify()
        notify.id = self.union_doc['_id']
        notify.name = self.union_doc['name']
        notify.bulletin = self.union_doc['bulletin']
        notify.level = self.union_doc['level']
        notify.contribution = self.union_doc['contribution']

        if rank is None:
            rank = self.get_rank()
        notify.rank = rank
        notify.my_contribution = self.member_doc['contribution']

        members = self.get_members()
        for m in members:
            notify_member = notify.members.add()
            notify_member.MergeFrom(m.make_member_protomsg())

        notify.signin_id = self.get_signed_id()

        MessagePipe(self.char_id).put(msg=notify)

    def send_my_applied_notify(self):
        notify = UnionMyAppliedNotify()
        MessagePipe(self.char_id).put(msg=notify)

    def send_explore_notify(self):
        ei = ExploreInfo(self.server_id, self.char_id)
        hi = HarassInfo(self.server_id, self.char_id)

        notify = UnionExploreNotify()
        notify.explore_staff = self.member_doc['explore_staff']
        notify.explore_remained_times = ei.remained_times
        notify.explore_cd = ei.get_cd()
        notify.harass_staff = self.member_doc['harass_staff']
        notify.harass_remained_times = hi.remained_times
        notify.harass_buy_times = hi.current_buy_times
        notify.harass_buy_cost = hi.buy_cost

        MessagePipe(self.char_id).put(msg=notify)

    def send_skill_notify(self, skill_id=None):
        if skill_id:
            act = ACT_UPDATE
            ids = [skill_id]
        else:
            act = ACT_INIT
            ids = ConfigUnionSkill.INSTANCES.keys()

        notify = UnionSkillNotify()
        notify.act = act

        skills = self.member_doc['skills']
        for i in ids:
            lv = skills.get(str(i), 0)

            notify_skill = notify.skill.add()
            notify_skill.id = i
            notify_skill.level = lv

        MessagePipe(self.char_id).put(msg=notify)


# 普通公会成员
class UnionMember(UnionJoined):
    __slots__ = []

    def send_my_check_notify(self):
        notify = UnionMyCheckNotify()
        MessagePipe(self.char_id).put(msg=notify)


# 会长
class UnionOwner(UnionJoined):
    __slots__ = []

    @classmethod
    def try_auto_transfer(cls, server_id):
        transfer = []

        for doc in MongoUnion.db(server_id).find({}, {'owner': 1}):
            if Club.days_since_last_login(server_id, doc['owner']) <= 7:
                continue

            u = Union(server_id, doc['owner'])
            assert isinstance(u, UnionOwner)

            if u.get_members_amount() == 1:
                continue

            members = u.get_members()
            next_char_id = members[1].id
            u.transfer(next_char_id, send_mail=False)

            MailManager(server_id, doc['owner']).add(
                title=UNION_AUTO_TRANSFER_OLD_OWNER_MAIL_TITLE,
                content=UNION_AUTO_TRANSFER_OLD_OWNER_MAIL_CONTENT
            )

            MailManager(server_id, next_char_id).add(
                title=UNION_AUTO_TRANSFER_NEW_OWNER_MAIL_TITLE,
                content=UNION_AUTO_TRANSFER_NEW_OWNER_MAIL_CONTENT
            )

            transfer.append((doc['_id'], doc['owner'], next_char_id))

        return transfer

    def set_bulletin(self, content):
        if len(content) > BULLETIN_MAX_LENGTH:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_BULLETIN_TOO_LONG"))

        self.union_doc['bulletin'] = content
        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'bulletin': content
            }}
        )

        self.send_notify_to_all_members()

    def agree(self, char_id):
        if char_id not in self.union_doc['apply_list']:
            self.send_my_check_notify()
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_ALREADY_JOIN_A_UNION"))

        self.union_doc['apply_list'].remove(char_id)
        MongoUnion.db(self.server_id).update_many(
            {'apply_list': char_id},
            {'$pull': {
                'apply_list': char_id
            }}
        )

        self.send_my_check_notify()

        if self.get_members_amount() >= ConfigUnionLevel.get(self.union_doc['level']).members_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_MEMBERS_REACH_LIMIT"))

        u = Union(self.server_id, char_id)
        if isinstance(u, UnionJoined):
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_ALREADY_JOIN_A_UNION"))

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': char_id},
            {'$set': {
                'joined': self.union_doc['_id'],
                'joined_at': arrow.utcnow().timestamp
            }}
        )

        self.send_notify()
        Union(self.server_id, char_id).send_all_notify()

    def refuse(self, char_id):
        try:
            self.union_doc['apply_list'].remove(char_id)
        except ValueError:
            pass

        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$pull': {
                'apply_list': char_id
            }}
        )

        self.send_my_check_notify()
        Union(self.server_id, char_id).send_my_applied_notify()

    def kick(self, char_id):
        if char_id == self.char_id:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        u = Union(self.server_id, char_id)
        if not isinstance(u, UnionMember) or u.member_doc['joined'] != self.union_doc['_id']:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_NOT_MEMBER"))

        u.quit()

    def transfer(self, char_id, send_mail=True):
        if char_id == self.char_id:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        u = Union(self.server_id, char_id)
        if not isinstance(u, UnionMember) or u.member_doc['joined'] != self.union_doc['_id']:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_NOT_MEMBER"))

        self.union_doc['owner'] = char_id
        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'owner': char_id
            }}
        )

        if send_mail:
            MailManager(self.server_id, char_id).add(
                title=UNION_MANUAL_TRANSFER_NEW_OWNER_MAIL_TITLE,
                content=UNION_MANUAL_TRANSFER_NEW_OWNER_MAIL_CONTENT
            )

        self.send_notify_to_all_members(send_my_check_notify=True)

    def quit(self, *args):
        super(UnionOwner, self).quit(send_notify=False)
        if self.get_members_amount() == 0:
            MongoUnion.db(self.server_id).delete_one({'_id': self.union_doc['_id']})
            return

        members = self.get_members()
        next_char_id = members[0].char_id
        self.transfer(next_char_id, send_mail=False)

        MailManager(self.server_id, next_char_id).add(
            title=UNION_QUIT_TRANSFER_NEW_OWNER_MAIL_TITLE,
            content=UNION_QUIT_TRANSFER_NEW_OWNER_MAIL_CONTENT,
        )

    def send_my_check_notify(self):
        notify = UnionMyCheckNotify()

        for cid in self.union_doc['apply_list']:
            m = _MemberClub(self.server_id, cid, 0, 0)
            notify_member = notify.members.add()
            notify_member.MergeFrom(m.make_member_protomsg())

        MessagePipe(self.char_id).put(msg=notify)


class _ExploreMember(object):
    __slots__ = ['rank', 'id', 'name', 'explore_point']

    def __init__(self):
        self.rank = 0
        self.id = 0
        self.name = ''
        self.explore_point = 0


class _ExploreUnion(object):
    __slots__ = ['rank', 'id', 'name', 'explore_point']

    def __init__(self):
        self.rank = 0
        self.id = ''
        self.name = ''
        self.explore_point = 0


def get_members_ordered_by_explore_point(server_id, char_id, names=True, limit=None):
    """

    :rtype: (list[_ExploreMember], _ExploreMember | None)
    """
    docs = MongoUnionMember.db(server_id).find(
        {'explore_point': {'$gt': 0}}
    ).sort('explore_point', -1)

    result = []
    """:type: list[_ExploreMember]"""
    self_info = None
    """:type: _ExploreMember | None"""

    for index, doc in enumerate(docs):
        rank = index + 1
        if limit and rank > limit:
            break

        obj = _ExploreMember()
        obj.rank = rank
        obj.id = doc['_id']
        obj.explore_point = doc['explore_point']

        result.append(obj)

        if doc['_id'] == char_id:
            self_info = obj

    if names:
        # find names
        char_ids = [r.id for r in result]
        names = batch_get_club_property(server_id, char_ids, 'name')
        for r in result:
            r.name = names[r.id]

    if char_id == 0:
        return result, None

    if self_info:
        return result, self_info

    doc = MongoUnionMember.db(server_id).find_one({'_id': char_id}, {'explore_point': 1})
    if not doc:
        return result, None

    self_info = _ExploreMember()
    self_info.id = char_id
    self_info.name = get_club_property(server_id, char_id, 'name')
    self_info.explore_point = doc.get('explore_point', 0)
    if not self_info.explore_point:
        self_info.rank = 0
        return result, self_info

    rank = MongoUnionMember.db(server_id).find(
        {'explore_point': {'$gt': self_info.explore_point}}
    ).count()

    self_info.rank = rank
    return result, self_info


def get_unions_ordered_by_explore_point(server_id, char_id, around_rank=None):
    """

    :rtype: (list[_ExploreUnion], _ExploreUnion | None)
    """
    docs = MongoUnion.db(server_id).find(
        {'explore_point': {'$gt': 0}}
    ).sort('explore_point', -1)

    member_doc = MongoUnionMember.db(server_id).find_one(
        {'_id': char_id},
        {'joined': 1}
    )

    if not member_doc:
        self_union_id = ''
    else:
        self_union_id = member_doc['joined']

    result = []
    """:type: list[_ExploreUnion]"""
    self_info = None
    """:type: _ExploreUnion | None"""

    for index, doc in enumerate(docs):
        obj = _ExploreUnion()
        obj.rank = index + 1
        obj.id = doc['_id']
        obj.name = doc['name']
        obj.explore_point = doc['explore_point']

        result.append(obj)

        if doc['_id'] == self_union_id:
            self_info = obj

    if not around_rank:
        return result, self_info

    around_result = []

    if not self_info:
        for i in [-1, -2]:
            try:
                this_obj = result[i]
            except IndexError:
                continue

            around_result.append(this_obj)
    else:
        for i in range(self_info.rank - 1 - around_rank, self_info.rank + around_rank):
            try:
                this_obj = result[i]
            except IndexError:
                continue

            if this_obj not in around_result and this_obj.id != self_union_id:
                around_result.append(this_obj)

    return around_result, self_info


def cronjob_of_union_explore(server_id):
    members, _ = get_members_ordered_by_explore_point(server_id, 0, names=False)
    unions, _ = get_unions_ordered_by_explore_point(server_id, 0)

    MongoUnionMember.db(server_id).update_many(
        {},
        {'$set': {
            'explore_point': 0,
        }}
    )

    MongoUnion.db(server_id).update_many(
        {},
        {'$set': {
            'explore_point': 0,
        }}
    )

    for m in members:
        reward = ConfigUnionMemberExploreRankReward.get_by_rank(m.rank)
        if not reward:
            continue

        attachment = ResourceClassification.classify(reward.reward).to_json()
        m = MailManager(server_id, m.id)
        m.add(reward.mail_title, reward.mail_content, attachment=attachment)

    for u in unions:
        reward = ConfigUnionExploreRankReward.get_by_rank(u.rank)
        if not reward:
            continue

        attachment = ResourceClassification.classify(reward.reward).to_json()
        docs = MongoUnionMember.db(server_id).find(
            {'joined': u.id},
            {'_id': 1}
        )

        for doc in docs:
            m = MailManager(server_id, doc['_id'])
            m.add(reward.mail_title, reward.mail_content, attachment=attachment)
