# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-05-18 15:28
Description:

"""
import random

import uwsgidecorators

from django.conf import settings

from utils.log import Logger

from apps.league.core import GameEntry
from apps.league.models import LeagueGame, LeagueBattle, LeaguePair, LeagueClubInfo, LeagueNPCInfo
from apps.server.models import Server


START_TIME_ONE = settings.LEAGUE_START_TIME_ONE.split(':')
START_TIME_TWO = settings.LEAGUE_START_TIME_TWO.split(':')


# 每周创建新的联赛
@uwsgidecorators.cron(0, 0, -1, -1, 1)
def league_new(signum):
    logger = Logger("league_new")

    servers = Server.opened_servers()
    for s in servers:
        logger.write("server {0} start".format(s.id))

        GameEntry.new(s.id)

        logger.write("server {0} finish".format(s.id))

    logger.write("done")
    logger.close()


# 每天定时开启的比赛
def league_battle(signum):
    logger = Logger("league_battle")

    current_order = GameEntry.current_order()
    battles = LeagueBattle.objects.filter(league_order=current_order)

    logger.write("League Battle Start. Order: {0}, Battles: {1}".format(current_order, battles.count()))


    def club_info_saver(Model, info_id, win):
        club = Model.objects.get(id=info_id)
        club.battle_times += 1
        if win:
            club.win_times += 1
            # FIXME score
            club.score += 10

        club.save()


    for b in battles:
        pairs = LeaguePair.objects.filter(league_battle=b.id)
        for pair in pairs:
            # TODO real battle
            win_one = random.choice([True, False])

            pair.win_one = win_one
            pair.save()

            if pair.club_one_type == 1:
                club_info_saver(LeagueClubInfo, pair.club_one, pair.win_one)
            else:
                club_info_saver(LeagueNPCInfo, pair.club_one, pair.win_one)

            if pair.club_two_type == 1:
                club_info_saver(LeagueClubInfo, pair.club_two, not pair.win_one)
            else:
                club_info_saver(LeagueNPCInfo, pair.club_two, not pair.win_one)

    game = LeagueGame.objects.order_by('-id')[0:1][0]
    game.current_order += 1
    game.save()

    logger.write("League Battle Finish.")


uwsgidecorators.cron(int(START_TIME_ONE[1]), int(START_TIME_ONE[0]), -1, -1, -1)(league_battle)
uwsgidecorators.cron(int(START_TIME_TWO[1]), int(START_TIME_TWO[0]), -1, -1, -1)(league_battle)
