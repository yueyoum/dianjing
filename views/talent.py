"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-15 00:45
Description:

"""

from core.talent import TalentManager

from utils.http import ProtobufResponse

# from protomsg.unit_pb2 impor


def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tp = request._proto.tp
    position = request._proto.position

    ret = TalentManager(server_id, char_id).level_up(tp, position)


def reset(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    ret = TalentManager(server_id, char_id).reset()
