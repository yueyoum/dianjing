
from core.unit import UnitManager

from utils.http import ProtobufResponse

from protomsg.unit_pb2 import UnitLevelUpResponse, UnitStepUpResponse, UnitDestroyResponse


def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    uid = request._proto.id
    single = request._proto.single

    if single:
        add_level = 1
    else:
        add_level = 5

    UnitManager(server_id, char_id).level_up(uid, add_level)

    response = UnitLevelUpResponse()
    response.ret = 0

    return ProtobufResponse(response)


def step_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    uid = request._proto.id

    UnitManager(server_id, char_id).step_up(uid)

    response = UnitStepUpResponse()
    response.ret = 0

    return ProtobufResponse(response)

def destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    uid = request._proto.id
    using_sycee = request._proto.using_sycee

    um = UnitManager(server_id, char_id)
    rc = um.destroy(uid, using_sycee)

    response = UnitDestroyResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())

    return ProtobufResponse(response)
