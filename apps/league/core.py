# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-05-13 14:01
Description:

"""

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

        print "clubs =", clubs

        ge = GroupEntry(server_id, 1)
        for c in clubs:
            try:
                ge.add_club(c)
            except GroupEntry.ClubAddFinish:
                print "GroupEntry AddFinish"
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

        self.clubs = []


    def create_npc(self):
        npc_info = LeagueNPCInfo.objects.filter(group_id=self.id)
        taken_club_name = []
        taken_manager_name = []
        for n in npc_info:
            taken_club_name.append(n.club_name)
            taken_manager_name.append(n.manager_name)

        NPC_CLUB_NAME = CONFIG.NPC_CLUB_NAME[:]
        npc_club_name = ""
        while True:
            if not NPC_CLUB_NAME:
                raise RuntimeError("Not Available NPC_CLUB_NAME")

            npc_club_name = random.choice(NPC_CLUB_NAME)
            NPC_CLUB_NAME.remove(npc_club_name)
            if npc_club_name not in taken_club_name:
                break

        npc_manager_name = ""
        NPC_MANAGER_NAME = CONFIG.NPC_MANAGER_NAME[:]
        while True:
            if not NPC_MANAGER_NAME:
                raise RuntimeError("Not Available NPC_MANAGER_NAME")

            npc_manager_name = random.choice(NPC_MANAGER_NAME)
            NPC_MANAGER_NAME.remove(npc_manager_name)
            if npc_manager_name not in taken_manager_name:
                break

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

        npc = LeagueNPCInfo.objects.create(
            group_id=self.id,
            club_name=npc_club_name,
            manager_name=npc_manager_name,
            staffs_info=json.dumps(staffs)
        )

        return npc


    def add_club(self, club_id):
        club_info = LeagueClubInfo.objects.create(
            club_id=club_id,
            group_id=self.id,
        )

        self.clubs.append(club_info)

        if len(self.clubs) >= MAX_REAL_CLUBS_IN_ONE_CLUB:
            raise GroupEntry.ClubAddFinish()


    def finish(self, order=1):
        # 添加结束，加入NPC
        # order 表示正要开始第几场
        if not self.clubs:
            return

        npc_need_amount = MAX_CLUBS_IN_ONE_CLUB - len(self.clubs)
        for i in range(npc_need_amount):
            self.clubs.append(self.create_npc())

        # 真实和npc club 都添加完毕后
        # 开始在小组内匹配
        # 确保每个club每天要和另外两个各打一场

        battles = self.arrangement()

        # save
        for index, bs in enumerate(battles):
            this_order = index + 1

            be = BattleEntry.create(self.id, this_order)
            for club_one, club_two in bs:
                if this_order < order:
                    win_one = random.choice([True, False])
                else:
                    win_one = None

                be.add_pair(club_one, club_two, win_one)


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

        battles = []
        for day in range(7):
            this = []
            for i in range(MAX_CLUBS_IN_ONE_CLUB):
                j = i + 1 + day
                if j >= MAX_CLUBS_IN_ONE_CLUB:
                    j -= MAX_CLUBS_IN_ONE_CLUB

                this.append((self.clubs[i], self.clubs[j]))


            battles.append( this[:MAX_CLUBS_IN_ONE_CLUB/2] )
            battles.append( this[MAX_CLUBS_IN_ONE_CLUB/2:] )

        return battles


class BattleEntry(object):
    # 一次战斗
    @classmethod
    def create(cls, group_id, order):
        b = LeagueBattle.objects.create(
            league_group=group_id,
            league_order=order
        )

        return cls(b.id)


    def __init__(self, battle_id):
        self.id = battle_id

    def add_pair(self, club_one, club_two, win_one=None):
        # win_one = None  还没开始打
        # win_one = True  打过了， club_one 赢
        # win_one = False 打过了， club_two 赢
        kwargs = {
            'league_battle': self.id,
        }

        if win_one is not None:
            kwargs['win_one'] = win_one
            club_one.battle_times += 1
            club_two.battle_times += 1

        if win_one is True:
            club_one.win_times += 1
            # TODO score
        elif win_one is False:
            club_two.win_times += 1
            # TODO score

        club_one.save()
        club_two.save()


        if isinstance(club_one, LeagueClubInfo):
            kwargs['club_one'] = club_one.id
        else:
            kwargs['npc_one'] = club_one.id

        if isinstance(club_two, LeagueClubInfo):
            kwargs['club_two'] = club_two.id
        else:
            kwargs['npc_two'] = club_two.id

        pair = LeaguePair.objects.create(**kwargs)
        return pair





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

