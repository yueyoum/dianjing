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

        # 挑战赛ID
        'challenge_id': null,
        # 所属联赛小组
        'league_group': 0,
        'league_level': 1,
        # 是否报名参加了杯赛
        'in_cup': 0,
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'league_level', 'in_cup']

    @classmethod
    def document(cls):
        from config import ConfigChallengeMatch

        doc = super(MongoCharacter, cls).document()
        doc['challenge_id'] = ConfigChallengeMatch.FIRST_ID
        return doc


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
        # 拥有的训练 训练商店中生产的是 已经生成 好的训练，所以这里是 字典 要记录训练数据
        'trainings': {}
    }

    STAFF_DOCUMENT = {
        'exp': 0,
        'level': 1,
        'status': 3,
        'skills': {},
        'trainings': [],
    }

    # 嵌入staff中
    STAFF_SKILL_DOCUMENT = {
        'level': 1,
        'locked': 0
    }

    # 嵌入staff中
    STAFF_TRAININGS_DOCUMENT = {
        'oid': null,
        'item': null,
        'start_at': null
    }

    @classmethod
    def document_staff(cls):
        return cls.STAFF_DOCUMENT.copy()

    @classmethod
    def document_staff_skill(cls):
        return cls.STAFF_SKILL_DOCUMENT.copy()

    @classmethod
    def document_staff_trainings(cls):
        return cls.STAFF_TRAININGS_DOCUMENT.copy()

    COLLECTION = "staff"


# 训练商店 和 背包
class MongoTraining(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'store': {},
        'bag': {}
    }

    TRAINING_ITEM_DOCUMENT = {
        'oid': null,
        'item': null,
    }

    @classmethod
    def document_training_item(cls):
        return cls.TRAINING_ITEM_DOCUMENT.copy()

    COLLECTION = "training"


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

    COLLECTION = "building"


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
        'tasks': {}
    }

    TASK_DOCUMENT = {
        'num': 0,
        'status': 0,
    }

    COLLECTION = "task"

    @classmethod
    def document_task(cls):
        return cls.TASK_DOCUMENT.copy()


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
    DOCUMENT = {
        '_id': null,
        'level': null,
        # clubs 记录了这个小组中的14个club 信息
        # 见下面的 LEAGUE_EMBEDDED_CLUB_DOCUMENT
        'clubs': {},
        # events 是记录的一组一组的比赛，一共14场
        # 要打哪一场是根据 LeagueGame.find_order() 来决定的，
        # 这里面记录是的 event_id
        'events': [],
    }

    # club 嵌入 group 中
    # 为了降低查询IO请求
    # 如果不嵌入，那么查询过程是这样的：
    # 从 group 中根据 order 取到 [pair_id, pair_id,...]
    # 再遍历这7个pair_id，并以此从 pair 中取到 club_one_id和 club_two_id
    # 然后 再根据这些 club_id 到 club 中取 club 信息...
    # 每次 取完 group 和 pair 后，还有 额外的14次IO
    # 如果 有大量的分组 (group)，那么这个IO开销将是很消耗系统资源的
    # 如果嵌套起来， 那么只有两次IO
    # 因为取 group 的时候，这些 clubs 信息也一起返回了
    # 但是要注意协议中ID的处理
    # 而且 一个group中 club 只有14个，其大小是比较小的
    # 所以可以嵌入
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
        'staffs': []
    }

    COLLECTION = "league_group"

    @classmethod
    def document_embedded_club(cls):
        return cls.CLUB_DOCUMENT.copy()


class MongoLeagueEvent(BaseDocument):
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
        'sponsor_to_id': 0,     # 赞助了谁
        'income': 0,            # 总收益
        'sponsors': {},         # id: income.  这里的income不清零
        'logs': []              # [(template_id, args), ...]
    }

    COLLECTION = "sponsor"


# 活动
class MongoActivity(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 已经获取奖励的 活动item ID
        'gots': {}
    }

    COLLECTION = "activity"


# 签到
class MongoSignIn(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'sign': {}
    }

    SIGN_DOCUMENT = {
        'last_sign_at': 0,      # 日期
        'last_sign_day': 0,     # day 是对应配置中的第几天。而不是真是日期中的天
        'is_continued': True,
    }

    COLLECTION = "sign_in"

    @classmethod
    def document_sign(cls):
        return cls.SIGN_DOCUMENT.copy()
