# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 17:43
Description:

"""

from utils.http import ProtobufResponse

from core.challenge import Challenge

from protomsg.challenge_pb2 import (
    ChallengeStartResponse,
    ChallengeBuyEnergyResponse,
    ChallengeMatchReportResponse,
    ChapterGetStarRewardResponse,
    ChallengeSweepResponse,
)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    challenge_id = request._proto.id

    c = Challenge(server_id, char_id)
    msg = c.start(challenge_id)

    response = ChallengeStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)

def sweep(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    challenge_id = request._proto.id

    c = Challenge(server_id, char_id)
    drops = c.sweep(challenge_id)

    response = ChallengeSweepResponse()
    response.ret = 0
    for drop in drops:
        response_drop = response.drop.add()
        for _id, _amount in drop:
            response_drop_item = response_drop.items.add()
            response_drop_item.id = _id
            response_drop_item.amount = _amount

    return ProtobufResponse(response)

def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    star = request._proto.star

    items = Challenge(server_id, char_id).report(key, star)
    response = ChallengeMatchReportResponse()
    response.ret = 0

    # TODO drop message
    for _id, _amount in items:
        drop_item = response.drop.items.add()
        drop_item.id = _id
        drop_item.amount = _amount

    return ProtobufResponse(response)


def chapter_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    chapter_id = request._proto.area_id
    index = request._proto.index

    item_id, item_amount = Challenge(server_id, char_id).get_chapter_reward(chapter_id, index)
    response = ChapterGetStarRewardResponse()
    response.ret = 0

    response_drop = response.drop.items.add()
    response_drop.id = item_id
    response_drop.amount = item_amount
    return ProtobufResponse(response)


def buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Challenge(server_id, char_id).buy_energy()

    response = ChallengeBuyEnergyResponse()
    response.ret = 0

    return ProtobufResponse(response)
