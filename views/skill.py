# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 11:42
Description:

"""


from utils.http import ProtobufResponse

from core.skill import SkillManager

from protomsg.skill_pb2 import SkillLockToggleResponse, SkillWashResponse, SkillUpgradeResponse, SkillUpgradeSpeedupResponse



def lock_toggle(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    skill_id = request._proto.skill_id

    sk = SkillManager(server_id, char_id)
    sk.lock_toggle(staff_id, skill_id)

    response = SkillLockToggleResponse()
    response.ret = 0
    return ProtobufResponse(response)



def wash(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    sk = SkillManager(server_id, char_id)
    sk.wash(staff_id)

    response = SkillWashResponse()
    response.ret = 0
    return ProtobufResponse(response)


def upgrade(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    skill_id = request._proto.skill_id

    sk = SkillManager(server_id, char_id)
    sk.upgrade(staff_id, skill_id)

    response = SkillUpgradeResponse()
    response.ret = 0
    return ProtobufResponse(response)

def upgrade_speedup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    skill_id = request._proto.skill_id

    sk = SkillManager(server_id, char_id)
    sk.upgrade_speedup(staff_id, skill_id)

    response = SkillUpgradeSpeedupResponse()
    response.ret = 0
    return ProtobufResponse(response)
