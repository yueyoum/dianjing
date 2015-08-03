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

DEFAULT_COMMON_DOCUMENT = {
    '_id': null,
    'value': null,
}

DEFAULT_CHARACTER_DOCUMENT = {
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

    # 员工列表
    'staffs': {},
    # 挑战赛ID
    'challenge_id': ConfigChallengeMatch.FIRST_ID,
    # 拥有的训练ID列表
    'own_trainings': {},
    # 所属联赛小组
    'league_group': 0,
}

DEFAULT_STAFF_DOCUMENT = {
    'exp': 0,
    'level': 1,
    'status': 3,
    'skills': {},
    'trainings': [],
}

# 嵌入上staff中
DEFAULT_SKILL_DOCUMENT = {
    'level': 1,
    'locked': 0
}


DEFAULT_RECRUIT_DOCUMENT = {
    '_id': null,
    'tp': null,
    'staffs': [],
    'times': {}
}

DEFAULT_BUILDING_DOCUMENT = {
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


# 联赛
DEFAULT_LEAGUE_GROUP_DOCUMENT = {
    '_id': null,
    'level': null,
    # clubs 记录了这个小组中的14个club 信息
    'clubs': {},
    # events 是记录的一组一组的比赛，一共14场
    # 要打哪一场是根据 LeagueGame.find_order() 来决定的，
    'events': [],
}

# 每天定时打的比赛，其中有7对俱乐部比赛
DEFAULT_LEAGUE_EVENT_DOCUMENT = {
    '_id': null,
    # 开始的时间，UTC时间戳
    'start_at': 0,
    'finished': False,
    'pairs': {}
}

# pair 嵌入到上面 event 中的 pairs
# 理由和下面一样
DEFAULT_LEAGUE_PAIR_DOCUMENT = {
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
# 因为取 group 的时候，这些 clubs信息也一起返回了
# 但是要注意协议中ID的处理
# 而且 一个group中 club 只有14个，其大小是比较小的
# 所以可以嵌入
DEFAULT_LEAGUE_CLUB_DOCUMENT = {
    # club_id 为 0 表示为npc
    'club_id': 0,
    'match_times': 0,
    'win_times': 0,
    'score': 0,

    # 如果是npc才会设置下面的几项
    'club_name': "",
    'manager_name': "",
    'staffs': ""
}


class Document(object):
    DOCUMENTS = {
        "common": DEFAULT_COMMON_DOCUMENT,
        "character": DEFAULT_CHARACTER_DOCUMENT,
        "staff": DEFAULT_STAFF_DOCUMENT,
        "skill": DEFAULT_SKILL_DOCUMENT,
        "recruit": DEFAULT_RECRUIT_DOCUMENT,
        "building": DEFAULT_BUILDING_DOCUMENT,
        "friend": DEFAULT_FRIEND_DOCUMENT,
        "mail": MAIL_DOCUMENT,
        "mail.embedded": MAIL_EMBEDDED_DOCUMENT,

        "task.common": TASK_COMMON_DOCUMENT,
        "task.char": TASK_CHAR_DOCUMENT,
        "task.char.embedded": TASK_CHAR_EMBEDDED_DOCUMENT,

        "league_group": DEFAULT_LEAGUE_GROUP_DOCUMENT,
        "league_event": DEFAULT_LEAGUE_EVENT_DOCUMENT,
        "league_pair": DEFAULT_LEAGUE_PAIR_DOCUMENT,
        "league_club": DEFAULT_LEAGUE_CLUB_DOCUMENT,
    }

    @classmethod
    def get(cls, name):
        return cls.DOCUMENTS[name].copy()

