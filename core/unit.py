# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2016-04-08 14:22
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractUnit
from core.mongo import MongoUnit
from core.club import Club, get_club_property
from core.resource import ResourceClassification, money_text_to_item_id
from core.value_log import ValueLogUnitLevelUpTimes
from core.signals import task_condition_trig_signal

from utils.message import MessagePipe

from config import GlobalConfig, ConfigErrorMessage, ConfigUnitUnLock, ConfigUnitAddition

from protomsg.unit_pb2 import UnitNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

UNIT_INIT_LEVEL = 1
UNIT_INIT_STEP = 0


class UnitAddition(object):
    __slots__ = [
        'hp_percent', 'attack_percent', 'defense_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',
        'hurt_addition_to_terran', 'hurt_addition_to_protoss', 'hurt_addition_to_zerg',
        'hurt_addition_by_terran', 'hurt_addition_by_protoss', 'hurt_addition_by_zerg',
    ]

    def __init__(self):
        self.hp_percent = 0
        self.attack_percent = 0
        self.defense_percent = 0
        self.hit_rate = 0
        self.dodge_rate = 0
        self.crit_rate = 0
        self.toughness_rate = 0
        self.crit_multiple = 0
        self.hurt_addition_to_terran = 0
        self.hurt_addition_to_protoss = 0
        self.hurt_addition_to_zerg = 0
        self.hurt_addition_by_terran = 0
        self.hurt_addition_by_protoss = 0
        self.hurt_addition_by_zerg = 0

    def add_property(self, attr, value):
        v = getattr(self, attr)
        v += value
        setattr(self, attr, v)


# 用于NPC的
class NPCUnit(AbstractUnit):
    __slots__ = []

    def __init__(self, _id, step, level):
        super(NPCUnit, self).__init__()
        self.id = _id
        self.step = step
        self.level = level
        self.after_init()
        self.calculate()


# 用于玩家的
class Unit(AbstractUnit):
    __slots__ = []

    def __init__(self, server_id, char_id, _id, data):
        super(Unit, self).__init__()
        self.server_id = server_id
        self.char_id = char_id
        self.id = _id
        self.step = data['step']
        self.level = data['level']
        self.after_init()

    def level_up(self, add_level):
        assert add_level > 0

        from core.club import get_club_property
        max_level = min(self.config.max_level, get_club_property(self.server_id, self.char_id, 'level') * 2)
        if self.level >= max_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_LEVEL"))

        old_level = self.level

        if add_level == 1:
            using_items = self.config.levels[self.level].update_item_need
            resource_classified = ResourceClassification.classify(using_items)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id, message="Unit.level_up:{0}".format(self.id))

            self.level += 1
        else:
            # 这里要反过来试，如果正向试的话， 可能需要试5次，此时有点慢
            # 反过来只对 只是升一两次的情况比较慢，但这种可以接受
            can_add_level = max_level - self.level
            if add_level > can_add_level:
                add_level = can_add_level

            def _try_up(_add):
                _using_items = []
                this_level = self.level

                for _ in range(_add):
                    items = self.config.levels[this_level].update_item_need
                    _using_items.extend(items)
                    this_level += 1

                rc = ResourceClassification.classify(_using_items)
                rc.check_exist(self.server_id, self.char_id)
                rc.remove(self.server_id, self.char_id, message="Unit.level_up:{0}".format(self.id))

            for i in range(add_level, 0, -1):
                try:
                    _try_up(i)
                except GameException as e:
                    if i == 1:
                        # 只升一级都报错
                        raise e
                else:
                    # 没有raise GameException 资源是够的
                    self.level += i
                    break

        if self.level != old_level:
            MongoUnit.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'units.{0}.level'.format(self.id): self.level
                }}
            )

        # 升级可能会导致其他的unit属性改变（加成）
        # 所以在UnitManage 里统一load一次unit
        return self.level - old_level

    def step_up(self):
        if self.step >= self.config.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_STEP"))

        if self.level < self.config.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_LEVEL_NOT_ENOUGH"))

        using_items = self.config.steps[self.step].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id, message="Unit.step_up:{0}".format(self.id))

        self.step += 1

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'units.{0}.step'.format(self.id): self.step
            }}
        )

    def get_strengthen_cost(self):
        items = {}
        # 升级消耗
        for i in range(self.level-1, UNIT_INIT_LEVEL-1, -1):
            for _id, _amount in self.config.levels[i].update_item_need:
                if _id not in items:
                    items[_id] = _amount
                else:
                    items[_id] += _amount

        # 升阶消耗
        for i in range(self.step-1, UNIT_INIT_STEP-1, -1):
            for _id, _amount in self.config.steps[i].update_item_need:
                if _id not in items:
                    items[_id] = _amount
                else:
                    items[_id] += _amount

        return items.items()

    def destroy(self, using_sycee):
        if self.level == UNIT_INIT_LEVEL and self.step == UNIT_INIT_STEP:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_IS_INIT_CANNOT_DESTROY"))

        if using_sycee:
            need_diamond = GlobalConfig.value("UNIT_DESTROY_SYCEE")
            cost = [(money_text_to_item_id('diamond'), need_diamond), ]
            rc = ResourceClassification.classify(cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id, message="Unit.destroy:{0}".format(self.id))

            percent = 1
        else:
            percent = 0.7

        items = self.get_strengthen_cost()
        items = [(_id, int(_amount * percent)) for _id, _amount in items]
        rc = ResourceClassification.classify(items)
        rc.add(self.server_id, self.char_id, message="Unit.destroy:{0}".format(self.id))

        self.level = UNIT_INIT_LEVEL
        self.step = UNIT_INIT_STEP

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'units.{0}.level'.format(self.id): self.level,
                'units.{0}.step'.format(self.id): self.step,
            }}
        )

        return rc

    def send_notify(self):
        notify = UnitNotify()
        notify.act = ACT_UPDATE
        notify_unit = notify.units.add()
        notify_unit.MergeFrom(self.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)


