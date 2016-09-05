# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-05 15-46
Description:

"""
import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoTower
from core.club import Club, get_club_property
from core.match import ClubMatch
from core.resource import ResourceClassification, money_text_to_item_id
from core.value_log import ValueLogTowerResetTimes, ValueLogTowerWinTimes
from core.vip import VIP
from core.mail import MailManager
from core.formation import Formation
from core.signals import task_condition_trig_signal

from utils.message import MessagePipe

from config import (
    ConfigTowerLevel,
    ConfigErrorMessage,
    ConfigTowerResetCost,
    GlobalConfig,
    ConfigTowerSaleGoods,
    ConfigTowerRankReward,
)

from protomsg.tower_pb2 import (
    TowerNotify,
    TowerGoodsNotify,
    TOWER_LEVEL_CURRENT,
    TOWER_LEVEL_FAILURE,
    TOWER_LEVEL_NOT_OPEN,
    TOWER_LEVEL_PASSED,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

MAX_LEVEL = max(ConfigTowerLevel.INSTANCES.keys())


def get_tower_talent_effects(server_id, char_id):
    # 这里单独提供一个方法是为了 统一处理的时候
    # 如果用了 Tower 这个类， NPC也会给创建记录
    doc = MongoTower.db(server_id).find_one({'_id': char_id}, {'talents': 1})
    if not doc:
        return []

    return doc.get('talents', [])


class ResetInfo(object):
    __slots__ = ['reset_times', 'remained_times', 'reset_cost']

    def __init__(self, server_id, char_id):
        self.reset_times = ValueLogTowerResetTimes(server_id, char_id).count_of_today()
        self.remained_times = VIP(server_id, char_id).tower_reset_times - self.reset_times
        if self.remained_times < 0:
            self.remained_times = 0

        self.reset_cost = ConfigTowerResetCost.get_cost(self.reset_times + 1)


class Tower(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoTower.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoTower.document()
            self.doc['_id'] = self.char_id
            self.doc['levels'] = {'1': 0}
            MongoTower.db(self.server_id).insert_one(self.doc)

    @classmethod
    def send_rank_reward_and_reset_star(cls, server_id):
        char_ids = Club.get_recent_login_char_ids(server_id)
        char_ids = [i for i in char_ids]

        condition = {'$and': [
            {'_id': {'$in': char_ids}},
            {'today_max_star': {'$ne': 0}}
        ]}
        docs = MongoTower.db(server_id).find(condition, {'_id': 1}).sort('today_max_star', -1)

        rank = 1
        for doc in docs:
            cid = doc['_id']

            config = ConfigTowerRankReward.get(rank)

            rc = ResourceClassification.classify(config.reward)

            m = MailManager(server_id, cid)
            m.add(
                config.mail_title,
                config.mail_content,
                attachment=rc.to_json(),
            )

            rank += 1

        # reset today max star
        MongoTower.db(server_id).update_many(
            {},
            {'$set': {
                'today_max_star': 0,
            }}
        )

    def talent_effects(self):
        return self.doc['talents']

    def check_history_max_star(self, star):
        if star > self.doc['history_max_star']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_HISTORY_MAX_STAR_CHECK_FAILURE"))

    def get_today_rank(self):
        # XXX
        if not self.doc['today_max_star']:
            return 0

        doc = MongoTower.db(self.server_id).find({'today_max_star': {'$gt': self.doc['today_max_star']}})
        return doc.count() + 1

    def get_current_level(self):
        for k, v in self.doc['levels'].iteritems():
            if v == 0:
                return int(k)

        return 0

    def get_history_max_level(self):
        return self.doc.get('history_max_level', 0)

    def get_total_current_star(self):
        # 获得本阶段总星数
        star = 0
        for v in self.doc['levels'].values():
            if v > 0:
                star += v

        return star

    def is_all_complete(self):
        # 0　表示可以打，　-1 表示失败，　不能打的没有记录，　这里就用-2表示
        return self.doc['levels'].get(str(MAX_LEVEL), -2) > 0

    def set_today_max_star(self):
        # 今天重置后的最高星数，
        # 不重置还不算！！！
        # 这里不能直接 $set， 得用 $inc
        # 因为有定时任务在 直接清零
        # NOTE: 因为用了 sef.doc 的数据，必须在 设置完后 才能调用
        # NOTE: 还要判断是不是当天创建的新角色，新角色就算没重置也得记录啊啊啊
        if Club.create_days(self.server_id, self.char_id) > 1:
            ri = ResetInfo(self.server_id, self.char_id)
            if not ri.reset_times:
                # 只有当天重置过的，才记录当天最高星数
                return

        inc_value = self.get_total_current_star() - self.doc['today_max_star']
        if inc_value <= 0:
            return

        self.doc['today_max_star'] += inc_value
        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'today_max_star': inc_value
            }}
        )

    def match(self, formation_slots=None):
        sweep_end_at = self.doc.get('sweep_end_at', 0)
        if sweep_end_at:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_IN_SWEEP_CANNOT_OPERATE"))

        level = self.get_current_level()
        if not level:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_ALREADY_ALL_PASSED"))

        if formation_slots:
            Formation(self.server_id, self.char_id).sync_slots(formation_slots)

        config = ConfigTowerLevel.get(level)

        club_one = Club(self.server_id, self.char_id)
        if config.talent_id:
            club_one.add_talent_effects([config.talent_id])

        club_two = config.make_club()

        if not club_one.formation_staffs:
            club_one.load_staffs()
        if not club_two.formation_staffs:
            club_two.load_staffs()

        club_one.add_tower_temporary_talent_effects()
        club_two.add_tower_temporary_talent_effects()

        club_match = ClubMatch(club_one, club_two)
        msg = club_match.start()
        msg.key = str(level)
        return msg

    def report(self, key, star):
        sweep_end_at = self.doc.get('sweep_end_at', 0)
        if sweep_end_at:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_IN_SWEEP_CANNOT_OPERATE"))

        if star not in [0, 1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        level = int(key)
        config = ConfigTowerLevel.get(level)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        update_levels = [level]
        self.doc['current_star'] += star

        updater = {
            'current_star': self.doc['current_star']
        }

        if star == 0:
            # 输了
            # NOTE 坑
            self.doc['levels'][str(level)] = -1

            updater['levels.{0}'.format(level)] = -1
            updater['turntable'] = {}
            all_list = []
            goods = []

            resource_classified = ResourceClassification.classify([])
        else:
            self.doc['levels'][str(level)] = star
            updater['levels.{0}'.format(level)] = star

            # 开启下一关
            if level < MAX_LEVEL:
                next_level = level + 1
                self.doc['levels'][str(next_level)] = 0

                update_levels.append(next_level)
                updater['levels.{0}'.format(next_level)] = 0

            # 记录连续最大三星
            if star == 3 and level == self.doc['max_star_level'] + 1:
                self.doc['max_star_level'] = level
                updater['max_star_level'] = level

            # 记录最高层
            if level > self.get_history_max_level():
                self.doc['history_max_level'] = level
                updater['history_max_level'] = level

            # 转盘信息
            turntable = config.get_turntable()
            if turntable:
                all_list = []
                for _, v in turntable.iteritems():
                    all_list.extend(v)

                random.shuffle(all_list)

                turntable['all_list'] = all_list
                updater['turntable'] = turntable
            else:
                all_list = []
                updater['turntable'] = {}

            # 是否有商品可购买
            goods = config.get_sale_goods()
            if goods:
                self.doc['goods'].append([goods[0], 0])
                self.doc['goods'].append([goods[1], 0])

                updater['goods'] = self.doc['goods']

            resource_classified = ResourceClassification.classify(config.get_star_reward(star))
            resource_classified.add(self.server_id, self.char_id)

            ValueLogTowerWinTimes(self.server_id, self.char_id).record()

        self.set_today_max_star()
        total_star = self.get_total_current_star()
        if total_star > self.doc['history_max_star']:
            self.doc['history_max_star'] = total_star
            updater['history_max_star'] = total_star

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(act=ACT_UPDATE, levels=update_levels)
        if goods:
            self.send_goods_notify()

        if 'history_max_level' in updater:
            task_condition_trig_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                condition_name='core.tower.Tower'
            )

        return resource_classified, self.doc['current_star'], all_list, bool(goods)

    def reset(self):
        sweep_end_at = self.doc.get('sweep_end_at', 0)
        if sweep_end_at:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_IN_SWEEP_CANNOT_OPERATE"))

        ri = ResetInfo(self.server_id, self.char_id)
        if not ri.remained_times:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_NO_RESET_TIMES"))

        if -1 not in self.doc['levels'].values():
            # 没有失败的， 看看是不是全部完成了
            if not self.is_all_complete():
                raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_RESET_NO_FAILURE"))

        if ri.reset_cost:
            cost = [(money_text_to_item_id('diamond'), ri.reset_cost)]
            resource_classified = ResourceClassification.classify(cost)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

        self.doc['levels'] = {'1': 0}
        self.doc['talents'] = []
        self.doc['current_star'] = 0
        self.doc['turntable'] = {}
        self.doc['goods'] = []

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels': self.doc['levels'],
                'talents': self.doc['talents'],
                'current_star': self.doc['current_star'],
                'turntable': {},
                'goods': [],
            }}
        )

        ValueLogTowerResetTimes(self.server_id, self.char_id).record()
        self.send_notify()
        self.send_goods_notify()

    def _sweep_check(self):
        if not self.doc['max_star_level']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_NO_MAX_STAR_LEVEL"))

        if -1 in self.doc['levels'].values():
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_TO_MAX_LEVEL_HAS_FAILURE"))

        levels_amount = self.doc['max_star_level'] - self.get_current_level()
        if levels_amount <= 0:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CURRENT_LEVEL_GREAT_THAN_MAX_STAR_LEVEL"))

        return levels_amount

    def sweep(self):
        sweep_end_at = self.doc.get('sweep_end_at', 0)
        if sweep_end_at:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_ALREADY_IN_SWEEP"))

        levels_amount = self._sweep_check()
        end_at = arrow.utcnow().timestamp + levels_amount * GlobalConfig.value("TOWER_SWEEP_SECONDS_PER_LEVEL")

        self.doc['sweep_end_at'] = end_at
        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'sweep_end_at': end_at
            }}
        )

        ValueLogTowerWinTimes(self.server_id, self.char_id).record(value=levels_amount)
        self.send_notify(act=ACT_UPDATE, levels=[])

    def sweep_finish(self):
        # 加速或者领奖 都是这一个协议

        start_level = self.get_current_level()
        sweep_end_at = self.doc.get('sweep_end_at', 0)
        if sweep_end_at == 0:
            # 没有扫荡过，直接 完成
            levels_amount = self._sweep_check()
        else:
            # 已经扫荡了， 现在要加速完成
            need_seconds = sweep_end_at - arrow.utcnow().timestamp
            if need_seconds <= 0:
                # 已经完成了， 直接领奖
                levels_amount = 0
            else:
                levels_amount, _remained = divmod(need_seconds, GlobalConfig.value("TOWER_SWEEP_SECONDS_PER_LEVEL"))
                if _remained:
                    levels_amount += 1

        if levels_amount:
            need_diamond = levels_amount * GlobalConfig.value("TOWER_SWEEP_DIAMOND_PER_LEVEL")
            resource_classified = ResourceClassification.classify([(money_text_to_item_id('diamond'), need_diamond)])
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

        drops = {}
        updater = {}
        for i in range(start_level, self.doc['max_star_level'] + 1):
            updater['levels.{0}'.format(i)] = 3
            self.doc['levels'][str(i)] = 3
            self.doc['current_star'] += 3

            config = ConfigTowerLevel.get(i)
            drop = config.get_star_reward(3)
            for _id, _amount in drop:
                if _id in drops:
                    drops[_id] += _amount
                else:
                    drops[_id] = _amount

            turntable = config.get_turntable()
            if turntable:
                if self.doc['current_star'] >= 9:
                    got = random.choice(turntable['9'])
                    self.doc['talents'].append(got)
                    self.doc['current_star'] -= 9

                elif self.doc['current_star'] >= 6:
                    got = random.choice(turntable['6'])
                    self.doc['talents'].append(got)
                    self.doc['current_star'] -= 6

                elif self.doc['current_star'] >= 3:
                    got = random.choice(turntable['3'])
                    self.doc['talents'].append(got)
                    self.doc['current_star'] -= 3

            goods = config.get_sale_goods()
            if goods:
                self.doc['goods'].append([goods[0], 0])
                self.doc['goods'].append([goods[1], 0])

        self.doc['sweep_end_at'] = 0
        updater['sweep_end_at'] = 0
        updater['current_star'] = self.doc['current_star']
        updater['talents'] = self.doc['talents']
        updater['goods'] = self.doc['goods']

        # 扫荡完下一关要可打
        next_level = self.doc['max_star_level'] + 1
        if next_level < MAX_LEVEL:
            self.doc['levels'][str(next_level)] = 0
            updater['levels.{0}'.format(next_level)] = 0

        self.set_today_max_star()

        total_star = self.get_total_current_star()
        if total_star > self.doc['history_max_star']:
            self.doc['history_max_star'] = total_star
            updater['history_max_star'] = total_star

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        resource_classified = ResourceClassification.classify(drops.items())
        resource_classified.add(self.server_id, self.char_id)

        self.send_notify(act=ACT_UPDATE)
        self.send_goods_notify()
        return resource_classified

    def turntable_pick(self, star):
        if star not in [3, 6, 9]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if star > self.doc['current_star']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_STAR_NOT_ENOUGH"))

        turntable = self.doc.get('turntable', {})
        if not turntable:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        got = random.choice(turntable[str(star)])
        index = turntable['all_list'].index(got)

        self.doc['current_star'] -= star
        self.doc['talents'].append(got)

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$set': {
                    'current_star': self.doc['current_star'],
                    'talents': self.doc['talents'],
                    'turntable': {},
                }
            }
        )

        self.send_notify(act=ACT_UPDATE, levels=[])
        return index

    def buy_goods(self, goods_index):
        goods = self.doc.get('goods', [])
        try:
            goods_id, bought = goods[goods_index]
        except IndexError:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if bought:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_GOODS_HAS_BOUGHT"))

        config = ConfigTowerSaleGoods.get(goods_id)

        if config.vip_need:
            VIP(self.server_id, self.char_id).check(config.vip_need)

        cost = [(money_text_to_item_id('diamond'), config.price_now)]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        got = [(config.item_id, config.amount)]
        rc = ResourceClassification.classify(got)
        rc.add(self.server_id, self.char_id)

        self.doc['goods'][goods_index][1] = 1

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'goods': self.doc['goods']
            }}
        )

        self.send_goods_notify()
        return rc

    def get_leader_board(self, amount=30):
        docs = MongoTower.db(self.server_id).find(
            {'today_max_star': {'$ne': 0}},
            {'today_max_star': 1}
        ).sort('today_max_star', -1).limit(amount)

        info = []
        for doc in docs:
            _id = doc['_id']
            name = get_club_property(self.server_id, _id, 'name')
            star = doc['today_max_star']

            info.append((_id, name, star))

        return info

    def send_notify(self, act=ACT_INIT, levels=None):
        notify = TowerNotify()
        notify.act = act
        notify.current_star = self.doc['current_star']
        notify.today_max_star = self.doc['today_max_star']
        notify.history_max_star = self.doc['history_max_star']
        notify.today_rank = self.get_today_rank()
        notify.talent_ids.extend(self.doc['talents'])

        notify.max_star_level = self.doc['max_star_level']
        notify.sweep_end_at = self.doc.get('sweep_end_at', 0)

        ri = ResetInfo(self.server_id, self.char_id)
        notify.reset_times = ri.remained_times
        notify.reset_cost = ri.reset_cost

        if levels is None:
            # 全部发送
            levels = ConfigTowerLevel.INSTANCES.keys()

        for lv in levels:
            notify_level = notify.levels.add()
            notify_level.level = int(lv)

            star = self.doc['levels'].get(str(lv), None)
            if star is None:
                notify_level.status = TOWER_LEVEL_NOT_OPEN
            elif star == -1:
                notify_level.status = TOWER_LEVEL_FAILURE
            elif star == 0:
                notify_level.status = TOWER_LEVEL_CURRENT
            else:
                notify_level.status = TOWER_LEVEL_PASSED
                notify_level.star = star

        MessagePipe(self.char_id).put(msg=notify)

    def send_goods_notify(self):
        notify = TowerGoodsNotify()
        goods = self.doc.get('goods', [])

        for i in range(0, len(goods) - 1, 2):
            id1, b1 = goods[i]
            id2, b2 = goods[i + 1]
            if b1 and b2:
                continue

            notify_goods = notify.goods.add()
            notify_goods.id = id1
            notify_goods.has_bought = b1

            notify_goods = notify.goods.add()
            notify_goods.id = id2
            notify_goods.has_bought = b2

        MessagePipe(self.char_id).put(msg=notify)
