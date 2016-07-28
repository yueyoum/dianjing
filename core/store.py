# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       store
Date Created:   2016-05-23 14-33
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoStore
from core.value_log import ValueLogStoreRefreshTimes
from core.club import get_club_property
from core.resource import ResourceClassification, money_text_to_item_id
from core.vip import VIP
from core.tower import Tower
from core.arena import Arena
from core.union import Union

from utils.message import MessagePipe

from config import ConfigStore, ConfigStoreRefreshCost, ConfigStoreType, ConfigErrorMessage

from protomsg.store_pb2 import StoreNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

ALL_TYPES = ConfigStoreType.INSTANCES.keys()


class RefreshInfo(object):
    __slots__ = ['current_refresh_times', 'remained_refresh_times', 'refresh_cost']

    def __init__(self, server_id, char_id, tp):
        self.current_refresh_times = ValueLogStoreRefreshTimes(server_id, char_id).count_of_today(sub_id=tp)
        self.remained_refresh_times = VIP(server_id, char_id).store_refresh_times - self.current_refresh_times
        if self.remained_refresh_times < 0:
            self.remained_refresh_times = 0

        self.refresh_cost = ConfigStoreRefreshCost.get_cost(tp, self.current_refresh_times + 1)


class Store(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoStore.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoStore.document()
            self.doc['_id'] = self.char_id
            for tp in ALL_TYPES:
                self.make_refresh(tp, set_timestamp=True, save=False, send_notify=False)

            MongoStore.db(self.server_id).insert_one(self.doc)

    def make_refresh(self, tp, set_timestamp=False, save=True, send_notify=True):
        club_level = get_club_property(self.server_id, self.char_id, 'level')
        goods = ConfigStore.refresh(tp, club_level)

        try:
            tp_doc = self.doc['tp'][str(tp)]
        except KeyError:
            tp_doc = MongoStore.document_tp()

        if set_timestamp:
            tp_doc['refresh_at'] = arrow.utcnow().timestamp

        tp_doc['goods'] = {str(_id): {'index': _index, 'times': 0} for _id, _index in goods}
        self.doc['tp'][str(tp)] = tp_doc

        if save:
            MongoStore.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'tp.{0}'.format(tp): tp_doc
                }}
            )

        if send_notify:
            self.send_notify(tp=tp)

    def next_auto_refresh_timestamp(self, tp):
        config = ConfigStoreType.get(tp)
        if not config.refresh_hour_interval:
            return 0

        last_at = self.doc['tp'][str(tp)]['refresh_at']
        if not last_at:
            # 立即可刷
            return arrow.utcnow().timestamp - 1

        return last_at + config.refresh_hour_interval * 3600

    def buy(self, tp, goods_id):
        if tp not in ALL_TYPES:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        config = ConfigStore.get(goods_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_GOODS_NOT_EXIST"))

        try:
            data = self.doc['tp'][str(tp)]['goods'][str(goods_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if data['times'] >= config.times_limit:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_GOODS_NO_TIMES"))

        if config.condition_id == 1:
            # VIP 等级
            VIP(self.server_id, self.char_id).check(config.condition_value)
        elif config.condition_id == 2:
            # 爬塔历史最高星
            Tower(self.server_id, self.char_id).check_history_max_star(config.condition_value)
        elif config.condition_id == 3:
            # 竞技场历史最高排名
            Arena(self.server_id, self.char_id).check_max_rank(config.condition_value)
        elif config.condition_id == 4:
            # 当前公会等级
            Union(self.server_id, self.char_id).check_level(config.condition_value)

        item_id, item_amount, need_id, need_amount = config.content[data['index']]
        resource_classify = ResourceClassification.classify([(need_id, need_amount)])
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id)

        resource_classify = ResourceClassification.classify([(item_id, item_amount)])
        resource_classify.add(self.server_id, self.char_id)

        data['times'] += 1

        MongoStore.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'tp.{0}.goods.{1}.times'.format(tp, goods_id): data['times']
            }}
        )

        self.send_notify(tp=tp, goods_id=goods_id)
        return resource_classify

    def refresh(self, tp):
        if tp not in ALL_TYPES:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        ri = RefreshInfo(self.server_id, self.char_id, tp)
        if not ri.remained_refresh_times:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_REFRESH_NO_TIMES"))

        cost = [(money_text_to_item_id('diamond'), ri.refresh_cost), ]
        resource_classified = ResourceClassification.classify(cost)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        ValueLogStoreRefreshTimes(self.server_id, self.char_id).record(sub_id=tp)
        self.make_refresh(tp)

    def auto_refresh(self, tp):
        if tp not in ALL_TYPES:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if self.next_auto_refresh_timestamp(tp) > arrow.utcnow().timestamp:
            return

        self.make_refresh(tp, set_timestamp=True)

    def send_notify(self, tp=None, goods_id=None):
        # tp没有， goods_id没有：  全部同步
        # tp 有，goods_id 没有 ： 更新这个tp的
        # tp 有，goods_id 有：    更新这个tp中的 这个goods_id
        # tp 没有， goods_id 有： 错误情况

        tp_goods_id_table = {}

        def _get_goods_id_of_tp(_tp):
            try:
                return tp_goods_id_table[_tp]
            except KeyError:
                ids = self.doc['tp'][str(_tp)]['goods'].keys()
                return [int(i) for i in ids]

        if tp:
            act = ACT_UPDATE
            tps = [tp]
            if goods_id:
                tp_goods_id_table[tp] = [goods_id]
        else:
            act = ACT_INIT
            tps = ConfigStoreType.INSTANCES.keys()
            if goods_id:
                raise RuntimeError("Store.send_notify, Invalid arguments")

        notify = StoreNotify()
        notify.act = act
        for _t in tps:
            ri = RefreshInfo(self.server_id, self.char_id, _t)

            notify_type = notify.store_types.add()
            notify_type.tp = _t
            notify_type.auto_refresh_at = self.next_auto_refresh_timestamp(_t)
            notify_type.remained_refresh_times = ri.remained_refresh_times
            notify_type.refresh_cost = ri.refresh_cost

            for _g in _get_goods_id_of_tp(_t):
                _g_data = self.doc['tp'][str(_t)]['goods'][str(_g)]
                notify_type_goods = notify_type.goods.add()
                notify_type_goods.id = _g
                notify_type_goods.content_index = _g_data['index']
                notify_type_goods.remained_times = ConfigStore.get(_g).times_limit - _g_data['times']

        MessagePipe(self.char_id).put(msg=notify)
