# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-08-19 14:13
Description:

"""

from utils.http import ProtobufResponse

from core.ladder import Ladder, LadderStore

from protomsg.ladder_pb2 import (
    LadderRefreshResponse,
    LadderMatchResponse,
    LadderLeaderBoardResponse,
    LadderStoreBuyResponse,
    LadderStoreRefreshResponse,
)


def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Ladder(server_id, char_id).make_refresh()

    response = LadderRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def match(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.id

    ladder = Ladder(server_id, char_id)
    msg, drop = ladder.match(target_id)

    response = LadderMatchResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    response.drop.MergeFrom(drop)
    return ProtobufResponse(response)


def get_leader_board(request):
    server_id = request._game_session.server_id

    clubs = Ladder.get_top_clubs(server_id)

    response = LadderLeaderBoardResponse()
    response.ret = 0
    for club in clubs:
        c = response.clubs.add()
        c.id = str(club.id)
        c.name = club.name
        c.flag = club.flag
        c.order = club.order
        c.power = 999
        c.score = club.score

    return ProtobufResponse(response)


def store_refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    s = LadderStore(server_id, char_id)
    s.items = LadderStore.refresh(s.server_id, force=True)
    s.send_notify()

    response = LadderStoreRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def store_buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    item_id = request._proto.id

    s = LadderStore(server_id, char_id)
    s.buy(item_id)

    response = LadderStoreBuyResponse()
    response.ret = 0
    return ProtobufResponse(response)
