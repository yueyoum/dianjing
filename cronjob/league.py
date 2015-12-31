# # -*- coding: utf-8 -*-
# """
# Author:         Wang Chao <yueyoum@gmail.com>
# Filename:       league
# Date Created:   2015-05-18 15:28
# Description:
#
# """
#
# import traceback
#
# import arrow
# import uwsgidecorators
#
# from django.conf import settings
# from apps.server.models import Server
# from cronjob.log import Logger
# from core.league import LeagueGame
# from config.settings import LEAGUE_START_TIME_ONE, LEAGUE_START_TIME_TWO
#
# time_one = arrow.get(LEAGUE_START_TIME_ONE, "HH:mm:ssZ").to(settings.TIME_ZONE)
# time_two = arrow.get(LEAGUE_START_TIME_TWO, "HH:mm:ssZ").to(settings.TIME_ZONE)
#
#
# # 每周创建新的联赛
# @uwsgidecorators.cron(0, 0, -1, -1, 1, target="spooler")
# def league_new(*args):
#     logger = Logger("league_new")
#     logger.write("Start")
#
#     try:
#         server_ids = Server.opened_server_ids()
#         for s in server_ids:
#             logger.write("server {0} start".format(s))
#             LeagueGame.new(s)
#             logger.write("server {0} finish".format(s))
#     except:
#         logger.error(traceback.format_exc())
#     else:
#         logger.write("Done")
#     finally:
#         logger.close()
#
#
# # 每天定时开启的比赛
# def league_match(*args):
#     logger = Logger("league_match")
#     logger.write("Start")
#
#     try:
#         server_ids = Server.opened_server_ids()
#         for s in server_ids:
#             logger.write("server {0} start".format(s))
#             LeagueGame.start_match(s)
#             logger.write("server {0} finish".format(s))
#     except:
#         logger.error(traceback.format_exc())
#     else:
#         logger.write("Done")
#     finally:
#         logger.close()
#
#
# uwsgidecorators.cron(time_one.minute, time_one.hour, -1, -1, -1, target="spooler")(league_match)
# uwsgidecorators.cron(time_two.minute, time_two.hour, -1, -1, -1, target="spooler")(league_match)
