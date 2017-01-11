# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       times_log
Date Created:   2016-04-21 15-04
Description:

"""

import arrow

from core.mongo import MongoTimesLog
from core.signals import task_condition_trig_signal
from utils.functional import make_string_id, get_start_time_of_today

KEEP_DAYS = 100


class ValueLog(object):
    KEY = None
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    @classmethod
    def clean(cls, server_id):
        now = arrow.utcnow().replace(days=-KEEP_DAYS)
        MongoTimesLog.db(server_id).delete_many({'timestamp': {'$lte': now.timestamp}})

    def make_key(self, sub_id=None):
        # sub_id 是给大类用的， 比如关卡ID
        if not sub_id:
            return "{0}:{1}".format(self.KEY, self.char_id)
        return "{0}:{1}:{2}".format(self.KEY, self.char_id, sub_id)

    def record(self, sub_id=None, value=1):
        doc = MongoTimesLog.document()
        doc['_id'] = make_string_id()
        doc['key'] = self.make_key(sub_id=sub_id)
        doc['timestamp'] = arrow.utcnow().timestamp
        doc['value'] = value

        MongoTimesLog.db(self.server_id).insert_one(doc)

        # task trig
        condition_name = 'core.value_log.{0}'.format(self.__class__.__name__)
        task_condition_trig_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            condition_name=condition_name
        )

    def count_of_today(self, sub_id=None):
        # 今天多少次
        today = get_start_time_of_today()
        tomorrow = today.replace(days=1)
        return self.count(sub_id=sub_id, start_at=today.timestamp, end_at=tomorrow.timestamp)

    def count(self, sub_id=None, start_at=None, end_at=None):
        # 一共多少次
        condition = [{'key': self.make_key(sub_id=sub_id)}]
        if start_at:
            condition.append({'timestamp': {'$gte': start_at}})
        if end_at:
            condition.append({'timestamp': {'$lte': end_at}})

        docs = MongoTimesLog.db(self.server_id).find({'$and': condition}, {'value': 1})

        value = 0
        for d in docs:
            value += d['value']

        return value


class CategoryValueLog(ValueLog):
    __slots__ = []

    def batch_count_of_today(self):
        """

        :rtype: dict[str, int]
        """
        today = get_start_time_of_today()
        tomorrow = today.replace(days=1)
        return self.batch_count(start_at=today.timestamp, end_at=tomorrow.timestamp)

    def batch_count(self, start_at=None, end_at=None):
        """

        :rtype: dict[str, int]
        """
        key_pattern = '^{0}:'.format(self.make_key())
        condition = [{'key': {'$regex': key_pattern}}]

        if start_at:
            condition.append({'timestamp': {'$gte': start_at}})
        if end_at:
            condition.append({'timestamp': {'$lte': end_at}})

        docs = MongoTimesLog.db(self.server_id).find({'$and': condition})
        counts = {}
        for d in docs:
            _, _id = d['key'].rsplit(':', 1)
            if _id in counts:
                counts[_id] += d['value']
            else:
                counts[_id] = d['value']

        return counts

    def count_of_today(self, sub_id=None):
        if sub_id is not None:
            return super(CategoryValueLog, self).count_of_today(sub_id=sub_id)

        counts = self.batch_count_of_today()
        return sum(counts.values())

    def count(self, sub_id=None, start_at=None, end_at=None):
        if sub_id is not None:
            return super(CategoryValueLog, self).count(sub_id=sub_id, start_at=start_at, end_at=end_at)

        counts = self.batch_count(start_at=start_at, end_at=end_at)
        return sum(counts.values())


# 抽卡次数
class ValueLogStaffRecruitTimes(CategoryValueLog):
    KEY = 'staff_recruit_times'
    __slots__ = []


# 抽卡获得积分
class ValueLogStaffRecruitScore(CategoryValueLog):
    KEY = 'staff_recruit_score'
    __slots__ = []


# 抽卡金币 免费 次数
class ValueLogStaffRecruitGoldFreeTimes(ValueLog):
    KEY = 'staff_recruit_gold_free_times'
    __slots__ = []


# 金币抽卡次数
class ValueLogStaffRecruitGoldTimes(ValueLog):
    KEY = 'staff_recruit_gold_times'
    __slots__ = []


# 钻石抽卡次数
class ValueLogStaffRecruitDiamondTimes(ValueLog):
    KEY = 'staff_recruit_diamond_times'
    __slots__ = []


# 挑战赛关卡次数 (单个)
class ValueLogChallengeMatchTimes(CategoryValueLog):
    KEY = 'challenge_match'
    __slots__ = []


# 挑战赛关卡重置次数 (单个)
class ValueLogChallengeResetTimes(CategoryValueLog):
    KEY = 'challenge_reset'
    __slots__ = []


# 所有挑战赛胜利次数
class ValueLogAllChallengeWinTimes(ValueLog):
    KEY = 'all_challenge_win'
    __slots__ = []


# 日常副本 胜利次数 (大类)
class ValueLogDungeonMatchTimes(CategoryValueLog):
    KEY = 'dungeon_match'
    __slots__ = []


# 日常副本购买次数 (大类)
class ValueLogDungeonBuyTimes(CategoryValueLog):
    KEY = 'dungeon_buy_times'
    __slots__ = []


# 竞技场挑战次数
class ValueLogArenaMatchTimes(ValueLog):
    KEY = 'arena_match'
    __slots__ = []


# 竞技场胜利次数
class ValueLogArenaWinTimes(ValueLog):
    KEY = 'arena_win'
    __slots__ = []


# 竞技场购买次数
class ValueLogArenaBuyTimes(ValueLog):
    KEY = 'arena_buy'
    __slots__ = []


# 竞技场搜索重置次数
class ValueLogArenaSearchResetTimes(ValueLog):
    KEY = 'arena_search_reset'
    __slots__ = []


# 竞技场荣耀点
class ValueLogArenaHonorPoints(ValueLog):
    KEY = 'arena_honor'
    __slots__ = []


# 训练塔胜利次数
class ValueLogTowerWinTimes(ValueLog):
    KEY = 'tower_win'
    __slots__ = []


# 训练塔重置次数
class ValueLogTowerResetTimes(ValueLog):
    KEY = 'tower_reset'
    __slots__ = []


# 领地训练次数
class ValueLogTerritoryTrainingTimes(ValueLog):
    KEY = 'territory_training'
    __slots__ = []


# 领地帮助好友次数
class ValueLogTerritoryHelpFriendTimes(ValueLog):
    KEY = 'territory_help_friend'
    __slots__ = []


# 领地 被帮助 次数
class ValueLogTerritoryGotHelpTimes(ValueLog):
    KEY = 'territory_got_help'
    __slots__ = []


# 领地建筑鼓舞次数
class ValueLogTerritoryBuildingInspireTimes(CategoryValueLog):
    KEY = 'territory_building_inspire'
    __slots__ = []


# 领地商店购买次数
class ValueLogTerritoryStoreBuyTimes(CategoryValueLog):
    KEY = 'territory_store'
    __slots__ = []


# 商店刷新次数
class ValueLogStoreRefreshTimes(CategoryValueLog):
    KEY = 'store_refresh'
    __slots__ = []


# 装备强化次数
class ValueLogEquipmentLevelUpTimes(ValueLog):
    KEY = 'equipment_level_up'
    __slots__ = []


# 选手升星次数
class ValueLogStaffStarUpTimes(ValueLog):
    KEY = 'staff_star_up'
    __slots__ = []


# 选手升级次数
class ValueLogStaffLevelUpTimes(ValueLog):
    KEY = 'staff_level_up'
    __slots__ = []


# 兵种升级次数
class ValueLogUnitLevelUpTimes(ValueLog):
    KEY = 'unit_level_up'
    __slots__ = []


# 体力购买次数
class ValueLogEnergyBuyTimes(ValueLog):
    KEY = 'energy_buy'
    __slots__ = []


# 福利签到
class ValueLogWelfareSignInTimes(ValueLog):
    KEY = 'welfare_signin'
    __slots__ = []


# 福利体力领取
class ValueLogWelfareEnergyRewardTimes(CategoryValueLog):
    KEY = 'welfare_energy'
    __slots__ = []


# 公会每日签到
class ValueLogUnionSignInTimes(CategoryValueLog):
    KEY = 'union_signin'
    __slots__ = []

# 掠夺次数
class ValueLogPlunderTimes(ValueLog):
    KEY = 'plunder_times'
    __slots__ = []

# 掠夺购买次数
class ValueLogPlunderBuyTimes(ValueLog):
    KEY = 'plunder_buy_times'
    __slots__ = []

# 掠夺复仇次数
class ValueLogPlunderRevengeTimes(ValueLog):
    KEY = 'plunder_revenge_times'
    __slots__ = []

# 打造特殊装备
class ValueLogSpecialEquipmentGenerateTimes(ValueLog):
    KEY = 'special_equipment_generate'
    __slots__ = []

# 创建宴会次数
class ValueLogPartyCreateTimes(ValueLog):
    KEY = 'party_create_times'
    __slots__ = []

# 加入宴会次数
class ValueLogPartyJoinTimes(ValueLog):
    KEY = 'party_join_times'
    __slots__ = []

# 参与宴会次数, 不管创建还是加入
class ValueLogPartyEngageTimes(ValueLog):
    KEY = 'party_engage_times'
    __slots__ = []

# 公会探索次数
class ValueLogUnionExploreTimes(ValueLog):
    KEY = 'union_explore_times'
    __slots__ = []

# 公会骚扰次数
class ValueLogUnionHarassTimes(ValueLog):
    KEY = 'union_harass_times'
    __slots__ = []

# 公会骚扰购买次数
class ValueLogUnionHarassBuyTimes(ValueLog):
    KEY = 'union_harass_buy_times'
    __slots__ = []
