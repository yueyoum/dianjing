# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 18:14
Description:

"""

from dianjing.exception import GameException
from utils.http import ProtobufResponse
from config import ConfigErrorMessage

from core.union import (
    Union,
    get_all_unions,
    get_unions_ordered_by_explore_point,
    get_members_ordered_by_explore_point,
)
from core.club import get_club_property

from protomsg.union_pb2 import (
    UnionAgreeResponse,
    UnionApplyResponse,
    UnionCreateResponse,
    UnionKickResponse,
    UnionListResponse,
    UnionQuitResponse,
    UnionRefuseResponse,
    UnionSetBulletinResponse,
    UnionSigninResponse,
    UnionTransferResponse,

    UnionExploreLeaderboardResponse,
    UnionExploreResponse,
    UnionHarassQueryResponse,
    UnionHarassResponse,
    UnionHarassBuyTimesResponse,
    UnionSkillLevelupResponse,
)

def get_list(request):
    server_id = request._game_session.server_id
    # char_id = request._game_session.char_id

    unions = get_all_unions(server_id)

    response = UnionListResponse()
    response.ret = 0

    for _, v in unions.iteritems():
        response_union = response.union.add()
        response_union.id = v.id
        response_union.rank = v.rank
        response_union.level = v.level
        response_union.name = v.name
        response_union.members_amount = v.members_amount
        response_union.bulletin = v.bulletin

    return ProtobufResponse(response)


def create(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    name = request._proto.name

    u = Union(server_id, char_id)
    u.create(name)

    response = UnionCreateResponse()
    response.ret = 0
    return ProtobufResponse(response)


def set_bulletin(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    content = request._proto.bulletin

    u = Union(server_id, char_id)
    u.set_bulletin(content)

    response = UnionSetBulletinResponse()
    response.ret = 0
    return ProtobufResponse(response)


def apply_union(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    union_id = request._proto.union_id

    u = Union(server_id, char_id)
    u.apply_union(union_id)

    response = UnionApplyResponse()
    response.ret = 0
    return ProtobufResponse(response)

def agree(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.char_id

    u = Union(server_id, char_id)
    u.agree(int(target_id))

    response = UnionAgreeResponse()
    response.ret = 0
    return ProtobufResponse(response)

def refuse(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.char_id

    u = Union(server_id, char_id)
    u.refuse(int(target_id))

    response = UnionRefuseResponse()
    response.ret = 0
    return ProtobufResponse(response)

def kick(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.char_id

    u = Union(server_id, char_id)
    u.kick(int(target_id))

    response = UnionKickResponse()
    response.ret = 0
    return ProtobufResponse(response)

def transfer(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.char_id

    u = Union(server_id, char_id)
    u.transfer(int(target_id))

    response = UnionTransferResponse()
    response.ret = 0
    return ProtobufResponse(response)

def quit(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    u = Union(server_id, char_id)
    u.quit()

    response = UnionQuitResponse()
    response.ret = 0
    return ProtobufResponse(response)

def signin(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    u = Union(server_id, char_id)
    rc = u.sign_in(_id)

    response = UnionSigninResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)

def explore_leader_board(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    members, self_member = get_members_ordered_by_explore_point(server_id, char_id, limit=10)
    unions, self_union = get_unions_ordered_by_explore_point(server_id, char_id)

    response = UnionExploreLeaderboardResponse()
    response.ret = 0

    if self_member:
        response.my_club.rank = self_member.rank
        response.my_club.id = str(self_member.id)
        response.my_club.name = self_member.name
        response.my_club.explore_point = self_member.explore_point
    else:
        response.my_club.rank = 0
        response.my_club.id = str(char_id)
        response.my_club.name = get_club_property(server_id, char_id, 'name')
        response.my_club.explore_point = 0

    if self_union:
        response.my_union.rank = self_union.rank
        response.my_union.id = self_union.id
        response.my_union.name = self_union.name
        response.my_union.explore_point = self_union.explore_point
    else:
        _union = Union(server_id, char_id)
        _union_id = _union.get_joined_union_id()
        if not _union_id:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        response.my_union.rank = 0
        response.my_union.id = _union_id
        response.my_union.name = _union.union_doc['name']
        response.my_union.explore_point = 0

    for i in range(10):
        try:
            m = members[i]
        except IndexError:
            break

        res_club = response.club.add()
        res_club.rank = m.rank
        res_club.id = str(m.id)
        res_club.name = m.name
        res_club.explore_point = m.explore_point

    for i in range(10):
        try:
            u = unions[i]
        except IndexError:
            break

        res_union = response.union.add()
        res_union.rank = u.rank
        res_union.id = u.id
        res_union.name = u.name
        res_union.explore_point = u.explore_point

    return ProtobufResponse(response)

def explore(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    u = Union(server_id, char_id)
    explore_point, rc = u.explore(staff_id)

    response = UnionExploreResponse()
    response.ret = 0
    response.explore_point = explore_point
    response.drop.MergeFrom(rc.make_protomsg())

    return ProtobufResponse(response)

def harass_query_union(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    u = Union(server_id, char_id)
    unions, self_union = u.query_by_explore_point_rank()

    response = UnionHarassQueryResponse()
    response.ret = 0

    if not self_union:
        response.my_union.rank = 0
        response.my_union.id = u.union_doc['_id']
        response.my_union.name = u.union_doc['name']
        response.my_union.explore_point = 0
    else:
        response.my_union.rank = self_union.rank
        response.my_union.id = self_union.id
        response.my_union.name = self_union.name
        response.my_union.explore_point = self_union.explore_point

    for u in unions:
        res_union = response.union.add()
        res_union.rank = u.rank
        res_union.id = u.id
        res_union.name = u.name
        res_union.explore_point = u.explore_point

    return ProtobufResponse(response)

def harass(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    union_id = request._proto.union_id
    staff_id = request._proto.staff_id

    u = Union(server_id, char_id)
    explore_point, rc, my_explore_point = u.harass(union_id, staff_id)

    response = UnionHarassResponse()
    response.ret = 0
    response.explore_point = explore_point
    response.my_explore_point = my_explore_point
    response.drop.MergeFrom(rc.make_protomsg())

    return ProtobufResponse(response)

def harass_buy_times(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    u = Union(server_id, char_id)
    u.harass_buy_times()

    response = UnionHarassBuyTimesResponse()
    response.ret = 0
    return ProtobufResponse(response)

def skill_level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    skill_id = request._proto.skill_id
    u = Union(server_id, char_id)
    u.skill_level_up(skill_id)

    response = UnionSkillLevelupResponse()
    response.ret = 0
    return ProtobufResponse(response)
