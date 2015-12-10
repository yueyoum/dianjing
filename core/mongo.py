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
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'league_level', 'in_cup', 'club.level']


# 挑战赛
class MongoChallenge(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 当前大区ID
        'area_id': 1,
        # 大区， {area_id: challenge_id}， 标注当前area要打的关卡，如果challenge_id为0,表示已经通关
        'areas': {}
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
    }

    STAFF_DOCUMENT = {
        'exp': 0,
        'level': 1,
        'status': null,
        'skills': {},
        'winning_rate': {},
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
class MongoBag(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 技能训练书 id: amount
        'training_skills': {},
        # 道具 id: amount
        'items': {},
    }

    COLLECTION = 'bag'


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
        'times': {}
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


# 联赛
class MongoLeagueGroup(BaseDocument):
    # 一个小组
    # 联赛分组完后，就有很多个group

    DOCUMENT = {
        '_id': null,
        'level': null,
        # clubs 记录了这个小组中的14个club 信息
        # 见下面的 CLUB_DOCUMENT
        'clubs': {},
        # events 是记录的这个小组里的一场一场的比赛，一共14场
        # 要打哪一场是根据 LeagueGame.find_order() 来决定的，
        # 这里面记录是的 event_id
        'events': [],
    }

    # club 嵌入 group 中 (为了方便查询)
    # 进行比赛查询过程是这样的：
    # 从 group 中根据 order 取到 event_id
    # 从 MongoLeagueEvent 中 根据 event_id 获取到 7 个pair
    # 再遍历这7个pair，并一次取到 club_one_id 和 club_two_id
    # 因为club是嵌套在group中的，所以可以直接获取 club信息
    # 最后开打，保存
    CLUB_DOCUMENT = {
        # 真实玩家为 str(club id), npc为uuid
        'club_id': 0,
        'match_times': 0,
        'win_times': 0,
        'score': 0,

        # 如果是npc 就会设置下面的几项
        'club_name': "",
        'manager_name': "",
        'club_flag': 1,
        'staffs': [],
        # staff_winning_rate格式{staff_id: {'win': num, 'total': num}}
        'staff_winning_rate': {}
    }

    STAFF_WINNING_RATE_DOCUMENT = {
        'win': 0,
        'total': 0
    }

    COLLECTION = "league_group"

    @classmethod
    def document_embedded_club(cls):
        return cls.CLUB_DOCUMENT.copy()


class MongoLeagueEvent(BaseDocument):
    # 每个group中对应14场 event
    # 每场会进行 7组比赛， pairs 的数量是7
    # 所以一个group总共会打 14 * 7 = 98组比赛
    DOCUMENT = {
        '_id': null,
        'start_at': 0,
        'finished': False,
        'pairs': {}
    }

    PAIR_DOCUMENT = {
        'club_one': null,
        'club_two': null,
        'club_one_win': False,
        # 战斗日志，用来回放
        'log': "",
        # 比分
        'points': [0, 0]
    }

    COLLECTION = "league_event"

    @classmethod
    def document_embedded_pair(cls):
        """

        :rtype : dict
        """
        return cls.PAIR_DOCUMENT.copy()


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
        # areas
        # {
        #     area_id: {
        #         match_id: times,
        #         match_id: times,
        #         ...
        #     },
        #     area_id: {
        #         match_id: times,
        #         match_id: times,
        #     }
        # }
        'areas': {},
        # 当前的可以打的次数， 会恢复
        'cur_times': 0,
        # 打过比赛的。用来跑定时任务
        'has_matched': False
    }

    COLLECTION = 'elite_match'

    INDEXES = ['cur_times', 'has_matched']
