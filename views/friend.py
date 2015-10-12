# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       friend
Date Created:   2015-07-29 18:29
Description:

"""

from utils.http import ProtobufResponse

from core.friend import FriendManager

from protomsg.friend_pb2 import (
    FriendGetInfoResponse,
    FriendAddResponse,
    FriendRemoveResponse,
    FriendAcceptResponse,
    FriendMatchResponse,
)

def get_info(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    friend_id = request._proto.id


    fm = FriendManager(server_id, char_id)
    char, club = fm.get_info(friend_id)

    response = FriendGetInfoResponse()
    response.ret = 0
    response.char.MergeFrom(char.make_protomsg())
    response.club.MergeFrom(club.make_protomsg())

    return ProtobufResponse(response)


def add(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    name = request._proto.name


    fm = FriendManager(server_id, char_id)
    fm.add(name)

    response = FriendAddResponse()
    response.ret = 0
    return ProtobufResponse(response)


def remove(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    friend_id = request._proto.id


    fm = FriendManager(server_id, char_id)
    fm.remove(friend_id)

    response = FriendRemoveResponse()
    response.ret = 0
    return ProtobufResponse(response)


def accept(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    friend_id = request._proto.id

    fm = FriendManager(server_id, char_id)
    fm.accept(friend_id)

    response = FriendAcceptResponse()
    response.ret = 0
    return ProtobufResponse(response)


def match(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    friend_id = request._proto.id


    fm = FriendManager(server_id, char_id)
    msg = fm.match(friend_id)

    response = FriendMatchResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    return ProtobufResponse(response)

