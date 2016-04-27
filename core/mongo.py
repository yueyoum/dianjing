# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""

import copy
from core.db import MongoDB


def ensure_index():
    from apps.server.models import Server
    for sid in Server.opened_server_ids():
        for i in BaseDocument.__subclasses__():
            i.create_indexes(sid)


class BaseDocument(object):
    DOCUMENT = {}
    COLLECTION = ""
    INDEXES = []

    @classmethod
    def document(cls):
        """

        :rtype : dict
        """
        return copy.deepcopy(cls.DOCUMENT)

    @classmethod
    def db(cls, server_id):
        """

        :rtype : pymongo.collection.Collection
        """
        return MongoDB.get(server_id)[cls.COLLECTION]

    @classmethod
    def exist(cls, server_id, _id):
        doc = cls.db(server_id).find_one({'_id': _id}, {'_id': 1})
        return True if doc else False

    @classmethod
    def create_indexes(cls, server_id):
        if not cls.INDEXES:
            return

        for i in cls.INDEXES:
            cls.db(server_id).create_index(i)


class Null(object):
    pass


null = Null()


class MongoCharacter(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'name': null,
        'create_at': 0,
        'last_login': 0,
        'avatar_key': '',
        'avatar_ok': False,

        'club': {
            'name': null,
            'flag': null,
            'level': 1,
            'renown': 0,
            'vip': 0,
            'gold': 0,
            'diamond': 0,
            'crystal': 0,
            'gas': 0,
        },

        # 所属联赛小组
        'league_group': 0,
        'league_level': 1,
        # 是否报名参加了杯赛
        'in_cup': 0,

        # 体力
        'energy': {
            'key': "",              # 充能回调key
            'power': 0,             # 体力
            'times': 0,             # 当天花费钻石充能次数
        },
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'league_level', 'in_cup', 'club.level']

class MongoStaff(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 员工， unique_id: data. 定义见下面的 STAFF
        'staffs': {},
    }

    STAFF_DOCUMENT = {
        'oid': null,
        'level': 1,
        'step': 0,
        # star 是根据 quality 算出来的
        'star': null,
        'level_exp': 0,
        'star_exp': 0,

        # 四件装备
        'equip_mouse': '',
        'equip_keyboard': '',
        'equip_monitor': '',
        'equip_decoration': '',
    }

    @classmethod
    def document_staff(cls):
        return copy.deepcopy(cls.STAFF_DOCUMENT)

    COLLECTION = "staff"


# 阵型
class MongoFormation(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # slot_id: data
        # 只保存开了的， slot_id 从1 递增
        'slots': {},
        # slot_id 序列， 0 表示这个位置（index）的 slot 没有开启
        'position': []
    }

    DOCUMENT_SLOT = {
        'staff_id': "",
        'unit_id': 0,
    }

    @classmethod
    def document_slot(cls):
        return copy.deepcopy(cls.DOCUMENT_SLOT)

    COLLECTION = 'formation'


# 挑战赛
class MongoChallenge(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 只记录已经开启的
        'chapters': {},
        # id: star
        'challenge_star': {},
        # 关卡次数记录在 TimesLog 里
        # 每个关卡对应的物品掉落次数
        'challenge_drop': {},
    }

    CHAPTER_DOCUMENT = {
        'star': 0,
        'rewards': []   # 保存已经领奖的index
    }

    COLLECTION = 'challenge'


# 公共数据
class MongoCommon(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'value': null,
    }

    COLLECTION = "common"


# 新背包
class MongoBag(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 格子
        'slots': {},
    }

    SLOT_DOCUMENT = {
        'item_id': 0,
        # 如果是一般道具，碎片，则有amount这个属性
        'amount': 0,
        # 如果是装备，则有下面的属性
        'level': 0,
    }

    COLLECTION = 'bag'


# 招募刷新
class MongoStaffRecruit(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'score': 0,
        'point': {},

        # 上次招募时间，用这个来算CD时间
        'recruit_at': {},

        # 其他记录在 RecordLog中
    }

    COLLECTION = "staff_recruit"


# 建筑
class MongoBuilding(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # id: level
        'buildings': {}
    }

    BUILDING_DOCUMENT = {
        'level': 1,
        'end_at': 0,
        'key': '',  # 定时器key
    }

    COLLECTION = "building"

    @classmethod
    def document_building(cls):
        return copy.deepcopy(cls.BUILDING_DOCUMENT)


# 好友
class MongoFriend(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # id: status
        'friends': {}
    }

    COLLECTION = "friend"


# 邮件
class MongoMail(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'mails': {}
    }

    MAIL_DOCUMENT = {
        # from_id 为0表示系统邮件， >0 表示来自这个id的玩家
        'from_id': null,
        'title': null,
        'content': null,
        'has_read': False,
        'create_at': null,
        'attachment': "",
        'function': 0,
        'data': None,
    }

    COLLECTION = "mail"

    @classmethod
    def document_mail(cls):
        return copy.deepcopy(cls.MAIL_DOCUMENT)


