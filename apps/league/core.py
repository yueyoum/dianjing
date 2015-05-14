# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-05-13 14:01
Description:

"""

import uuid
import json
import random

import arrow

from django.conf import settings

from apps.league.models import (
    LeagueGame,
    LeagueGroup,
    LeagueBattle,
    LeaguePair,
    LeagueClubInfo,
    LeagueNPCInfo,
)
from apps.club.models import Club


from protomsg.league_pb2 import LeagueNotify
from config import CONFIG


TIME_ZONE = settings.TIME_ZONE

MAX_CLUBS_IN_ONE_CLUB = 14
MAX_REAL_CLUBS_IN_ONE_CLUB = 12



class GameEntry(object):
    # 一场联赛

    @staticmethod
    def current_order():
        def start_time_of_this_day(start_time):
            date_string = "%s %s" % ( now.format("YYYY-MM-DD"), start_time )
            return arrow.get(date_string).replace(tzinfo=TIME_ZONE)

        now = arrow.utcnow().to(TIME_ZONE)
        weekday = now.weekday()
        passed_day = weekday - 0
        passed_times = passed_day * 2 + 1

        league_time_one = start_time_of_this_day(settings.LEAGUE_START_TIME_ONE)
        if now < league_time_one:
            return passed_times

        league_time_two = start_time_of_this_day(settings.LEAGUE_START_TIME_TWO)
        if now < league_time_two:
            return passed_times + 1

        return passed_times + 2



    @staticmethod
    def new(server_id):
        # 创建新联赛
        LeagueGroup.objects.all().delete()
        LeagueBattle.objects.all().delete()
        LeaguePair.objects.all().delete()
        LeagueClubInfo.objects.all().delete()
        LeagueNPCInfo.objects.all().delete()


        # 新的一场联赛
        LeagueGame.objects.create()

        # 分组
        # TODO 小组级别
        clubs = Club.objects.filter(server_id=server_id).values_list('id', flat=True)

        ge = GroupEntry(server_id, 1)
        for c in clubs:
            try:
                ge.add_club(c)
            except GroupEntry.ClubAddFinish:
                ge.finish()

                # new group
                ge = GroupEntry(server_id, 1)

        ge.finish()


    def __init__(self, server_id):
        self.server_id = server_id

        if LeagueGame.objects.count() == 0:
            # 这是第一个进游戏的人
            self.order = GameEntry.current_order()
            LeagueGame.objects.create(current_order=self.order)
        else:
            self.order = LeagueGame.objects.order_by('-id').first().current_order


    def add_to_already_started_league(self, club_id):
        # 周一零点以后进来的新用户错过了匹配时间
        # 给这个新用户一堆NPC，将其加入联赛

        ge = GroupEntry(self.server_id, 1)
        ge.add_club(club_id)
        ge.finish(order=self.order)




class GroupEntry(object):
    # 一个小组
    class ClubAddFinish(Exception):
        pass


    def __init__(self, server_id, level):
        self.server_id = server_id
        self.level = level

        self.group = LeagueGroup.objects.create(
            server_id=server_id,
            level=level
        )

        self.id = self.group.id

        self.club_ids = []
        self.clubs = []

        self.npc_taken_club_name = set()
        self.npc_taken_manager_name = set()


    def create_npc(self):
        # 随机取club name
        npc_club_name = ""
        NPC_CLUB_NAME = CONFIG.NPC_CLUB_NAME[:]
        while True:
            if not NPC_CLUB_NAME:
                raise RuntimeError("Not Available NPC_CLUB_NAME")

            npc_club_name = random.choice(NPC_CLUB_NAME)
            NPC_CLUB_NAME.remove(npc_club_name)
            if npc_club_name not in self.npc_taken_club_name:
                break

        self.npc_taken_club_name.add(npc_club_name)

        # 随机取manager name
        npc_manager_name = ""
        NPC_MANAGER_NAME = CONFIG.NPC_MANAGER_NAME[:]
        while True:
            if not NPC_MANAGER_NAME:
                raise RuntimeError("Not Available NPC_MANAGER_NAME")

            npc_manager_name = random.choice(NPC_MANAGER_NAME)
            NPC_MANAGER_NAME.remove(npc_manager_name)
            if npc_manager_name not in self.npc_taken_manager_name:
                break

        self.npc_taken_manager_name.add(npc_manager_name)

        npc_club = random.choice(CONFIG.NPC_CLUB.values())

        all_staffs = CONFIG.STAFF.keys()
        staff_ids = random.sample(all_staffs, 5)
        staffs = {}
        for i in staff_ids:
            p = {
                'jg': random.randint(npc_club.jingong_low, npc_club.jingong_high) * self.level,
                'qz': random.randint(npc_club.qianzhi_low, npc_club.qianzhi_high) * self.level,
                'xt': random.randint(npc_club.xintai_low, npc_club.xintai_high) * self.level,
                'bb': random.randint(npc_club.baobing_low, npc_club.baobing_high) * self.level,
                'fs': random.randint(npc_club.fangshou_low, npc_club.fangshou_high) * self.level,
                'yy': random.randint(npc_club.yunying_low, npc_club.yunying_high) * self.level,
                'ys': random.randint(npc_club.yishi_low, npc_club.yishi_high) * self.level,
                'cz': random.randint(npc_club.caozuo_low, npc_club.caozuo_high) * self.level,
                # TODO skill
                'skills': {}
            }

            staffs[i] = p

        return (npc_club_name, npc_manager_name, json.dumps(staffs))


    def add_club(self, club_id):
        self.club_ids.append(club_id)

        if len(self.club_ids) >= MAX_REAL_CLUBS_IN_ONE_CLUB:
            raise GroupEntry.ClubAddFinish()


    def finish(self, order=1):
        # 添加结束，加入NPC
        # order 表示正要开始第几场
        if not self.club_ids:
            return

        club_objs = [
            LeagueClubInfo(
                id=str(uuid.uuid4()),
                club_id=club_id,
                group_id=self.id,
            ) for club_id in self.club_ids
        ]

        self.clubs = LeagueClubInfo.objects.bulk_create(club_objs)

        npc_objs = []
        npc_need_amount = MAX_CLUBS_IN_ONE_CLUB - len(self.clubs)
        for i in range(npc_need_amount):
            npc_club_name, npc_manager_name, npc_staffs = self.create_npc()
            npc_objs.append(
                LeagueNPCInfo(
                    id=str(uuid.uuid4()),
                    group_id=self.id,
                    club_name=npc_club_name,
                    manager_name=npc_manager_name,
                    staffs=npc_staffs
                )
            )

        npcs = LeagueNPCInfo.objects.bulk_create(npc_objs)

        self.clubs.extend(npcs)

        # 真实和npc club 都添加完毕后
        # 开始在小组内匹配
        # 确保每个club每天要和另外两个各打一场

        battles = self.arrangement()

        bm = BattleManager(self.id)
        bm.add(battles)
        bm.create()


    def arrangement(self):
        # 对这些俱乐部进行排列
        # 算法实例代码
        # import pprint
        #
        # a = range(1, 15)
        # print a
        #
        # battles = []
        # for d in range(7):
        #     xx = []
        #     for i in range(len(a)):
        #         j = i + 1 + d
        #         if j >= len(a):
        #             j -= len(a)
        #
        #         xx.append((a[i], a[j]))
        #
        #     battles.append(xx)
        # pprint.pprint(battles)
        #

        random.shuffle(self.clubs)

        battles = []
        for day in range(7):
            this = []
            for i in range(MAX_CLUBS_IN_ONE_CLUB):
                j = i + 1 + day
                while j >= MAX_CLUBS_IN_ONE_CLUB:
                    j -= MAX_CLUBS_IN_ONE_CLUB

                this.append((self.clubs[i], self.clubs[j]))


            battles.append( this[:MAX_CLUBS_IN_ONE_CLUB/2] )
            battles.append( this[MAX_CLUBS_IN_ONE_CLUB/2:] )

        return battles



class BattleManager(object):
    def __init__(self, group_id):
        self.group_id = group_id
        self.battles = []


    def add(self, battles):
        self.battles = battles


    def create(self):
        battle_objs = [
            LeagueBattle(
                id=uuid.uuid4(),
                league_group=self.group_id,
                league_order=i+1
            ) for i in range(len(self.battles))
        ]

        LeagueBattle.objects.bulk_create(battle_objs)

        pair_objs = []
        for index, pairs in enumerate(self.battles):
            for club_one, club_two in pairs:
                if isinstance(club_one, LeagueClubInfo):
                    club_one_type = 1
                else:
                    club_one_type = 2

                if isinstance(club_two, LeagueClubInfo):
                    club_two_type = 1
                else:
                    club_two_type = 2

                obj = LeaguePair(
                    league_battle=battle_objs[index].id,
                    club_one=club_one.id,
                    club_two=club_two.id,
                    club_one_type=club_one_type,
                    club_two_type=club_two_type,
                )

                pair_objs.append(obj)

        LeaguePair.objects.bulk_create(pair_objs)




class League(object):
    def __init__(self, server_id, char_id, club_id):
        self.server_id = server_id
        self.char_id = char_id
        self.club_id = club_id

        self.load_info()


    def load_info(self):
        try:
            club_info = LeagueClubInfo.objects.get(club_id=self.club_id)
        except LeagueClubInfo.DoesNotExist:
            ge = GameEntry(self.server_id)
            ge.add_to_already_started_league(self.club_id)



    def send_notify(self):
        msg = LeagueNotify()

