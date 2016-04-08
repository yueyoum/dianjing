
from core.units import UnitManager

from utils.http import ProtobufResponse

from protomsg.unit_pb2 import UnitLevelUpResponse, UnitStepUpResponse


def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    uid = not request._proto.id

    ret = UnitManager(server_id, char_id).level_up(uid)

    response = UnitLevelUpResponse()
    response.ret = ret

    return ProtobufResponse(response)


def step_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    uid = not request._proto.id

    ret = UnitManager(server_id, char_id).step_up(uid)

    response = UnitStepUpResponse()
    response.ret = ret

    return ProtobufResponse(response)