# 任务
class MongoTask(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 只记录数值累加的，比较的 从 比较源 实时获取数据
        # {
        #     'task_id1': {
        #         'target_id:param': current_value,
        #         'target_id:param': current_value,
        #     },
        #     'task_id1': {
        #         'target_id:param': current_value,
        #         'target_id:param': current_value,
        #     },
        # }
        'doing': {},
        # 可以领奖
        'finish': [],
        # 彻底完成
        'history': [],
    }

    COLLECTION = "task"


# 通知
class MongoNotification(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # {id: [tp, args, timestamp], ...}
        'notis': {}
    }

    NOTIFICATION_DOCUMENT = {
        'tp': null,
        'args': null,
        'timestamp': null,
        'opened': False
    }

    COLLECTION = "notification"

    @classmethod
    def document_notification(cls):
        return copy.deepcopy(cls.NOTIFICATION_DOCUMENT)


# 赞助
class MongoSponsor(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'sponsor_to_id': 0,  # 赞助了谁
        'income': 0,  # 总收益
        'sponsors': {},  # id: income.  这里的income不清零
        'logs': []  # [(template_id, args), ...]
    }

    COLLECTION = "sponsor"


# 活动
class MongoActivity(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 已经获取奖励的 活动item ID
        'done': {}
    }

    COLLECTION = "activity"


# 签到
class MongoSignIn(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'sign': {},  # sign_id: [dates, dates...]
    }

    COLLECTION = "sign_in"


# 活跃度
class MongoActiveValue(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'value': 0,  # 活跃度
        'rewards': [],  # 已经领奖的ID列表
        'funcs': {},  # 已经触发的。 function_name: times
    }

    COLLECTION = 'active_value'


# 各种记录
class MongoRecord(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # sign: value
        'records': {}
    }

    COLLECTION = 'record'


# 训练赛
class MongoTrainingMatch(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'relive_times': 0,
        # 进度 id: flag. flag 1 表示新开启，2 表示通过 3 表示失败
        # 不在这里面的表示没有开启
        'status': {},
        # 俱乐部信息，序列化后的Club
        'clubs': [],
        'score': 0,
        # 商店，和ladder一样
        'store_items': [],
        'buy_times': {},
    }

    COLLECTION = 'training_match'


# 员工拍卖
class MongoAuctionStaff(BaseDocument):
    DOCUMENT = {
        '_id': null,        # 物品ID
        'char_id': 0,       # 出售者ID
        'club_name': "",

        # 员工属性 要存入购买者的 staffs 数据库中
        'staff_id': 0,      # 员工ID
        'exp': 0,           # 当前经验
        'level': 0,         # 当前等级
        'status': 0,        # 状态， 对应 staff_status.json
        'skills': {},       # 技能

        # 下面这些额外信息用于搜索
        'quality': '',
        'jingong': 0,       # 进攻
        'qianzhi': 0,       # 牵制
        'xintai': 0,        # 心态
        'baobing': 0,       # 暴兵
        'fangshou': 0,      # 防守
        'yunying': 0,       # 运营
        'yishi': 0,         # 意识
        'caozuo': 0,        # 操作
        'zhimingdu': 0,     # 知名度

        # 拍卖设置
        'start_at': 0,      # 开始时间
        'tp': 0,            # 拍卖类型
        'min_price': 0,     # 最低价
        'max_price': 0,     # 一口价

        # 拍卖信息
        'bidder': 0,        # 最新的竞标者(竞标者id)
        'bidding': 0,       # 最新的竞标价格
        # 定时任务key
        'key': "",
    }

    COLLECTION = 'auction_staff'
    INDEXES = ['char_id']


# 用户竞价列表
class MongoBidding(BaseDocument):
    DOCUMENT = {
        '_id': 0,           # 角色ID
        'items': [],        # 物品ID
        # 物品出价 类似于: item_1: bidding
    }

    COLLECTION = 'auction_bidding'
    INDEXES = ['items']


class MongoUnit(BaseDocument):
    DOCUMENT = {
        '_id': 0,
        # unit_id: unit
        # 只保存已解锁的
        'units': {},
    }

    UNIT_DOCUMENT = {
        'step': 0,
        'level': 1,
    }

    COLLECTION = 'unit'

    @classmethod
    def document_unit(cls):
        return copy.deepcopy(cls.UNIT_DOCUMENT)


class MongoTalent(BaseDocument):
    DOCUMENT = {
        '_id': 0,
        'total': 0,
        'cost': 0,
        'talent': [],
    }

    COLLECTION = 'talent'


class MongoTimesLog(BaseDocument):
    # 所有和次数相关的都记录在这里
    # 方便后面做活动
    DOCUMENT = {
        '_id': '',
        'key': '',  # 这个是 功能标识， 可以是 chat_id+function_name
        'timestamp': 0, # UTC
        'value': 1, # 次数， 默认一次
    }

    COLLECTION = 'times_log'
    INDEXES = ['key', 'timestamp',]


class MongoDungeon(BaseDocument):
    DOCUMENT = {
        '_id': 0,
        # tp: times
        'times': {},
        # tp: open_dungeon
        'open': {},
    }

    COLLECTION = 'dungeon'
