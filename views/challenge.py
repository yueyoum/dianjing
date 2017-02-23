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
    ChallengeMatchReportResponse,
    ChapterGetStarRewardResponse,
    ChallengeSweepResponse,
    ChallengeResetResponse,
)

from views.helper import parse_protocol_sync_formation_slots


def reset(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    challenge_id = request._proto.id

    c = Challenge(server_id, char_id)
    c.reset(challenge_id)

    response = ChallengeResetResponse()
    response.ret = 0
    return ProtobufResponse(response)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    challenge_id = request._proto.id

    formation_slots = parse_protocol_sync_formation_slots(request._proto.slots)

    c = Challenge(server_id, char_id)
    msg = c.start(challenge_id, formation_slots)

    response = ChallengeStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)

def sweep(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    challenge_id = request._proto.id
    tp = request._proto.tp

    c = Challenge(server_id, char_id)
    resource_classified_list = c.sweep(challenge_id, tp)

    response = ChallengeSweepResponse()
    response.ret = 0
    for r in resource_classified_list:
        response_drop = response.drop.add()
        response_drop.MergeFrom(r.make_protomsg())
    return ProtobufResponse(response)

def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    star = request._proto.star

    resource_classified = Challenge(server_id, char_id).report(key, star)
    response = ChallengeMatchReportResponse()
    response.ret = 0
    if resource_classified:
        response.drop.MergeFrom(resource_classified.make_protomsg())

    return ProtobufResponse(response)

def chapter_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    chapter_id = request._proto.id
    index = request._proto.index

    resource_classified = Challenge(server_id, char_id).get_chapter_reward(chapter_id, index)
    response = ChapterGetStarRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())

    return ProtobufResponse(response)
