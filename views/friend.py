# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       friend
Date Created:   2015-07-29 18:29
Description:

"""

from utils.http import ProtobufResponse

from core.mongo import MongoCharacter
from core.friend import FriendManager

from protomsg.friend_pb2 import (
    FRIEND_NOT,
    FriendGetInfoResponse,
    FriendAddResponse,
    FriendRemoveResponse,
    FriendAcceptResponse,
    FriendMatchResponse,
    FriendCandidatesResponse,
)


def get_candidates(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    fm = FriendManager(server_id, char_id)
    candidates = fm.get_candidates()

    response = FriendCandidatesResponse()

    if not candidates:
        return ProtobufResponse(response)

    char_docs = MongoCharacter.db(server_id).find(
        {'_id': {'$in': candidates}},
        # TODO, other fields
        {'name': 1, 'club': 1}
    )

    char_dict = {c['_id']: c for c in char_docs}

    for c in candidates:
        notify_friend = response.friends.add()
        notify_friend.status = FRIEND_NOT
        notify_friend.id = str(c)
        notify_friend.name = char_dict[c]['name']
        # TODO
        notify_friend.avatar = ""
        notify_friend.club_name = char_dict[c]['club']['name']
        notify_friend.club_flag = char_dict[c]['club']['flag']
        notify_friend.club_gold = char_dict[c]['club']['gold']
        notify_friend.club_level = char_dict[c]['club']['level']


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
