# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 18:14
Description:

"""

from utils.http import ProtobufResponse

from core.union import Union, get_all_unions

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
