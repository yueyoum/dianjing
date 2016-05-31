"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 20:02
Description:

"""

from core.dungeon import Dungeon

from utils.http import ProtobufResponse

from protomsg.dungeon_pb2 import DungeonMatchResponse, DungeonMatchReportResponse, DungeonBuyTimesResponse



def buy_times(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    category_id = request._proto.id

    Dungeon(server_id, char_id).buy_times(category_id)

    response = DungeonBuyTimesResponse()
    response.ret = 0
    return ProtobufResponse(response)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    dungeon_id = request._proto.id

    msg = Dungeon(server_id, char_id).start(dungeon_id)
    response = DungeonMatchResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    star = request._proto.star

    drop = Dungeon(server_id, char_id).report(key, star)
    response = DungeonMatchReportResponse()
    response.ret = 0

    if drop:
        response.drop.MergeFrom(drop.make_protomsg())

    return ProtobufResponse(response)
