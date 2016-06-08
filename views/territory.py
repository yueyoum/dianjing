# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-17 16-03
Description:

"""

from utils.http import ProtobufResponse

from core.territory import Territory, TerritoryStore, TerritoryFriend

from protomsg.territory_pb2 import (
    TerritoryTrainingGetRewardResponse,
    TerritoryTrainingStartResponse,
    TerritoryFriendHelpResponse,
    TerritoryFriendListResponse,
    TerritoryMatchReportResponse,
    TerritoryStoreBuyResponse,
    TerritoryInspireResponse,
)

def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id
    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id
    hour = request._proto.hour

    t = Territory(server_id, char_id)
    t.training_star(building_id, slot_id, staff_id, hour)

    response = TerritoryTrainingStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id
    slot_id = request._proto.slot_id

    t = Territory(server_id, char_id)
    resource_classified = t.training_get_reward(building_id, slot_id)

    response = TerritoryTrainingGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def store_buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    t = TerritoryStore(server_id, char_id)
    resource_classified = t.buy(_id)

    response = TerritoryStoreBuyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def friend_list(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tf = TerritoryFriend(server_id, char_id)
    info = tf.get_list()

    response = TerritoryFriendListResponse()
    response.ret = 0
    for fid, b_list in info.iteritems():
        response_friend = response.friends.add()
        response_friend.id = str(fid)

        for b_data in b_list:
            r_f_building = response_friend.buildings.add()
            r_f_building.id = b_data['id']
            r_f_building.level = b_data['level']
            r_f_building.event_id = b_data['event_id']

    return ProtobufResponse(response)


def friend_help(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    friend_id = request._proto.friend_id
    building_id = request._proto.building_id

    tf = TerritoryFriend(server_id, char_id)
    match, drop = tf.help(friend_id, building_id)

    response = TerritoryFriendHelpResponse()
    response.ret = 0
    if match:
        response.match.MergeFrom(match)
    else:
        response.drop.MergeFrom(drop.make_protomsg())

    return ProtobufResponse(response)


def friend_report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win = request._proto.win

    tf = TerritoryFriend(server_id, char_id)
    resource_classified = tf.match_report(key, win)

    response = TerritoryMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def inspire(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id

    t = Territory(server_id, char_id)
    drop = t.inspire_building(building_id)

    response = TerritoryInspireResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(drop.make_protomsg())

    return ProtobufResponse(response)