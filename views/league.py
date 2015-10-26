# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-07-23 19:04
Description:

"""

from utils.http import ProtobufResponse
from core.league import League

from protomsg.league_pb2 import LeagueGetStatisticsResponse, LeagueGetBattleLogResponse

def get_statistics(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    league_club_id = request._proto.id

    l = League(server_id, char_id)
    data = l.get_statistics(league_club_id)

    response = LeagueGetStatisticsResponse()
    response.ret = 0
    for staff_id, winning_rate in data.iteritems():
        ss = response.statistics.add()
        ss.staff_id = staff_id
        ss.winning_rate_to_terran = winning_rate['1']
        ss.winning_rate_to_zerg = winning_rate['2']
        ss.winning_rate_to_protoss = winning_rate['3']

    return ProtobufResponse(response)


def get_log(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    league_pair_id = request._proto.pair_id

    l = League(server_id, char_id)
    log = l.get_log(league_pair_id)

    response = LeagueGetBattleLogResponse()
    response.ret = 0
    response.match_log.MergeFromString(log)

    return ProtobufResponse(response)

