# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2016-08-05 15:21
Description:

"""

import arrow
from dianjing.exception import GameException

from core.mongo import (
    MongoActivityNewPlayer,
    MongoActivityOnlineTime,
    MongoActivityChallenge,
    MongoActivityPurchaseDailyCount,
    MongoActivityPurchaseContinues,
    MongoActivityLevelGrowing,
)

from core.club import Club, get_club_property
from core.resource import ResourceClassification, money_text_to_item_id
from core.purchase import Purchase
from core.vip import VIP

from utils.message import MessagePipe
from utils.functional import get_start_time_of_today

from config import (
    GlobalConfig,
    ConfigItemUse,
    ConfigErrorMessage,
    ConfigActivityNewPlayer,
    ConfigActivityDailyBuy,
    ConfigTaskCondition,
    ConfigActivityOnlineTime,
    ConfigActivityChallenge,
    ConfigActivityLevelGrowing,
    ConfigActivityPurchaseContinues,
)

from protomsg.activity_pb2 import (
    ACTIVITY_COMPLETE,
    ACTIVITY_DOING,
    ACTIVITY_REWARD,
    ActivityNewPlayerDailyBuyNotify,
    ActivityNewPlayerNotify,
    ActivityOnlineTimeNotify,
    ActivityChallengeNotify,
    ActivityPurchaseDailyNotify,
    ActivityPurchaseContinuesNotify,
    ActivityLevelGrowingNotify,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class ActivityNewPlayer(object):
    __slots__ = ['server_id', 'char_id', 'doc', 'create_day', 'create_start_date', 'activity_end_at', 'reward_end_at']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityNewPlayer.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityNewPlayer.document()
            self.doc['_id'] = self.char_id
            MongoActivityNewPlayer.db(self.server_id).insert_one(self.doc)

        self.create_day = Club.create_days(server_id, char_id)

        today = get_start_time_of_today()
        self.create_start_date = today.replace(days=-(self.create_day - 1))

        self.activity_end_at = self.create_start_date.replace(days=7).timestamp
        self.reward_end_at = self.create_start_date.replace(days=8).timestamp

    def get_activity_status(self, _id):
        """

        :rtype: (int, int)
        """
        config = ConfigActivityNewPlayer.get(_id)

        # NOTE 新手活动是 活动开始的那一天，到第7天结束
        # 而不是 建立账号就开始算

        start_at = self.create_start_date.replace(days=config.day - 1).timestamp

        config_condition = ConfigTaskCondition.get(config.condition_id)
        value = config_condition.get_value(self.server_id, self.char_id, start_at=start_at, end_at=self.activity_end_at)

        if _id in self.doc['done']:
            return value, ACTIVITY_COMPLETE

        if config_condition.compare_value(self.server_id, self.char_id, value, config.condition_value):
            return value, ACTIVITY_REWARD

        return value, ACTIVITY_DOING

    def trig(self, condition_id):
        if arrow.utcnow().timestamp >= self.activity_end_at:
            return

        ids = ConfigActivityNewPlayer.get_activity_ids_by_condition_id(condition_id)
        if not ids:
            return

        self.send_notify(ids=ids)

    def get_reward(self, _id):
        if arrow.utcnow().timestamp >= self.reward_end_at:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_REWARD_EXPIRE"))

        config = ConfigActivityNewPlayer.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if config.day > self.create_day:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_DAY_NOT_ARRIVE"))

        _, status = self.get_activity_status(_id)
        if status == ACTIVITY_COMPLETE:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_HAS_GOT"))

        if status == ACTIVITY_DOING:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_CONDITION_NOT_SATISFY"))

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id, message="ActivityNewPlayer.get_reward:{0}".format(_id))

        self.doc['done'].append(_id)
        MongoActivityNewPlayer.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'done': _id
            }}
        )

        self.send_notify(ids=[_id])

        return rc

    def daily_buy(self):
        config = ConfigActivityDailyBuy.get(self.create_day)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if self.create_day in self.doc['daily_buy']:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_DAILY_BUY_HAS_BOUGHT"))

        cost = [(money_text_to_item_id('diamond'), config.diamond_now), ]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="ActivityNewPlayer.daily_buy")

        rc = ResourceClassification.classify(config.items)
        rc.add(self.server_id, self.char_id, message="ActivityNewPlayer.daily_buy")

        self.doc['daily_buy'].append(self.create_day)
        MongoActivityNewPlayer.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'daily_buy': self.create_day
            }}
        )

        self.send_daily_buy_notify()
        return rc

    def send_daily_buy_notify(self):
        if arrow.utcnow().timestamp >= self.reward_end_at:
            return

        notify = ActivityNewPlayerDailyBuyNotify()
        for i in range(1, self.create_day + 1):
            notify_status = notify.status.add()
            notify_status.day = i
            notify_status.has_bought = i in self.doc['daily_buy']

        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        if arrow.utcnow().timestamp >= self.reward_end_at:
            return

        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigActivityNewPlayer.INSTANCES.keys()

        notify = ActivityNewPlayerNotify()
        notify.act = act
        for i in ids:
            # 后面天数的情况不发
            if ConfigActivityNewPlayer.get(i).day > self.create_day:
                continue

            value, status = self.get_activity_status(i)

            notify_items = notify.items.add()
            notify_items.id = i
            notify_items.current_value = value
            notify_items.status = status

        notify.activity_end_at = self.activity_end_at
        notify.reward_end_at = self.reward_end_at

        MessagePipe(self.char_id).put(msg=notify)


class ActivityOnlineTime(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityOnlineTime.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityOnlineTime.document()
            self.doc['_id'] = self.char_id
            self.doc['doing'] = ConfigActivityOnlineTime.MIN_ID
            MongoActivityOnlineTime.db(self.server_id).insert_one(self.doc)

    def get_reward(self):
        if not self.doc['doing']:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        config = ConfigActivityOnlineTime.get(self.doc['doing'])
        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)

        next_id = ConfigActivityOnlineTime.find_next_id(self.doc['doing'])
        self.doc['doing'] = next_id
        MongoActivityOnlineTime.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'doing': next_id
            }}
        )

        self.send_notify()
        return rc

    def send_notify(self):
        notify = ActivityOnlineTimeNotify()
        notify.id = self.doc['doing']
        MessagePipe(self.char_id).put(msg=notify)


class ActivityChallenge(object):
    __slots__ = ['server_id', 'char_id', 'doc', 'passed_challenge_ids']

    def __init__(self, server_id, char_id, passed_challenge_ids=None):
        from core.challenge import Challenge

        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityChallenge.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityChallenge.document()
            self.doc['_id'] = self.char_id
            self.doc['done'] = []
            MongoActivityChallenge.db(self.server_id).insert_one(self.doc)

        self.passed_challenge_ids = passed_challenge_ids
        if not self.passed_challenge_ids:
            self.passed_challenge_ids = Challenge(self.server_id, self.char_id).get_passed_challenge_ids()

    def trig_notify(self, passed_id):
        if passed_id in self.doc['done']:
            return

        if passed_id not in ConfigActivityChallenge.INSTANCES.keys():
            return

        self.send_notify(passed_id)

    def get_reward(self, _id):
        config = ConfigActivityChallenge.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if self.get_status(_id) != ACTIVITY_REWARD:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)

        self.doc['done'].append(_id)
        MongoActivityChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'done': _id,
            }}
        )

        self.send_notify(_id)
        return rc

    def get_status(self, _id):
        if _id in self.doc['done']:
            return ACTIVITY_COMPLETE

        if _id in self.passed_challenge_ids:
            return ACTIVITY_REWARD

        return ACTIVITY_DOING

    def send_notify(self, _id=None):
        if not _id:
            act = ACT_INIT
            ids = ConfigActivityChallenge.INSTANCES.keys()
        else:
            act = ACT_UPDATE
            ids = [_id]

        notify = ActivityChallengeNotify()
        notify.act = act
        for i in ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.status = self.get_status(i)

        MessagePipe(self.char_id).put(msg=notify)


class ActivityPurchaseDaily(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityPurchaseDailyCount.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityPurchaseDailyCount.document()
            self.doc['_id'] = self.char_id
            MongoActivityPurchaseDailyCount.db(self.server_id).insert_one(self.doc)

    def add_count(self, count=1):
        self.doc['count'] += count
        MongoActivityPurchaseDailyCount.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'count': count
            }}
        )
        self.send_notify()

    def get_reward(self):
        if self.doc['count'] < 1:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        self.add_count(-1)

        item_id = GlobalConfig.value("PURCHASE_DAILY_REWARD_ITEM_ID")
        rc = ResourceClassification.classify(ConfigItemUse.get(item_id).using_result())
        rc.add(self.server_id, self.char_id)
        return rc

    def send_notify(self):
        notify = ActivityPurchaseDailyNotify()
        if self.doc['count'] > 0:
            status = ACTIVITY_REWARD
        else:
            if Purchase(self.server_id, self.char_id).get_purchase_info_of_day_shift():
                status = ACTIVITY_COMPLETE
            else:
                status = ACTIVITY_DOING

        notify.status = status
        item_id = GlobalConfig.value("PURCHASE_DAILY_REWARD_ITEM_ID")
        rc = ResourceClassification.classify(ConfigItemUse.get(item_id).using_result())
        notify.items.MergeFrom(rc.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)


class ActivityPurchaseContinues(object):
    __slots__ = ['server_id', 'char_id', 'doc', 'create_days']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityPurchaseContinues.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityPurchaseContinues.document()
            self.doc['_id'] = self.char_id
            MongoActivityPurchaseContinues.db(self.server_id).insert_one(self.doc)

        self.create_days = Club.create_days(self.server_id, self.char_id)

    def record(self, day=None):
        if not day:
            day = self.create_days

        if day not in ConfigActivityPurchaseContinues.INSTANCES:
            return

        if str(day) in self.doc['record']:
            return

        self.doc['record'][str(day)] = 0
        MongoActivityPurchaseContinues.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'record.{0}'.format(day): 0
            }}
        )

        self.send_notify(day)

    def get_reward(self, _id):
        config = ConfigActivityPurchaseContinues.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        status = self.get_status(_id)
        if status != ACTIVITY_REWARD:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        self.doc['record'][str(_id)] = 1
        MongoActivityPurchaseContinues.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'record.{0}'.format(_id): 1
            }}
        )

        self.send_notify(_id)

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)
        return rc

    def get_status(self, _id):
        if _id == 0:
            if str(_id) in self.doc['record']:
                return ACTIVITY_COMPLETE

            if len(self.doc['record']) < 7:
                return ACTIVITY_DOING

            return ACTIVITY_REWARD

        value = self.doc['record'].get(str(_id), -1)
        if value == -1:
            return ACTIVITY_DOING
        if value == 0:
            return ACTIVITY_REWARD
        if value == 1:
            return ACTIVITY_COMPLETE

    def send_notify(self, _id=None):
        if _id:
            ids = [0, _id]
            act = ACT_UPDATE
        else:
            ids = ConfigActivityPurchaseContinues.INSTANCES.keys()
            act = ACT_INIT

        notify = ActivityPurchaseContinuesNotify()
        notify.act = act
        for i in ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.status = self.get_status(i)

        MessagePipe(self.char_id).put(msg=notify)


class ActivityLevelGrowing(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityLevelGrowing.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityLevelGrowing.document()
            self.doc['_id'] = self.char_id
            self.doc['joined'] = False
            MongoActivityLevelGrowing.db(self.server_id).insert_one(self.doc)

    def join(self):
        if self.doc['joined']:
            return

        diamond = GlobalConfig.value("LEVEL_GROWING_ACTIVITY_JOIN_COST_DIAMOND")
        vip_need = GlobalConfig.value("LEVEL_GROWING_ACTIVITY_JOIN_VIP_LIMIT")

        VIP(self.server_id, self.char_id).check(vip_need)

        cost = [(money_text_to_item_id('diamond'), diamond), ]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        current_level = get_club_property(self.server_id, self.char_id, 'level')
        self._update(current_level, joined=True)
        self.send_notify()

    def record(self, level):
        if not self.doc['joined']:
            return

        ids = self._update(level)
        if ids:
            self.send_notify(ids)

    def _update(self, level, joined=None):
        updater = {}
        new_ids = []

        for i in ConfigActivityLevelGrowing.INSTANCES.keys():
            if str(i) in self.doc['levels']:
                continue

            if level >= i:
                self.doc['levels'][str(i)] = 0
                updater['levels.{0}'.format(i)] = 0
                new_ids.append(i)

        if joined is not None:
            self.doc['joined'] = joined
            updater['joined'] = joined

        if updater:
            MongoActivityLevelGrowing.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

        return new_ids

    def get_reward(self, _id):
        config = ConfigActivityLevelGrowing.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        status = self.get_status(_id)
        if status != ACTIVITY_REWARD:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)

        self.doc['levels'][str(_id)] = 1
        MongoActivityLevelGrowing.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels.{0}'.format(_id): 1
            }}
        )

        self.send_notify(_id)
        return rc

    def get_status(self, _id):
        value = self.doc['levels'].get(str(_id), -1)
        if value == -1:
            return ACTIVITY_DOING
        if value == 0:
            return ACTIVITY_REWARD
        if value == 1:
            return ACTIVITY_COMPLETE

    def send_notify(self, _id=None):
        if _id:
            if isinstance(_id, (list, tuple)):
                ids = _id
            else:
                ids = [_id]
            act = ACT_UPDATE
        else:
            ids = ConfigActivityLevelGrowing.INSTANCES.keys()
            act = ACT_INIT

        notify = ActivityLevelGrowingNotify()
        notify.act = act
        notify.has_joined = self.doc['joined']

        for i in ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.status = self.get_status(i)

        MessagePipe(self.char_id).put(msg=notify)
