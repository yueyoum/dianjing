# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       misc
Date Created:   2017-01-14 17:52
Description:

"""
import base64
from dianjing.exception import GameException

from utils.http import ProtobufResponse
from core.match import MatchRecord

from config import ConfigErrorMessage
from protomsg.match_pb2 import ClubMatchLogResponse

def get_match_log(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    log_id = request._proto.log_id

    obj = MatchRecord.get(server_id, log_id)
    if not obj:
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    # TODO
    # if obj.record == base64.b64decode('AAAAAA=='):
    #     raise GameException(ConfigErrorMessage.get_error_id("EMPTY_MATCH"))

    response = ClubMatchLogResponse()
    response.ret = 0
    response.match.MergeFromString(obj.club_match)
    response.record = obj.record

    return ProtobufResponse(response)
