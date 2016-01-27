# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-21 00:33
Description:

"""
import arrow

from dianjing.exception import GameException

from core.mongo import MongoBuilding
from core.club import Club
from core.resource import Resource
from core.item import ItemManager
from core.signals import building_level_up_done_signal, building_level_up_start_signal
from config import ConfigBuilding, ConfigErrorMessage

from utils.api import Timerd
from utils.message import MessagePipe

from protomsg.building_pb2 import BuildingNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

import formula

TIMERD_CALLBACK_PATH = '/api/timerd/building/'

RECRUIT_COST_CUT = 1        # 招募花费减少
BUSINESS_INCOME_ADD = 2     # 商务收益增加
BROADCAST_NUM_INC = 3       # 直播位置累计增加
SHOP_NUM_ADD = 4            # 网店数量累计增加
SPONSOR_NUM_INC = 5         # 合约数量累计增加
CHALLENGE_EXP_ADD = 6       # 联赛经验增加
FUNCTION_OPEN = 7           # 功能开放
TRAINING_SLOT_ADD = 8       # 训练位置累计增加
TRAINING_EXP_ADD = 9        # 训练效果加成


class BuildingManager(object):
    def __init__(self, server_id, char_id):
        """
        Building Object Init
            如果 mongo 不存在 building collection， 创建
            如果已经存在了， 检查时是否有 新建筑 或 未添加的建筑， 将其添加到 collection
        """
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoBuilding.db(server_id).find_one({'_id': self.char_id})
        if not doc:
            doc = MongoBuilding.document()
            doc['_id'] = self.char_id
            building_doc = MongoBuilding.document_building()
            doc['buildings'] = {str(i): building_doc for i in ConfigBuilding.INSTANCES.keys()}
            MongoBuilding.db(server_id).insert_one(doc)
        else:
            updater = {}
            for i in ConfigBuilding.INSTANCES.keys():
                if str(i) not in doc['buildings']:
                    updater['buildings.{0}.level'.format(i)] = 1
                    updater['buildings.{0}.end_at'.format(i)] = 0

            if updater:
                MongoBuilding.db(server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': updater}
                )

    def current_effect(self, building_id):
        """
        建筑效果
            传入建筑ID, 获取玩家该建筑当前拥有的 建筑效果
        """
        cur_lv = self.current_level(building_id)
        conf_building = ConfigBuilding.get(building_id).get_level(cur_lv)
        return conf_building.effect

    def current_level(self, building_id):
        """
        建筑等级
            传入建筑ID  获取建筑等级
        """
        doc = MongoBuilding.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'buildings.{0}.level'.format(building_id): 1}
        )

        return doc['buildings'].get(str(building_id), {}).get('level', 1)

    def level_up(self, building_id):
        """
        建筑升级
            通过建筑ID获取建筑配置, 检查建筑升级条件
            1 获取建筑配置
            2检测
                建筑配置是否存在
                是否为可升级建筑
                获取玩家建筑数据
                建筑是否已经是最高级
                建筑是否在升级中
                所依赖条件是否满足
                升级所需资源是否足够
            3 升级
                扣除资源
                升级建筑
                注册回调函数
                同步建筑信息给玩家
        """
        config = ConfigBuilding.get(building_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST"))

        if not config.max_levels:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_CAN_NOT_LEVEL_UP"))

        doc = MongoBuilding.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'buildings.{0}'.format(building_id): 1}
        )

        current_level = doc['buildings'][str(building_id)]['level']
        if current_level >= config.max_levels:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_ALREADY_MAX_LEVEL"))

        end_at = doc['buildings'][str(building_id)]['end_at']
        if end_at:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_IN_UPGRADING"))

        config_building_level = config.get_level(current_level)

        if config.level_up_condition_type == 1:
            if Club(self.server_id, self.char_id).level < config_building_level.up_condition_value:
                raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))
        else:
            if BuildingClubCenter(
                    self.server_id,
                    self.char_id).current_level() < config_building_level.up_condition_value:
                raise GameException(ConfigErrorMessage.get_error_id("BUILDING_CLUB_CENTER_LEVEL_NOT_ENOUGH"))

        im = ItemManager(self.server_id, self.char_id)
        im.check_exists(config_building_level.up_need_items, is_oid=True)

        check = {
            "gold": -config_building_level.up_need_gold,
            "message": u"Building {0} level up to {1}".format(building_id, current_level + 1)
        }

        with Resource(self.server_id, self.char_id).check(**check):
            end_at = arrow.utcnow().timestamp + config_building_level.up_need_minutes * 60
            # register to timerd
            data = {
                'sid': self.server_id,
                'cid': self.char_id,
                'building_id': building_id
            }

            key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)

            im.remove_items_by_oid(config_building_level.up_need_items)

            MongoBuilding.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'buildings.{0}.end_at'.format(building_id): end_at,
                    'buildings.{0}.key'.format(building_id): key
                }}
            )

        self.send_notify(building_ids=[building_id])

        building_level_up_start_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            building_id=building_id
        )

    def speedup(self, building_id):
        """
        建筑升级加速(立即完成建筑升级)
            1 获取玩家该建筑数据， 数据不存在, 返回错误码
            2 检测
                是否已完成升级
                是否是升级状态

            3 计算加速花费, 并检测资源是否足够

            4 完成升级
                取消定时任务
                调用回调接口完成升级
                扣除资源

        """
        # config = ConfigBuilding.get(building_id)
        # if not config:
        #     raise GameException(ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST"))

        doc = MongoBuilding.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'buildings.{0}'.format(building_id): 1}
        )

        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST"))

        end_at = doc['buildings'][str(building_id)]['end_at']
        if not end_at:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_CANNOT_SPEEDUP"))

        behind_seconds = end_at - arrow.utcnow().timestamp
        need_diamond = formula.training_speedup_need_diamond(behind_seconds)
        message = u"Building {0} Speedup".format(building_id)

        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            key = doc['buildings'][str(building_id)]['key']
            Timerd.cancel(key)

            self.levelup_callback(building_id)

    def levelup_callback(self, building_id):
        """
        升级完成接口
            完成建筑升级
            同步信息给玩家
        """
        MongoBuilding.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$inc': {'buildings.{0}.level'.format(building_id): 1},
                '$set': {
                    'buildings.{0}.end_at'.format(building_id): 0,
                    'buildings.{0}.key'.format(building_id): ''
                }
            }
        )

        self.send_notify(building_ids=[building_id])

        building_level_up_done_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            building_id=building_id
        )

    def send_notify(self, building_ids=None):
        if building_ids:
            projection = {'buildings.{0}'.format(i): 1 for i in building_ids}
            act = ACT_UPDATE
        else:
            projection = {'buildings': 1}
            act = ACT_INIT

        doc = MongoBuilding.db(self.server_id).find_one({'_id': self.char_id}, projection)
        notify = BuildingNotify()
        notify.act = act

        for b in ConfigBuilding.all_values():
            if building_ids and b.id not in building_ids:
                continue

            notify_building = notify.buildings.add()
            notify_building.id = b.id
            notify_building.level = doc['buildings'][str(b.id)]['level']
            notify_building.end_at = doc['buildings'][str(b.id)]['end_at']

        MessagePipe(self.char_id).put(msg=notify)


class BaseBuilding(object):
    BUILDING_ID = 0

    def __init__(self, server_id, char_id):
        self.bm = BuildingManager(server_id, char_id)

    def current_level(self):
        return self.bm.current_level(self.BUILDING_ID)

    def level_up(self):
        return self.bm.level_up(self.BUILDING_ID)

    def current_effect(self):
        return self.bm.current_effect(self.BUILDING_ID)


# 俱乐部总部
class BuildingClubCenter(BaseBuilding):
    BUILDING_ID = 1


# 培训中心
class BuildingTrainingCenter(BaseBuilding):
    BUILDING_ID = 2


# 人才市场
class BuildingStaffCenter(BaseBuilding):
    BUILDING_ID = 3


# 精彩活动
class BuildingTaskCenter(BaseBuilding):
    BUILDING_ID = 4


# 电竞赛场
class BuildingLeagueCenter(BaseBuilding):
    BUILDING_ID = 5


# 赞助商事务所
class BuildingSponsorCenter(BaseBuilding):
    BUILDING_ID = 6


# 商务部
class BuildingBusinessCenter(BaseBuilding):
    BUILDING_ID = 7
