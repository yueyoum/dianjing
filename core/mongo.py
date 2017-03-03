# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""

import copy
from core.db import MongoDB
from pymongo.collection import Collection
from pymongo.write_concern import WriteConcern

# NOTE:
# 需要 mongodb 3.2 及以上版本

def ensure_index(server_id):
    for i in BaseDocument.__subclasses__():
        i.create_indexes(server_id)

collection_cache = {}

class BaseDocument(object):
    DOCUMENT = {}
    COLLECTION = None
    INDEXES = []
    UNIQUE = []

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
        key = "{0}{1}".format(cls.__name__, server_id)

        if key not in collection_cache:
            write_concern = cls.get_write_concern()
            coll = Collection(MongoDB.get(server_id), cls.COLLECTION, write_concern=write_concern)
            collection_cache[key] = coll

        return collection_cache[key]

    @classmethod
    def get_write_concern(cls):
        return None

    @classmethod
    def exist(cls, server_id, _id):
        doc = cls.db(server_id).find_one({'_id': _id}, {'_id': 1})
        return True if doc else False

    @classmethod
    def create_indexes(cls, server_id):
        for i in cls.INDEXES:
            cls.db(server_id).create_index(i)

        for i in cls.UNIQUE:
            cls.db(server_id).create_index(i, unique=True)


class Null(object):
    pass


null = Null()


# 就是 club
class MongoCharacter(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'create_at': 0,
        'last_login': 0,


        'name': null,
        'flag': 1,
        'level': 1,
        'exp': 0,
        'renown': 0,
        'gold': 0,
        'diamond': 0,
        'crystal': 0,
        'gas': 0,
    }

    COLLECTION = "character"
    INDEXES = ['name', 'last_login', 'level',]

# 登陆某一个服 日志
class MongoCharacterLoginLog(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'char_id': null,
        'timestamp': null,
    }

    COLLECTION = 'character_login_log'
    INDEXES = ['char_id', 'timestamp',]


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
        'star': 0,
        'level_exp': 0,
        'star_exp': 0,

        # 四件装备
        'equip_mouse': '',
        'equip_keyboard': '',
        'equip_monitor': '',
        'equip_decoration': '',
        'equip_special': '',
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
        'position': [],

        # 新加 选择阵型，升级
        'levels': {},
        'using': 0,
    }

    DOCUMENT_SLOT = {
        'staff_id': "",
        'unit_id': 0,
        'policy': 1,
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

        # 如果是特殊装备，还有下面属性
        # 从哪个打造书而来
        'from_id': 0,
        # 打造类型
        'gen_tp': 0,
        'growing': 0,
        'properties': [],
        'skills': [],
    }

    COLLECTION = 'bag'

# 打造装备
class MongoSpecialEquipment(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'item_id': 0,
        'finish_at': 0,
        'tp': 0,

        # 每种类型的积分
        'score': {
            '1': 0,
            '2': 0,
        }
    }

    COLLECTION = 'special_equipment'

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
        # 有些类型的邮件，只要一个。 这里用unique_id来标示
        'unique_id': '',
    }

    COLLECTION = "mail"

    @classmethod
    def document_mail(cls):
        return copy.deepcopy(cls.MAIL_DOCUMENT)

# 共享邮件
# 一般用于全服发送的邮件
class MongoSharedMail(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 这邮件是给谁的
        'for_char_ids': [],

        # 其他字段就是上面的 MAIL_DOCUMENT
    }

    COLLECTION = "shared_mail"
    INDEXES = ['for_char_ids', 'create_at']


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

        # 历史最高排名
        'max_rank': 0,
        # 刷出来的对手
        'rival': 0,
        # 荣耀领奖记录
        # NOTE: 这里特殊处理，记录的是 当天日期: 领奖记录列表
        # 玩家每次登陆时删除过期的日期
        'honor_rewards': {},
        # 被挑战日志
        'logs': [],
        # 积分
        'point': 0,
        'search_index': 0,

        # 连胜次数
        'continue_win': 0,
        # 总共打的次数
        'match_times': 0,
    }

    COLLECTION = 'arena'


