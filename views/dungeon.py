"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 20:02
Description:

"""

from core.dungeon import DungeonManager

from utils.http import ProtobufResponse

from protomsg.dungeon_pb2 import DungeonMatchResponse, DungeonMathReportResponse


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    dungeon_id = request._proto.id

    match = DungeonManager(server_id, char_id).start(dungeon_id)
    response = DungeonMatchResponse()
    response.ret = 0
    response.match = match

    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    star = request._proto.star

    drop = DungeonManager(server_id, char_id).report(key, star)
    response = DungeonMathReportResponse()
    response.ret = 0

    for _id, _amount in drop:
        drop_item = response.drop.items.add()
        drop_item.id = _id
        drop_item.amount = _amount

    return ProtobufResponse(response)
