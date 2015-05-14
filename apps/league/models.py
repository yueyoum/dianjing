# -*- coding: utf-8 -*-

import uuid

from django.db import models

from utils.dbfields import BigAutoField


#                                      +------------+
#                                      | LeagueGame |  每周开始新的联赛
#                                      +------------+
#                                            |
#                  +-----------------------------------------------+
#                  |                                               |
#           +-------------+                                    +-------------+
#           | LeagueGroup |                                    | LeagueGroup |
#           +-------------+                                    +-------------+
#           |  小组 #1     |                                   |   小组 #N    |
#           +-------------+                                    +-------------+
#                  |                                                 |
#      +--------------------------+                     +------------------------+
#      |                          |                     |                        |
# +--------------+    ...  +--------------+     +--------------+    ...   +--------------+
# | LeaguePair   |         | LeaguePair   |     | LeaguePair   |          | LeaguePair   |
# +--------------+         +--------------+     +--------------+          +--------------+
# | 一次比赛 #1   |         | 一次比赛 #14  |     | 一次比赛 #1    |         | 一次比赛 #14   |
# | club vs club |         | club vs club |     | club vs club  |         | club vs club |
# +--------------+         +--------------+     +--------------+          +--------------+
#       |
# +--------------+
# | LeaguePair   |
# +--------------+          ......
# | 许多对俱乐部   |
# +--------------+
#
#
# 一场联赛是由很多小组赛组成的
# 小组根据俱乐部等级分组
# 每个小组有14支俱乐部 （包括NPC）
# 这14支俱乐部 分配为 14场比赛，每支俱乐部每天要参与两场比赛
# 每天 定时开启两场比赛，刚好一周14场
# 每天该开始哪场比赛由 LeagueGame 中的 current_order 确定
# 每周刷新的时候， LeagueGroup, LeagueBattle, LeaguePair, LeagueClubInfo, LeagueNPCInfo 都需要清空


class LeagueGame(models.Model):
    # 联赛
    id = BigAutoField(primary_key=True)

    # 当前联赛应该要进行第几场
    current_order = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "league_game"
        verbose_name = "League Game"
        verbose_name_plural = "League Game"


class LeagueGroup(models.Model):
    # 联赛小组
    # 俱乐部是分配到小组中进行比赛的。
    # 每个小组14个队伍（包括NPC俱乐部）
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    server_id = models.IntegerField(db_index=True)
    # 此小组所属的级别
    level = models.IntegerField()

    class Meta:
        db_table = 'league_group'
        verbose_name = "League Group"
        verbose_name_plural = "League Group"


class LeagueBattle(models.Model):
    # 时间点开始的比赛
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    league_group = models.UUIDField(db_index=True)
    # 排序
    league_order = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'league_battle'
        verbose_name = "League Battle"
        verbose_name_plural = "League Battle"


class LeaguePair(models.Model):
    # 小组中，一场比赛
    # 对抗双方 是两支俱乐部（包括NPC俱乐部）
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    league_battle = models.UUIDField(db_index=True)

    # 对抗的俱乐部 如果为0表示为NPC，否则从ClubInfo中获取信息
    club_one = models.UUIDField()
    club_two = models.UUIDField()

    # 1 club， 2 npc
    club_one_type = models.SmallIntegerField()
    club_two_type = models.SmallIntegerField()

    # club_one 赢？
    win_one = models.BooleanField(default=False)

    class Meta:
        db_table = 'league_pair'
        verbose_name = "League Pair"
        verbose_name_plural = "League Pair"


class LeagueClubInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    club_id = models.IntegerField(db_index=True)

    # 此club属于的小组。
    # 一个club会属于两场 LeagueBattle
    # 但只会属于一个 小组 LeagueGroup
    # 不过 那两场 LeagueBattle 肯定是属于同一个 LeagueGroup的
    # 这里记录冗余的 group_id 是为了从 club_id 直接查询到 其 group_id
    group_id = models.UUIDField(db_index=True)

    # 已战斗次数
    battle_times = models.IntegerField(default=0)
    # 胜利次数
    win_times = models.IntegerField(default=0)
    # 获得的积分
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'league_club_info'
        verbose_name = "Club Info"
        verbose_name_plural = "Club Info"


class LeagueNPCInfo(models.Model):
    # NPC俱乐部信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # 这里记录 小组ID 是因为同一小组中的NPC不能重民
    group_id = models.UUIDField(db_index=True)

    club_name = models.CharField(max_length=255)
    manager_name = models.CharField(max_length=255)

    # 员工信息
    staffs = models.TextField()

    battle_times = models.IntegerField(default=0)
    win_times = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'league_npc_info'
        verbose_name = "NPC Info"
        verbose_name_plural = "NPC Info"
