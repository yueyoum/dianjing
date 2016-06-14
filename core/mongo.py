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
            'gold': 0,
            'diamond': 0,
            'crystal': 0,
            'gas': 0,
        },
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'club.level',]

class MongoStaff(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 员工， unique_id: data. 定义见下面的 STAFF
        'staffs': {},
        'exp_pool': 0,
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
        # 关卡次数记录在 ValueLog 里
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
class MongoTaskMain(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # doing 从1开始， 0表示做完了
        'doing': 1,
    }

    COLLECTION = "task_main"


# 日常任务， 每天刷新的
class MongoTaskDaily(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 刷出来的 task id列表
        'tasks': [],
        # 已经完成的， 领完奖的
        'done': [],
    }

    COLLECTION = 'task_daily'


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
        '_id': null,
        'total_point': 0,
        'cost_point': 0,
        'talents': [],
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


# 竞技场
class MongoArena(BaseDocument):
    DOCUMENT = {
        # string id, 既有玩家，也有NPC
        '_id': null,
        # 排名
        'rank': 0,
        # 历史最高排名
        'max_rank': 0,
        # 刷出来的对手
        'rivals': [],
        # 荣耀领奖记录
        # NOTE: 这里特殊处理，记录的是 当天日期: 领奖记录列表
        # 玩家每次登陆时删除过期的日期
        'honor_rewards': {},
        # 被挑战日志
        'logs': [],
        # 积分
        'point': 0,
    }

    COLLECTION = 'arena'
    INDEXES = ['rank']


# 塔
class MongoTower(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 记录打过的每一层的星级 lv: star, star -1 表示失败， 0 表示可以打， 1,2,3 表示对应星级
        # 只记录打过的
        'levels': {},
        # 已经购买的talent id 列表
        'talents': [],

        # NOTE
        # 当前获得的星数, 每次重置清零
        'current_star': 0,
        # 今天获取到的最多星数， 每天重置后开始算， 每日排行榜也是根据这个算的，每天清零
        # 如果当天没有重置，那么就不往这个里面记录
        # 重置后才记录。。。
        'today_max_star': 0,
        # 历史最高星数，仅仅是一个简单的记录
        'history_max_star': 0,

        # 最高三星 (连续的，非连续的不记录)
        'max_star_level': 0,
        # 转盘信息
        'turntable': {},
        # 购买信息 [(id, bought), ...]  按顺序，bought 0 表示没有买过， 1 表示买过了
        'goods': [],
        # 扫荡完成时间 0 没有扫荡
        'sweep_end_at': 0,
    }

    COLLECTION = 'tower'
    INDEXES = ['today_max_star',]

# 领地建筑
class MongoTerritory(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'buildings': {},
        'work_card': 0,
    }

    BUILDING_DOCUMENT = {
        'level': 1,
        'exp': 0,
        'product_amount': 0,
        'slots': {},
        # 随机事件
        'event_id': 0,
        # 上次发生随机事件的时间戳，用来控制下次生成时间
        'event_at': 0,
    }

    SLOT_DOCUMENT = {
        'staff_id': "",
        'start_at': 0,
        'hour': 0,
        'report': [],
        'reward': {},
    }

    @classmethod
    def document_building(cls):
        return copy.deepcopy(cls.BUILDING_DOCUMENT)

    @classmethod
    def document_slot(cls):
        return copy.deepcopy(cls.SLOT_DOCUMENT)

    COLLECTION = 'territory'


# 商店
class MongoStore(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'tp': {},
    }

    TP_DOCUMENT = {
        'refresh_at': 0,
        'goods': {}
    }

    GOODS_DOCUMENT = {
        # 每次随机出来的index
        'index': 0,
        # 已经兑换的次数，这个不随系统刷新，是由玩家刷新面板的时候 刷的
        'times': 0,
    }

    @classmethod
    def document_tp(cls):
        return copy.deepcopy(cls.TP_DOCUMENT)

    @classmethod
    def document_goods(cls):
        return copy.deepcopy(cls.GOODS_DOCUMENT)

    COLLECTION = 'store'


# VIP
class MongoVIP(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'vip': 0,
        'exp': 0,
        # 领奖情况
        'rewards': []
    }

    COLLECTION = 'vip'
    INDEXES = ['vip',]


# 收集图鉴
class MongoStaffCollection(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'staffs': []
    }

    COLLECTION = 'staff_collection'

# 体力
class MongoEnergy(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'current': 0,
        'last_add_at': 0,
    }

    COLLECTION = 'energy'