class UnitManager(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoUnit.exist(self.server_id, self.char_id):
            doc = MongoUnit.document()
            doc['_id'] = self.char_id
            MongoUnit.db(self.server_id).insert_one(doc)

            self.try_unlock(send_notify=False)

    def try_unlock(self, send_notify=True):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units': 1}
        )

        unlocked_unit_ids = []

        club_level = get_club_property(self.server_id, self.char_id, 'level')
        for unit_id, config in ConfigUnitUnLock.INSTANCES.iteritems():
            if str(unit_id) in doc['units']:
                continue

            if config.need_club_level > club_level:
                continue

            condition_unit_level = True
            for _uid, _lv in config.need_unit_level:
                this_unit_level = doc['units'].get(str(_uid), {}).get('level', 0)
                if _lv > this_unit_level:
                    condition_unit_level = False
                    break

            if condition_unit_level:
                unlocked_unit_ids.append(unit_id)

        if not unlocked_unit_ids:
            return

        updater = {
            'units.{0}'.format(i): MongoUnit.document_unit() for i in unlocked_unit_ids
            }
        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        if send_notify:
            self.send_notify(ids=unlocked_unit_ids)

        self.after_units_change_for_trig_signal()

    def is_unit_unlocked(self, _id):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(_id): 1}
        )

        return str(_id) in doc['units']

    def check_unit_unlocked(self, _id):
        if not self.is_unit_unlocked(_id):
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_IS_UNLOCKED"))

    def get_units_data(self):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units': 1}
        )

        return {int(k): v for k, v in doc['units'].iteritems()}

    def after_units_change_for_trig_signal(self):
        task_condition_trig_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            condition_name='core.unit.UnitManager'
        )

    def get_all_units_step(self):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units': 1}
        )

        value = 0
        for k, v in doc['units'].iteritems():
            value += v['step']

        return value

    def get_all_units_level(self):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units': 1}
        )

        value = 0
        for k, v in doc['units'].iteritems():
            value += v['level']

        return value

    def load_units(self):
        from core.formation import Formation

        units = {}
        """:type: dict[int, Unit]"""

        doc = MongoUnit.db(self.server_id).find_one({'_id': self.char_id})
        for _id, _data in doc['units'].iteritems():
            u = Unit(self.server_id, self.char_id, int(_id), _data)
            u.calculate()
            u.make_cache()
            units[int(_id)] = u

        race = {
            1: {'level': 0, 'step': 0},
            2: {'level': 0, 'step': 0},
            3: {'level': 0, 'step': 0},
        }

        for _, u in units.iteritems():
            race[u.config.race]['level'] += u.level
            race[u.config.race]['step'] += u.step

        additions = {
            1: UnitAddition(),
            2: UnitAddition(),
            3: UnitAddition(),
        }

        for k, v in additions.iteritems():
            _level_addition = ConfigUnitAddition.get_level_addition(k, race[k]['level'])
            _step_addition = ConfigUnitAddition.get_step_addition(k, race[k]['step'])
            if _level_addition:
                for attr in UnitAddition.__slots__:
                    v.add_property(attr, getattr(_level_addition, attr))

            if _step_addition:
                for attr in UnitAddition.__slots__:
                    v.add_property(attr, getattr(_step_addition, attr))

        # 只作用于上阵兵种
        in_format_staffs = Formation(self.server_id, self.char_id).in_formation_staffs()
        for k, v in in_format_staffs.iteritems():
            if not v['unit_id']:
                continue

            u = units[v['unit_id']]
            _add = additions[u.config.race]

            for attr in UnitAddition.__slots__:
                _old_value = getattr(u, attr)
                _new_value = _old_value + getattr(_add, attr)
                setattr(u, attr, _new_value)

            u.make_cache()

    def get_unit_object(self, _id):
        """

        :param _id:
        :rtype: Unit
        """
        unit = Unit.get(self.char_id, _id)
        if unit:
            return unit

        self.load_units()
        unit = Unit.get(self.char_id, _id)
        if not unit:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_NOT_EXIST"))

        return unit

    def level_up(self, uid, add_level):
        unit = self.get_unit_object(uid)

        changed_level = unit.level_up(add_level)
        if changed_level:
            self.after_change(uid)
            self.try_unlock()
            ValueLogUnitLevelUpTimes(self.server_id, self.char_id).record(value=changed_level)
            self.after_units_change_for_trig_signal()

    def step_up(self, uid):
        unit = self.get_unit_object(uid)

        unit.step_up()
        self.after_change(uid)
        self.after_units_change_for_trig_signal()

    def destroy(self, uid, using_sycee):
        unit = self.get_unit_object(uid)
        rc = unit.destroy(using_sycee)
        self.after_change(uid)
        self.after_units_change_for_trig_signal()

        return rc

    def after_change(self, uid):
        from core.formation import Formation
        from core.plunder import Plunder
        from core.championship import Championship

        self.load_units()
        unit = self.get_unit_object(uid)
        all_units = self.get_units_data()

        all_units_object = [self.get_unit_object(k) for k, _ in all_units.iteritems()]

        changed_units = {}

        for u in all_units_object:
            if u.config.race == unit.config.race:
                changed_units[u.id] = u

        self.send_notify_with_unit_objs(changed_units.values())

        fm = Formation(self.server_id, self.char_id)

        _changed = False
        for k, v in fm.in_formation_staffs().iteritems():
            if v['unit_id'] in changed_units:
                _changed = True
                break

        if _changed:
            club = Club(self.server_id, self.char_id, load_staffs=False)
            club.force_load_staffs(send_notify=True)

        _p = Plunder(self.server_id, self.char_id)
        if _p.find_way_id_by_unit_id(uid):
            _p.send_formation_notify()

        _c = Championship(self.server_id, self.char_id)
        if _c.find_way_id_by_unit_id(uid):
            _c.send_formation_notify()


    def send_notify(self, ids=None):
        if not ids:
            act = ACT_INIT
            ids = self.get_units_data().keys()
        else:
            act = ACT_UPDATE

        notify = UnitNotify()
        notify.act = act

        for _id in ids:
            notify_unit = notify.units.add()
            unit = self.get_unit_object(_id)
            notify_unit.MergeFrom(unit.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)

    def send_notify_with_unit_objs(self, unit_objs):
        """

        :type unit_objs: list[Unit]
        """

        notify = UnitNotify()
        notify.act = ACT_UPDATE
        for u in unit_objs:
            notify_unit = notify.units.add()
            notify_unit.MergeFrom(u.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
