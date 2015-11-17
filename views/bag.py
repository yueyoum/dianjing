# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2015-11-17 11:49
Description:

"""

from utils.http import ProtobufResponse

from core.bag import BagTrainingSkill, BagItem

from protomsg.package_pb2 import TrainingSkillSellResponse, ItemSellResponse

def item_sell(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id
    amount = request._proto.amount

    bag = BagItem(server_id, char_id)
    bag.sell(_id, amount)

    response = ItemSellResponse()
    response.ret = 0
    return ProtobufResponse(response)


def training_skill_sell(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id
    amount = request._proto.amount

    bag = BagTrainingSkill(server_id, char_id)
    bag.sell(_id, amount)

    response = TrainingSkillSellResponse()
    response.ret = 0
    return ProtobufResponse(response)
