# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       energy
Date Created:   2016-06-02 11-19
Description:

"""


from utils.http import ProtobufResponse
from core.energy import Energy

from protomsg.energy_pb2 import EnergyBuyResponse




def buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Energy(server_id, char_id).buy()

    response = EnergyBuyResponse()
    response.ret = 0
    return ProtobufResponse(response)
