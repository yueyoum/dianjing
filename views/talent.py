"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-15 00:45
Description:

"""

from core.talent import TalentManager

from utils.http import ProtobufResponse

from protomsg.talent_pb2 import TalentLevelUpResponse, TalentResetTalentResponse


def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    talent_id = request._proto.talent_id

    TalentManager(server_id, char_id).level_up(talent_id)
    response = TalentLevelUpResponse()
    response.ret = 0

    return ProtobufResponse(response)


def reset(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    TalentManager(server_id, char_id).reset()
    response = TalentResetTalentResponse()
    response.ret = 0

    return ProtobufResponse(response)
