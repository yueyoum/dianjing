# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""

from config import ConfigChallengeMatch
from config import ConfigBuilding


class Null(object):
    pass

null = Null()

# 公共数据
COMMON_DOCUMENT = {
    '_id': null,
    'value': null,
}

# 锁
LOCK_DOCUMENT = {
    '_id': null,
    'locked': False,
}

# 角色
CHARACTER_DOCUMENT = {
    '_id': null,
    'name': null,

    'club': {
        'name': null,
        'flag': null,
        'level': 1,
        'renown': 0,
        'vip': 0,
        'exp': 0,
        'gold': 0,
        'diamond': 0,

        'policy': 1,
        'match_staffs': [],
        'tibu_staffs': []
    },

    # 挑战赛ID
    'challenge_id': ConfigChallengeMatch.FIRST_ID,
    # 所属联赛小组
    'league_group': 0,
    # 是否报名参加了杯赛
    # TODO 为 in_cup 建立索引
    'in_cup': 0,
}


STAFF_DOCUMENT = {
    '_id': null,
    # 员工， 定义见下面的 STAFF_EMBEDDED
    'staffs': {},
    # 拥有的训练 训练商店中生产的是 已经生成 好的训练，所以这里是 字典 要记录训练数据
    'trainings': {}
}


STAFF_EMBEDDED_DOCUMENT = {
    'exp': 0,
    'level': 1,
    'status': 3,
    'skills': {},
    'trainings': [],
}

# 嵌入staff中
STAFF_EMBEDDED_SKILL_DOCUMENT = {
    'level': 1,
    'locked': 0
}


# 嵌入staff中
STAFF_EMBEDDED_TRAININGS_DOCUMENT = {
    'training_data': null,
    'start_at': null
}


# 训练道具商店
TRAINING_STORE_DOCUMENT = {
    '_id': null,
    'trainings': {}
}

# 嵌入到上面
TRAINING_STORE_EMBEDDED_DOCUMENT = {
    'oid': null,
    # 如果是非技能训练，这里是生成好的package的 protobuf 消息
    'item': ""
}


# 招募刷新
RECRUIT_DOCUMENT = {
    '_id': null,
    'tp': null,
    # staffs 记录刷新出来的员工
    'staffs': [],
    # times 记录刷新次数 tp: times
    'times': {}
}

# 建筑
BUILDING_DOCUMENT = {
    '_id': null,
    'buildings': {str(i): 1 for i in ConfigBuilding.can_level_up_building_ids()}
}


# 好友
DEFAULT_FRIEND_DOCUMENT = {
    '_id': null,
    # id: status
    'friends': {}
}

MAIL_DOCUMENT = {
    '_id': null,
    'mails': {}
}

MAIL_EMBEDDED_DOCUMENT = {
    # from_id 为0表示系统邮件， >0 表示来自这个id的玩家
    'from_id': null,
    'title': null,
    'content': null,
    'has_read': False,
    'create_at': null,
    'attachment': ""
}

TASK_COMMON_DOCUMENT = {
    '_id': 'task',
    'levels': {},
}

TASK_CHAR_DOCUMENT = {
    '_id': null,
    'tasks': {}
}


TASK_CHAR_EMBEDDED_DOCUMENT = {
    'num': 0,
    'status': 0,
}


# 天梯
LADDER_DOCUMENT = {
    # id: 真实玩家就是str(char_id)，npc是 uuid
    '_id': null,
    'score': 0,
    # TODO 给order加索引
    'order': 0,

    # 刷新结果 _id: order
    'refreshed': {},
    # 剩余次数
    'remained_times': 0,
    # 战报 [(template_id, args) ...]
    'logs': [],

    # 以下几项只有NPC才有
    'club_name': "",
    'club_flag': 0,
    'manager_name': "",
    'staffs': []
}


# 联赛
LEAGUE_GROUP_DOCUMENT = {
    '_id': null,
    'level': null,
    # clubs 记录了这个小组中的14个club 信息
    # 见下面的 LEAGUE_EMBEDDED_CLUB_DOCUMENT
    'clubs': {},
    # events 是记录的一组一组的比赛，一共14场
    # 要打哪一场是根据 LeagueGame.find_order() 来决定的，
    # 这里没记录是的 gevent_id
    'events': [],
}

# 每天定时打的比赛，其中有7对俱乐部比赛
LEAGUE_EVENT_DOCUMENT = {
    '_id': null,
    # 开始的时间，UTC时间戳
    'start_at': 0,
    'finished': False,
    'pairs': {}
}

# pair 嵌入到上面 event 中的 pairs
# 理由和下面一样
LEAGUE_EVENT_EMBEDDED_PAIR_DOCUMENT = {
    'club_one': null,
    'club_two': null,
    'club_one_win': False,
    # 战斗日志，用来回放
    'log': "",
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
LEAGUE_EMBEDDED_CLUB_DOCUMENT = {
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


# 杯赛
CUP_DOCUMENT = {
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

CUP_CLUB_DOCUMENT = {
    # club id
    '_id': null,
    # 开始前一小时把玩家的阵容拷贝过来
    'staffs': "",
    # 下面几项只有NPC才有
    'club_name': "",
    'manager_name': "",
    'club_flag': 1,
}


class Document(object):
    DOCUMENTS = {
        "common": COMMON_DOCUMENT,
        "lock": LOCK_DOCUMENT,

        "character": CHARACTER_DOCUMENT,

        "staff": STAFF_DOCUMENT,
        "staff.embedded": STAFF_EMBEDDED_DOCUMENT,
        "skill.embedded": STAFF_EMBEDDED_SKILL_DOCUMENT,
        "training.embedded": STAFF_EMBEDDED_TRAININGS_DOCUMENT,

        "training_store": TRAINING_STORE_DOCUMENT,
        "training_store.embedded": TRAINING_STORE_EMBEDDED_DOCUMENT,


        "recruit": RECRUIT_DOCUMENT,
        "building": BUILDING_DOCUMENT,
        "friend": DEFAULT_FRIEND_DOCUMENT,
        "mail": MAIL_DOCUMENT,
        "mail.embedded": MAIL_EMBEDDED_DOCUMENT,

        "task.common": TASK_COMMON_DOCUMENT,
        "task.char": TASK_CHAR_DOCUMENT,
        "task.char.embedded": TASK_CHAR_EMBEDDED_DOCUMENT,

        "ladder": LADDER_DOCUMENT,

        "league.group": LEAGUE_GROUP_DOCUMENT,
        "league.event": LEAGUE_EVENT_DOCUMENT,
        "league.pair": LEAGUE_EVENT_EMBEDDED_PAIR_DOCUMENT,
        "league.club": LEAGUE_EMBEDDED_CLUB_DOCUMENT,

        "cup": CUP_DOCUMENT,
        "cup.club": CUP_CLUB_DOCUMENT,
    }

    @classmethod
    def get(cls, name):
        return cls.DOCUMENTS[name].copy()


MONGO_COMMON_KEY_RECRUIT_HOT = 'recruit_hot'
MONGO_COMMON_KEY_TASK = 'task'
MONGO_COMMON_KEY_LADDER_STORE = 'ladder_store'