# 竞技场积分排名
# 排名规则：
# 1， 根据score排名，score大的排在前面
# 2， 如果score一样，则根据达到这个score的先后顺序排序
#
# 使用 聚合框架 完成排名检索
# 首先查找自己的score 和 在此score中排序
# db.arena_score.aggregate([
#     {$match: {char_ids: <Char ID>}},
#     {$unwind: {path: "$char_ids", includeArrayIndex: "index"}},
#     {$match: {char_ids: <Char ID>}}
# ])
# 返回结果 {"_id": <_ID>, "index": <INDEX>}
# _ID 就是自己的score, 记作MyScore

# 接下来是找比MyScore大的有多少人
# db.arena_score.aggregate([
#     {$match: {_id: {$gt: <MyScore>}}},
#     {$project: {amount: {$size: "$char_ids"}}},
#     {$group: {_id: null, amount: {$sum: "$amount"}}}
# ])
# 会得到结果 {"_id": null, "amount": <AMOUNT>}
#
# 自己的排名就是 AMOUNT + INDEX + 1
#
class MongoArenaScore(BaseDocument):
    DOCUMENT = {
        # _id 就是score
        '_id': 0,
        # 这里面是 角色ID列表，
        'char_ids': [],
    }

    COLLECTION = 'arena_score'
    INDEXES = ['char_ids',]

# 每日胜率
class MongoArenaWinning(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'total_count': 0,
        'win_count': 0,
        'winning': 0,
    }

    COLLECTION = 'arena_winning'
    INDEXES = ['winning',]


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

        # 历史最高层
        'history_max_level': 0,
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


# 福利
class MongoWelfare(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 已经签到的次数，循环
        # 这个需要ValueLog配合
        # valuelog 检测今天是否签过了
        # signin 表示已经签的次数， 当前应该签到的次数就得 +1
        'signin': 0,
        # 已经领奖的 新手礼包id列表
        'new_player': [],
        # 已经领取的等级礼包
        'level_reward': [],
    }

    COLLECTION = 'welfare'


# 操作日志 也可以用来统计最近在线玩家
class MongoOperationLog(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'char_id': null,
        'action': '',
        'ret': 0,
        'timestamp': 0,
        'cost_millisecond': 0,
    }

    COLLECTION = 'operation_log'
    INDEXES = ['char_id', 'timestamp', 'cost_millisecond']

    @classmethod
    def get_write_concern(cls):
        return WriteConcern(w=0)

# 资源代币
# 现在所有的东西都是配置在item里面的，其实这些代币资源应该同意放在一起
# 这样好处理。
# 比如 gold, diamond, point, honor, xxx 都放在一起
# 但是以前是分模块 自己处理自己的， 其实是没设计好
# 后面的新资源，都同意在这里记录
class MongoResource(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'resource': {}
    }

    COLLECTION = 'resource'

# 公会
class MongoUnion(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'create_at': 0,
        'name': '',
        'owner': 0,
        'level': 1,
        'contribution': 0,
        'bulletin': '',
        'apply_list': [],

        'explore_point': 0,
    }

    COLLECTION = 'union'
    INDEXES = ['apply_list', 'explore_point']
    UNIQUE = ['name', 'owner',]

class MongoUnionMember(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'joined': '',
        'joined_at': 0,
        'contribution': 0,
        'today_contribution': 0,

        'explore_point': 0,
        'explore_staff': 0,
        'harass_staff': 0,

        # 当天是否退出或者被踢
        'quit_flag': False,
        'kick_flag': False,

        # 公会技能， id: level
        # 初始0级的，不在这里面记录
        # 只记录升级过的
        'skills': {},
    }

    COLLECTION = 'union_member'
    INDEXES = ['joined', 'explore_point']


