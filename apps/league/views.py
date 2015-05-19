from apps.league.core import League

from utils.http import ProtobufResponse

from protomsg.league_pb2 import LeagueGetStatisticsResponse, LeagueGetBattleLogResponse
from protomsg.common_pb2 import CLUB_TYPE_REAL


def get_statistics(request):
    req = request._proto
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    club_id = request._game_session.club_id

    l = League(server_id, char_id, club_id)

    if req.tp == CLUB_TYPE_REAL:
        statistics = l.get_club_statistics(req.id)
    else:
        statistics = l.get_npc_statistics(req.id)

    response = LeagueGetStatisticsResponse()
    response.ret = 0
    for oid, winning_rate in statistics:
        response_s = response.statistics.add()
        response_s.staff_oid = oid
        response_s.winning_rate_to_terran = winning_rate['t']
        response_s.winning_rate_to_zerg = winning_rate['z']
        response_s.winning_rate_to_protoss = winning_rate['p']

    return ProtobufResponse(response)


def get_battle_log(request):
    req = request._proto
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    club_id = request._game_session.club_id

    l = League(server_id, char_id, club_id)

    logs = l.get_battle_log(req.pair_id)

    response = LeagueGetBattleLogResponse()
    response.ret = 0

    for club_one, club_two in logs:
        response_log = response.logs.add()
        response_log.club_one_staff.staff_oid, \
        response_log.club_one_staff.level, \
        response_log.club_one_staff.win = club_one

        response_log.club_two_staff.staff_oid, \
        response_log.club_two_staff.level, \
        response_log.club_two_staff.win = club_two

    return ProtobufResponse(response)
