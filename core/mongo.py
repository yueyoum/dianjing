# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""
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
        return cls.DOCUMENT.copy()

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

            'policy': 1,
            'match_staffs': [],
            'tibu_staffs': []
        },

        # 所属联赛小组
        'league_group': 0,
        'league_level': 1,
        # 是否报名参加了杯赛
        'in_cup': 0,
        # 购买的员工格子数
        'buy_slots': 0,
        # 体力
        'energy': {
            'key': "",              # 充能回调key
            'power': 0,             # 体力
            'times': 0,             # 当天花费钻石充能次数
        },
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'league_level', 'in_cup', 'club.level']


# 挑战赛
class MongoChallenge(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 大区， {area_id: {'challenge_id': {'star': 0}},
        'areas': {
            '1': {
                'challenges': {
                    '1': {
                        'stars': 0,     # 历史最佳记录 0为未通过
                        'times': 0,     # 当天挑战次数， 每天刷新
                    }
                },
                'packages': {
                    '1': True,
                    '2': True,
                    '3': True,
                }
            }
        }
    }

    COLLECTION = 'challenge'


# 公共数据
class MongoCommon(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'value': null,
    }

    COLLECTION = "common"


class MongoStaff(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 员工， 定义见下面的 STAFF
        'staffs': {},
        'on_sell': {},
    }

    STAFF_DOCUMENT = {
        'exp': 0,
        'level': 1,
        'star': 0,
        'status': null,
        'skills': {},
        'winning_rate': {},
        # equips 直接从 item 中移动过来
        'equips': {},
        # 此外这里还有属性

    }

    # 嵌入staff中
    STAFF_SKILL_DOCUMENT = {
        'level': 1,
        'locked': 0,
        # 升级结束时间戳
        'end_at': 0,
        # timerd callback key
        'key': ''
    }

    # 嵌入到staff中
    STAFF_WINNING_RATE_DOCUMENT = {
        'win': 0,
        'total': 0,
    }

    @classmethod
    def document_staff(cls):
        return cls.STAFF_DOCUMENT.copy()

    @classmethod
    def document_staff_skill(cls):
        return cls.STAFF_SKILL_DOCUMENT.copy()

    COLLECTION = "staff"


# 背包
class MongoItem(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # id: meta_data
        # id 是物品的唯一ID， meta data 就是其数据
        # 不同类型的物品，记录的数据不一样
    }

    COLLECTION = 'item'


# 经验训练
class MongoTrainingExp(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'slots': {}
    }

    TRAINING_DOCUMENT = {
        'staff_id': 0,
        'start_at': 0,
        'exp': -1,
        # exp 是完成时的经验值，领奖就领的是这个
        # 只有在完成时（加速或者正常完成），才设置这个值
        # 所以只要exp > -1，就表示训练完成了
        'key': '',
        # timer key
    }

    @classmethod
    def document_training(cls):
        return cls.TRAINING_DOCUMENT.copy()

    COLLECTION = 'training_exp'


# 属性训练
class MongoTrainingProperty(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'staffs': {},
        'keys': {},  # 定时器key, staff_id: key
    }

    TRAINING_DOCUMENT = {
        'id': null,
        'end_at': 0,
        # 加速会改变这个end_at
        # 属性训练只和使用的id训练有关，所以这里直接记录完成的end_at，
        # 不用考虑其他变量
    }

    @classmethod
    def document_training(cls):
        return cls.TRAINING_DOCUMENT.copy()

    COLLECTION = 'training_property'


# 直播训练
class MongoTrainingBroadcast(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'slots': {}
    }

    SLOT_DOCUMENT = {
        'staff_id': 0,
        'start_at': 0,
        'gold': -1,
        # 只要 gold > -1，肯定就是训练时间满了，不管是加速还是正常结束
        'key': '',
        # 随机种子，给这个slot计算获得物品用的
        # 因为每次计算并不保存，所以为了领奖时最终结果和先前计算的一样，需要相同的随机种子
        'seed': 0,
    }

    @classmethod
    def document_slot(cls):
        return cls.SLOT_DOCUMENT.copy()

    COLLECTION = 'training_broadcast'


# 网店训练
class MongoTrainingShop(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # shop_id: staff_id. staff_id 0 表示这个网店没人
        'shops': {},
    }

    SHOP_DOCUMENT = {
        'staff_id': 0,
        'sells_per_hour': 0,
        'start_at': 0,
        'end_at': 0,
        'key': '',

        'goods': 0,
    }

    COLLECTION = 'training_shop'


# 赞助训练
class MongoTrainingSponsor(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # sponsor_id: start_at_timestamp.  timestamp 0 表示没有签约
        'has_sponsors': False,
        'sponsors': {}
    }

    COLLECTION = 'training_sponsor'
    INDEXES = ['has_sponsors']


# 招募刷新
class MongoRecruit(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'tp': null,
        # staffs 记录刷新出来的员工
        'staffs': [],
        # times 记录刷新次数 tp: times
        'times': {},
        # 记录本次刷新中的 已经招募过的
        'recruited': [],
    }

    COLLECTION = "recruit"


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
        return cls.BUILDING_DOCUMENT.copy()


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
    }

    COLLECTION = "mail"

    @classmethod
    def document_mail(cls):
        return cls.MAIL_DOCUMENT.copy()


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


