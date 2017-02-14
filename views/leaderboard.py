# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       leaderboard
Date Created:   2017-02-14 10:49
Description:

"""

from utils.http import ProtobufResponse
from core.winning import Worship
from core.common import CommonArenaWinningChat, CommonPlunderWinningChat, CommonChampionshipChat

from protomsg.leaderboard_pb2 import (
    LeaderboardWorshipResponse,
    LeaderboardArenaChatResponse,
    LeaderboardArenaChatApprovalResponse,
    LeaderboardPlunderChatResponse,
    LeaderboardPlunderChatApprovalResponse,
    LeaderboardChampionshipChatResponse,
    LeaderboardChampionshipChatApprovalResponse,
)


def worship(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    ws = Worship(server_id, char_id)
    drop = ws.worship()

    response = LeaderboardWorshipResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)

def arena_chat(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    content = request._proto.content

    cc = CommonArenaWinningChat(server_id, char_id)
    cc.post(content)

    response = LeaderboardArenaChatResponse()
    response.ret = 0
    return ProtobufResponse(response)

def arena_approval(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    msg_id = request._proto.msg_id

    cc = CommonArenaWinningChat(server_id, char_id)
    cc.approval(msg_id)

    response = LeaderboardArenaChatApprovalResponse()
    response.ret = 0
    return ProtobufResponse(response)

def plunder_chat(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    content = request._proto.content

    cc = CommonPlunderWinningChat(server_id, char_id)
    cc.post(content)

    response = LeaderboardPlunderChatResponse()
    response.ret = 0
    return ProtobufResponse(response)

def plunder_approval(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    msg_id = request._proto.msg_id

    cc = CommonPlunderWinningChat(server_id, char_id)
    cc.approval(msg_id)

    response = LeaderboardPlunderChatApprovalResponse()
    response.ret = 0
    return ProtobufResponse(response)

def championship_chat(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    content = request._proto.content

    cc = CommonChampionshipChat(server_id, char_id)
    cc.post(content)

    response = LeaderboardChampionshipChatResponse()
    response.ret = 0
    return ProtobufResponse(response)

def championship_approval(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    msg_id = request._proto.msg_id

    cc = CommonChampionshipChat(server_id, char_id)
    cc.approval(msg_id)

    response = LeaderboardArenaChatApprovalResponse()
    response.ret = 0
    return ProtobufResponse(response)
