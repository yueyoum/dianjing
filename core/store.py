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
from core.times_log import TimesLogStoreRefreshTimes
from core.club import get_club_property
from core.staff import StaffRecruit
from core.resource import ResourceClassification, money_text_to_item_id

from utils.message import MessagePipe

from config import ConfigStore, ConfigStoreRefreshCost, ConfigStoreType, ConfigErrorMessage

from protomsg.store_pb2 import StoreNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

ALL_TYPES = ConfigStoreType.INSTANCES.keys()

MAX_REFRESH_TIMES = 10


def get_money_value(server_id, char_id, tp):
    config = ConfigStoreType.get(tp)
    if config.money_id == 30000:
        return get_club_property(server_id, char_id, 'diamond')

    if config.money_id == 30001:
        return get_club_property(server_id, char_id, 'gold')

    if config.money_id == 30002:
        return get_club_property(server_id, char_id, 'renown')

    if config.money_id == 30003:
        return get_club_property(server_id, char_id, 'crystal')

    if config.money_id == 30004:
        return get_club_property(server_id, char_id, 'gas')

    if config.money_id == 30005:
        return StaffRecruit(server_id, char_id).get_score()

    raise RuntimeError("Store get_money_value, unknown tp: {0}".format(tp))


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

        tp_doc = MongoStore.document_tp()
        if set_timestamp:
            tp_doc['refresh_at'] = arrow.utcnow().timestamp

        tp_doc['goods'] = {str(_id): {'index': _index, 'times': 0} for _id, _index in goods}
        self.doc['tp.{0}'.format(tp)] = tp_doc

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
        last_at = self.doc['tp'][str(tp)]['refresh_at']
        if not last_at:
            return 0

        config = ConfigStoreType.get(tp)
        return last_at + config.refresh_hour_interval * 3600


    def get_current_refresh_times(self, tp):
        return TimesLogStoreRefreshTimes(self.server_id, self.char_id).count_of_today()

    def get_remained_refresh_times(self, tp):
        remained_times = MAX_REFRESH_TIMES - self.get_current_refresh_times(tp)
        if remained_times < 0:
            remained_times = 0

        return remained_times

    def get_refresh_cost(self, tp):
        return ConfigStoreRefreshCost.get_cost(tp, self.get_current_refresh_times(tp))

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

        item_id, item_amount, need_id, need_amount = config.content[data['index']]
        resource_classify = ResourceClassification.classify([(need_id, need_amount)])
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id)

        resource_classify = ResourceClassification.classify([(item_id, item_amount)])
        resource_classify.add(self.server_id, self.char_id)

        data['times'] += 1
        self.send_notify(tp=tp, goods_id=goods_id)

        return resource_classify


    def refresh(self, tp):
        if tp not in ALL_TYPES:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        remained_times = self.get_remained_refresh_times(tp)
        if not remained_times:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_REFRESH_NO_TIMES"))

        diamond = self.get_refresh_cost(tp)
        resource_classified = ResourceClassification.classify([(money_text_to_item_id('diamond'), diamond)])
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.make_refresh(tp)


    def auto_refresh(self, tp):
        if tp not in ALL_TYPES:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if self.next_auto_refresh_timestamp(tp) < arrow.utcnow().timestamp:
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
            notify_type = notify.store_types.add()
            notify_type.tp = _t
            notify_type.auto_refresh_at = self.next_auto_refresh_timestamp(_t)
            notify_type.remained_refresh_times = self.get_remained_refresh_times(_t)
            notify_type.refresh_cost = self.get_refresh_cost(_t)
            notify_type.money_value = get_money_value(self.server_id, self.char_id, _t)

            for _g in _get_goods_id_of_tp(_t):
                _g_data = self.doc['tp'][str(_t)]['goods'][str(_g)]
                notify_type_goods = notify_type.goods.add()
                notify_type_goods.id = _g
                notify_type_goods.content_index = _g_data['index']
                notify_type_goods.remained_times = ConfigStore.get(_g).times_limit - _g_data['times']

        MessagePipe(self.char_id).put(msg=notify)
