# -*- coding: utf-8 -*-

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
# | LeagueBattle |         | LeagueBattle |     | LeagueBattle |          | LeagueBattle |
# +--------------+         +--------------+     +--------------+          +--------------+
# | 一场比赛 #1   |         | 一场比赛 #14  |     | 一场比赛 #1    |         | 一场比赛 #14   |
# | club vs club |         | club vs club |     | club vs club  |         | club vs club |
# +--------------+         +--------------+     +--------------+          +--------------+
#
# 一场联赛是由很多小组赛组成的
# 小组根据俱乐部等级分组
# 每个小组有14支俱乐部 （包括NPC）
# 这14支俱乐部 分配为 14场比赛，每支俱乐部要参与两场比赛
# 每天 定时开启两场比赛，刚好一周14场
# 每天该开始哪场比赛由 LeagueGame 中的 current_order 确定
# 每周刷新的时候， LeagueGroup, LeagueBattle, LeagueClubInfo, LeagueNPCInfo 都需要清空


class LeagueGame(models.Model):
    # 联赛
    id = BigAutoField(primary_key=True)

    # 当前联赛进行到第几场
    current_order = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "league_game"
        ordering = ('-id',)
        verbose_name = "League Game"
        verbose_name_plural = "League Game"


class LeagueGroup(models.Model):
    # 联赛小组
    # 俱乐部是分配到小组中进行比赛的。
    # 每个小组14个队伍（包括NPC俱乐部）
    id = BigAutoField(primary_key=True)
    # 此小组所属的级别
    level = models.IntegerField()

    class Meta:
        db_table = 'league_group'
        verbose_name = "League Group"
        verbose_name_plural = "League Group"


class LeagueBattle(models.Model):
    # 小组中，一场比赛
    # 对抗双方 是两支俱乐部（包括NPC俱乐部）
    id = BigAutoField(primary_key=True)
    league_group = models.BigIntegerField(db_index=True)
    # 本场比赛的排序，属于第几组
    league_order = models.IntegerField(db_index=True)

    # 对抗的俱乐部 如果为0表示为NPC，否则从ClubInfo中获取信息
    club_one = models.BigIntegerField(default=0)
    club_two = models.BigIntegerField(default=0)

    # 如果是NPC，从NPCInfo中获取信息
    npc_one = models.BigIntegerField(default=0)
    npc_two = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'league_battle'
        verbose_name = "League Battle"
        verbose_name_plural = "League Battle"


class LeagueClubInfo(models.Model):
    id = BigAutoField(primary_key=True)
    club_id = models.IntegerField(db_index=True)

    # 此club属于的小组。
    # 一个club会属于两场 LeagueBattle
    # 但只会属于一个 小组 LeagueGroup
    # 不过 那两场 LeagueBattle 肯定是属于同一个 LeagueGroup的
    # 这里记录冗余的 group_id 是为了从 club_id 直接查询到 其 group_id
    group_id = models.BigIntegerField()

    # 已战斗次数
    battle_times = models.IntegerField()
    # 获得的积分
    score = models.IntegerField()

    class Meta:
        db_table = 'league_club_info'
        verbose_name = "Club Info"
        verbose_name_plural = "Club Info"


class LeagueNPCInfo(models.Model):
    # NPC俱乐部信息
    id = BigAutoField(primary_key=True)
    club_name = models.CharField(max_length=255)
    manager_name = models.CharField(max_length=255)
    npc_id = models.IntegerField()

    # 员工信息
    staffs_info = models.TextField()

    class Meta:
        db_table = 'league_npc_info'
        verbose_name = "NPC Info"
        verbose_name_plural = "NPC Info"