# 充值
class MongoPurchase(BaseDocument):
    DOCUMENT = {
        '_id': null,

        'yueka_remained_days': 0,
        # 是不是新买的月卡，  因为要立即发送，这个标识用来过滤
        'yueka_new': True,

        # 首充礼品是否已经领取
        'first_reward_got': False,
    }

    COLLECTION = 'purchase'
    INDEXES = ['yueka_remained_days', 'yueka_new']

class MongoPurchaseLog(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'char_id': null,
        'goods_id': 0,

        # 充值钻石
        'got': 0,
        # 充值确切获得钻石，包括翻倍，赠送等等
        'actual_got': 0,
        'timestamp': 0,
    }

    COLLECTION = 'purchase_log'
    INDEXES = ['char_id', 'timestamp']


# 新手活动
class MongoActivityNewPlayer(BaseDocument):
    DOCUMENT = {
        '_id': null,

        # 已经完成的
        'done': [],

        # 新手每日购买，买过的天数
        'daily_buy': [],
    }

    COLLECTION = 'activity_new_player'

# 每日在线时长
class MongoActivityOnlineTime(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 可以领奖的ID，初始化就是配置中最小的ID，0表示当天的已经全部领完了
        'doing': 0,
    }

    COLLECTION = 'activity_online_time'

# 冲关
class MongoActivityChallenge(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 已经完成领奖的
        'done': [],
    }

    COLLECTION = 'activity_challenge'


# 俱乐部排行榜
class MongoClubLeaderboard(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'level': 0,
        'power': 0,
    }

    COLLECTION = 'club_leaderboard'
    INDEXES = ['level', 'power']

# 掠夺阵型， 结构和 MongoFormation 一样，为了复用代码
class MongoPlunderFormationWay1(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # slot_id: data
        # 只保存开了的， slot_id 从1 递增
        'slots': {},
        # slot_id 序列， 0 表示这个位置（index）的 slot 没有开启
        'position': [],
    }

    DOCUMENT_SLOT = {
        'staff_id': "",
        'unit_id': 0,
        'policy': 1,
    }

    @classmethod
    def document_slot(cls):
        return copy.deepcopy(cls.DOCUMENT_SLOT)

    COLLECTION = 'plunder_formation_way1'

class MongoPlunderFormationWay2(MongoPlunderFormationWay1):
    COLLECTION = 'plunder_formation_way2'

class MongoPlunderFormationWay3(MongoPlunderFormationWay1):
    COLLECTION = 'plunder_formation_way3'

class MongoPlunder(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 掠夺功能是否激活
        'active': False,
        # 搜索出的对手, 列表的元素是字典
        'search': [],

        # 正在进行的
        'matching': {
            'id': 0,
            # 三路比赛的结果列表，0 没有开始，1 胜利, 2 失败
            'result': [0, 0, 0],
            # 类型 是 掠夺，还是复仇
            'tp': 0,
        },

        # 掠夺剩余次数
        'plunder_remained_times': 0,

        # 基地的
        'level': 1,
        'exp': 0,
        'product_level': 1,
        'loss_percent': 0,
        # 复仇列表， 因为可能列表中有重复的人， 所以还需要一个 unique_id
        # [(unique_id, real_id), ...]
        'revenge_list': [],
        # 上次的产出， 领了就清空，没领就到下次生成的时候覆盖
        'drop': '',
        # 恢复掠夺次数
        'recover_times': 0,

        # 每日奖励情况
        # 这里用日期做key，这样第二天就自然更新了， 但是要清除以前的key
        'daily_reward': {}
    }

    SEARCH_DOCUMENT = {
        'id': null,
        # 是否侦查过了
        'spied': False,

        # NPC才有的属性
        'name': '',
        'station_level': 0,
        'ways_npc': [],
    }

    COLLECTION = 'plunder'
    INDEXES = ['active', 'plunder_remained_times', 'loss_percent',]