# 天梯
class MongoLadder(BaseDocument):
    DOCUMENT = {
        # id: 真实玩家就是str(char_id)，npc是 uuid
        '_id': null,
        'score': 0,
        'order': 0,

        # 刷新结果 _id: order
        'refreshed': {},
        # 剩余次数
        'remained_times': 0,
        # 战报 [(template_id, args) ...]
        'logs': [],

        # 天梯商店购买次数，每天清空
        'buy_times': {},

        # 以下几项只有NPC才有
        'club_name': "",
        'club_flag': 0,
        'manager_name': "",
        'staffs': []
    }

    COLLECTION = "ladder"
    INDEXES = ['order']


# 杯赛
class MongoCup(BaseDocument):
    DOCUMENT = {
        # 这里的 _id 是定死的：1, 因为一个服务器只有一个杯赛
        '_id': 1,
        # 第几届杯赛
        'order': 1,
        # 上一届冠军
        'last_champion': "",
        # level 的 key 表示多少强
        # values [club_id, club_id...] 列表
        'levels': {},
    }

    COLLECTION = "cup"


class MongoCupClub(BaseDocument):
    DOCUMENT = {
        # club id
        '_id': null,
        # 开始前一小时把玩家的阵容拷贝过来
        'staffs': "",
        # 下面几项只有NPC才有
        'club_name': "",
        'manager_name': "",
        'club_flag': 1,
    }

    COLLECTION = "cup_club"


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
        return cls.NOTIFICATION_DOCUMENT.copy()


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
        # 已领取额外奖励的
        'rewards': [],
        # 俱乐部信息，序列化后的Club
        'clubs': []
    }

    COLLECTION = 'training_match'


# 精英赛
class MongoEliteMatch(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 大区， {area_id: {'challenge_id': {'star': 0}},
        'areas': {}
    }

    AREA_DOCUMENT = {
        'challenges': {
            '1': {
                'stars': 0,     # 历史最佳记录 0为未通过
                'times': 0,     # 当天挑战次数， 每天刷新
            }
        },
        'packages': {
            '1': True,
            '2': True,
            '3': True,
        }
    }

    COLLECTION = 'elite_match'


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


# 用户联赛mongo
class MongoLeague(BaseDocument):
    """
    联赛表
    """
    DOCUMENT = {
        '_id': 0,
        'score': 1,
        'level': 1,
        'daily_reward': "",
        'challenge_times': 0,
        'win_rate': {
            'total': 0,
            'win': 0,
        },
        'in_rise': False,
        'refresh_time': 0,
        'match_club': {},  # club_id: MATCH_CLUB_DOCUMENT
    }

    MATCH_CLUB_DOCUMENT = {
        'status': 0,
        'npc_club': False,
        ################
        'flag': 0,
        'name': "",
        'win_rate': {
            'total': 0,
            'win': 0,
        },
        'score': 0,
        'manager_name': "",
        'staffs': {}
    }

    COLLECTION = 'league'
    INDEXES = ['level']