# 每日胜率
class MongoPlunderWinning(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'total_count': 0,
        'win_count': 0,
        'winning': 0,
    }

    COLLECTION = 'plunder_winning'
    INDEXES = ['winning',]


# 宴会 这部分功能用 socket 实现
class MongoParty(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # 获得的 天赋 , 定时清理
        'talent_id': 0,
    }

    COLLECTION = 'party'
    INDEXES = ['talent_id',]

# 助威
class MongoInspire(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # slot id 从配置中来, value 是 staff_id
        # 只记录开启的
        'slots': {}
    }

    COLLECTION = 'inspire'


# 争霸赛 - 阵型 （和掠夺阵型一样）
class MongoChampionshipFormationWay1(BaseDocument):
    DOCUMENT = {
        '_id': null,
        # slot_id: data
        # 只保存开了的， slot_id 从1 递增
        'slots': {},
        # slot_id 序列， 0 表示这个位置（index）的 slot 没有开启
        'position': [],
    }

    DOCUMENT_SLOT = {
        'staff_id': "",
        'unit_id': 0,
        'policy': 1,
    }

    @classmethod
    def document_slot(cls):
        return copy.deepcopy(cls.DOCUMENT_SLOT)

    COLLECTION = 'championship_formation_way1'

class MongoChampionshipFormationWay2(MongoChampionshipFormationWay1):
    COLLECTION = 'championship_formation_way2'

class MongoChampionshipFormationWay3(MongoChampionshipFormationWay1):
    COLLECTION = 'championship_formation_way3'


# 争霸赛 - 个人
class MongoChampionship(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'active': False,
        'applied': False,
        # 下注, level: {'club_id': 0, 'bet_id': 0}
        'bet': {},
        'has_bet': False,
    }

    COLLECTION = 'championship'
    INDEXES = ['applied', 'has_bet',]


# 争霸赛 - 小组
class MongoChampionshipGroup(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'member_ids': [],
        # 信息, id: info
        'info': {},
        # 分数, id: score
        'scores': {},
        # 日志
        'logs': {},
        # 将要进行第几次
        'match_times': 1,
    }

    MATCH_LOG_DOCUMENT = {
        'timestamp': 0,
        'target_name': '',
        'got_score': 0,
        'way_wins': [0, 0, 0],
        'record_ids': ['', '', ''],
    }

    @classmethod
    def document_match_log(cls):
        return copy.deepcopy(cls.MATCH_LOG_DOCUMENT)

    COLLECTION = 'championship_group'
    INDEXES = ['member_ids',]

# 争霸赛 - XX强
class MongoChampionshipLevel(BaseDocument):
    DOC_ID = 'championship_level'

    DOCUMENT = {
        '_id': DOC_ID,
        'info': {},
        # XX强, xx: level_doc
        # xx就是 16, 8, 4, 2, 1
        'levels': {},
        # 当前level
        'current_level': 16,
    }

    LEVEL_DOCUMENT = {
        'member_ids': [],
        'way_wins': {},
        'record_ids': {},
    }

    COLLECTION = 'championship_level'

    @classmethod
    def document_level(cls):
        return copy.deepcopy(cls.LEVEL_DOCUMENT)

# 争霸赛历史前三
class MongoChampionHistory(BaseDocument):
    DOC_ID = 'championship_history'

    DOCUMENT = {
        '_id': DOC_ID,
        'member_ids': [],
        'info': {},
    }

    COLLECTION = 'championship_history'


# 战斗录像
class MongoMatchRecord(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'id_one': '',
        'id_two': '',
        'club_match': '',
        'record': '',
        'create_at': 0,
    }

    COLLECTION = 'match_record'
    INDEXES = ['id_one', 'id_two', 'create_at',]


# 标志
class MongoMark(BaseDocument):
    DOCUMENT = {
        '_id': null,
        'create_at': 0,
    }

    COLLECTION = 'mark'
